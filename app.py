"""
Resume AI Helper App
--------------------
A Flask web application that helps users generate personalized cover letters based on their resumes and job descriptions using OpenAI's GPT model.

Features:
- Upload or paste a resume
- Paste or scrape a job description from a URL
- Generate AI-based resume improvement suggestions
- Generate a customized cover letter
- Download output files (TXT, DOCX, PDF, ZIP)
- Submit feedback via email (Flask-Mail)
- Support for dark mode and multiple languages
- Custom error handling (404 and 500 pages)

Author: Gustavo W. M. da Silva
Date: March 2025
"""

#app.py
#The code in this file is responsible for:Route definitions, Request/response handling and Rendering templates

from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_session import Session
from flask_mail import Mail, Message

from ai_logic import generate_ai_suggestions, generate_cover_letter
from utils import (
    safe_filename,
    extract_text_from_file,
    generate_docx_file,
    generate_pdf_file,
    create_zip,
    extract_job_description_from_url,
    extract_contact_info,
)

from dotenv import load_dotenv
import os
import io

"""
app.py

Main Flask application for Resume AI Helper. Handles routing, user session management,
file uploads, OpenAI integration for resume/cover letter generation, and email feedback.
"""


# Load sensitive credentials like OpenAI and email from .env file
load_dotenv()

# -------------------------------
# Flask + Server-side Session Setup
# -------------------------------
# Use filesystem-based session instead of browser cookies
# This avoids cookie size limitations and supports larger data (like resumes)
app = Flask(__name__)

# Server-side session configuration (using filesystem instead of cookies)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./.flask_session/" # Where session files will be stored
app.config["SESSION_PERMANENT"] = False # Sessions will expire when browser is closed
Session(app)

app.secret_key = "supersecretkey" # Required for session encryption

# -------------------------------
# Flask-Mail Configuration
# -------------------------------
# Uses Gmail SMTP to send feedback confirmation emails.
# Make sure MAIL_USERNAME and MAIL_PASSWORD are stored in .env
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
mail = Mail(app)

# -------------------------
# Upload Resume (Home Page)
# -------------------------
# Allows user to upload a file or paste their resume text.
# Saves the resume in the session under 'resume'.
@app.route("/")
def home():
    return redirect(url_for("upload_resume"))

# -------------------------------
# Upload or Paste Resume Page
# -------------------------------
# Allows user to either upload a resume file or paste plain text.
# Saves resume text to the session for further processing.
@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        # Check if a file was uploaded
        # If not, fallback to pasted text
        resume_text = ""
        pasted_text = request.form.get("resume", "").strip()
        uploaded_file = request.files.get("resume_file")

        # Prefer pasted text if present, fallback to file upload
        if pasted_text:
            resume_text = pasted_text
        elif uploaded_file and uploaded_file.filename != "":
            try:
                resume_text = extract_text_from_file(uploaded_file)
            except Exception as e:
                print(f"Error reading file: {e}")
                return render_template("upload_resume.html", error="There was an issue with the uploaded file.")

        # If nothing is provided, show error
        if not resume_text:
            return render_template("upload_resume.html", error="Please paste your resume or upload a valid file.")

        # Save extracted or pasted resume to session for use in suggestions and cover letter
        session["resume"] = resume_text
        print("Resume saved to session:", len(resume_text))
        return redirect(url_for("job_description"))

    return render_template("upload_resume.html", resume=session.get("resume", ""))

# -------------------------------
# Enter Job Description Page
# -------------------------------
# Lets user paste or provide a URL for the job description.
# Extracts job text (if URL) and stores it in the session.
@app.route("/job_description", methods=["GET", "POST"])
def job_description():
    resume = session.get("resume", "")

    if request.method == "POST":
        job_desc = request.form.get("job", "").strip()
        job_url = request.form.get("job_url", "").strip()

        print(f"Job URL: {job_url}")
        print(f"Job Desc: {job_desc[:100]}")

        # If URL is provided and job description is empty, attempt to scrape job content
        if job_url and not job_desc:
            job_desc = extract_job_description_from_url(job_url)

            if job_desc is None or job_desc.startswith("Error:"):
                return render_template(
                    "job_description.html",
                    resume=resume,
                    error="We couldn’t extract the job description from this URL. Please paste it instead.",
                    job_url=job_url,
                    job=""
                )


        # If neither field has data
        if not job_desc:
            return render_template(
                "job_description.html",
                resume=resume,
                error="Please provide a job description or a valid URL.",
                job_url=job_url,
                job=""
                )

        # Save job description and job URL to session
        session["job"] = job_desc
        session["job_url"] = job_url

        return redirect(url_for("ai_suggestions"))

    # Initial GET request
    return render_template(
        "job_description.html",
        resume=resume,
        job=session.get("job", ""),
        job_url=session.get("job_url", "")
    )

