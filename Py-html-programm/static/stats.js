const slides = document.querySelectorAll('.slide');
let index = 0;

const classField = document.getElementById("class-field");
const form = document.querySelector(".form");
let sendTimeout;

function sendStats() {
    const stats = {};
    document.querySelectorAll(".range").forEach(slider => {
        stats[slider.name] = slider.value;

        const hiddenInput = document.querySelector(`input[name="${slider.name}"][type="hidden"]`);
        if (hiddenInput) hiddenInput.value = slider.value;
    });

    if (classField) {
        classField.value = document.querySelector(".slide.active").dataset.class;
    }

    const formData = new FormData();
    Object.entries(stats).forEach(([key, value]) => formData.append(key, value));

    fetch("/save_stats", {
        method: "POST",
        body: formData
    });
}

function loadStatsFromSlide(slide) {
    const stats = ["hp", "damage", "armor", "stamina", "evade"];

    if (classField) {
        classField.value = slide.dataset.class;
    }

    stats.forEach(stat => {
        const slider = document.querySelector(`input[name="${stat}"]`);
        const text = slider.parentElement.querySelector(".value-inside");

        slider.value = slide.dataset[stat];
        text.textContent = slide.dataset[stat];
        updateSliderColor(slider);

        const hiddenInput = document.querySelector(`input[name="${stat}"][type="hidden"]`);
        if (hiddenInput) hiddenInput.value = slide.dataset[stat];
    });

    sendStats();
}

function updateSliderColor(slider) {
    const value = slider.value;
    const r = 255;
    const g = Math.floor(165 - (165 * (value / 100)));
    const b = 0;
    slider.style.background = `rgb(${r}, ${g}, ${b})`;
}

function showSlide(newIndex, direction) {
    slides.forEach(slide => slide.classList.remove('active', 'slide-left', 'slide-right'));

    if (direction === "left") {
        slides[index].classList.add('slide-left');
    } else if (direction === "right") {
        slides[index].classList.add('slide-right');
    }

    index = newIndex;
    slides[index].classList.add('active');

    loadStatsFromSlide(slides[index]);
}

document.querySelector('.next').addEventListener('click', () => {
    const newIndex = (index + 1) % slides.length;
    showSlide(newIndex, "right");
});

document.querySelector('.prev').addEventListener('click', () => {
    const newIndex = (index - 1 + slides.length) % slides.length;
    showSlide(newIndex, "left");
});

document.querySelectorAll(".slider-box").forEach(box => {
    const slider = box.querySelector(".range");
    const text = box.querySelector(".value-inside");

    text.textContent = slider.value;
    updateSliderColor(slider);

    slider.addEventListener("input", () => {
        text.textContent = slider.value;
        updateSliderColor(slider);

        clearTimeout(sendTimeout);
        sendTimeout = setTimeout(sendStats, 150);
    });
});

if (form) {
    form.addEventListener("submit", () => {
        sendStats();
    });
}

loadStatsFromSlide(slides[index]);
