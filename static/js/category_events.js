document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("category_select");
    const categoryEventsContainer = document.getElementById("category-events-container");

    if (categorySelect && categoryEventsContainer) {
        categorySelect.addEventListener("change", function () {
            const selectedCategory = categorySelect.value;
            const ajaxUrl = categoryEventsContainer.getAttribute("data-ajax-url");

            const url = new URL(ajaxUrl, window.location.origin);
            if (selectedCategory) {
                url.searchParams.append("category", selectedCategory);
            }

            fetch(url)
                .then((response) => {
                    if (response.ok) {
                        return response.text();
                    } else {
                        throw new Error("Błąd ładowania danych.");
                    }
                })
                .then(async (html) => {
                    categoryEventsContainer.innerHTML = await html;
                })
                .catch((error) => {
                    console.error("Wystąpił błąd podczas ładowania danych:", error);
                });
        });
    }
});
