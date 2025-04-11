import unittest
from app import app
from flask import session
from io import BytesIO

class ResumeAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        self.resume_text = (
            "John Doe\n"
            "123 Main Street\n"
            "Anytown, USA\n"
            "johndoe@email.com\n"
            "555-555-5555\n\n"
            "Experienced software engineer with expertise in Python, Flask, and web development."
        )

        self.job_text = (
            "We are looking for a skilled Python developer with experience in Flask, HTML, CSS, and JavaScript. "
            "The ideal candidate is passionate about building efficient and scalable web apps."
        )

        self.sample_email = "test@example.com"
        self.feedback_message = "Amazing tool!"

    def test_home(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 302)

    def test_404_page(self):
        response = self.app.get("/nonexistentpage")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404 - Page Not Found", response.data)

    def test_500_page(self):
        response = self.app.get("/force500")
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"500 - Server Error", response.data)

    def test_resume_upload_text(self):
        response = self.app.post("/upload_resume", data={
            "resume": self.resume_text
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Paste the Job Description", response.data)

    def test_resume_upload_file(self):
        with open("tests/test_files/sample_resume.docx", "rb") as f:
            data = {
                "resume_file": (BytesIO(f.read()), "sample_resume.docx")
            }
            response = self.app.post("/upload_resume", data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Paste the Job Description", response.data)

    def test_job_description_text(self):
        with self.app.session_transaction() as sess:
            sess["resume"] = self.resume_text
        response = self.app.post("/job_description", data={
            "job": self.job_text
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Suggestions", response.data)

    def test_start_over(self):
        response = self.app.get("/start_over", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upload or Paste Your Resume", response.data)

    def test_feedback_form(self):
        response = self.app.post("/feedback", data={
            "feedback": self.feedback_message,
            "email": self.sample_email
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your feedback has been received", response.data)

    def test_about_page(self):
        response = self.app.get("/about")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resume AI Helper", response.data)