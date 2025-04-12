// script.js
//Used for:
//* Input validation and dark mode toggle are handled
//* Resume and job description validations 


//This is part of a client-side script designed to enhance the user experience on a page where a user can either:
//upload a resume file OR
//paste their resume into a textarea.
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

  const toggle = document.getElementById("darkModeToggle");
  const body = document.body;

  // Load saved theme preference
  if (localStorage.getItem("dark-mode") === "enabled") {
    body.classList.add("dark-mode");
    if (toggle) toggle.checked = true;
  }

  if (toggle) {
    toggle.addEventListener("change", () => {
      if (toggle.checked) {
        body.classList.add("dark-mode");
        localStorage.setItem("dark-mode", "enabled");
      } else {
        body.classList.remove("dark-mode");
        localStorage.setItem("dark-mode", "disabled");
      }
    });
  }

  // JavaScript to Handle Field Disabling
  // Ensures no input field is accidentally sent blank when it was never used.
  const jobForm = document.querySelector("form[action='/job_description']");
  if (jobForm) {
    jobForm.addEventListener("submit", function (e) {
      const activeTabId = document.querySelector(".tab-pane.active").id;

      if (activeTabId === "url") {
        document.getElementById("job").disabled = true;
      } else {
        document.getElementById("job_url").disabled = true;
      }
    });

    // Re-enable fields if user navigates back
    window.addEventListener("pageshow", () => {
      document.getElementById("job").disabled = false;
      document.getElementById("job_url").disabled = false;
    });
  }

  // JavaScript to Handle Field Disabling
  // Ensures no input field is accidentally sent blank when it was never used.
  const resumeForm = document.querySelector("form[action='/upload_resume']");
  if (resumeForm) {
    resumeForm.addEventListener("submit", function (e) {
      const activeTabId = document.querySelector(".tab-pane.active").id;

      if (activeTabId === "upload") {
        document.getElementById("resume").disabled = true;
      } else {
        document.getElementById("resume_file").disabled = true;
      }
    });

    window.addEventListener("pageshow", () => {
      const resumeText = document.getElementById("resume");
      const resumeFile = document.getElementById("resume_file");
      if (resumeText) resumeText.disabled = false;
      if (resumeFile) resumeFile.disabled = false;
    });
  }

}); 

function downloadTxt() {
  const text = document.getElementById("letter-content").innerText;
  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "cover_letter.txt";
  a.click();
  URL.revokeObjectURL(url);
}

function downloadPdf() {
  const text = document.getElementById("letter-content").innerText;
  const doc = new jsPDF(); 
  doc.setFont("Helvetica");
  doc.setFontSize(12);
  const lines = doc.splitTextToSize(text, 180);
  doc.text(lines, 15, 20);
  doc.save("cover_letter.pdf");
}

function downloadDocx() {
  const text = document.getElementById("letter-content").innerText;
  const blob = new Blob([text], {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "cover_letter.docx";
  a.click();
  URL.revokeObjectURL(url);
}
