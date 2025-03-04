document.addEventListener('DOMContentLoaded', function () {
    const scrollToTopButton = document.getElementById('scrollToTop');

    const toggleScrollToTopButton = () => {
        if (window.scrollY > 20) {
            scrollToTopButton.style.display = 'flex';
        } else {
            scrollToTopButton.style.display = 'none';
        }
    };

    scrollToTopButton.addEventListener('click', function () {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    window.addEventListener('scroll', toggleScrollToTopButton);

    toggleScrollToTopButton();
});


