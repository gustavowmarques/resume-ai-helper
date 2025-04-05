import unittest
from app import app
import os

class ResumeAppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("✅ Home page loads")

    def test_upload_resume_text(self):
        response = self.client.post('/upload_resume', data={
            'resume': 'John Doe\nExperienced Software Engineer with 10+ years...'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("✅ Resume upload works with pasted text")

    def test_upload_resume_file(self):
        with open('test_files/sample_resume.docx', 'rb') as f:
            data = {
                'resume_file': (f, 'sample_resume.docx')
            }
            response = self.client.post('/upload_resume', data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            print("✅ Resume upload works with .docx file")

    def test_job_description_text(self):
        with self.client.session_transaction() as sess:
            sess['resume'] = "John Doe\nExperience..."

        response = self.client.post('/job_description', data={
            'job': 'Looking for a Python developer with Flask experience...'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("✅ Job description submission works with pasted text")

    def test_job_description_url(self):
        with self.client.session_transaction() as sess:
            sess['resume'] = "John Doe\nExperience..."

        test_url = 'https://proofpoint.wd5.myworkdayjobs.com/ProofpointCareers/job/Belfast-Northern-Ireland/Network-Engineer-II_R11484?source=LinkedIn'
        response = self.client.post('/job_description', data={
            'job_url': test_url
        }, follow_redirects=True)

        # Because we're hitting an external URL, check for either success or appropriate error
        self.assertIn(response.status_code, [200])
        print("✅ Job description from URL handled (check for warning if needed)")

    def test_ai_suggestions(self):
        with self.client.session_transaction() as sess:
            sess['resume'] = "John Doe\nExperience..."
            sess['job'] = "Looking for a Python developer..."

        response = self.client.get('/ai_suggestions')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Suggestions", response.data)
        print("✅ AI suggestions route returns content")

    def test_cover_letter_generation(self):
        with self.client.session_transaction() as sess:
            sess['resume'] = "John Doe\nExperience..."
            sess['job'] = "Looking for a Python developer..."

        response = self.client.post('/cover_letter', data={
            'name': 'John Doe',
            'job_title': 'Python Developer',
            'tone': 'Formal',
            'language': 'English'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Download", response.data)
        print("✅ Cover letter generation works")

    def test_feedback_form(self):
        response = self.client.post('/feedback', data={
            'feedback': 'Amazing tool!',
            'email': 'test@example.com'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("✅ Feedback form submits successfully")

    def test_start_over(self):
        response = self.client.get('/start_over', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("✅ Start over route works")

    def test_about_page(self):
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        print("✅ About page loads")

    def test_404_page(self):
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page Not Found", response.data)
        print("✅ Custom 404 page works")

    def test_500_page(self):
        response = self.client.get("/force500")
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"500 - Server Error", response.data)
        self.assertIn(b"Something went wrong", response.data)
        print("✅ Custom 500 page works")



if __name__ == '__main__':
    unittest.main()
    print("\n✅ All tests completed. Review above for any warnings.")

