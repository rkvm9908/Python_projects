// src/static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('detectionForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    if (form && loadingIndicator) {
        form.addEventListener('submit', function() {
            loadingIndicator.style.display = 'block';
            const submitButton = form.querySelector('.submit-btn');
            submitButton.disabled = true;
            submitButton.innerHTML = 'Analyzing... Please Wait';
        });
    }
            document.getElementById("timeBox").innerText = new Date().toLocaleString();
});

// src/static/js/main.js (Add this function)

function animateScoreCounters() {
    const counters = document.querySelectorAll('.score-value');
    const duration = 1500; // 1.5 seconds animation

    counters.forEach(counter => {
        const target = parseFloat(counter.dataset.target);
        let start = 0;
        const step = target / (duration / 16); // 16ms is roughly 60fps

        const count = () => {
            start += step;
            
            // If the current number exceeds the target, stop the animation
            if (start >= target) {
                counter.textContent = target.toFixed(1);
                return;
            }

            // Update the text, formatted to one decimal place
            counter.textContent = start.toFixed(1);
            
            // Continue the animation
            requestAnimationFrame(count);
        };
        
        // Start the animation only when the element is visible
        requestAnimationFrame(count);
    });
}
function animateSubmittedText() {
    const headerElement = document.querySelector('.typing-effect-header');
    
    if (headerElement) {
        const textToType = headerElement.dataset.text;
        headerElement.textContent = ''; // Clear initial text
        
        let charIndex = 0;
        const typingSpeed = 70; // milliseconds per character

        function type() {
            if (charIndex < textToType.length) {
                headerElement.textContent += textToType.charAt(charIndex);
                charIndex++;
                setTimeout(type, typingSpeed);
            } else {
                headerElement.classList.add('typed'); // Remove cursor after typing
            }
        }
        
        // Start typing after a small delay to align with card animation
        setTimeout(type, 1200); 
    }
}
// Ensure the function is exported or globally available if you use module structure.
// In the updated HTML, we call: document.addEventListener('DOMContentLoaded', animateScoreCounters);