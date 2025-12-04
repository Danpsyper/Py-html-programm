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


function updateSliderColor(slider) {
    let value = slider.value;

    let r = 255;
    let g = Math.floor(165 - (165 * (value / 100)));
    let b = 0;

    slider.style.background = `rgb(${r}, ${g}, ${b})`;
}

document.querySelectorAll(".slider-box").forEach(box => {
    let slider = box.querySelector(".range");
    let text = box.querySelector(".value-inside");

    updateSliderColor(slider);
    text.textContent = slider.value;

    slider.addEventListener("input", () => {
        text.textContent = slider.value;
        updateSliderColor(slider);
    });
});


setTimeout(() => {
    let s = document.querySelectorAll(".range")[0];
    s.value = 0;        
    updateSliderColor(s);
    s.parentElement.querySelector(".value-inside").textContent = s.value;
}, 2000);