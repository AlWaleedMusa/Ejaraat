// Close sidebar on click
const links = document.querySelectorAll(".list-group-item");
links.forEach((link) => {
    link.addEventListener("click", () => {
        document.getElementById("sidebar-wrapper").classList.toggle("d-block");
    });
});

// Sidebar Toggle
document.getElementById("menu-toggle").addEventListener("click", function () {
    document.getElementById("sidebar-wrapper").classList.toggle("d-block");
});

// Notifications counter
const notificationsCount = document.querySelectorAll(".notification-counter");

document.body.addEventListener("htmx:wsAfterMessage", () => {
    let numberOfNotifications = parseInt(notificationsCount[0].innerHTML);

    if (isNaN(numberOfNotifications)) {
        numberOfNotifications = 0;
    }

    numberOfNotifications += 1;

    notificationsCount.forEach((count) => {
        count.classList.remove("d-none");

        count.innerHTML = numberOfNotifications;
    });
});

// Notifications
const bellIcon = document.querySelectorAll(".bi-bell");
const notificationsContainer = document.querySelectorAll(
    ".notifications-container"
);
const closeNotifications = document.querySelectorAll(".close-notifications");

bellIcon.forEach((icon) => {
    icon.addEventListener("click", () => {
        // Toggle the notificationsContainer container
        notificationsContainer.forEach((container) => {
            container.classList.toggle("d-none");

        // Hide the notifications counter
        notificationsCount.forEach((count) => {
            count.classList.add("d-none");
            count.innerHTML = "";
        });


            // Close the notificationsContainer container when the user clicks outside of it
            window.addEventListener("click", (e) => {
                if (!container.contains(e.target) && !icon.contains(e.target)) {
                    container.classList.add("d-none");
                }
            });

            // Close the notificationsContainer container when the user clicks an <a> inside the container
            const links = container.querySelectorAll("a");
            links.forEach((link) => {
                link.addEventListener("click", () => {
                    container.classList.add("d-none");
                });
            });

            // Close the notificationsContainer container when the user clicks the close button
            closeNotifications.forEach((close) => {
                close.addEventListener("click", () => {
                    container.classList.add("d-none");
                });
            });
        });
    });
});
