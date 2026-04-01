// js/chat.js — Chatbot logic for FindX (v2 — streaming + rich formatting)

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

// ── Download Support ──────────────────────────────────────────────
function triggerFileDownload(btn) {
  const ogHtml = btn.innerHTML;
  btn.innerHTML = '<span>Downloading...</span>';
  
  // Directly trigger the browser's native download manager
  window.location.assign(`${API_BASE}/download`);
  
  setTimeout(() => {
    btn.innerHTML = '<span>✅ Success</span>';
    setTimeout(() => btn.innerHTML = ogHtml, 3000);
  }, 1000);
}


// ── Initialize ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const user = requireAuth();
  populateUserUI(user);
  renderHistoryList();
  autoResizeTextarea(chatInput);

  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  sendBtn.addEventListener('click', handleSend);
  checkBackendHealth();
  fetchAndPopulateSuggestions();

  // Autonomous First-Time Greeting
  if (!currentSession && chatSessions.length === 0) {
    setTimeout(triggerWelcomeGreeting, 500);
  }
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

// ── Autonomous Greeting ──────────────────────────────────────────
async function triggerWelcomeGreeting() {
  if (welcomeState) welcomeState.style.display = 'none';
  startNewSession();
  
  showTypingIndicator();
  await sleep(600);
  removeTypingIndicator();

  const text = "Hi there! 👋 I am **FindX**, your intelligent data assistant.\n\nUpload an Excel, CSV, or Text file and I'll help you instantly query its contents. I can also perform advanced data modifications—if you ask me to **update, delete, or add** records, I will directly modify the structured dataset for you to download!\n\nHow can I help you today?";
  
  await appendAIMessageStreaming(text, [], '0.1', false);
  
  // Save greeting silently
  if (currentSession) {
    currentSession.title = "Welcome to FindX";
    currentSession.messages.push({ role: 'ai', content: text, sources: [], fileUpdated: false });
    const idx = chatSessions.findIndex(s => s.id === currentSession.id);
    if (idx >= 0) chatSessions[idx] = currentSession;
    else chatSessions.unshift(currentSession);
    localStorage.setItem('findx_sessions', JSON.stringify(chatSessions));
    renderHistoryList();
  }
}

