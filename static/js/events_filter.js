document.addEventListener("DOMContentLoaded", function () {
    const eventsContainer = document.getElementById("events-container");
    const filterButtons = document.querySelectorAll(".filter-btn");

    function loadEvents(period) {
        fetch(`${eventsContainer.dataset.url}?period=${period}`)
            .then(response => response.json())
            .then(data => {
                eventsContainer.innerHTML = data.html;
                if (!data.success) {
                    console.warn("Brak wydarzeń dla wybranego okresu.");
                }
            })
            .catch(error => console.error("Błąd ładowania wydarzeń:", error));
    }

    filterButtons.forEach(button => {
        button.addEventListener("click", () => {
            filterButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");
            const period = button.getAttribute("data-period");
            loadEvents(period);
        });
    });

    loadEvents("today");
});

