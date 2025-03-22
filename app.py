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

@app.route("/job_description", methods=["POST"])
def job_description():
    job_desc = request.form["job"]
    resume = request.form["resume"]

    ai_response = "Your resume is a great fit for this role!"

    return render_template("ai_suggestions.html", response=ai_response)

@app.route("/cover_letter", methods=["POST"])
def cover_letter():
    job_desc = request.form["job"]
    resume = request.form["resume"]

    letter = "Dear Hiring Manager, based on your job description..."

    return render_template("cover_letter.html", letter=letter)

if __name__ =="__main__":
    app.run(debug=True)