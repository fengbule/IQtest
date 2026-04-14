const adminTokenKey = 'iq_admin_token';

const state = {
  page: 1,
  pageSize: 10,
  total: 0,
};

const el = (id) => document.getElementById(id);

function getToken() {
  return localStorage.getItem(adminTokenKey);
}

function buildQueryParams() {
  const params = new URLSearchParams();
  params.set('page', String(state.page));
  params.set('page_size', String(state.pageSize));

  const keyword = el('filter-keyword')?.value?.trim();
  const level = el('filter-level')?.value;
  const validity = el('filter-validity')?.value;
  const dateFrom = el('filter-date-from')?.value;
  const dateTo = el('filter-date-to')?.value;

  if (keyword) params.set('keyword', keyword);
  if (level) params.set('level', level);
  if (validity) params.set('validity', validity);
  if (dateFrom) params.set('date_from', dateFrom);
  if (dateTo) params.set('date_to', dateTo);

  return params;
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = new Headers(options.headers || {});
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(path, { ...options, headers });
  if (response.status === 401) {
    el('login-message').textContent = '登录态已失效，请重新登录。';
    throw new Error('unauthorized');
  }
  return response;
}

async function login() {
  const username = el('admin-username').value.trim();
  const password = el('admin-password').value;

  const response = await fetch('/api/admin/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    el('login-message').textContent = '登录失败，请检查用户名和密码。';
    return;
  }

  const data = await response.json();
  localStorage.setItem(adminTokenKey, data.access_token);
  el('login-message').textContent = '登录成功，正在加载后台数据…';
  await Promise.all([loadDashboard(), loadAttempts()]);
}

function logout() {
  localStorage.removeItem(adminTokenKey);
  location.reload();
}

function renderDashboard(data) {
  el('dashboard-section').classList.remove('hidden');
  el('attempts-section').classList.remove('hidden');

  el('dashboard-metrics').innerHTML = `
    <div class="metric highlight">
      <span>总尝试数</span>
      <strong>${data.total_attempts}</strong>
    </div>
    <div class="metric">
      <span>已完成提交</span>
      <strong>${data.completed_attempts}</strong>
    </div>
    <div class="metric">
      <span>平均 CPI</span>
      <strong>${data.average_cpi_score}</strong>
    </div>
    <div class="metric">
      <span>平均完整度</span>
      <strong>${data.average_completion_score}%</strong>
    </div>
    <div class="metric">
      <span>有效作答率</span>
      <strong>${data.valid_attempt_rate}%</strong>
    </div>
  `;

  el('dashboard-categories').innerHTML = Object.entries(data.dimension_accuracy).map(([label, accuracy]) => `
    <article class="dimension-card compact-card">
      <div class="dimension-top">
        <div>
          <h4>${label}</h4>
          <p class="muted">维度正确率</p>
        </div>
        <div class="score-chip">${accuracy}%</div>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width:${accuracy}%"></div>
      </div>
    </article>
  `).join('');
}

function renderAttempts(data) {
  state.total = data.total;
  const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));
  el('page-info').textContent = `第 ${data.page} / ${totalPages} 页，共 ${data.total} 条`;
  el('prev-page-btn').disabled = data.page <= 1;
  el('next-page-btn').disabled = data.page >= totalPages;

  el('attempt-list').innerHTML = data.items.length ? data.items.map((item) => `
    <article class="admin-item">
      <div class="admin-item-main">
        <div class="admin-item-head">
          <strong>#${item.attempt_id} · ${item.nickname}</strong>
          <span class="pill">${item.validity_label}</span>
        </div>
        <p class="muted">
          CPI ${item.cpi_score} ｜ 等级 ${item.ability_level} / ${item.ability_label} ｜ 百分位 P${item.percentile}
        </p>
        <p class="small muted">
          提交时间：${item.submitted_at || '-'} ｜ 用时：${item.duration_seconds}s ｜ 参考 IQ：${item.iq_range}
        </p>
      </div>
      <div class="actions">
        <a class="button secondary" href="/iq/admin-attempt.html?id=${item.attempt_id}">查看详情</a>
      </div>
    </article>
  `).join('') : '<p class="muted">当前筛选条件下暂无记录。</p>';
}

async function loadDashboard() {
  const response = await apiFetch('/api/admin/dashboard');
  if (!response.ok) {
    el('login-message').textContent = '后台概览加载失败，请重新登录。';
    return;
  }
  const data = await response.json();
  renderDashboard(data);
}

async function loadAttempts() {
  const params = buildQueryParams();
  const response = await apiFetch(`/api/admin/attempts?${params.toString()}`);
  if (!response.ok) {
    el('attempt-list').innerHTML = '<p class="muted">记录加载失败，请稍后重试。</p>';
    return;
  }
  const data = await response.json();
  renderAttempts(data);
}

async function exportCsv() {
  const params = buildQueryParams();
  params.delete('page');
  params.delete('page_size');

  const response = await apiFetch(`/api/admin/attempts/export.csv?${params.toString()}`);
  if (!response.ok) {
    alert('导出失败，请稍后重试。');
    return;
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'iq-attempts.csv';
  link.click();
  URL.revokeObjectURL(url);
}

function resetFilters() {
  el('filter-keyword').value = '';
  el('filter-level').value = '';
  el('filter-validity').value = '';
  el('filter-date-from').value = '';
  el('filter-date-to').value = '';
  state.page = 1;
  loadAttempts();
}

function bindEvents() {
  el('login-btn')?.addEventListener('click', login);
  el('logout-btn')?.addEventListener('click', logout);
  el('search-btn')?.addEventListener('click', () => {
    state.page = 1;
    loadAttempts();
  });
  el('reset-btn')?.addEventListener('click', resetFilters);
  el('export-btn')?.addEventListener('click', exportCsv);
  el('prev-page-btn')?.addEventListener('click', () => {
    if (state.page <= 1) return;
    state.page -= 1;
    loadAttempts();
  });
  el('next-page-btn')?.addEventListener('click', () => {
    state.page += 1;
    loadAttempts();
  });
}

async function bootstrap() {
  bindEvents();
  if (!getToken()) return;
  try {
    await Promise.all([loadDashboard(), loadAttempts()]);
  } catch (_) {
    // Ignore bootstrap errors; message is rendered in the page.
  }
}

bootstrap();
