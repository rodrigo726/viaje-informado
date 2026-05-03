document.addEventListener("DOMContentLoaded", function() {
    // Set current year in footer
    const yearSpan = document.getElementById('current-year');
    if(yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
});
