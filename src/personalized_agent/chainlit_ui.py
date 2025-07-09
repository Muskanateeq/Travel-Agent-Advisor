import chainlit as cl
import re
import nest_asyncio
from personalized_agent import travel_agent, currency_utils, pdf_utils, config
from personalized_agent.config import MOOD_OPTIONS

nest_asyncio.apply()

# ====== STATE MANAGEMENT =======
@cl.on_chat_start
async def start():
    cl.user_session.set("user_data", {})
    cl.user_session.set("state", "name")
    await cl.Message(content="👋 Welcome to Mood-Based Travel Agent!").send()
    await cl.Message(content="Please enter your name:").send()

@cl.on_message
async def handle_message(message: cl.Message):
    state = cl.user_session.get("state")
    user_data = cl.user_session.get("user_data", {})
    content = message.content.strip().lower()
    
    if state == "name":
        await handle_name(message, user_data)
    elif state == "current_location":
        await handle_location(message, user_data)
    elif state == "destination":
        await handle_destination(message, user_data)
    elif state == "budget":
        await handle_budget(message, user_data)
    elif state == "custom_mood":
        await handle_custom_mood(message, user_data)
    elif state == "customizing":
        await handle_customization(message, user_data)
    elif state == "ask_customization":
        await handle_customization_response(message, user_data)
    elif state == "ask_next_trip":
        await handle_next_trip(message, user_data)

async def handle_name(message: cl.Message, user_data: dict):
    user_data["name"] = message.content
    cl.user_session.set("user_data", user_data)
    cl.user_session.set("state", "current_location")
    await cl.Message(content="📍 Where are you currently located?").send()

async def handle_location(message: cl.Message, user_data: dict):
    user_data["current_location"] = message.content
    user_data["src_currency"] = currency_utils.get_currency(message.content)
    cl.user_session.set("user_data", user_data)
    cl.user_session.set("state", "destination")
    await cl.Message(content="🌍 Where do you want to travel?").send()

async def handle_destination(message: cl.Message, user_data: dict):
    user_data["destination"] = message.content
    user_data["dest_currency"] = currency_utils.get_currency(message.content)
    cl.user_session.set("user_data", user_data)
    cl.user_session.set("state", "budget")
    await cl.Message(content=f"💰 What's your budget in {user_data['src_currency']}?").send()

async def handle_budget(message: cl.Message, user_data: dict):
    budget_value = currency_utils.parse_budget(message.content)
    if budget_value is None:
        await cl.Message(content="⚠️ Please enter a valid budget amount (e.g., 1500 or $1,500)").send()
        return

    user_data["src_budget"] = budget_value
    dest_budget = await currency_utils.convert_currency(
        budget_value, 
        user_data['src_currency'], 
        user_data['dest_currency']
    )
    
    if dest_budget:
        user_data["dest_budget"] = dest_budget
        await cl.Message(
            content=f"💱 Converted budget: {budget_value} {user_data['src_currency']} = "
                    f"{dest_budget} {user_data['dest_currency']}"
        ).send()
    else:
        user_data["dest_budget"] = budget_value
        user_data["dest_currency"] = user_data["src_currency"]
        await cl.Message(content="⚠️ Currency conversion failed. Using original currency").send()
    
    cl.user_session.set("user_data", user_data)
    cl.user_session.set("state", "mood_selection")
    await show_mood_options()

async def handle_custom_mood(message: cl.Message, user_data: dict):
    user_data["mood"] = message.content
    cl.user_session.set("user_data", user_data)
    cl.user_session.set("state", "processing")
    await generate_travel_plan()

async def handle_customization(message: cl.Message, user_data: dict):
    await update_travel_plan(message.content)

async def handle_customization_response(message: cl.Message, user_data: dict):
    content = message.content.strip().lower()
    if content in ["y", "yes"]:
        cl.user_session.set("state", "customizing")
        await cl.Message(content="What would you like to add or change in the plan?").send()
    elif content in ["n", "no"]:
        await show_pdf_option()
        cl.user_session.set("state", "ask_next_trip")
        await cl.Message(content="✈️ Would you like to plan another trip? (y/n)").send()
    else:
        await cl.Message(content="⚠️ Please type 'yes' or 'no'.").send()

