document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.countdown-btn').forEach(btn => {
        let seconds = parseInt(btn.dataset.seconds);
        const timeSpan = btn.querySelector('.time');

        function updateTimer() {
            if (seconds <= 0) {
                location.reload(); // auto enable after cooldown
                return;
            }

            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;

            timeSpan.innerText =
                String(mins).padStart(2, '0') + ':' +
                String(secs).padStart(2, '0');

            seconds--;
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    });
});
