const chatContainer = document.getElementById('chat-container');
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const historyOverlay = document.getElementById('history-overlay');
const historyList = document.getElementById('history-list');
const historyToggleBtn = document.getElementById('history-toggle-btn');
const closeHistoryBtn = document.getElementById('close-history-btn');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const timeDisplay = document.getElementById('time-display');
const startTimerBtn = document.getElementById('start-timer-btn');
const stopTimerBtn = document.getElementById('stop-timer-btn');
const avatarZone = document.querySelector('.avatar-zone');
const pixelBunny = document.querySelector('.pixel-bunny');
const companionSvg = document.getElementById('companion-svg');
const timerMinutesInput = document.getElementById('timer-minutes');
const avatarPrompt = document.getElementById('avatar-prompt');
const miniTimer = document.getElementById('mini-timer');

function setAvatarState(stateName) {
    if (!companionSvg) return;
    Array.from(companionSvg.classList).forEach(className => {
        if (className.startsWith('state-')) {
            companionSvg.classList.remove(className);
        }
    });
    companionSvg.classList.add(`state-${stateName}`);
}

let timerInterval = null;
let secondsRemaining = 25 * 60;
let defaultSessionMinutes = 25;

// Toggle Chat logic
window.electronAPI.onToggleChat(() => {
    console.log('Toggling chat visibility');
    if (chatContainer.style.display === 'flex') {
        chatContainer.style.display = 'none';
        historyOverlay.classList.remove('active');
    } else {
        chatContainer.style.display = 'flex';
        // Hide the prompt if it was visible when opening chat
        avatarPrompt.classList.remove('visible');
        chatInput.focus();
    }
});

// Avatar Interaction
avatarZone.addEventListener('click', () => {
    // Only show prompt if chat is closed
    if (chatContainer.style.display !== 'flex') {
        avatarPrompt.classList.add('visible');
        setTimeout(() => {
            avatarPrompt.classList.remove('visible');
        }, 5000);
    }
});

// History Logic
async function fetchHistory() {
    try {
        const response = await fetch('http://localhost:8000/history');
        const data = await response.json();
        renderHistory(data.history);
    } catch (error) {
        console.error("Fetch History Error:", error);
    }
}

function renderHistory(history) {
    historyList.innerHTML = '';
    if (history.length === 0) {
        historyList.innerHTML = '<div style="text-align:center; padding: 20px; color: #666;">No interactions yet.</div>';
        return;
    }

    history.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'history-item';
        itemDiv.innerHTML = `
            <span class="sender">${item.sender}</span>
            <span class="text">${item.message}</span>
            <button class="delete-item-btn" onclick="deleteHistoryItem(${item.id})">×</button>
        `;
        historyList.appendChild(itemDiv);
    });
}

window.deleteHistoryItem = async (id) => {
    try {
        await fetch(`http://localhost:8000/history/${id}`, { method: 'DELETE' });
        fetchHistory();
    } catch (error) {
        console.error("Delete History Item Error:", error);
    }
};

async function clearAllHistory() {
    if (!confirm("Are you sure you want to clear all history?")) return;
    try {
        await fetch('http://localhost:8000/history', { method: 'DELETE' });
        fetchHistory();
    } catch (error) {
        console.error("Clear History Error:", error);
    }
}

historyToggleBtn.addEventListener('click', () => {
    historyOverlay.classList.toggle('active');
    if (historyOverlay.classList.contains('active')) {
        fetchHistory();
    }
});

closeHistoryBtn.addEventListener('click', () => {
    historyOverlay.classList.remove('active');
});

clearHistoryBtn.addEventListener('click', clearAllHistory);

function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender.toLowerCase() === 'you' ? 'user' : 'bot');
    
    // Simple typing effect for Byte
    if (sender.toLowerCase() !== 'you') {
        msgDiv.textContent = '';
        chatLog.appendChild(msgDiv);
        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                msgDiv.textContent += text[i];
                i++;
                chatLog.scrollTop = chatLog.scrollHeight;
            } else {
                clearInterval(interval);
            }
        }, 30);
    } else {
        msgDiv.textContent = text;
        chatLog.appendChild(msgDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }
}

async function sendMessage(overrideMessage = null, isSystemEvent = false) {
    const message = overrideMessage || chatInput.value.trim();
    if (!message) return;

    if (!isSystemEvent) {
        appendMessage('You', message);
    }
    
    if (!overrideMessage) {
        chatInput.value = '';
    }

    // Automatically open chat if it was closed
    if (chatContainer.style.display !== 'flex') {
        chatContainer.style.display = 'flex';
    }

    // Show Thinking State
    const botMsgDiv = document.createElement('div');
    botMsgDiv.classList.add('message', 'bot', 'thinking');
    botMsgDiv.textContent = '...';
    chatLog.appendChild(botMsgDiv);
    chatLog.scrollTop = chatLog.scrollHeight;

    setAvatarState('thinking');

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.body) throw new Error("No response body");
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";
        
        botMsgDiv.classList.remove('thinking');
        botMsgDiv.textContent = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;
            
            // Clean display text (strip [ACTIONS:] and [SYSTEM_EVENT:] even if partially typed)
            let displayChat = fullText
                .replace(/\[ACTIONS:.*?\]/g, '')
                .replace(/\[SYSTEM_EVENT:.*?\]/g, '')
                .replace(/\[ACTIONS:.*$/, '')
                .replace(/\[SYSTEM_EVENT:.*$/, '')
                .trim();
            
            botMsgDiv.textContent = displayChat; 
            chatLog.scrollTop = chatLog.scrollHeight;
        }

        // Final clean up and stat refresh
        setTimeout(updateUI, 1000); 
        
    } catch (error) {
        console.error("Chat Error:", error);
        botMsgDiv.classList.remove('thinking');
        botMsgDiv.textContent = 'Byte is disconnected from the backend.';
    } finally {
        if (timerInterval) {
            setAvatarState('focusing');
        } else {
            setAvatarState('idle');
        }
    }
}

