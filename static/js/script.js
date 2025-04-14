document.addEventListener('DOMContentLoaded', () => {
    // Fetch and update request count
    async function updateRequestCount() {
        try {
            const response = await fetch('/api/requests');
            const requests = await response.json();
            const count = requests.length;
            const counter = document.getElementById('requestCount');
            if (counter) {
                counter.textContent = count;
                // Pulse animation on update
                counter.style.animation = 'pulse 0.5s ease';
                setTimeout(() => counter.style.animation = '', 500);
            }
        } catch (error) {
            console.error('Error fetching request count:', error);
        }
    }

    // Define pulse animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);

    // Update immediately and every 5 seconds
    updateRequestCount();
    setInterval(updateRequestCount, 5000);
});