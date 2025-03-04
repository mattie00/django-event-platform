document.addEventListener("DOMContentLoaded", function () {
    const artistSelect = document.getElementById("artist_select");
    const artistEventsContainer = document.getElementById("artist-events-container");

    if (artistSelect && artistEventsContainer) {
        artistSelect.addEventListener("change", function () {
            const selectedArtist = artistSelect.value;
            const ajaxUrl = artistEventsContainer.getAttribute("data-ajax-url");

            const url = new URL(ajaxUrl, window.location.origin);
            if (selectedArtist) {
                url.searchParams.append("artist", selectedArtist);
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
                    artistEventsContainer.innerHTML = await html;
                })
                .catch((error) => {
                    console.error("Wystąpił błąd podczas ładowania danych:", error);
                });
        });

        artistSelect.dispatchEvent(new Event("change"));
    }
});
