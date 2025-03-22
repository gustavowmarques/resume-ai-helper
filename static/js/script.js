document.addEventListener("DOMContentLoaded", ()=> {
    const textarea = document.getElementById("resume");
    const button = document.getElementById("generate");

    if(textarea && button) {
        textarea.addEventListener("input", () => {
            button.style.backgroundColor = "#007bff"
        });
    }
});