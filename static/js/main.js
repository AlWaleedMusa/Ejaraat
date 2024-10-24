// Close sidebar on click
const links = document.querySelectorAll(".list-group-item");
links.forEach((link) => {
    link.addEventListener("click", () => {
        document.getElementById("sidebar-wrapper").classList.toggle("d-block");
    });
});

// Sidebar Toggle
document.getElementById("menu-toggle").addEventListener("click", function () {
    const sidebar = document.getElementById("sidebar-wrapper");
    sidebar.classList.toggle("d-block");

    // Add or remove the click outside event listener based on sidebar state
    if (sidebar.classList.contains("d-block")) {
        document.addEventListener("click", closeSidebarOnClickOutside);
    } else {
        document.removeEventListener("click", closeSidebarOnClickOutside);
    }
});

function closeSidebarOnClickOutside(event) {
    const sidebar = document.getElementById("sidebar-wrapper");
    const menuToggle = document.getElementById("menu-toggle");

    // Check if the click happened outside the sidebar and the menu toggle button
    if (!sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
        sidebar.classList.remove("d-block"); // Close the sidebar
        document.removeEventListener("click", closeSidebarOnClickOutside);
    }
}

// Notifications
const bellIcon = document.querySelectorAll(".bi-bell");
const notificationsContainer = document.querySelectorAll(
    ".notifications-container"
);
const recentActivitiesContainer = document.querySelector(
    ".recent-activities-container"
);
const closeNotifications = document.querySelectorAll(".close-notifications");
const closeRecentActivities = document.querySelector(".close-recent-activities");

bellIcon.forEach((icon) => {
    icon.addEventListener("click", () => {
        // Toggle the notificationsContainer container
        notificationsContainer.forEach((container) => {
            container.classList.toggle("d-none");

            // Hide the notifications counter
            // notificationsCount.forEach((count) => {
            //     count.classList.add("d-none");
            //     count.innerHTML = "";
            // });

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
        });
    });
});

// Close the notificationsContainer container when the user clicks the close button
closeNotifications.forEach((close) => {
    close.addEventListener("click", () => {
        notificationsContainer.forEach((container) => {
            container.classList.add("d-none");
        });
    });
});

// Close recent activities container when close is pressed
closeRecentActivities.addEventListener("click", () => {
    recentActivitiesContainer.classList.add("d-none");
});

// Notifications counter
const notificationsCount = document.querySelectorAll(".notification-counter");

document.body.addEventListener("htmx:wsAfterMessage", (event) => {
    const message = JSON.parse(event.detail.message);

    if (message.type === "notifications") {
        let numberOfNotifications = parseInt(notificationsCount[0].innerHTML);

        if (isNaN(numberOfNotifications)) {
            numberOfNotifications = 0;
        }

        numberOfNotifications += 1;

        notificationsCount.forEach((count) => {
            count.classList.remove("d-none");
            count.innerHTML = numberOfNotifications;
        });

        notificationsContainer.forEach((container) => {
            container.innerHTML = message.notifications_html;
            attachCloseButtonListener();
        });
    } else if (message.type === "recent_activities") {
        recentActivitiesContainer.innerHTML = message.activities_html;
        attachCloseButtonListener();
    } else if (message.type === "clear_notifications") {
        notificationsCount.forEach((count) => {
            count.classList.add("d-none");
            count.innerHTML = "";
        });

        notificationsContainer.forEach((container) => {
            container.innerHTML = message.notifications_html;
            container.classList.add("d-none");
            attachCloseButtonListener();
        });
    } else if ((message.type = "payment_status_chart")) {        
        paymentCharts(
            parseInt(message.data["paid"]),
            parseInt(message.data["pending"]),
            parseInt(message.data["overdue"])
        );
    }
});

function paymentCharts(paid, pending, overdue) {
    rentPaymentChart.data.datasets[0].data = [paid, pending, overdue];
    rentPaymentChart.update();
}

// Function to attach the close button event listener
function attachCloseButtonListener() {
    const closeNotifications = document.querySelectorAll(
        ".close-notifications"
    );
    const closeRecentActivities = document.querySelector(
        ".close-recent-activities"
    );

    closeRecentActivities.addEventListener("click", function () {
        const container = this.closest(".navbar-recent-activities");
        if (container) {
            container.classList.add("d-none");
        }
    });

    closeNotifications.forEach((close) => {
        close.addEventListener("click", function () {
            const container = this.closest(".notifications-container");
            if (container) {
                container.classList.add("d-none");
            }
        });
    });
}

attachCloseButtonListener();


const clock = document.querySelector(".bi-clock-nav");
const clockContainer = document.querySelector(".navbar-recent-activities");

clock.addEventListener("click", () => {
    clockContainer.classList.toggle("d-none");

    window.addEventListener("click", (e) => {
        if (!clockContainer.contains(e.target) && !clock.contains(e.target)) {
            clockContainer.classList.add("d-none");
        }
    });

    const links = clockContainer.querySelectorAll("a");
    links.forEach((link) => {
        link.addEventListener("click", () => {
            clockContainer.classList.add("d-none");
        });
    });
});