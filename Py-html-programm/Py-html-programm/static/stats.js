const slides = document.querySelectorAll('.slide');
let index = 0;

function showSlide(newIndex, direction) {
    slides.forEach(slide => slide.classList.remove('active', 'slide-left'));

    if (direction === "left") {
        slides[index].classList.add('slide-left');
    }

    index = newIndex;
    slides[index].classList.add('active');
}

document.querySelector('.next').addEventListener('click', () => {
    const newIndex = (index + 1) % slides.length;
    showSlide(newIndex, "right");
});

document.querySelector('.prev').addEventListener('click', () => {
    const newIndex = (index - 1 + slides.length) % slides.length;
    showSlide(newIndex, "left");
});