// ── Sending Messages ─────────────────────────────────────────────
async function handleSend() {
  const query = chatInput.value.trim();
  if (!query || isLoading) return;

  if (!currentSession) startNewSession();

  chatInput.value = '';
  autoResizeTextarea(chatInput);

  if (welcomeState) welcomeState.style.display = 'none';

  appendUserMessage(query);
  showTypingIndicator();
  setSendState(true);

  const startTime = Date.now();

  try {
    const topK = parseInt(topKInput?.value || '3');
    const res  = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_query: query, top_k: topK })
    });
    const json = await res.json();

    removeTypingIndicator();

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

    if (!res.ok || json.errors?.length) {
      const errMsg = json.errors?.[0]?.message || json.message || 'Unknown error.';
      appendAIMessage(`⚠️ ${errMsg}`, [], elapsed, false);
    } else {
      const { answer, sources, file_updated } = json.data;
      await appendAIMessageStreaming(answer, sources || [], elapsed, file_updated);
      saveToSession(query, answer, sources || [], file_updated);
    }
  } catch (err) {
    removeTypingIndicator();
    appendAIMessage(
      '⚠️ Could not reach the backend. Make sure the server is running at `http://localhost:8000`.',
      [], '—'
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
  const user     = getUser();
  const initials = user?.initials || '?';
  const time     = formatTime(new Date());

  const el = document.createElement('div');
  el.className = 'message user animate-fade-up';
  el.innerHTML = `
    <div class="message-avatar user-avatar-msg">${initials}</div>
    <div class="message-content">
      <div class="message-bubble user-bubble">${escapeHtml(text)}</div>
      <div class="message-time">${time}</div>
    </div>
  `;
  messagesArea.appendChild(el);
  scrollToBottom();
}

// Instant append (for loading sessions, errors)
function appendAIMessage(text, sources, elapsed, fileUpdated = false) {
  const time = formatTime(new Date());
  const sourcesHtml = sources.length > 0 ? buildSourcesPanel(sources) : '';
  const metaHtml = buildResponseMeta(sources.length, elapsed, fileUpdated);

  const el = document.createElement('div');
  el.className = 'message ai animate-fade-up';
  el.innerHTML = `
    <div class="message-avatar ai-avatar">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
    </div>
    <div class="message-content">
      <div class="ai-label">FindX AI</div>
      <div class="message-bubble ai-bubble">${renderMarkdown(text)}</div>
      ${metaHtml}
      ${sourcesHtml}
      <div class="message-time">${time}</div>
    </div>
  `;
  messagesArea.appendChild(el);
  scrollToBottom();
}

// Streaming typewriter append
async function appendAIMessageStreaming(text, sources, elapsed) {
  const time = formatTime(new Date());

  const el = document.createElement('div');
  el.className = 'message ai animate-fade-up';

  const bubbleId  = 'bubble-' + Date.now();

  el.innerHTML = `
    <div class="message-avatar ai-avatar">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
    </div>
    <div class="message-content">
      <div class="ai-label">FindX AI</div>
      <div class="message-bubble ai-bubble" id="${bubbleId}"><span class="streaming-cursor"></span></div>
    </div>
  `;
  messagesArea.appendChild(el);
  scrollToBottom();

  // Typewriter effect — stream characters
  const bubbleEl = document.getElementById(bubbleId);
  await typewriterEffect(bubbleEl, text);

  // After streaming, render full markdown
  bubbleEl.innerHTML = renderMarkdown(text);

  // Append meta and sources after streaming
  const contentDiv = el.querySelector('.message-content');

  const metaHtml = buildResponseMeta(sources.length, elapsed);
  const metaContainer = document.createElement('div');
  metaContainer.innerHTML = metaHtml;
  contentDiv.appendChild(metaContainer);

  if (sources.length > 0) {
    const srcContainer = document.createElement('div');
    srcContainer.innerHTML = buildSourcesPanel(sources);
    contentDiv.appendChild(srcContainer);

    // Animate sources in
    setTimeout(() => {
      srcContainer.querySelector('.sources-panel')?.classList.add('animate-fade-up');
    }, 100);
  }

  const timeEl = document.createElement('div');
  timeEl.className = 'message-time';
  timeEl.textContent = time;
  contentDiv.appendChild(timeEl);

  scrollToBottom();
}

async function typewriterEffect(el, text) {
  const chars = text.split('');
  let displayed = '';
  const speed = Math.max(5, Math.min(15, 3000 / chars.length)); // adaptive speed

  for (let i = 0; i < chars.length; i++) {
    displayed += chars[i];

    // Render partial markdown every 8 chars or at newlines for smooth visual
    if (i % 8 === 0 || chars[i] === '\n' || i === chars.length - 1) {
      el.innerHTML = renderMarkdown(displayed) + '<span class="streaming-cursor"></span>';
      scrollToBottom();
    }

    await sleep(speed);
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function buildResponseMeta(sourceCount, elapsed, fileUpdated = false) {
  return `
    <div class="response-meta">
      <span class="meta-chip">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        ${elapsed}s
      </span>
      <span class="meta-chip">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        ${sourceCount} sources
      </span>
      <span class="meta-chip meta-model">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        Llama 3.1
      </span>
      <button class="meta-chip meta-copy" onclick="copyResponse(this)" title="Copy answer">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        Copy
      </button>
      ${fileUpdated ? `
      <button class="meta-chip meta-download" style="border-color: var(--accent-emerald); color: var(--accent-emerald);" onclick="triggerFileDownload(this)">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <span>Download CSV/Excel</span>
      </button>
      ` : ''}
    </div>
  `;
}

function copyResponse(btn) {
  const bubble = btn.closest('.message-content').querySelector('.ai-bubble');
  const text = bubble.innerText;
  navigator.clipboard.writeText(text).then(() => {
    btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
    setTimeout(() => {
      btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy`;
    }, 2000);
  });
}

function buildSourcesPanel(sources) {
  const items = sources.map((s, i) => {
    const dist = typeof s.distance === 'number' ? (s.distance).toFixed(2) : '—';
    const relevance = s.distance < 0.7 ? 'high' : s.distance < 1.2 ? 'medium' : 'low';
    return `
      <div class="source-item">
        <div class="source-header">
          <span class="source-id">📄 ${escapeHtml(String(s.document_id))}</span>
          <span class="source-relevance source-relevance-${relevance}">${relevance} relevance</span>
        </div>
        <div class="source-text">${escapeHtml(s.text.slice(0, 200))}${s.text.length > 200 ? '…' : ''}</div>
      </div>
    `;
  }).join('');

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
    <div class="message-avatar ai-avatar" style="background:var(--grad-accent)">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
    </div>
    <div class="typing-bubble">
      <span class="typing-label">FindX is thinking</span>
      <div class="typing-dots">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
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
  Array.from(messagesArea.children).forEach(c => {
    if (c.id !== 'welcome-state') c.remove();
  });
}

function saveToSession(query, answer, sources, fileUpdated = false) {
  if (!currentSession) return;

  if (currentSession.messages.length === 0) {
    currentSession.title = query.slice(0, 45) + (query.length > 45 ? '…' : '');
  }
  currentSession.messages.push({ role: 'user', content: query });
  currentSession.messages.push({ role: 'ai', content: answer, sources, fileUpdated });

  const idx = chatSessions.findIndex(s => s.id === currentSession.id);
  if (idx >= 0) chatSessions[idx] = currentSession;
  else          chatSessions.unshift(currentSession);

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

  Array.from(messagesArea.children).forEach(c => {
    if (c.id !== 'welcome-state') c.remove();
  });

  session.messages.forEach(msg => {
    if (msg.role === 'user') appendUserMessage(msg.content);
    else appendAIMessage(msg.content, msg.sources || [], '—', msg.fileUpdated);
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
  if (loading) {
    sendBtn.innerHTML = '<div class="send-spinner"></div>';
  } else {
    sendBtn.innerHTML = '➤';
  }
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
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Horizontal Rule
    .replace(/^---$/gm, '<hr class="md-hr" />')
    // Headers
    .replace(/^### (.+)$/gm, '<h4 class="md-h4">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="md-h3">$1</h3>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Block Code (```...```)
    .replace(/```([\s\S]*?)```/g, '<pre class="md-pre"><code class="md-code-block">$1</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="md-code">$1</code>')
    // Numbered list items
    .replace(/^\d+\.\s+(.+)$/gm, '<div class="md-list-item"><span class="md-list-num"></span>$1</div>')
    // Bullet list items
    .replace(/^[-•]\s+(.+)$/gm, '<div class="md-list-item"><span class="md-list-bullet">•</span>$1</div>')
    // Line breaks
    .replace(/\n{2,}/g, '<div class="md-paragraph-break"></div>')
    .replace(/\n/g, '<br/>');

  // Inject High-End UI Component for Agent Responses
  const successCardRegex = /:::SUCCESS_CARD:::<br\/>([\s\S]*?)<br\/>:::END_CARD:::/g;
  html = html.replace(successCardRegex, (match, p1) => {
    return `
      <div style="background: linear-gradient(145deg, rgba(16,185,129,0.1), rgba(16,185,129,0.02)); border: 1px solid rgba(16,185,129,0.2); border-left: 4px solid var(--accent-emerald); border-radius: 12px; padding: 20px; margin: 16px 0; font-family: var(--font-sans); box-shadow: 0 8px 32px rgba(0,0,0,0.15); animation: fadeUp 0.6s ease-out forwards;">
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 18px;">
          <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(16,185,129,0.15); display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">✨</div>
          <div>
            <h3 style="margin: 0; color: var(--accent-emerald); font-size: 1.15rem; font-family: var(--font-display); letter-spacing: -0.01em;">Dataset Seamlessly Updated</h3>
            <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Real-time memory mutation completed</p>
          </div>
        </div>
        <p style="font-size: 0.92rem; color: var(--text-secondary); margin-bottom: 18px; line-height: 1.6;">I successfully executed your request. For maximum system transparency, here is the exact Python logic I authored and deployed to manipulate your underlying vector data:</p>
        <div style="background: rgba(0,0,0,0.4); border-radius: 8px; padding: 14px; font-family: ui-monospace, Consolas, monospace; font-size: 0.85rem; color: #a1a1aa; margin-bottom: 18px; border: 1px solid rgba(255,255,255,0.05); overflow-x: auto;">
          <span style="color: #cba6f7;">${p1}</span>
        </div>
        <div style="display: flex; gap: 16px; align-items: center; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08);">
          <div style="display: flex; align-items: center; gap: 6px; font-size: 0.82rem; color: var(--text-muted);">
            <span style="color:var(--accent-emerald); font-size: 0.9rem;">✔</span> <span>Index Synchronized</span>
          </div>
          <div style="display: flex; align-items: center; gap: 6px; font-size: 0.82rem; color: var(--text-muted);">
            <span style="color:var(--accent-emerald); font-size: 0.9rem;">✔</span> <span>Database Persisted</span>
          </div>
        </div>
      </div>
    `;
  });

  return html;
}

// ── Upload & Suggestions ─────────────────────────────────────────

async function handleSidebarUpload(file) {
  if (!file) return;

  const allowed = ['.xlsx', '.xls', '.csv', '.txt'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  
  const label = document.querySelector('label[for="inline-file-input"]');
  if (label) label.style.color = 'var(--text-muted)';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
    const json = await res.json();
    if (!res.ok) throw new Error(json.errors?.[0]?.message || 'Upload failed');
    
    if (label) {
      label.style.color = 'var(--accent-emerald)';
      setTimeout(() => label.style.color = '', 3000);
    }
    checkBackendHealth();
    fetchAndPopulateSuggestions();
  } catch (err) {
    if (label) {
      label.style.color = 'var(--accent-pink)';
      console.error(err);
      setTimeout(() => label.style.color = '', 3000);
    }
  }
}

async function fetchAndPopulateSuggestions() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const json = await res.json();
    const suggestions = json.data?.rag_engine?.suggestions;
    
    if (suggestions && suggestions.length > 0) {
      // Create HTML strings for chips
      const quickPromptsHTML = suggestions.slice(0, 4).map(s => {
        const textOnly = s.substring(2).replace(/'/g, "\\'").trim();
        return `<button class="quick-prompt-chip" onclick="sendQuickPrompt('${textOnly}')">${escapeHtml(s)}</button>`;
      }).join('');
      
      const welcomeChipsHTML = suggestions.slice(0, 4).map(s => {
        const textOnly = s.substring(2).replace(/'/g, "\\'").trim();
        return `<button class="welcome-chip" onclick="sendQuickPrompt('${textOnly}')">${escapeHtml(s)}</button>`;
      }).join('');

      // Populate sidebar (first 4)
      const sidebarContainer = document.querySelector('.quick-prompts');
      if (sidebarContainer) sidebarContainer.innerHTML = quickPromptsHTML;
      
      // Populate main welcome area (all 4)
      const welcomeChips = document.querySelector('.welcome-chips');
      if (welcomeChips) welcomeChips.innerHTML = welcomeChipsHTML;
    }
  } catch (e) {
    console.error('Failed to load suggestions', e);
  }
}
