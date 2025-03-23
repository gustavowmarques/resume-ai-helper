from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
import os 
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import requests
from bs4 import BeautifulSoup
import docx
import pdfplumber
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    print("📥 /upload_resume triggered")

    if request.method == "POST":
        print("✅ POST method received on /upload_resume")

        resume_text = request.form.get("resume", "").strip()
        print(f"📝 Pasted resume length: {len(resume_text)} characters")

        uploaded_file = request.files.get("resume_file")

        if uploaded_file and uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            print(f"📄 Uploaded file: {filename}")

            try:
                if file_ext == ".txt":
                    resume_text = uploaded_file.read().decode("utf-8")

                elif file_ext == ".pdf":
                    with pdfplumber.open(uploaded_file) as pdf:
                        resume_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

                elif file_ext == ".docx":
                    doc = docx.Document(uploaded_file)
                    resume_text = "\n".join([para.text for para in doc.paragraphs])
                else:
                    return render_template("upload_resume.html", error="Unsupported file format.")

                print(f"📄 Extracted resume from file: {len(resume_text)} characters")

            except Exception as e:
                print(f"❌ Error reading file: {e}")
                return render_template("upload_resume.html", error="There was an error processing the uploaded file.")

        if not resume_text:
            return render_template("upload_resume.html", error="Please upload a resume file or paste the text.")

        # ✅ These must be inside the POST block
        session["resume"] = resume_text
        return redirect(url_for("job_description"))

    # Default GET request
    return render_template("upload_resume.html")


@app.route("/test_form", methods=["GET", "POST"])
def test_form():
    if request.method == "POST":
        print("✅ Test form POST received")
        return "Success!"

    return '''
    <form method="POST">
      <textarea name="resume"></textarea>
      <button type="submit">Submit</button>
    </form>
    '''

@app.route("/job_description", methods=["GET", "POST"])
def job_description():
    resume = session.get("resume", "") 
    
    

    if request.method == "POST":
        job_desc = request.form.get("job", "")
        job_url = request.form.get("job_url", "")
        
        if job_url:
            try:
                response = requests.get(job_url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                paragraphs = soup.find_all(["p", "li"])
                job_desc = "\n".join(p.get_text() for p in paragraphs)
            except Exception as e:
                job_desc = f"Could not fetch job description from URL: {str(e)}"

        if not job_desc.strip():
            return render_template("job_description.html", resume=resume, error="Please paste a job description or URL.")
        print("🧠 job_desc length:", len(job_desc))
        print("📥 session['resume']:", len(resume))

        # Save to session
        session["job"] = job_desc
        return redirect(url_for("ai_suggestions"))


    return render_template("job_description.html", resume=resume)



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

@app.route("/ai_suggestions", methods=["GET"])
def ai_suggestions():
    resume = session.get("resume", "")
    job = session.get("job", "")

    if not resume or not job:
        return render_template("ai_suggestions.html", response="⚠️ Missing resume or job description.", resume="", job="")

    resume = resume[:3000]
    job = job[:2000]

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



if __name__ =="__main__":
    app.run(debug=True)