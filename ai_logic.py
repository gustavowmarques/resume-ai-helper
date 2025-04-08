from dotenv import load_dotenv
from datetime import date
load_dotenv()
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_ai_suggestions(resume, job):
    prompt = f"""
    You are an expert career coach. Compare the following resume with the job description
    and provide personalized, actionable suggestions to improve the resume for this role.

    Resume:
    {resume}

    Job Description:
    {job}

    Suggestions:
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def generate_cover_letter(name, job_title, resume, job, tone, language, contact):
    today = date.today().strftime("%B %d, %Y")
    prompt = f"""
    Write a professional cover letter in {language}, in a {tone} tone,
    based on the following resume and job description.

    Name: {name}
    Contact Info: {contact}
    Date: {today}

    Resume:
    {resume}

    Job Description:
    {job}

    Cover Letter:
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()
