document.addEventListener('DOMContentLoaded', function() {
    const citySelect = document.getElementById('city_select');
    const cityEventsContainer = document.getElementById('city-events-container');

    if (citySelect) {
        citySelect.addEventListener('change', function() {
            const city = citySelect.value;

            let url = cityEventsContainer.dataset.ajaxUrl;

            if (city) {
                url += "?city=" + encodeURIComponent(city);
            }

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                cityEventsContainer.innerHTML = html;
            })
            .catch(err => console.error(err));
        });
    }
});