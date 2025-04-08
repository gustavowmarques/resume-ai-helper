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
from werkzeug.utils import secure_filename
import io

from utils import extract_contact_info
from ai_logic import generate_ai_suggestions, generate_cover_letter
from utils import extract_text_from_file, generate_docx_file, create_zip

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def home():
    return redirect(url_for("upload_resume"))


@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        pasted_resume = request.form.get("resume", "")
        uploaded_file = request.files.get("resume_file")

        if pasted_resume:
            session["resume"] = pasted_resume
        elif uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_text = extract_text_from_file(uploaded_file)
            session["resume"] = file_text
        else:
            return render_template("upload_resume.html", error="Please upload a file or paste your resume.")

        return redirect(url_for("job_description"))

    return render_template("upload_resume.html", resume=session.get("resume", ""))


@app.route("/job_description", methods=["GET", "POST"])
def job_description():
    resume = session.get("resume", "")
    if request.method == "POST":
        job_desc = request.form.get("job", "")
        job_url = request.form.get("job_url", "")

        if not job_desc and not job_url:
            return render_template("job_description.html", resume=resume, error="Please paste a job description or enter a job URL.")

        if job_url:
            import requests
            from bs4 import BeautifulSoup
            try:
                response = requests.get(job_url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                paragraphs = soup.find_all(["p", "li"])
                job_desc = "\n".join(p.get_text() for p in paragraphs).strip()
                if not job_desc:
                    return render_template("job_description.html", resume=resume, error="Unable to extract job description from this URL. Try copying and pasting it instead.")
            except Exception as e:
                return render_template("job_description.html", resume=resume, error=f"Error fetching job description: {str(e)}")

        session["job"] = job_desc
        session["job_url"] = job_url
        return redirect(url_for("ai_suggestions"))

    return render_template("job_description.html", resume=resume, job=session.get("job", ""), job_url=session.get("job_url", ""))


@app.route("/ai_suggestions", methods=["GET"])
def ai_suggestions():
    resume = session.get("resume", "")
    job = session.get("job", "")

    if not resume or not job:
        return render_template("ai_suggestions.html", response="⚠️ Missing resume or job description.", resume="", job="")

    ai_response = generate_ai_suggestions(resume, job)
    return render_template("ai_suggestions.html", response=ai_response, resume=resume, job=job)


@app.route("/cover_letter", methods=["POST"])
def cover_letter():
    name = request.form.get("name", "")
    job_title = request.form.get("job_title", "")
    resume = session.get("resume", "")
    job = session.get("job", "")
    tone = request.form.get("tone", "Professional")
    language = request.form.get("language", "English")

    if not resume or not job or not name or not job_title:
        return render_template("cover_letter.html", error="Missing required inputs.", name=name, job_title=job_title)

    contact_info = extract_contact_info(job)
    letter = generate_cover_letter(name, job_title, resume, job, tone, language, contact_info)
    session["cover_letter"] = letter

    return render_template("cover_letter.html", cover_letter=letter, name=name, job_title=job_title)

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

    return create_zip(resume, job, cover_letter)


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