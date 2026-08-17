// IMPORTANT: Replace this with your deployed backend URL once you deploy to Railway.
// Example: "https://ask-talal-production.up.railway.app"
const BACKEND_URL = "https://ask-talal-v2-production-ff13.up.railway.app";
const loginCard = document.getElementById("login-card");
const loginForm = document.getElementById("login-form");
const loginBtn = document.getElementById("login-btn");

const chatWindow = document.getElementById("chat-window");
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const chipRow = document.getElementById("chip-row");

let visitorId = null;
let visitorName = null;
let history = [];

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

function addTypingIndicator() {
  const div = document.createElement("div");
  div.className = "message agent";
  div.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

async function sendMessage(userMessage) {
  addMessage(userMessage, "user");
  history.push({ role: "user", content: userMessage });
  chatInput.value = "";
  sendBtn.disabled = true;
  chipRow.style.display = "none"; // hide chips after first message

  const typingEl = addTypingIndicator();

  try {
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ visitor_id: visitorId, message: userMessage, history }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `Server responded ${response.status}`);
    }

    typingEl.remove();
    addMessage(data.reply, "agent");
    history.push({ role: "assistant", content: data.reply });
  } catch (err) {
    typingEl.remove();
    addMessage("Sorry, something went wrong: " + err.message, "agent");
    console.error("Chat error:", err);
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

// ---------- Login ----------

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("login-name").value.trim();
  const email = document.getElementById("login-email").value.trim();
  if (!name || !email) return;

  loginBtn.disabled = true;
  loginBtn.textContent = "Starting...";

  try {
    const response = await fetch(`${BACKEND_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Login failed");

    visitorId = data.visitor_id;
    visitorName = data.name;

    loginCard.style.display = "none";
    chatWindow.style.display = "flex";

    addMessage(
      `Hi ${visitorName.split(" ")[0]} 👋 I'm Talal's AI agent. Ask me about my projects, skills, or experience — or tap a suggestion below.`,
      "agent"
    );
  } catch (err) {
    alert("Couldn't start chat: " + err.message);
    loginBtn.disabled = false;
    loginBtn.textContent = "Start chatting";
  }
});

// ---------- Chat ----------

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const userMessage = chatInput.value.trim();
  if (!userMessage) return;
  sendMessage(userMessage);
});

// ---------- Suggested chips ----------

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    const q = chip.dataset.q;
    sendMessage(q);
  });
});
