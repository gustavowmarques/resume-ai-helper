
document.addEventListener("DOMContentLoaded", () => {
    const textarea = document.getElementById("resume");
    const fileInput = document.getElementById("resume_file");
    const button = document.getElementById("generate");
    const form = document.querySelector("form");
  
    // Change button color when text is typed
    if (textarea && button) {
      textarea.addEventListener("input", () => {
        button.style.backgroundColor = "#007bff";
      });
    }
  
    // Show loading spinner on form submit
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
      form.addEventListener("submit", () => {
        const loading = document.getElementById("loading");
        if (loading) {
          loading.style.display = "block";
        }
      });
    });
  
    // Validate that either resume file OR text is provided
    if (form && textarea) {
      form.addEventListener("submit", (event) => {
        // Only apply this validation on the resume upload page
        if (fileInput && textarea) {
          const hasText = textarea.value.trim().length > 0;
          const hasFile = fileInput.files.length > 0;
  
          if (!hasText && !hasFile) {
            alert("Please either paste your resume or upload a file.");
            event.preventDefault(); // Stop form submission
          }
        }
      });
    }

    // Validation for /job_description form
if (window.location.pathname === "/job_description") {
    const jobForm = document.querySelector("form");
    const jobTextarea = document.getElementById("job");
    const jobURLInput = document.getElementById("job_url");
  
    if (jobForm && jobTextarea && jobURLInput) {
      jobForm.addEventListener("submit", (event) => {
        const hasJobText = jobTextarea.value.trim().length > 0;
        const hasJobURL = jobURLInput.value.trim().length > 0;
  
        if (!hasJobText && !hasJobURL) {
          alert("Please either paste the job description or enter the job URL.");
          event.preventDefault();
        }
      });
    }
  }

  });
  