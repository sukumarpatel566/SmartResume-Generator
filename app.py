from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

app = Flask(__name__)

# Define template styles
TEMPLATE_STYLES = {
    "professional": {
        "font": "Helvetica-Bold",
        "color": colors.darkblue,
        "line_color": colors.darkblue,
        "heading_size": 14,
        "text_size": 10,
    },
    "minimalistic": {
        "font": "Courier-Bold",
        "color": colors.darkgray,
        "line_color": colors.darkgray,
        "heading_size": 12,
        "text_size": 10,
    },
    "creative": {
        "font": "Times-Bold",
        "color": colors.darkgreen,
        "line_color": colors.darkgreen,
        "heading_size": 16,
        "text_size": 12,
    },
    "modern": {
        "font": "Helvetica-BoldOblique",
        "color": colors.purple,
        "line_color": colors.purple,
        "heading_size": 14,
        "text_size": 10,
    },
}

def draw_header(c, name, contact, y, style):
    """Draws the header section with name and contact details."""
    c.setFont(style["font"], 18)
    c.setFillColor(style["color"])
    c.drawString(50, y, name)
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(50, y - 20, contact)
    return y - 40

def draw_section_title(c, title, y, style):
    """Draws a section title with an underline."""
    c.setFont(style["font"], style["heading_size"])
    c.setFillColor(style["color"])
    c.drawString(50, y, title.upper())
    c.setStrokeColor(style["line_color"])
    c.line(50, y - 2, 550, y - 2)  # Underline
    return y - 20

def draw_text(c, x, y, text, style):
    """Draws text at the specified position."""
    c.setFont("Helvetica", style["text_size"])
    c.setFillColor(colors.black)
    c.drawString(x, y, text)
    return y - 15

def draw_bullet(c, x, y, text, style):
    """Draws bullet points."""
    c.setFont("Helvetica", style["text_size"])
    c.setFillColor(colors.black)
    c.drawString(x, y, "• " + text)
    return y - 15

def generate_resume(details, template="professional", filename="resume.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    style = TEMPLATE_STYLES.get(template, TEMPLATE_STYLES["professional"])

    # Header Section
    contact_info = f"{details.get('phone', '')} • {details.get('linkedin', '')} • {details.get('github', '')} • {details.get('email', '')}"
    y = height - 50
    y = draw_header(c, details.get("name", "Your Name"), contact_info, y, style)

    # Career Objective
    y = draw_section_title(c, "Career Objective", y, style)
    y = draw_text(c, 50, y, details.get("objective", ""), style)

    # Education
    y = draw_section_title(c, "Education", y, style)
    for edu in details.get("education", []):
        parts = edu.split("|")
        if len(parts) == 4:
            y = draw_text(c, 50, y, parts[0], style)  # Degree
            y = draw_text(c, 50, y, parts[1], style)  # Institution
            y = draw_text(c, 50, y, f"Relevant coursework: {parts[2]}", style)
            y = draw_text(c, 50, y, parts[3], style)  # Year
        y -= 10  # Extra space between entries

    # Project Experience
    y = draw_section_title(c, "Project Experience", y, style)
    for project in details.get("projects", []):
        parts = project.split("|")
        if len(parts) >= 2:
            y = draw_text(c, 50, y, parts[0], style)  # Project title
            for line in parts[1].split("\\n"):
                y = draw_bullet(c, 60, y, line, style)
        y -= 10  # Extra space between entries

    # Technical Proficiency
    y = draw_section_title(c, "Technical Proficiency", y, style)
    y = draw_text(c, 50, y, ", ".join(details.get("skills", "").split(",")), style)

    # Certifications
    y = draw_section_title(c, "Certifications", y, style)
    for cert in details.get("certifications", []):
        y = draw_bullet(c, 60, y, cert, style)

    # Soft Skills
    y = draw_section_title(c, "Soft Skills", y, style)
    y = draw_text(c, 50, y, ", ".join(details.get("soft_skills", "").split(",")), style)

    c.save()
    return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    details = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone"),
        "email": request.form.get("email"),
        "linkedin": request.form.get("linkedin"),
        "github": request.form.get("github"),
        "objective": request.form.get("objective", ""),
        "education": request.form.get("education", "").split("\n") if request.form.get("education") else [],
        "skills": request.form.get("skills", ""),
        "projects": request.form.get("projects", "").split("\n") if request.form.get("projects") else [],
        "certifications": request.form.get("certifications", "").split("\n") if request.form.get("certifications") else [],
        "soft_skills": request.form.get("soft_skills", ""),
    }
    template = request.form.get("template", "professional")
    filename = generate_resume(details, template)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
