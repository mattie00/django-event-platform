document.addEventListener("DOMContentLoaded", function () {
    const tagSelect = document.getElementById("tag_select");
    const tagEventsContainer = document.getElementById("tag-events-container");

    if (tagSelect && tagEventsContainer) {
        tagSelect.addEventListener("change", function () {
            const selectedTag = tagSelect.value;
            const ajaxUrl = tagEventsContainer.getAttribute("data-ajax-url");

            const url = new URL(ajaxUrl, window.location.origin);
            if (selectedTag) {
                url.searchParams.append("tag", selectedTag);
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
                    tagEventsContainer.innerHTML = await html;
                })
                .catch((error) => {
                    console.error("Wystąpił błąd podczas ładowania danych:", error);
                });
        });
    }
});
