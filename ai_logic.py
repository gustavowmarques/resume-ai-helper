"""
ai_logic.py

Handles all interactions with the OpenAI API. Includes functions for:
- Generating personalized resume suggestions based on a job description.
- Creating a tailored cover letter using user input and resume content.
"""

import os
import openai
from datetime import date
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_ai_suggestions(resume, job):
    """
    Sends resume and job description content to OpenAI's GPT model
    to receive personalized suggestions for improving the resume.

    Args:
        resume (str): Raw text of the user's resume.
        job (str): Job description text.

    Returns:
        str: AI-generated resume improvement suggestions.
    """
    try:
        trimmed_resume = resume[:3000] # Limit resume length to avoid exceeding token limits
        trimmed_job = job[:2000]       # Same for job description

        prompt = f"""
    You are an expert career coach. Compare the following resume with the job description
    and provide personalized, actionable suggestions to improve the resume for this role.

    Resume:
    {trimmed_resume}

    Job Description:
    {trimmed_job}

    Suggestions:
    """
        logging.info("Generating AI suggestions...")    
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        suggestions = response.choices[0].message.content.strip()
        logging.info(" Suggestions generated successfully.")
        return suggestions

    except Exception as e:
        logging.error(f" Error generating AI suggestions: {e}")
        return "There was an issue generating suggestions. Please try again later."


def generate_cover_letter(name, job_title, resume, job, tone, language, contact):
    """
    Generates a customized cover letter using the user's details and resume/job description.

    Args:
        name (str): Applicant's full name.
        job_title (str): Title of the position the user is applying for.
        resume (str): Resume text.
        job (str): Job description text.
        tone (str): Desired tone of the letter (e.g., professional, friendly).
        language (str): Language to write the letter in.
        contact (str): Extracted or provided contact info (email, phone).

    Returns:
        str: AI-generated cover letter.
    """
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
