// js/chat.js — Chatbot logic for FindX

const API_BASE = 'http://localhost:8000/api/v1';

// ── State ────────────────────────────────────────────────────────
let isLoading      = false;
let chatSessions   = JSON.parse(localStorage.getItem('findx_sessions') || '[]');
let currentSession = null;

// ── DOM References ────────────────────────────────────────────────
const messagesArea   = document.getElementById('messages-area');
const chatInput      = document.getElementById('chat-input');
const sendBtn        = document.getElementById('send-btn');
const welcomeState   = document.getElementById('welcome-state');
const historyList    = document.getElementById('history-list');
const topKInput      = document.getElementById('top-k-input');

// ── Initialize ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const user = requireAuth();
  populateUserUI(user);
  renderHistoryList();
  autoResizeTextarea(chatInput);

  // Keyboard shortcuts
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  sendBtn.addEventListener('click', handleSend);

  // Check backend health on load
  checkBackendHealth();
});

// ── Backend Health ───────────────────────────────────────────────
async function checkBackendHealth() {
  const statusEl = document.getElementById('engine-status');
  const docsEl   = document.getElementById('doc-count');
  try {
    const res  = await fetch(`${API_BASE}/health`);
    const json = await res.json();
    const rag  = json.data?.rag_engine;

    if (rag?.index_loaded) {
      if (statusEl) { statusEl.textContent = 'Ready'; statusEl.style.color = 'var(--accent-emerald)'; }
      if (docsEl)   docsEl.textContent = `${rag.document_count} docs`;
    } else {
      if (statusEl) { statusEl.textContent = 'No Index'; statusEl.style.color = 'var(--accent-pink)'; }
    }
  } catch {
    if (statusEl) { statusEl.textContent = 'Offline'; statusEl.style.color = 'hsl(0,80%,70%)'; }
  }
}

// ── Sending Messages ─────────────────────────────────────────────
async function handleSend() {
  const query = chatInput.value.trim();
  if (!query || isLoading) return;

  // Start new session if none active
  if (!currentSession) startNewSession();

  chatInput.value = '';
  autoResizeTextarea(chatInput);

  // Hide welcome state
  if (welcomeState) welcomeState.style.display = 'none';

  appendUserMessage(query);
  showTypingIndicator();
  setSendState(true);

  try {
    const topK = parseInt(topKInput?.value || '3');
    const res  = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_query: query, top_k: topK })
    });
    const json = await res.json();

    removeTypingIndicator();

    if (!res.ok || json.errors?.length) {
      const errMsg = json.errors?.[0]?.message || json.message || 'Unknown error.';
      appendAIMessage(`⚠️ ${errMsg}`, []);
    } else {
      const { answer, sources } = json.data;
      appendAIMessage(answer, sources || []);
      saveToSession(query, answer, sources || []);
    }
  } catch (err) {
    removeTypingIndicator();
    appendAIMessage(
      '⚠️ Could not reach the backend. Make sure the server is running at `http://localhost:8000`.',
      []
    );
  } finally {
    setSendState(false);
    scrollToBottom();
  }
}

// ── Quick Prompts ────────────────────────────────────────────────
function sendQuickPrompt(text) {
  chatInput.value = text;
  handleSend();
}

// ── Message Rendering ────────────────────────────────────────────
function appendUserMessage(text) {
  const user    = getUser();
  const initials = user?.initials || '?';
  const time    = formatTime(new Date());

  const el = document.createElement('div');
  el.className = 'message user animate-fade-up';
  el.innerHTML = `
    <div class="message-avatar">${initials}</div>
    <div class="message-content">
      <div class="message-bubble">${escapeHtml(text)}</div>
      <div class="message-time">${time}</div>
    </div>
  `;
  messagesArea.appendChild(el);
  scrollToBottom();
}

function appendAIMessage(text, sources) {
  const time = formatTime(new Date());

  const sourcesHtml = sources.length > 0 ? buildSourcesPanel(sources) : '';

  const el = document.createElement('div');
  el.className = 'message ai animate-fade-up';
  el.innerHTML = `
    <div class="message-avatar">✦</div>
    <div class="message-content">
      <div class="message-bubble">${renderMarkdown(text)}</div>
      ${sourcesHtml}
      <div class="message-time">${time}</div>
    </div>
  `;
  messagesArea.appendChild(el);
  scrollToBottom();
}

