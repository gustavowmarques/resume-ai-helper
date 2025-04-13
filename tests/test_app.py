# test_app.py 
# To run the script use the following command on the application root (folder that contains app.py):
# python -m unittest discover -s tests
# Flask app test script using Python’s built-in unittest module and the Flask test client.
# What the script do:
#* Test all key routes (/, /upload_resume, /job_description, /ai_suggestions, /cover_letter, etc.)
#* Simulate form submissions using pasted text
#* Use assert statements to fail if something breaks
#* Print clear messages for each step


import unittest
from app import app
from flask import session
from io import BytesIO

class ResumeAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Thext below used in the resume text field
        self.resume_text = (
            "John Doe\n"
            "123 Main Street\n"
            "Anytown, USA\n"
            "johndoe@email.com\n"
            "555-555-5555\n\n"
            "Experienced software engineer with expertise in Python, Flask, and web development."
        )

        # Below description entered iin the job text field 
        self.job_text = (
            "We are looking for a skilled Python developer with experience in Flask, HTML, CSS, and JavaScript. "
            "The ideal candidate is passionate about building efficient and scalable web apps."
        )

        # This is used for the feedback form
        self.sample_email = "test@example.com"
        self.feedback_message = "Amazing tool!"

    # Home page test
    def test_home(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 302)

    # Test for 404 errors
    def test_404_page(self):
        response = self.app.get("/nonexistentpage")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404 - Page Not Found", response.data)

    #Test for 500 errors
    def test_500_page(self):
        response = self.app.get("/force500")
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"500 - Server Error", response.data)

    # Test for /upload_resume route
    def test_resume_upload_text(self):
        response = self.app.post("/upload_resume", data={
            "resume": self.resume_text
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Paste the Job Description", response.data)

    # example CV saved tests/test_files/ folder. It's uploaded to the application during test
    def test_resume_upload_file(self):
        with open("tests/test_files/sample_resume.docx", "rb") as f:
            data = {
                "resume_file": (BytesIO(f.read()), "sample_resume.docx")
            }
            response = self.app.post("/upload_resume", data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Paste the Job Description", response.data)
    
    # Test for /job_description route
    def test_job_description_text(self):
        with self.app.session_transaction() as sess:
            sess["resume"] = self.resume_text
        response = self.app.post("/job_description", data={
            "job": self.job_text
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Suggestions", response.data)

    # Test for startover button/function
    def test_start_over(self):
        response = self.app.get("/start_over", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upload or Paste Your Resume", response.data)

    #Test for Feedback form
    def test_feedback_form(self):
        response = self.app.post("/feedback", data={
            "feedback": self.feedback_message,
            "email": self.sample_email
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your feedback has been received", response.data)

    # Checks about page
    def test_about_page(self):
        response = self.app.get("/about")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resume AI Helper", response.data)