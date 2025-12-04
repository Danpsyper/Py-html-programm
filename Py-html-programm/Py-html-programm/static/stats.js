const slides = document.querySelectorAll('.slide');
let index = 0;

function showSlide(newIndex, direction) {
    slides.forEach(slide => slide.classList.remove('active', 'slide-left'));
    if (direction === "left") slides[index].classList.add('slide-left');
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

// Update slider color and send values to Python
document.querySelectorAll(".slider-box").forEach(box => {
    const slider = box.querySelector(".range");
    const text = box.querySelector(".value-inside");

    const updateSliderColor = () => {
        const value = slider.value;
        const r = 255;
        const g = Math.floor(165 - (165 * (value / 100)));
        const b = 0;
        slider.style.background = `rgb(${r}, ${g}, ${b})`;
    }

    // Initialize
    text.textContent = slider.value;
    updateSliderColor();

    slider.addEventListener("input", () => {
        text.textContent = slider.value;
        updateSliderColor();

        // Send updated value to Python
        const stats = {};
        document.querySelectorAll(".range").forEach(s => {
            stats[s.name] = s.value;
        });

        fetch("/save_stats", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(stats)
        })
        .then(res => res.json())
        .then(data => console.log("Saved:", data));
    });
});
