
document.addEventListener("DOMContentLoaded", () => {
    const hamburgerIcon = document.getElementById("hamburger-icon");
    const menu = document.getElementById("menu");

    // Toggle the visibility of the menu
    hamburgerIcon.addEventListener("click", () => {
        menu.classList.toggle("show"); // Toggle the 'show' class
    });

    // Close the menu if the user clicks outside
    window.addEventListener("click", (event) => {
        if (!menu.contains(event.target) && !hamburgerIcon.contains(event.target)) {
            menu.classList.remove("show"); // Hide the menu by removing the 'show' class
        }
    });
});