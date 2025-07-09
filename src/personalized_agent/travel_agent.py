from openai import AsyncOpenAI
from personalized_agent.config import GEMINI_API_KEY, BASE_URL, MODEL
from agents import Agent, OpenAIChatCompletionsModel

# ====== AGENT SETUP =======
client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)

agent = Agent(
    name="TravelAgentBot",
    instructions=(
        "You are a professional travel planner. Based on user's mood, budget, and destination, "
        "you suggest a personalized plan including:\n"
        "- Places to visit\n"
        "- Famous food\n"
        "- Hotels (budget wise)\n"
        "- Cost estimates in local currency\n"
        "Respond in a clear, day-wise format with emojis."
    ),
    model=OpenAIChatCompletionsModel(model=MODEL, openai_client=client),
)

async def build_prompt(user_data: dict) -> str:
    """Construct the prompt for the travel agent"""
    return (
        f"My name is {user_data['name']}, I'm from {user_data['current_location']}, "
        f"planning to travel to {user_data['destination']}.\n"
        f"My budget is {user_data['src_budget']} {user_data['src_currency']} "
        f"(≈ {user_data['dest_budget']} {user_data['dest_currency']}) "
        f"and my travel mood is {user_data['mood']}.\n\n"
        "Suggest a detailed travel plan including:\n"
        "- Famous spots to visit\n"
        "- Local food to try\n"
        "- Budget hotels\n"
        "- Estimated costs in local currency\n"
        "- Transportation options\n"
        "- Any special recommendations based on the mood\n\n"
        "Format in clear, day-wise sections with emojis."
    )

async def generate_plan_response(prompt: str):
    """Generate response from the AI model"""
    return await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )