// --- Security Features ---

window.addEventListener('blur', () => {
    if (typeof quizFinished !== 'undefined' && quizFinished) return;
    if (typeof warnings !== 'undefined') {
        warnings++;
        logCheating('tab_switch');

        if (warnings >= 3) {
            showSuspensionAlert("Maximum warnings reached. Your session has been suspended. Returning to waiting room in 3 seconds...");
        } else {
            showSecurityAlert(`Warning ${warnings}/3: Tab switching detected. Do not switch tabs or windows. Multiple violations will result in suspension.`);
        }
    }
});

document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement && (typeof quizFinished === 'undefined' || !quizFinished)) {
        logCheating('fullscreen_exit');
        showSecurityAlert("Fullscreen exited. Please stay in fullscreen mode.");
    }
});

function showSecurityAlert(msg) {
    const msgEl = document.getElementById('violation-msg');
    const overlay = document.getElementById('security-overlay');
    if (msgEl && overlay) {
        msgEl.innerText = msg;
        overlay.style.display = 'flex';
    }
}

function showSuspensionAlert(msg) {
    const msgEl = document.getElementById('violation-msg');
    const overlay = document.getElementById('security-overlay');
    const title = document.getElementById('security-title');
    const resumeBtn = document.getElementById('resume-btn');

    if (msgEl && overlay && title) {
        title.innerText = "SESSION SUSPENDED";
        msgEl.innerText = msg;
        if (resumeBtn) resumeBtn.style.display = 'none';
        overlay.style.display = 'flex';

        fetch('/api/suspend_participant', { method: 'POST' }).then(() => {
            setTimeout(() => {
                window.location.href = '/participant/waiting_room';
            }, 3000);
        });
    }
}

function resumeQuiz() {
    const overlay = document.getElementById('security-overlay');
    if (overlay) overlay.style.display = 'none';

    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(e => { console.log(e); });
    }
}

function logCheating(type) {
    fetch('/api/cheating_log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_type: type })
    }).catch(e => console.error(e));
}

// Initial Fullscreen Request
window.addEventListener('click', function initFS() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(e => { console.log(e); });
    }
    window.removeEventListener('click', initFS);
});
