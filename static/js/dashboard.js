// Global admin dashboard utilities

function confirmDelete(id, title) {
    if (confirm(`Are you sure you want to delete "${title}"? This will remove all associated results and questions.`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/delete_quiz/${id}`;
        document.body.appendChild(form);
        form.submit();
    }
}

function approveParticipant(pId, button) {
    fetch('/api/approve_participant/' + pId, { method: 'POST' })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (data.success && button) {
                button.closest('.participant-row').remove();
            }
        });
}

// Auto-refresh for live dashboard views
function initLivePolling(intervalMs = 10000) {
    setInterval(function () {
        window.location.reload();
    }, intervalMs);
}
