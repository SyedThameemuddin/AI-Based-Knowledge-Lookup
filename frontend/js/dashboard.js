// js/dashboard.js — Knowledge base management for FindX

const API_BASE = 'http://localhost:8000/api/v1';

// ── Initialize ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const user = requireAuth();
  populateUserUI(user);

  loadStats();
  loadHistory();
  setupUploadZone();
  setupIntervals();
});

// ── Stats ────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const res  = await fetch(`${API_BASE}/health`);
    const json = await res.json();
    const rag  = json.data?.rag_engine || {};

    animateCount('stat-docs',    rag.document_count  || 0);
    animateCount('stat-status',  rag.index_loaded ? 1 : 0, true);

    // Update KB info card
    const kbStatus = document.getElementById('kb-status');
    const kbDocs   = document.getElementById('kb-doc-count');
    const kbModel  = document.getElementById('kb-model');
    const kbLLM    = document.getElementById('kb-llm');

    if (kbStatus) {
      kbStatus.textContent  = rag.index_loaded ? 'Loaded ✓' : 'Not Loaded';
      kbStatus.className    = `badge ${rag.index_loaded ? 'badge-emerald' : 'badge-pink'}`;
    }
    if (kbDocs)   kbDocs.textContent  = rag.document_count || 0;
    if (kbModel)  kbModel.textContent = rag.embedding_model || 'all-MiniLM-L6-v2';
    if (kbLLM)    kbLLM.textContent   = rag.llm_model       || 'llama-3.1-8b-instant';

  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

async function loadHistory() {
  try {
    const res  = await fetch(`${API_BASE}/history`);
    const json = await res.json();
    const history = json.data || [];

    const tbody = document.getElementById('history-tbody');
    const statQueries = document.getElementById('stat-queries');
    if (statQueries) animateCount('stat-queries', history.length);

    if (!tbody) return;
    tbody.innerHTML = '';

    if (history.length === 0) {
      tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;color:var(--text-muted);padding:30px">No queries yet — ask something in the chat!</td></tr>`;
      return;
    }

    const reversed = [...history].reverse();
    reversed.forEach((item, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="query-cell">${escapeHtml(item.query)}</td>
        <td>${escapeHtml(item.answer_preview)}</td>
        <td><span class="badge badge-violet badge-dot">${item.source_count} src</span></td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

// ── Upload Zone ──────────────────────────────────────────────────
function setupUploadZone() {
  const zone      = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');
  const status    = document.getElementById('upload-status');

  if (!zone || !fileInput) return;

  zone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => handleUpload(fileInput.files[0]));

  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    handleUpload(e.dataTransfer.files[0]);
  });
}

async function handleUpload(file) {
  if (!file) return;

  const allowed = ['.xlsx', '.xls', '.csv', '.txt'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showUploadStatus('error', `❌ Unsupported file type: ${ext}. Use ${allowed.join(', ')}`);
    return;
  }

  showUploadStatus('loading', `⏳ Indexing "${file.name}"…`);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res  = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
    const json = await res.json();

    if (!res.ok || json.errors?.length) {
      const err = json.errors?.[0]?.message || 'Upload failed';
      showUploadStatus('error', `❌ ${err}`);
    } else {
      const { document_count, message } = json.data;
      showUploadStatus('success', `✅ ${message}`);
      showToast(`Indexed ${document_count} documents from "${file.name}"`, 'success');
      // Refresh stats
      setTimeout(() => { loadStats(); loadHistory(); }, 800);
    }
  } catch (err) {
    showUploadStatus('error', `❌ Network error: ${err.message}`);
  }
}

function showUploadStatus(type, message) {
  const el = document.getElementById('upload-status');
  if (!el) return;
  el.className  = `upload-status ${type}`;
  el.textContent = message;
  el.style.display = 'block';
}

// ── Counter Animation ────────────────────────────────────────────
function animateCount(id, target, isBoolean = false) {
  const el = document.getElementById(id);
  if (!el) return;
  if (isBoolean) { el.textContent = target ? 'Active' : 'Offline'; return; }
  const duration = 800;
  const start    = performance.now();
  const from     = 0;

  function update(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased    = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (target - from) * eased);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ── Intervals ────────────────────────────────────────────────────
function setupIntervals() {
  // Refresh stats every 30s
  setInterval(() => { loadStats(); loadHistory(); }, 30000);
}

// ── Toast Notifications ──────────────────────────────────────────
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.4s'; setTimeout(() => toast.remove(), 400); }, 4000);
}

// ── Utilities ────────────────────────────────────────────────────
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