# -------------------------------
# AI Suggestions Page
# -------------------------------
# Compares resume and job description using OpenAI API
# Returns resume improvement suggestions for the user
@app.route("/ai_suggestions", methods=["GET"])
def ai_suggestions():
    resume = session.get("resume", "")
    job = session.get("job", "")

    print("DEBUG /ai_suggestions")

    # Limit resume and job description lengths to avoid exceeding OpenAI token limits
    print("Resume Length:", len(resume))
    print("Job Length:", len(job)) 

    if not resume or not job:
        return render_template("ai_suggestions.html", response="Missing resume or job description.", resume="", job="")

    ai_response = generate_ai_suggestions(resume, job)
    session["ai_suggestions"] = ai_response
    return render_template("ai_suggestions.html", response=ai_response, resume=resume, job=job)

# -------------------------------
# Cover Letter Generation Page
# -------------------------------
# Uses OpenAI to generate a customized cover letter
# Based on user's resume, job, tone, language, and contact info
@app.route("/cover_letter", methods=["POST"])
def cover_letter():
    name = request.form.get("name", "").strip()
    job_title = request.form.get("job_title", "").strip()
    tone = request.form.get("tone", "Professional")
    language = request.form.get("language", "English")

    resume = session.get("resume", "")
    job = session.get("job", "")
    contact_info = "Hiring Manager"

    print("Cover letter form submission:")
    print(f"Name: {name}")
    print(f"Job Title: {job_title}")
    print(f"Tone: {tone}")
    print(f"Language: {language}")
    print(f"Resume length: {len(resume)}")
    print(f"Job length: {len(job)}")

    if not name or not job_title:
        return render_template("cover_letter.html", letter=None, error="Please fill in your name and job title.")

    # Save the generated cover letter to session for future download
    letter = generate_cover_letter(name, job_title, resume, job, tone, language, contact_info)
    session["cover_letter"] = letter

    print("Generated cover letter:", letter[:150])
    return render_template("cover_letter.html", letter=letter)

# Download routes to export the cover letter and AI suggestions
# as individual files or a .zip archive with all formats
@app.route("/download_docx")
def download_docx():
    letter = session.get("cover_letter", "")
    if not letter:
        return "No cover letter to download."
    return send_file(
    generate_docx_file(letter),
    as_attachment=True,
    download_name="cover_letter.docx",
    mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.route("/download_all")
def download_all():
    letter = session.get("cover_letter", "")
    suggestions = session.get("ai_suggestions", "")

    if not letter or not suggestions:
        return "Missing content to zip."

    # Generate content in different formats
    letter_docx = generate_docx_file(letter).getvalue()
    suggestions_docx = generate_docx_file(suggestions).getvalue()
    letter_pdf = generate_pdf_file(letter).getvalue()


    files = {
        "cover_letter.txt": letter,
        "cover_letter.docx": letter_docx,
        "cover_letter.pdf": letter_pdf,
        "ai_suggestions.docx": suggestions_docx
    }

    zip_buffer = create_zip(files)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="resume_ai_output.zip",
        mimetype="application/zip"
    )

@app.route("/start_over")
def start_over():
    session.clear()
    return redirect(url_for("home"))

# -------------------------------
# Feedback Form Submission
# -------------------------------
# Sends feedback message via email (using Flask-Mail)
# Also writes the feedback to a local file
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        feedback = request.form.get("feedback", "")
        email = request.form.get("email", "")
        print("Feedback received:", feedback)
        if email:
            print("Optional email:", email)

        # Send the email
        try:
            msg = Message(
                subject="New Feedback Received",
                sender=app.config["MAIL_USERNAME"],
                recipients=[app.config["MAIL_USERNAME"]],  # Sends to yourself
                body=f"Feedback: {feedback}\n\nEmail: {email or 'Not provided'}"
            )

            # Email the feedback to the configured recipient
            mail.send(msg)
            print("Feedback email sent.")
        except Exception as e:
            print(f"Failed to send feedback email: {e}")

        return render_template("feedback_thankyou.html", success=True)

    return render_template("feedback.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/force500")
def force500():
    raise Exception("Test 500 error")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500

# ---------------------------
# Run the Flask App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=False)