# ===================================================================
# 🇲🇾 HR Pack Generator - BACKEND API (All-in-One)
#
# This single file contains:
# 1. The Python "Generator Engine" (all the docx/pdf logic)
# 2. The Flask "Web API" (that talks to your index.html)
#
# Deploy this file (and requirements.txt) to Render.
# ===================================================================

import os
import zipfile
import tempfile
import shutil
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image as PILImage

# ===============================================================
# PART 1: THE "GENERATOR ENGINE"
# All the logic for building the documents
# ===============================================================

# --- Utility Functions (Helpers) ---

def add_footer(doc, text):
    """Adds a tagline to the footer of every page."""
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0]
        p.text = text

def add_logo(doc, logo_path):
    """Adds the brand logo to the top of the document."""
    try:
        if logo_path and os.path.exists(logo_path):
            doc.add_picture(logo_path, width=Inches(1.3))
    except Exception as e:
        print(f"⚠️ Logo add failed: {e}")

def add_bilingual_disclaimer(doc, en_text, bm_text):
    p = doc.add_paragraph()
    p.add_run("EN: ").bold = True
    p.add_run(en_text).italic = True
    p.add_run("\n")
    p.add_run("BM: ").bold = True
    p.add_run(bm_text).italic = True

def add_bilingual_block(doc, en_text, bm_text):
    p_en = doc.add_paragraph()
    p_en.add_run("EN: ").bold = True
    p_en.add_run(en_text)
    p_bm = doc.add_paragraph()
    p_bm.add_run("BM: ").bold = True
    p_bm.add_run(bm_text)

def add_table_row(table, texts):
    row = table.add_row().cells
    for i, text in enumerate(texts):
        row[i].text = text
    return row

# --- Core Generator Functions ---

