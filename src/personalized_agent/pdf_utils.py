from fpdf import FPDF
import tempfile

async def generate_pdf(user_data: dict) -> str:
    """Generate PDF from travel plan and return temp file path"""
    plan_text = user_data.get("plan", "No plan generated")
    
    pdf = FPDF()
    pdf.add_page()
    
    # Add header with user details
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Travel Plan for {user_data.get('name', '')}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Destination: {user_data.get('destination', '')}", ln=True)
    pdf.cell(0, 10, f"Budget: {user_data.get('src_budget', '')} {user_data.get('src_currency', '')} "
              f"({user_data.get('dest_budget', '')} {user_data.get('dest_currency', '')})", ln=True)
    pdf.cell(0, 10, f"Mood: {user_data.get('mood', '')}", ln=True)
    pdf.ln(10)
    
    # Add plan content
    pdf.set_font("Arial", size=10)
    try:
        plan_text = plan_text.encode('latin-1', 'replace').decode('latin-1')
    except:
        plan_text = plan_text.encode('utf-8', 'replace').decode('latin-1', 'ignore')
    
    for line in plan_text.split('\n'):
        pdf.multi_cell(0, 5, line)

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        return tmpfile.name