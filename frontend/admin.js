const adminTokenKey = 'iq_admin_token';

const el = (id) => document.getElementById(id);

async function login() {
  const username = el('admin-username').value;
  const password = el('admin-password').value;
  const res = await fetch('/api/admin/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    el('login-message').textContent = '登录失败，请检查账号密码。';
    return;
  }

  const data = await res.json();
  localStorage.setItem(adminTokenKey, data.access_token);
  el('login-message').textContent = '登录成功，正在加载统计...';
  loadDashboard();
}

function renderDashboard(data) {
  el('dashboard-section').classList.remove('hidden');
  el('dashboard-metrics').innerHTML = `
    <div class="metric"><span>总记录</span><strong>${data.total_attempts}</strong></div>
    <div class="metric"><span>已完成</span><strong>${data.completed_attempts}</strong></div>
    <div class="metric highlight"><span>平均参考 IQ</span><strong>${data.average_estimated_iq}</strong></div>
    <div class="metric"><span>平均用时</span><strong>${Math.round(data.average_duration_seconds)}s</strong></div>
    <div class="metric"><span>平均正确率</span><strong>${data.average_accuracy}%</strong></div>
  `;

  el('dashboard-categories').innerHTML = Object.entries(data.category_accuracy).map(([key, value]) => `
    <div class="dimension-card">
      <span>${key}</span>
      <strong>${value}%</strong>
      <div>平均正确率</div>
    </div>
  `).join('');

  el('recent-results').innerHTML = data.recent_results.map((item) => `
    <div class="review-item">
      <div><strong>#${item.attempt_id}</strong> · ${item.nickname}</div>
      <div>参考 IQ：${item.estimated_iq} ｜ 百分位：P${item.percentile} ｜ 用时：${item.duration_seconds}s</div>
      <div class="small">提交时间：${item.submitted_at || '-'}</div>
    </div>
  `).join('') || '<p class="small">暂无数据</p>';
}

async function loadDashboard() {
  const token = localStorage.getItem(adminTokenKey);
  if (!token) return;
  const res = await fetch('/api/admin/dashboard', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    el('login-message').textContent = '读取后台数据失败，请重新登录。';
    return;
  }
  const data = await res.json();
  renderDashboard(data);
}

el('login-btn')?.addEventListener('click', login);
loadDashboard();
