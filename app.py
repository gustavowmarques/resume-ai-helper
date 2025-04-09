"""
Resume AI Helper App
--------------------
A Flask web application that helps users generate personalized cover letters based on their resumes and job descriptions using OpenAI's GPT model.

Key Features:
- Upload or paste a resume
- Paste or scrape a job description from a URL
- Generate AI-based improvement suggestions
- Generate a customized cover letter
- Option to download suggestions and letter as a ZIP
- Feedback form with email integration
- Dark mode toggle
- Language selection for cover letter
- Custom error pages (404 & 500)

Author: Gustavo W. M. da Silva
Date: March 2025
"""

from flask import Flask, render_template, request, session, redirect, url_for, send_file

import io

from ai_logic import generate_ai_suggestions, generate_cover_letter
from utils import extract_text_from_file, generate_docx_file, create_zip, extract_job_description_from_url, extract_contact_info
from flask_session import Session

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup

load_dotenv()

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)


@app.route("/")
def home():
    return redirect(url_for("upload_resume"))


@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        resume_text = ""
        pasted_text = request.form.get("resume", "").strip()
        uploaded_file = request.files.get("resume_file")

        # ✅ Use pasted resume if provided
        if pasted_text:
            resume_text = pasted_text
        elif uploaded_file and uploaded_file.filename != "":
            try:
                resume_text = extract_text_from_file(uploaded_file)
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                return render_template("upload_resume.html", error="There was an issue with the uploaded file.")

        # ❌ If nothing is provided, show error
        if not resume_text:
            return render_template("upload_resume.html", error="Please paste your resume or upload a valid file.")

        # ✅ Save to session
        session["resume"] = resume_text
        print("✅ Resume saved to session:", len(resume_text))
        return redirect(url_for("job_description"))

    return render_template("upload_resume.html", resume=session.get("resume", ""))




@app.route("/job_description", methods=["GET", "POST"])
def job_description():
    resume = session.get("resume", "")

    if request.method == "POST":
        job_desc = request.form.get("job", "").strip()
        job_url = request.form.get("job_url", "").strip()

        print(f"Job URL: {job_url}")
        print(f"Job Desc: {job_desc[:100]}")

        # 🔍 If job URL is present and job description is blank, try scraping
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


                # ❗ If neither field has data
                if not job_desc:
                    return render_template(
                        "job_description.html",
                        resume=resume,
                        error="Please provide a job description or a valid URL.",
                        job_url=job_url,
                        job=""
                    )

        # ✅ All good, save and continue
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


@app.route("/ai_suggestions", methods=["GET"])
def ai_suggestions():
    resume = session.get("resume", "")
    job = session.get("job", "")

    print("🔍 DEBUG /ai_suggestions")
    print("Resume Length:", len(resume))
    print("Job Length:", len(job))

    if not resume or not job:
        return render_template("ai_suggestions.html", response="Missing resume or job description.", resume="", job="")

    ai_response = generate_ai_suggestions(resume, job)
    return render_template("ai_suggestions.html", response=ai_response, resume=resume, job=job)


@app.route("/cover_letter", methods=["POST"])
def cover_letter():
    name = request.form.get("name", "").strip()
    job_title = request.form.get("job_title", "").strip()
    tone = request.form.get("tone", "Professional")
    language = request.form.get("language", "English")

    resume = session.get("resume", "")
    job = session.get("job", "")
    contact_info = "Hiring Manager"

    print("📩 Cover letter form submission:")
    print(f"Name: {name}")
    print(f"Job Title: {job_title}")
    print(f"Tone: {tone}")
    print(f"Language: {language}")
    print(f"Resume length: {len(resume)}")
    print(f"Job length: {len(job)}")

    if not name or not job_title:
        return render_template("cover_letter.html", letter=None, error="Please fill in your name and job title.")

    letter = generate_cover_letter(name, job_title, resume, job, tone, language, contact_info)
    session["cover_letter"] = letter

    print("✅ Generated cover letter:", letter[:150])
    return render_template("cover_letter.html", letter=letter)


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
    resume = session.get("resume", "")
    job = session.get("job", "")
    cover_letter = session.get("cover_letter", "")

    if not resume or not job or not cover_letter:
        return "Missing data for zip."

    files = {
        "resume.txt": io.BytesIO(resume.encode("utf-8")),
        "job_description.txt": io.BytesIO(job.encode("utf-8")),
        "cover_letter.txt": io.BytesIO(cover_letter.encode("utf-8")),
    }

    return send_file(
        create_zip(files),
        as_attachment=True,
        download_name="resume_ai_package.zip",
        mimetype="application/zip"
    )



@app.route("/start_over")
def start_over():
    session.clear()
    return redirect(url_for("home"))


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
            mail.send(msg)
            print("Feedback email sent.")
        except Exception as e:
            print(f"Failed to send feedback email: {e}")

        return render_template("feedback.html", success=True)

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

if __name__ == "__main__":
    app.run(debug=False)