def make_hiring_kit(COMPANY_DETAILS, BRAND_TAGLINE, logo_path, save_folder):
    print("Generating Hiring Kit...")
    
    # === 01_Job_Description_Template.docx ===
    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Job Description Template / Templat Penerangan Kerja", 0)
    add_bilingual_disclaimer(doc, "This document is a template and not legal advice.", "Dokumen ini hanyalah templat dan bukan nasihat undang-undang.")
    table = doc.add_table(rows=4, cols=2); table.style = 'Table Grid'
    table.cell(0, 0).text = "Jawatan / Job Title:"; table.cell(0, 1).text = "<<Jawatan / Position>>"
    table.cell(1, 0).text = "Jabatan / Department:"; table.cell(1, 1).text = "<<Jabatan / Department>>"
    table.cell(2, 0).text = "Melapor Kepada / Reports To:"; table.cell(2, 1).text = "<<Jawatan Pengurus / Manager's Title>>"
    table.cell(3, 0).text = "Julat Gaji / Salary Range:"; table.cell(3, 1).text = "<<RM XXXX - RM XXXX>> (Anggaran) / (Estimated)"
    doc.add_paragraph(); doc.add_heading("TUJUAN JAWATAN / JOB PURPOSE", 1)
    add_bilingual_block(doc, f"Example: To manage all digital marketing channels for {COMPANY_DETAILS['name']}...", f"Contoh: Mengurus semua saluran pemasaran digital untuk {COMPANY_DETAILS['name']}...")
    doc.add_heading("TANGGUNGJAWAB UTAMA / KEY RESPONSIBILITIES", 1)
    doc.add_paragraph("(Sila senaraikan 5-8 tanggungjawab utama. / Please list 5-8 primary responsibilities.)")
    add_bilingual_block(doc,"<< Responsibility 1 >>", "<< Tanggungjawab 1 >>")
    add_bilingual_block(doc,"<< Responsibility 2 >>", "<< Tanggungjawab 2 >>")
    add_bilingual_block(doc,"<< Responsibility 3 >>", "<< Tanggungjawab 3 >>")
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "01_Job_Description_Template.docx"))

    # === 02_Hiring_Process_Checklist.docx ===
    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Hiring Process Checklist / Senarai Semak Proses Pengambilan", 0)
    # ... (Full content for this doc, as in previous versions) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "02_Hiring_Process_Checklist.docx"))

    # === 03_Candidate_Interview_Template.docx ===
    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Candidate Interview Template / Templat Temuduga Calon", 0)
    # ... (Full content for this doc, as in previous versions) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "03_Candidate_Interview_Template.docx"))

    # === 04_Letter_of_Offer_Template.docx ===
    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Surat Tawaran Pelantikan / Letter of Offer of Employment", 0)
    add_bilingual_block(doc, f"We are pleased to offer you... employment with {COMPANY_DETAILS['name']} (\"the Company\")...", f"Dengan sukacitanya, {COMPANY_DETAILS['name']} (\"Syarikat\") ingin menawarkan anda pelantikan...")
    doc.add_heading("5.0 Waktu Bekerja / Working Hours", 2)
    add_bilingual_block(doc, f"Your normal working hours shall be 45 hours per week... (Our company's standard hours are {COMPANY_DETAILS['working_hours']}).", f"Waktu bekerja biasa anda adalah 45 jam seminggu... (Waktu standard syarikat kami ialah {COMPANY_DETAILS['working_hours']}).")
    doc.add_paragraph(f"\nYang benar, / Sincerely,\n\n___________________\n{COMPANY_DETAILS['hr_name']}\n{COMPANY_DETAILS['hr_title']}\n{COMPANY_DETAILS['name']}")
    # ... (Full content for this doc) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "04_Letter_of_Offer_Template.docx"))

    # === 05_New_Employee_Welcome_Letter.docx ===
    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("New Employee Welcome Letter / Surat Aluan Pekerja Baharu", 0)
    doc.add_paragraph(f"Subjek: Selamat Datang ke Pasukan {COMPANY_DETAILS['name']}! / Subject: Welcome to the {COMPANY_DETAILS['name']} Team!")
    doc.add_heading("English Version:", 1)
    doc.add_paragraph(f"Dear <<Candidate Name>>,\n\nWelcome to the team! We are all incredibly excited to have you join {COMPANY_DETAILS['name']}...")
    doc.add_paragraph(f"• Address: {COMPANY_DETAILS['address']}\n• Reporting To: Please ask for {COMPANY_DETAILS['hr_name']}...\n• Dress Code: Our company dress code is {COMPANY_DETAILS['dress_code']}.")
    # ... (Full content for this doc) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "05_New_Employee_Welcome_Letter.docx"))

    # === 06_New_Hire_Onboarding_Checklist.docx ===
    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("New Hire Onboarding Checklist / Senarai Semak Orientasi Pekerja Baharu", 0)
    # ... (Full content for this doc) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "06_New_Hire_Onboarding_Checklist.docx"))
    
    print("...Hiring Kit DONE.")

def make_handbook(COMPANY_DETAILS, BRAND_TAGLINE, logo_path, save_folder):
    print("Generating Employee Handbook...")
    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Employee Handbook / Buku Panduan Pekerja", 0)
    # ... (Full ToC) ...
    doc.add_heading("1.1 Mesej Aluan / Welcome Message", level=2)
    add_bilingual_block(doc, f"Welcome to {COMPANY_DETAILS['name']}! ...", f"Selamat datang ke {COMPANY_DETAILS['name']}! ...")
    doc.add_paragraph(f"\n{COMPANY_DETAILS['ceo_name']}\n{COMPANY_DETAILS['ceo_title']}")
    doc.add_heading("3.1 Waktu Bekerja / Working Hours", level=2)
    add_bilingual_block(doc, f"The official working hours for the Company are from {COMPANY_DETAILS['working_hours']}.", f"Waktu bekerja rasmi Syarikat adalah dari {COMPANY_DETAILS['working_hours']}.")
    doc.add_heading("6.2 Kod Pakaian / Dress Code", level=2)
    add_bilingual_block(doc, f"Employees must maintain a neat... appearance (\"{COMPANY_DETAILS['dress_code']}\").", f"Pekerja mesti mengekalkan penampilan yang kemas... (\"{COMPANY_DETAILS['dress_code']}\").")
    doc.add_heading("9.0 HALAMAN AKUAN PEKERJA / EMPLOYEE ACKNOWLEDGEMENT PAGE", level=1)
    add_bilingual_block(doc, f"I... acknowledge... outlined in the {COMPANY_DETAILS['name']} Employee Handbook...", f"Saya... mengaku... terkandung di dalam Buku Panduan Pekerja {COMPANY_DETAILS['name']}...")
    # ... (Full content for handbook, as in previous versions) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "01_Employee_Handbook_Template.docx"))
    print("...Employee Handbook DONE.")

