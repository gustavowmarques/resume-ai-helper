# Resume AI Helper

**Resume AI Helper** is a Flask web application that helps users generate AI-powered suggestions and tailored cover letters based on a submitted resume and a job description (or job URL). It uses OpenAI’s GPT-3.5 to analyze and assist users in enhancing their application documents with actionable advice.

---

##  Features

- **Upload or paste a resume** (supports `.txt`, `.pdf`, and `.docx`)
- **Enter or paste a job description** (or scrape from a job URL)
- **Get AI-powered suggestions** to tailor your resume to the job
- **Generate a personalized cover letter**
- **Download outputs** in `.txt`, `.pdf`, `.docx`, or as a `.zip`
- **Feedback form** with email functionality
- **Dark Mode** toggle for accessibility
- **Multilingual cover letter support**
- **Custom error pages** (404 and 500)

---

## Project Structure

```
resume_project/
│
├── app.py                  # Main application file (Flask routes and logic)
├── ai_logic.py             # OpenAI integration and cover letter generation
├── utils.py                # File extraction, PDF/ZIP generation, scraping
├── requirements.txt        # Python dependencies
│
├── templates/              # All HTML templates
│   ├── base.html           # Base layout with navigation and footer
│   ├── upload_resume.html  # Upload/paste resume step
│   ├── job_description.html # Upload/paste job description or URL
│   ├── ai_suggestions.html # Suggestions view
│   ├── cover_letter.html   # Cover letter generation view
│   ├── feedback.html       # Feedback form
│   ├── feedback_thankyou.html # Feedback thank you page
│   ├── 404.html, 500.html  # Custom error pages
│
├── static/
│   ├── css/style.css       # Custom styles
│   ├── js/script.js        # Form validation, tab logic, dark mode
│
├── tests/
│   └── test_app.py         # Unit tests for routes and logic
│
├── .flask_session/         # Server-side session data (ignored by git)
├── .env                    # Environment variables (not included in repo)
├── .gitignore              # Specifies files not tracked by Git
```

---

## Installation & Usage

### 1. Clone the repository:

```bash
git clone https://github.com/gustavowmarques/resume-ai-helper.git
cd resume-ai-helper
```

### 2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Set environment variables:

Create a `.env` file and include:

```env
OPENAI_API_KEY=your_openai_key_here
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_app_password
```

> **Never commit `.env` to version control.**

---

### 5. Run the app:

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000)

---

## Running Tests

```bash
python -m unittest discover -s tests
```

---

## Accessibility & Best Practices

- ARIA labels added for screen readers
- Keyboard navigation support
- Server-side session storage to avoid session overflow
- Error handling for 404 and 500 routes
- Code split into reusable modules (`ai_logic.py`, `utils.py`)

---

## Sample Output

Once you provide a resume and job description, the app generates:

- AI Suggestions (plain text + optional `.docx`)
- Cover Letter (.txt, .pdf, .docx)
- Download all as `.zip`

---

## Feedback

Users can submit feedback which is:

- Saved locally to `feedback.txt`
- Sent via email using Flask-Mail

---

## Author

**Gustavo W. M. da Silva**  
UCD Full Stack Software Development Program – 2025  
Project completed under guidance from Hassan  
Submitted: April 2025


---

## Notes

- This project was developed as part of a **professional diploma assignment**.
- It focuses on integrating AI into web development using **Flask**, **OpenAI**, and **good UI/UX practices**