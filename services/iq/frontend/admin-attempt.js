const adminTokenKey = 'iq_admin_token';

const el = (id) => document.getElementById(id);

function getToken() {
  return localStorage.getItem(adminTokenKey);
}

function formatTime(seconds) {
  const minute = String(Math.floor(seconds / 60)).padStart(2, '0');
  const second = String(seconds % 60).padStart(2, '0');
  return `${minute}:${second}`;
}

function formatPercent(ratio) {
  return `${Math.round(Number(ratio || 0) * 100)}%`;
}

async function apiFetch(path) {
  const token = getToken();
  if (!token) {
    window.location.href = '/iq/admin.html';
    return null;
  }

  const response = await fetch(path, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    localStorage.removeItem(adminTokenKey);
    window.location.href = '/iq/admin.html';
    return null;
  }
  return response;
}

function renderDimensions(items) {
  el('detail-dimensions').innerHTML = items.map((item) => `
    <article class="dimension-card">
      <div class="dimension-top">
        <div>
          <h4>${item.label}</h4>
          <p class="muted">${item.level_label}</p>
        </div>
        <div class="score-chip">${item.score}</div>
      </div>
      <div class="progress-row">
        <div class="progress-track">
          <div class="progress-fill" style="width:${Math.min(item.score, 130) / 130 * 100}%"></div>
        </div>
        <span>${item.correct}/${item.total}</span>
      </div>
      <p class="small muted">正确率：${item.accuracy}%</p>
      <p>${item.description}</p>
      <p class="small advice">${item.advice}</p>
    </article>
  `).join('');
}

function renderReview(items) {
  el('detail-review').innerHTML = items.map((item) => `
    <article class="review-item ${item.is_correct ? 'is-correct' : 'is-wrong'}">
      <div class="review-head">
        <strong>第 ${item.question_order} 题</strong>
        <span class="review-status">${item.is_correct ? '答对' : '答错'}</span>
      </div>
      <p class="review-prompt">${item.prompt}</p>
      <div class="review-meta">
        <span>${item.dimension}</span>
        <span>${item.difficulty}</span>
        <span>作答用时 ${item.time_spent_seconds}s</span>
      </div>
      <p class="small">你的答案：${item.selected_option || '未作答'} ｜ 正确答案：${item.correct_option}</p>
      <p class="small muted">解析：${item.explanation || '暂无解析'}</p>
    </article>
  `).join('');
}

function fillDetail(data) {
  el('detail-section').classList.remove('hidden');
  el('detail-meta').textContent = `记录 #${data.attempt_id} ｜ 用户：${data.nickname} ｜ 提交时间：${data.submitted_at}`;
  el('detail-headline').textContent = `CPI ${data.cpi_score} · 参考 IQ ${data.estimated_iq} · ${data.ability_level} / ${data.ability_label}`;
  el('detail-summary').textContent = data.summary;
  el('detail-level-tag').textContent = `${data.ability_level} · ${data.ability_label}`;
  el('detail-validity-tag').textContent = data.validity_label;
  el('detail-validity-title').textContent = data.validity_label;
  el('detail-validity-note').textContent = data.validity_note;
  el('detail-interpretation').textContent = data.interpretation;
  el('detail-disclaimer').textContent = data.disclaimer;

  el('detail-metrics').innerHTML = `
    <div class="metric highlight">
      <span>综合认知表现指数 CPI</span>
      <strong>${data.cpi_score}</strong>
    </div>
    <div class="metric">
      <span>参考 IQ 值</span>
      <strong>${data.estimated_iq}</strong>
    </div>
    <div class="metric">
      <span>答对题数</span>
      <strong>${data.correct_count}/${data.total_questions}</strong>
    </div>
    <div class="metric">
      <span>站内百分位</span>
      <strong>P${data.percentile}</strong>
    </div>
    <div class="metric">
      <span>参考 IQ 区间</span>
      <strong>${data.iq_range}</strong>
    </div>
    <div class="metric">
      <span>正确率得分</span>
      <strong>${formatPercent(data.score_factors.accuracy_score)}</strong>
    </div>
    <div class="metric">
      <span>难度加权得分</span>
      <strong>${formatPercent(data.score_factors.difficulty_score)}</strong>
    </div>
    <div class="metric">
      <span>完整度得分</span>
      <strong>${formatPercent(data.score_factors.completion_score)}</strong>
    </div>
    <div class="metric">
      <span>作答质量得分</span>
      <strong>${formatPercent(data.score_factors.response_quality_score)}</strong>
    </div>
    <div class="metric">
      <span>用时</span>
      <strong>${formatTime(data.duration_seconds)}</strong>
    </div>
  `;

  renderDimensions(data.dimension_breakdown);
  renderReview(data.answer_review);
}

async function bootstrap() {
  const attemptId = new URLSearchParams(window.location.search).get('id');
  if (!attemptId) {
    el('detail-meta').textContent = '缺少 attempt id，无法加载详情。';
    return;
  }

  const response = await apiFetch(`/api/admin/attempts/${attemptId}`);
  if (!response || !response.ok) {
    el('detail-meta').textContent = '记录加载失败，请返回后台重试。';
    return;
  }

  const data = await response.json();
  fillDetail(data);
}

bootstrap();
