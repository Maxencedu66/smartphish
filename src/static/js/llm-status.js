function fetchStatus() {
    fetch('/llm-status-get')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('model-status');
            tbody.innerHTML = '';
            data.forEach(model => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="badge bg-${model.expires_at ? 'success' : 'danger'}">${model.expires_at ? 'En mémoire' : 'Non chargé'}</span></td>
                    <td>${model.name}</td>
                    <td>${model.size_mb}</td>
                    <td>${model.family}</td>
                    <td>${model.parameter_size}</td>
                    <td>${model.modified_at}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching status:', error));
}

function startCountdown() {
    let countdown = 5;
    const countdownElement = document.getElementById('countdown');
    const interval = setInterval(() => {
        countdown--;
        countdownElement.textContent = countdown;
        if (countdown <= 0) {
            clearInterval(interval);
            countdown = 5;
            fetchStatus();
            startCountdown();
        }
    }, 1000);
}

fetchStatus(); // Initial fetch
startCountdown();