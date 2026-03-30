// js/history.js — History feed logic for FindX
const API_BASE = 'http://localhost:8000/api/v1';

let globalHistoryData = [];

document.addEventListener('DOMContentLoaded', () => {
  const user = requireAuth();
  populateUserUI(user);
  loadFullHistory();
});

async function loadFullHistory(forceRefresh = false) {
  const btn = document.getElementById('refresh-btn');
  
  if (forceRefresh && btn) btn.classList.add('spinning');
  
  try {
    const res = await fetch(`${API_BASE}/history`);
    const json = await res.json();
    globalHistoryData = json.data || [];
    renderHistory();
  } catch (err) {
    console.error('Failed to load history:', err);
    document.getElementById('history-feed-container').innerHTML = 
      `<div class="empty-history" style="color:var(--accent-pink);">❌ Failed to load history feed.</div>`;
  } finally {
    if (forceRefresh && btn) {
      setTimeout(() => btn.classList.remove('spinning'), 500);
    }
  }
}

function renderHistory() {
  const container = document.getElementById('history-feed-container');
  const sortOrder = document.getElementById('sort-select')?.value || 'newest';

  if (globalHistoryData.length === 0) {
    container.innerHTML = `
      <div class="empty-history">
        <div class="empty-icon">💭</div>
        <p>Your history is empty.</p>
        <a href="/app/chat" class="btn btn-primary" style="margin-top:16px;">Ask a Question</a>
      </div>`;
    return;
  }

  container.innerHTML = '';
  
  // Create a copy to sort
  let itemsToRender = [...globalHistoryData];
  
  // Sort based on timestamp
  if (sortOrder === 'newest') {
    // Reversing puts newest at top, since backend appends dynamically to end of array
    itemsToRender.reverse();
  } else {
    // 'oldest' means keep the array as it was appended (chronological)
    // No reverse needed since it's already chronological from backend
  }

  itemsToRender.forEach(item => {
    const card = document.createElement('div');
    card.className = 'history-card animate-fade-up';
    
    // Format timestamp nicely
    let timeStr = 'Recent session';
    if (item.timestamp) {
      const dateObj = new Date(item.timestamp);
      timeStr = dateObj.toLocaleDateString() + ' ' + dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }

    card.innerHTML = `
      <div class="history-card-header">
        <div class="history-query">${escapeHtml(item.query)}</div>
      </div>
      <div class="history-answer markdown-body">
        ${renderMarkdown(item.answer || item.answer_preview)}
      </div>
      <div class="history-meta mt-3">
        <span class="badge badge-violet">${item.source_count || 0} Sources</span>
        <span class="badge badge-cyan" style="font-size:0.7rem;">💬 Chat API</span>
        <span class="history-time" style="margin-left:auto;">📅 ${timeStr}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

// ── Markdown Parser (Reused from chat.js) ──────────────────────────────────
function renderMarkdown(text) {
  if (!text) return '';
  let html = text;

  // Code blocks
  html = html.replace(/```([\s\S]*?)```/g, (match, code) => 
    `<pre><code>${escapeHtml(code.trim())}</code></pre>`
  );

  // Headers (H3, H2, H1)
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold & Italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Bullet Lists
  html = html.replace(/^\+ (.*$)/gim, '<ul><li>$1</li></ul>');
  html = html.replace(/^\* (.*$)/gim, '<ul><li>$1</li></ul>');
  html = html.replace(/- (.*$)/gim, '<ul><li>$1</li></ul>');
  html = html.replace(/<\/ul>\n<ul>/g, '\n');

  // Numbered Lists
  html = html.replace(/^\d+\.\s(.*$)/gim, '<ol><li>$1</li></ol>');
  html = html.replace(/<\/ol>\n<ol>/g, '\n');

  // Paragraphs (double newline to <p>)
  html = html.split(/\n\n+/).map(p => {
    if (p.startsWith('<h') || p.startsWith('<ul>') || p.startsWith('<ol>') || p.startsWith('<pre>')) {
      return p;
    }
    return `<p>${p}</p>`;
  }).join('');

  // Single newlines to <br> if not closing tags
  html = html.replace(/(?<!>)\n(?!<)/g, '<br/>');

  return html;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
