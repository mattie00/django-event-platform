document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("kids-events");
    const nextButton = document.getElementById("next-kids");
    const prevButton = document.getElementById("prev-kids");

    nextButton.addEventListener("click", function () {
        container.scrollBy({ left: 300, behavior: "smooth" });
    });

    prevButton.addEventListener("click", function () {
        container.scrollBy({ left: -300, behavior: "smooth" });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const cityContainer = document.querySelector(".city-scroll-container");
    const nextCityBtn = document.getElementById("next-city-btn");
    const prevCityBtn = document.getElementById("prev-city-btn");

    const updateCityButtonsVisibility = () => {
        const maxScrollLeft = cityContainer.scrollWidth - cityContainer.clientWidth;
        prevCityBtn.disabled = cityContainer.scrollLeft === 0;
        nextCityBtn.disabled = cityContainer.scrollLeft >= maxScrollLeft - 1;
    };

    nextCityBtn.addEventListener("click", function () {
        cityContainer.scrollBy({ left: 300, behavior: "smooth" });
    });

    prevCityBtn.addEventListener("click", function () {
        cityContainer.scrollBy({ left: -300, behavior: "smooth" });
    });

    cityContainer.addEventListener("scroll", updateCityButtonsVisibility);

    updateCityButtonsVisibility();
});