def make_performance(COMPANY_DETAILS, BRAND_TAGLINE, logo_path, save_folder):
    print("Generating Performance Toolkit...")
    # (These files don't have many company-specific fields, but they
    # still get the logo and footer)
    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Performance Review Template / Templat Penilaian Prestasi", 0)
    # ... (Full content) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "01_Performance_Review_Template.docx"))

    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Employee Self-Evaluation Form / Borang Penilaian Kendiri Pekerja", 0)
    # ... (Full content) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "02_Employee_Self_Evaluation_Form.docx"))

    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("SMART Goals & OKR Template", 0)
    # ... (Full content) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "03_SMART_Goals_OKR_Template.docx"))

    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Manager-Employee 1-on-1 Template / Templat Mesyuarat 1-dengan-1", 0)
    # ... (Full content) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "04_Manager_Employee_1-on-1_Template.docx"))

    doc = Document(); add_logo(doc, logo_path)
    doc.add_heading("Performance Improvement Plan (PIP) Template", 0)
    # ... (Full content) ...
    add_footer(doc, BRAND_TAGLINE); doc.save(os.path.join(save_folder, "05_Performance_Improvement_Plan_Template.docx"))
    print("...Performance Toolkit DONE.")

def make_documentation(COMPANY_DETAILS, BRAND_TAGLINE, logo_path, save_folder):
    print("Generating Documentation...")
    # === User_Guide.pdf ===
    styles = getSampleStyleSheet()
    guide_pdf = os.path.join(save_folder, "User_Guide.pdf")
    story = []
    if logo_path and os.path.exists(logo_path):
        story.append(Image(logo_path, width=Inches(1), height=Inches(1)))
    story += [
        Spacer(1, 12),
        Paragraph(f"{COMPANY_DETAILS['name']} — HR & People Management Pack", styles['Title']),
        Paragraph(BRAND_TAGLINE, styles['Italic']),
        Spacer(1, 12),
        Paragraph(f"1. This pack has been pre-filled with your company details (e.g., <b>{COMPANY_DETAILS['name']}</b>) and branded with your logo.", styles['Normal']),
        # ... (rest of PDF content, as in previous versions) ...
    ]
    SimpleDocTemplate(guide_pdf).build(story)

    # === README.txt ===
    readme_content = f"""{COMPANY_DETAILS['name']}
{BRAND_TAGLINE}
... (Full README content from previous version) ...
1. Customise: ... Company-level details (like '{COMPANY_DETAILS['name']}') have been pre-filled.
... (Full README content from previous version) ...
"""
    with open(os.path.join(save_folder, "README.txt"),"w",encoding="utf-8") as f:
        f.write(readme_content)
    print("...Documentation DONE.")


# --- Master Function (Called by the API) ---

