// --- STATE MANAGEMENT ---
let currentWindow = 'spiral';
let isTransitioning = false;

// --- DOM ELEMENTS ---
const mainContainer = document.querySelector('main');
const viewport = document.getElementById('viewport');
const chatInput = document.getElementById('chatInput');
const placeholders = {
    spores: 'reflect...',
    spiral: 'compose...',
    throttle: 'ignite...'
};
const outputAreas = {
    spores: document.getElementById('spores-output'),
    spiral: document.getElementById('spiral-output'),
    throttle: document.getElementById('throttle-output'),
};
const fullscreenViewer = document.getElementById('fullscreen-viewer');
const fullscreenContent = document.getElementById('fullscreen-content');
const fullscreenCloseBtn = document.getElementById('fullscreen-close-btn');
const constellationIframe = document.getElementById('constellation-iframe');
  
// --- LOCAL LEDGER SYSTEM ---
let ledgerStore = JSON.parse(localStorage.getItem("ledgerStore") || "{}");

function newSession() {
  const id = "session_" + new Date().toISOString();
  if (!ledgerStore.sessions) ledgerStore.sessions = {};
  ledgerStore.sessions[id] = [];
  ledgerStore.activeSession = id;
  localStorage.setItem("ledgerStore", JSON.stringify(ledgerStore));
  clearChatUI();
  console.log("Joojit session initialized:", id);
}

function getActiveLedger() {
  if (!ledgerStore.activeSession || !ledgerStore.sessions) return [];
  return ledgerStore.sessions[ledgerStore.activeSession];
}

function generateUUID() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }


function saveTurn(prompt, reply, model, latency) {
  const record = {
    id: generateUUID(),
    timestamp: new Date().toISOString(),
    prompt,
    reply,
    model,
    latency_ms: latency
  };
  const activeLedger = getActiveLedger();
  activeLedger.push(record);
  localStorage.setItem("ledgerStore", JSON.stringify(ledgerStore));
}
async function exportLedger() {
  const ledger = getActiveLedger();
  if (!ledger.length) return alert("Nothing to export");

  try {
    const res = await fetch("/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ledger)
    });

    if (!res.ok) throw new Error("Export failed");

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `session_${new Date().toISOString().slice(0,10)}.jsonl`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 3000);
  } catch (err) {
    console.error("Error exporting ledger:", err);
    alert("There was an issue exporting the conversation.");
  }
}


function clearAllSessions() {
  if (confirm("This will erase all saved chats. Are you sure?")) {
    localStorage.removeItem("ledgerStore");
    ledgerStore = {}; // Reset the in-memory store
    newSession(); // Initialize a fresh session state and clear UI
    console.log("All sessions cleared.");
  }
}

function clearChatUI() {
    for (const key in outputAreas) {
        outputAreas[key].innerHTML = '';
    }
}

function loadActiveSessionHistory() {
    clearChatUI(); 
    const activeLedger = getActiveLedger();
    if (!activeLedger) return;

    const outputContainer = outputAreas[currentWindow]; 

    activeLedger.forEach(turn => {
        const userPromptElem = document.createElement('div');
        userPromptElem.className = 'chat-message user-prompt';
        userPromptElem.textContent = turn.prompt;
        outputContainer.appendChild(userPromptElem);

        const aiResponseElem = document.createElement('div');
        aiResponseElem.className = 'chat-message ai-response';
        aiResponseElem.textContent = turn.reply;
        outputContainer.appendChild(aiResponseElem);
    });

    if (outputContainer.children.length > 0) {
        outputContainer.scrollTop = outputContainer.scrollHeight;
    }
}

// --- INITIALIZATION ---
window.onload = function() {
  viewport.style.transition = 'none';
  viewport.style.transform = 'translateX(-100vw)';
  updateActiveWindow('spiral');
  
  setTimeout(() => {
      viewport.style.transition = 'transform 1s ease-in-out, opacity 0.4s ease-in-out';
  }, 50);

  if (!ledgerStore.sessions || !ledgerStore.activeSession) {
      newSession();
  } else {
      loadActiveSessionHistory();
  }
};