async function updateUI() {
    try {
        // We still fetch stats to ensure connection is alive, 
        // but we no longer display them in a status bar.
        const response = await fetch('http://localhost:8000/stats');
        const stats = await response.json();
        
        // Sync animation state
        if (stats.current_activity === 'idle') {
            setAvatarState('idle');
        } else if (stats.current_activity === 'focusing') {
            setAvatarState('focusing');
        }
    } catch (error) {
        console.error("Update UI Error:", error);
    }
}

// Initial update
updateUI();

sendBtn.addEventListener('click', () => sendMessage());
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Timer Logic
function updateTimerDisplay() {
    const mins = Math.floor(secondsRemaining / 60);
    const secs = secondsRemaining % 60;
    const timeStr = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    timeDisplay.textContent = timeStr;
    miniTimer.textContent = timeStr;
}

async function startFocus() {
    if (timerInterval) return;
    
    // Lock the input
    timerMinutesInput.disabled = true;
    
    // Instant visual feedback
    setAvatarState('focusing');

    try {
        await fetch('http://localhost:8000/focus/start', { method: 'POST' });
        updateUI(); 
    } catch (e) { 
        console.error("Start Focus Error:", e); 
    }

    startTimerBtn.disabled = true;
    startTimerBtn.textContent = "Focusing...";
    
    // Add visual states
    avatarZone.classList.add('is-focusing');
    pixelBunny.classList.add('is-focusing');
    timeDisplay.classList.add('is-focusing');
    miniTimer.classList.add('visible');

    timerInterval = setInterval(() => {
        if (secondsRemaining > 0) {
            secondsRemaining--;
            updateTimerDisplay();
        }
        
        if (secondsRemaining <= 0) {
            completeFocus();
        }
    }, 1000);
}

async function completeFocus() {
    clearInterval(timerInterval);
    timerInterval = null;
    
    // Remove visual states
    avatarZone.classList.remove('is-focusing');
    pixelBunny.classList.remove('is-focusing');
    timeDisplay.classList.remove('is-focusing');
    miniTimer.classList.remove('visible');

    // Celebrate briefly
    setAvatarState('celebrate');
    setTimeout(() => {
        setAvatarState('idle');
    }, 5000);

    try {
        const response = await fetch('http://localhost:8000/focus/complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                minutes: defaultSessionMinutes,
                completed: true 
            })
        });
        
        // Trigger AI Congratulation
        sendMessage(`[SYSTEM_EVENT: The user just successfully completed a focus session. Congratulate them briefly.]`, true);
        
        secondsRemaining = defaultSessionMinutes * 60;
        updateTimerDisplay();
        updateUI();
    } catch (e) { 
        console.error("Complete Focus Error:", e); 
    } finally {
        startTimerBtn.disabled = false;
        startTimerBtn.textContent = "Start Focus";
        timerMinutesInput.disabled = false;
    }
}

async function stopFocus() {
    if (!timerInterval) return;
    
    const minutesSpent = Math.floor((defaultSessionMinutes * 60 - secondsRemaining) / 60);
    
    clearInterval(timerInterval);
    timerInterval = null;
    
    // Remove visual states
    avatarZone.classList.remove('is-focusing');
    pixelBunny.classList.remove('is-focusing');
    timeDisplay.classList.remove('is-focusing');
    miniTimer.classList.remove('visible');

    startTimerBtn.disabled = false;
    startTimerBtn.textContent = "Start Focus";

    if (minutesSpent > 0) {
        try {
            await fetch('http://localhost:8000/focus/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    minutes: minutesSpent,
                    completed: false 
                })
            });
            appendMessage('Byte', `Stopped early, but logged ${minutesSpent} minutes of work. Good job!`);
            updateUI();
        } catch (e) {
            console.error("Stop Focus Error:", e);
        }
    } else {
        // Just reset activity to idle if < 1 min
        try {
            await fetch('http://localhost:8000/focus/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    minutes: 0,
                    completed: false 
                })
            });
            updateUI();
        } catch (e) {}
    }

    secondsRemaining = defaultSessionMinutes * 60;
    updateTimerDisplay();
    timerMinutesInput.disabled = false;
}

timerMinutesInput.addEventListener('change', () => {
    let val = parseInt(timerMinutesInput.value);
    if (isNaN(val) || val < 1) val = 1;
    if (val > 120) val = 120;
    timerMinutesInput.value = val;
    
    defaultSessionMinutes = val;
    if (!timerInterval) {
        secondsRemaining = defaultSessionMinutes * 60;
        updateTimerDisplay();
    }
});

startTimerBtn.addEventListener('click', startFocus);
stopTimerBtn.addEventListener('click', stopFocus);

// Initial display
updateTimerDisplay();
