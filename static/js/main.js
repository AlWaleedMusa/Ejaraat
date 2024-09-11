// Close sidebar on click
const links = document.querySelectorAll(".list-group-item");

links.forEach((link) => {
    link.addEventListener("click", () => {
        document
            .getElementById("sidebar-wrapper")
            .classList.toggle("d-block");
    });
});

// Sidebar Toggle
document.getElementById("menu-toggle").addEventListener("click", function () {
    document.getElementById("sidebar-wrapper").classList.toggle("d-block");
});