function buildSourcesPanel(sources) {
  const items = sources.map((s, i) => `
    <div class="source-item">
      <div class="source-item-id">📄 Source ${i + 1} — ID: ${escapeHtml(String(s.document_id))}</div>
      <div>${escapeHtml(s.text.slice(0, 160))}${s.text.length > 160 ? '…' : ''}</div>
    </div>
  `).join('');

  return `
    <div class="sources-panel" id="src-${Date.now()}">
      <div class="sources-toggle" onclick="toggleSources(this.parentElement)">
        <span>📚 ${sources.length} source${sources.length > 1 ? 's' : ''} retrieved</span>
        <span class="sources-toggle-icon">▼</span>
      </div>
      <div class="sources-list">${items}</div>
    </div>
  `;
}

function toggleSources(panel) {
  panel.classList.toggle('open');
}

// ── Typing Indicator ─────────────────────────────────────────────
function showTypingIndicator() {
  const el = document.createElement('div');
  el.className = 'typing-indicator animate-fade-in';
  el.id = 'typing-indicator';
  el.innerHTML = `
    <div class="message-avatar" style="background:var(--grad-accent)">✦</div>
    <div class="typing-bubble">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  `;
  messagesArea.appendChild(el);
  scrollToBottom();
}

function removeTypingIndicator() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

// ── Sessions ─────────────────────────────────────────────────────
function startNewSession() {
  if (welcomeState) welcomeState.style.display = 'none';
  currentSession = {
    id: Date.now(),
    title: 'New Chat',
    messages: [],
    createdAt: new Date().toISOString()
  };
  // Clear the messages area but keep welcome state element
  Array.from(messagesArea.children).forEach(c => {
    if (c.id !== 'welcome-state') c.remove();
  });
}

function saveToSession(query, answer, sources) {
  if (!currentSession) return;

  if (currentSession.messages.length === 0) {
    currentSession.title = query.slice(0, 45) + (query.length > 45 ? '…' : '');
  }
  currentSession.messages.push({ role: 'user', content: query });
  currentSession.messages.push({ role: 'ai', content: answer, sources });

  // Update sessions list
  const idx = chatSessions.findIndex(s => s.id === currentSession.id);
  if (idx >= 0) chatSessions[idx] = currentSession;
  else          chatSessions.unshift(currentSession);

  // Keep last 20 sessions
  if (chatSessions.length > 20) chatSessions.pop();
  localStorage.setItem('findx_sessions', JSON.stringify(chatSessions));

  renderHistoryList();
}

function renderHistoryList() {
  if (!historyList) return;
  historyList.innerHTML = '';
  if (chatSessions.length === 0) {
    historyList.innerHTML = '<div style="padding:12px 20px;font-size:0.8rem;color:var(--text-muted)">No sessions yet</div>';
    return;
  }
  chatSessions.slice(0, 15).forEach(s => {
    const el = document.createElement('div');
    el.className = `chat-history-item ${currentSession?.id === s.id ? 'active' : ''}`;
    el.innerHTML = `<span class="history-icon">💬</span><span class="history-text">${escapeHtml(s.title)}</span>`;
    el.onclick = () => loadSession(s);
    historyList.appendChild(el);
  });
}

function loadSession(session) {
  currentSession = session;
  if (welcomeState) welcomeState.style.display = 'none';

  // Clear current messages
  Array.from(messagesArea.children).forEach(c => {
    if (c.id !== 'welcome-state') c.remove();
  });

  // Replay messages
  session.messages.forEach(msg => {
    if (msg.role === 'user') appendUserMessage(msg.content);
    else appendAIMessage(msg.content, msg.sources || []);
  });

  renderHistoryList();
}

function clearSessions() {
  chatSessions = [];
  currentSession = null;
  localStorage.removeItem('findx_sessions');
  renderHistoryList();
  if (welcomeState) welcomeState.style.display = 'flex';
  Array.from(messagesArea.children).forEach(c => {
    if (c.id !== 'welcome-state') c.remove();
  });
}

// ── Utilities ────────────────────────────────────────────────────
function setSendState(loading) {
  isLoading = loading;
  sendBtn.disabled = loading;
  chatInput.disabled = loading;
}

function scrollToBottom() {
  setTimeout(() => {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }, 50);
}

function autoResizeTextarea(el) {
  const resize = () => {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  };
  el.addEventListener('input', resize);
}

function formatTime(date) {
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>');
}

function renderMarkdown(text) {
  // Very minimal markdown: bold, code, line breaks
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code style="background:var(--bg-card);padding:2px 6px;border-radius:4px;font-size:0.85em">$1</code>')
    .replace(/\n/g, '<br>');
}
