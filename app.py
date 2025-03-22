import os

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        resume_text = request.form["resume"]
        return render_template("job_description.html", resume=resume_text)
    return render_template("upload_resume.html")

@app.route("/job_description", methods=["GET", "POST"])
def job_description():
    if request.method == "POST":
        job = request.form["job"]
        resume = request.form["resume"]
        
        ai_response = "Your resume highlights strong analytical skills, which aligns with the job's requirement for data analysis."
        return render_template("ai_suggestions.html", response=ai_response, resume=resume, job=job)
    return render_template("job_description.html")

@app.route("/cover_letter", methods=["GET", "POST"])
def cover_letter():
    if request.method == "POST":
        resume = request.form.get("resume", "").lower()
        job = request.form.get("job", "").lower()
        user_name = request.form.get("name", "Your Name")
        job_title = request.form.get("job_title", "the advertised role")

        # Basic keyword matching
        job_keywords = set(job.replace(",", "").replace(".", "").split())
        resume_words = set(resume.replace(",", "").replace(".", "").split())

        common_keywords = job_keywords & resume_words
        top_keywords = sorted(common_keywords)[:5]

        # Build letter using a simple template
        generated_letter = f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title}. With a background in {', '.join(top_keywords)}, I believe I could bring valuable skills to your team and contribute meaningfully to your goals.

Throughout my career, I have demonstrated the ability to learn quickly, adapt to new challenges, and collaborate effectively — all of which align with your job requirements. I would welcome the opportunity to apply my experience in a dynamic and rewarding environment.

Thank you for considering my application.

Sincerely,  
{user_name}
"""

        return render_template("cover_letter.html", letter=generated_letter, name=user_name)

    return render_template("cover_letter.html", letter="You must generate a cover letter via the AI Suggestions page.", name="")


@app.route("/ai_suggestions", methods=["GET", "POST"])
def ai_suggestions():
    if request.method == "POST":
        resume = request.form.get("resume", "").lower()
        job = request.form.get("job", "").lower()

        # Simple keyword extraction: split by common separators
        job_keywords = set(job.replace(",", "").replace(".", "").split())
        resume_words = set(resume.replace(",", "").replace(".", "").split())

        # Find which job keywords are missing from the resume
        missing_keywords = job_keywords - resume_words
        common_keywords = job_keywords & resume_words

        if missing_keywords:
            ai_response = f"""
Your resume is missing some keywords that are important in the job description:
<br><strong>{', '.join(sorted(missing_keywords))}</strong>

You already include:
<br><em>{', '.join(sorted(common_keywords))}</em>

Tip: Consider updating your resume to include some of the missing terms, if relevant.
"""
        else:
            ai_response = "Your resume already includes all the major keywords from the job description. Nice work!"

        return render_template("ai_suggestions.html", response=ai_response, resume=resume, job=job)

    return render_template("ai_suggestions.html", response="You must upload a resume and job description first.", resume="", job="")


if __name__ =="__main__":
    app.run(debug=True)