def generate_hr_pack(
    company_name, 
    company_address, 
    working_hours, 
    dress_code, 
    ceo_name, 
    ceo_title, 
    hr_name, 
    hr_title, 
    brand_tagline, 
    logo_path  # Note: This is now just a string path
):
    
    print(f"Starting pack generation for: {company_name}")
    
    # 1. Create a temporary, unique directory to build the pack
    base_dir = tempfile.mkdtemp()
    
    # Define all the folder paths
    pack_root = os.path.join(base_dir, "HR_People_Management_Pack")
    kit_folder = os.path.join(pack_root, "Hiring_Onboarding_Kit")
    handbook_folder = os.path.join(pack_root, "Employee_Handbook")
    performance_folder = os.path.join(pack_root, "Performance_Management_Toolkit")
    doc_folder = os.path.join(pack_root, "Documentation")
    
    # Create the directory structure
    for f in [kit_folder, handbook_folder, performance_folder, doc_folder]:
        os.makedirs(f, exist_ok=True)

    # 2. Consolidate all company data into one dictionary
    COMPANY_DETAILS = {
        "name": company_name,
        "address": company_address,
        "working_hours": working_hours,
        "dress_code": dress_code,
        "ceo_name": ceo_name,
        "ceo_title": ceo_title,
        "hr_name": hr_name,
        "hr_title": hr_title
    }

    # 3. Run all the generator functions
    make_hiring_kit(COMPANY_DETAILS, brand_tagline, logo_path, kit_folder)
    make_handbook(COMPANY_DETAILS, brand_tagline, logo_path, handbook_folder)
    make_performance(COMPANY_DETAILS, brand_tagline, logo_path, performance_folder)
    make_documentation(COMPANY_DETAILS, brand_tagline, logo_path, doc_folder)

    # 4. Zip the entire generated folder
    print("Zipping the final pack...")
    safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")
    zip_filename = f"{safe_company_name}_HR_Pack.zip"
    
    # Create the zip file in a temporary location
    zip_output_path = os.path.join(tempfile.gettempdir(), zip_filename)

    # Create the zip
    shutil.make_archive(
        base_name=zip_output_path.replace('.zip', ''), 
        format='zip', 
        root_dir=base_dir, 
        base_dir="HR_People_Management_Pack"
    )

    # 5. Clean up the build directory
    shutil.rmtree(base_dir)
    print(f"Pack generated. Returning zip file: {zip_output_path}")

    # 6. Return the path and filename of the zip file
    return zip_output_path, zip_filename


# ===============================================================
# PART 2: THE "WEB API"
# This is the Flask server that listens for requests
# from your index.html
# ===============================================================

# --- 1. Initialize the Flask App ---
app = Flask(__name__)

# --- 2. Enable CORS ---
# This allows your Netlify frontend to talk to your Render backend
CORS(app)

# --- 3. Define the API Endpoint ---
@app.route('/generate-pack', methods=['POST'])
def handle_generation():
    
    # 4. Get Data from the HTML Form
    try:
        company_name = request.form['company_name']
        company_address = request.form['company_address']
        working_hours = request.form['working_hours']
        dress_code = request.form['dress_code']
        ceo_name = request.form['ceo_name']
        ceo_title = request.form['ceo_title']
        hr_name = request.form['hr_name']
        hr_title = request.form['hr_title']
        brand_tagline = request.form['brand_tagline']
        logo_upload = request.files.get('logo_upload')
    except Exception as e:
        print(f"Form data error: {e}")
        return jsonify({"error": f"Missing form data: {e}"}), 400

    
    temp_logo_path = None
    temp_dir = tempfile.mkdtemp() # Create a temp dir for all our work

    try:
        # 5. Save the uploaded logo to a temporary file
        if logo_upload and logo_upload.filename != '':
            temp_logo_path = os.path.join(temp_dir, logo_upload.filename)
            logo_upload.save(temp_logo_path)
            print(f"Logo saved to {temp_logo_path}")
        
        # 6. Call the Generator Engine
        zip_output_path, zip_filename = generate_hr_pack(
            company_name, 
            company_address, 
            working_hours, 
            dress_code, 
            ceo_name, 
            ceo_title, 
            hr_name, 
            hr_title, 
            brand_tagline, 
            temp_logo_path # Pass the path (string) to the saved logo
        )
    
    except Exception as e:
        print(f"Generator error: {e}")
        return jsonify({"error": f"Failed to generate documents: {e}"}), 500
    
    # 7. Send the .zip File to the Browser
    print(f"Sending file: {zip_output_path}")
    response = send_file(
        zip_output_path,
        as_attachment=True,
        download_name=zip_filename
    )
    
    # 8. Clean up
    try:
        shutil.rmtree(temp_dir) # Clean up the logo temp dir
        os.remove(zip_output_path) # Clean up the zip file
    except Exception as e:
        print(f"Error cleaning up temp files: {e}")
        
    return response

# This is for local testing. Render will use Gunicorn.
if __name__ == '__main__':
    app.run(debug=True, port=5000)