async def handle_next_trip(message: cl.Message, user_data: dict):
    content = message.content.strip().lower()
    if content in ["y", "yes"]:
        # Reset session for new trip
        keys_to_keep = ["name", "current_location", "src_currency"]
        new_data = {k: user_data[k] for k in keys_to_keep if k in user_data}
        cl.user_session.set("user_data", new_data)
        cl.user_session.set("state", "destination")
        await cl.Message(content="🌍 Where do you want to travel for your next trip?").send()
    elif content in ["n", "no"]:
        await cl.Message(content="🙏 Thank you for using our service! Have a great journey!").send()
        cl.user_session.set("state", "end")
    else:
        await cl.Message(content="⚠️ Please type 'y' for yes or 'n' for no.").send()

# ====== UI COMPONENTS =======
async def show_mood_options():
    actions = [
        cl.Action(name="mood", payload={"mood": opt["mood"]}, label=opt["label"])
        for opt in MOOD_OPTIONS
    ]
    await cl.Message(content="🎭 Select your travel mood:", author="System", actions=actions).send()

@cl.action_callback("mood")
async def mood_selected(action: cl.Action):
    selected_mood = action.payload["mood"]
    user_data = cl.user_session.get("user_data", {})
    
    if selected_mood == "Custom":
        cl.user_session.set("state", "custom_mood")
        await cl.Message(content="✨ Please describe your desired travel mood:").send()
        return
    
    user_data["mood"] = selected_mood
    cl.user_session.set("user_data", user_data)
    cl.user_session.set("state", "processing")
    await generate_travel_plan()

async def show_pdf_option():
    await cl.Message(
        content="📄 Would you like to download your travel plan as a PDF?",
        actions=[cl.Action(name="pdf", payload={"action": "export"}, label="📥 Download PDF")]
    ).send()

# ====== CORE FUNCTIONALITY =======
async def generate_travel_plan():
    user_data = cl.user_session.get("user_data", {})
    prompt = await travel_agent.build_prompt(user_data)
    
    msg = cl.Message(content="")
    await msg.send()
    
    full_response = ""
    stream = await travel_agent.generate_plan_response(prompt)
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            full_response += token
            await msg.stream_token(token)
    
    await msg.update()
    user_data["plan"] = full_response
    cl.user_session.set("user_data", user_data)
    cl.user_session.set("state", "ask_customization")
    await cl.Message(content="🔧 Would you like to customize or add anything to this plan? (yes/no)").send()

async def update_travel_plan(user_request: str):
    user_data = cl.user_session.get("user_data", {})
    existing_plan = user_data.get("plan", "")
    
    updating_msg = cl.Message(content="🔄 Updating your plan...")
    await updating_msg.send()
    
    prompt = (
        f"Here is the current travel plan:\n{existing_plan}\n\n"
        f"The user wants to make these changes: {user_request}\n\n"
        "Please update the travel plan accordingly while maintaining:\n"
        "- The original format with day-wise sections\n"
        "- Budget constraints\n"
        "- Travel mood\n"
        "- Include all important elements from the original plan\n\n"
        "Provide the complete updated plan in the same format."
    )

    new_msg = cl.Message(content="")
    await new_msg.send()
    
    full_response = ""
    stream = await travel_agent.generate_plan_response(prompt)
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            full_response += token
            await new_msg.stream_token(token)
    
    await new_msg.update()
    await updating_msg.remove()
    
    user_data["plan"] = full_response
    cl.user_session.set("user_data", user_data)
    cl.user_session.set("state", "ask_customization")
    await cl.Message(content="🔧 Would you like to make any more changes? (yes/no)").send()

@cl.action_callback("pdf")
async def export_pdf(action: cl.Action):
    user_data = cl.user_session.get("user_data", {})
    file_path = await pdf_utils.generate_pdf(user_data)
    
    pdf_file = cl.File(
        name=f"{user_data['name']}_Travel_Plan.pdf",
        path=file_path,
        display="inline"
    )
    
    await cl.Message(
        content="✅ Your travel plan PDF is ready! Click below to download:",
        elements=[pdf_file]
    ).send()
    
    await cl.Message(content="✈️ Would you like to plan another trip? (y/n)").send()
    cl.user_session.set("state", "ask_next_trip")