import os
from openai import OpenAI
client = OpenAI()

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

@app.route("/cover_letter", methods=["POST"])
def cover_letter():
    resume = request.form.get("resume", "")
    job = request.form.get("job", "")
    user_name = request.form.get("name", "Your Name")
    job_title = request.form.get("job_title", "the advertised position")

    prompt = f"""
Using the resume and job description below, write a personalized cover letter for a position titled '{job_title}'.

Resume:
{resume}

Job Description:
{job}

Please make the tone professional and enthusiastic. Sign it off with: {user_name}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7
        )

        generated_letter = response.choices[0].message.content.strip()

    except Exception as e:
        generated_letter = f"OpenAI API Error: {str(e)}"

    return render_template("cover_letter.html", letter=generated_letter)

@app.route("/ai_suggestions", methods=["GET", "POST"])
def ai_suggestions():
    if request.method == "POST":
        resume = request.form.get("resume", "")
        job = request.form.get("job", "")

        prompt = f"""
You are an expert career coach. Compare the following resume with the job description and provide personalized, actionable suggestions to improve the resume for this role.

Resume:
{resume}

Job Description:
{job}

Suggestions:
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()

        except Exception as e:
            ai_response = f"⚠️ OpenAI API Error: {str(e)}"

        return render_template("ai_suggestions.html", response=ai_response, resume=resume, job=job)

    return render_template("ai_suggestions.html", response="⚠️ Please start from the Upload Resume page.", resume="", job="")


if __name__ =="__main__":
    app.run(debug=True)