// --- MAIN NAVIGATION (Chat <-> Constellation) ---
function showConstellation() {
    // Lazy-load the iframe source to improve initial page performance
    if (!constellationIframe.src) {
        const constellationSrc = constellationIframe.dataset.src;
        if(constellationSrc) {
            console.log("Loading constellation assets for the first time.");
            constellationIframe.src = constellationSrc;
        } else {
            console.warn("Constellation iframe data-src attribute is missing.");
        }
    }
    mainContainer.style.transform = 'translateX(-100vw)';
}

function showChat() {
    mainContainer.style.transform = 'translateX(0vw)';
}

// --- NAVIGATION LOGIC ---
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

function updateActiveWindow(windowName) {
    currentWindow = windowName;
    chatInput.placeholder = placeholders[windowName];
    loadActiveSessionHistory();
}

async function showSpores() {
    if (isTransitioning || currentWindow === 'spores') return;
    isTransitioning = true;
    viewport.style.transition = 'transform 1s ease-in-out';
    viewport.style.transform = 'translateX(0vw)';
    updateActiveWindow('spores');
    await wait(1000);
    isTransitioning = false;
}

async function showSpiral() {
    if (isTransitioning || currentWindow === 'spiral') return;
    isTransitioning = true;
    viewport.style.transition = 'transform 1s ease-in-out';
    viewport.style.transform = 'translateX(-100vw)';
    updateActiveWindow('spiral');
    await wait(1000);
    isTransitioning = false;
}

async function showThrottle() {
    if (isTransitioning || currentWindow === 'throttle') return;
    isTransitioning = true;
    viewport.style.transition = 'transform 1s ease-in-out';
    viewport.style.transform = 'translateX(-200vw)';
    updateActiveWindow('throttle');
    await wait(1000);
    isTransitioning = false;
}

// --- TOOLBAR AND INPUT LOGIC ---
function clearInput() {
    chatInput.value = '';
    chatInput.style.height = '96px'; /* DECREASED by ~30% */
}

chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = (chatInput.scrollHeight) + 'px';
});

// --- FULLSCREEN LOGIC ---
function enterFullscreen() {
    const currentOutput = outputAreas[currentWindow];
    fullscreenContent.innerHTML = currentOutput.innerHTML;
    fullscreenViewer.classList.add('active');
    fullscreenContent.scrollTop = fullscreenContent.scrollHeight;
}

function exitFullscreen() {
    fullscreenViewer.classList.remove('active');
    fullscreenContent.innerHTML = '';
}

const API_BASE = window.location.hostname.includes("localhost")
? "http://127.0.0.1:5001"
: "https://web-production-385b3.up.railway.app"; // replace with your actual URL


// --- API & SUBMISSION LOGIC ---
async function submitChat(prompt, outputContainer) {
  const userPromptElem = document.createElement('div');
  userPromptElem.className = 'chat-message user-prompt';
  userPromptElem.textContent = prompt;
  outputContainer.appendChild(userPromptElem);
  
  const thinkingIndicator = document.createElement('div');
  thinkingIndicator.className = 'chat-message ai-response';
  thinkingIndicator.textContent = '...';
  outputContainer.appendChild(thinkingIndicator);
  outputContainer.scrollTop = outputContainer.scrollHeight;

  try {
    const start = performance.now();
    const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
    });
    const latency = performance.now() - start;
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const data = await res.json();
    thinkingIndicator.textContent = data.reply;
    // --- SAVE LOCALLY ---
    saveTurn(prompt, data.reply, data.model || "gpt-4o", Math.round(latency));

  } catch (error) {
    console.error("Failed to fetch from API:", error);
    thinkingIndicator.textContent = `Error: Could not connect to the agent.`;
    thinkingIndicator.style.backgroundColor = 'var(--primary-pink)';
  } finally {
    outputContainer.scrollTop = outputContainer.scrollHeight;
  }
}

async function handleMainSubmit() {
    const prompt = chatInput.value.trim();
    if(!prompt) return;
    submitChat(prompt, outputAreas[currentWindow]);
    clearInput();
}

// --- EVENT LISTENERS ---
chatInput.addEventListener("keydown", function(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleMainSubmit();
  }
});

fullscreenCloseBtn.addEventListener('click', exitFullscreen);
