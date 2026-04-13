const state = {
  attemptId: null,
  questions: [],
  startTimestamp: null,
  timerId: null,
  remainingSeconds: 20 * 60,
};

const el = (id) => document.getElementById(id);

function formatTime(seconds) {
  const m = String(Math.floor(seconds / 60)).padStart(2, '0');
  const s = String(seconds % 60).padStart(2, '0');
  return `${m}:${s}`;
}

function renderQuestions() {
  const form = el('questions-form');
  form.innerHTML = state.questions.map((q, index) => `
    <div class="question-card">
      <div class="question-head">
        <strong>第 ${index + 1} 题</strong>
        <span class="badge">${q.category} · 难度 ${q.difficulty}</span>
      </div>
      <p>${q.prompt}</p>
      <div class="option-grid">
        ${Object.entries(q.options).map(([key, value]) => `
          <div class="option-item">
            <label>
              <input type="radio" name="q_${q.id}" value="${key}" />
              <strong>${key}.</strong> ${value}
            </label>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function collectAnswers() {
  return state.questions.map((q) => {
    const checked = document.querySelector(`input[name="q_${q.id}"]:checked`);
    return {
      question_id: q.id,
      selected_option: checked ? checked.value : null,
    };
  });
}

function startTimer() {
  el('timer').textContent = formatTime(state.remainingSeconds);
  state.timerId = setInterval(() => {
    state.remainingSeconds -= 1;
    el('timer').textContent = formatTime(state.remainingSeconds);
    if (state.remainingSeconds <= 0) {
      clearInterval(state.timerId);
      submitTest();
    }
  }, 1000);
}

async function startTest() {
  const payload = {
    nickname: el('nickname').value || null,
    email: el('email').value || null,
  };
  const res = await fetch('/iq/api/attempts/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    alert('开始测评失败，请检查后端是否正常运行。');
    return;
  }
  const data = await res.json();
  state.attemptId = data.attempt_id;
  state.questions = data.questions;
  state.startTimestamp = Date.now();
  state.remainingSeconds = data.time_limit_seconds;

  el('welcome-section').classList.add('hidden');
  el('test-section').classList.remove('hidden');
  el('meta-text').textContent = `共 ${data.questions.length} 题，建议在 20 分钟内完成`;
  renderQuestions();
  startTimer();
}

function renderCategoryBreakdown(categoryBreakdown) {
  el('category-breakdown').innerHTML = Object.entries(categoryBreakdown).map(([name, info]) => `
    <div class="dimension-card">
      <span>${name}</span>
      <strong>${info.correct}/${info.total}</strong>
      <div>正确率 ${info.accuracy}%</div>
    </div>
  `).join('');
}

function renderReview(answerReview) {
  el('review-list').innerHTML = answerReview.map((item, idx) => `
    <div class="review-item">
      <div><strong>第 ${idx + 1} 题</strong> · <span class="review-status ${item.is_correct ? 'correct' : 'wrong'}">${item.is_correct ? '答对' : '答错'}</span></div>
      <div>你的答案：${item.selected_option || '未作答'} ｜ 正确答案：${item.correct_option}</div>
      <div class="small">解析：${item.explanation || '暂无解析'}</div>
    </div>
  `).join('');
}

function fillResult(data) {
  el('correct-count').textContent = `${data.correct_count}/${data.total_questions}`;
  el('raw-score').textContent = data.raw_score;
  el('normalized-score').textContent = data.normalized_score;
  el('estimated-iq').textContent = data.estimated_iq;
  el('percentile').textContent = `P${data.percentile}`;
  el('duration').textContent = formatTime(data.duration_seconds);
  el('interpretation').textContent = data.interpretation;
  el('disclaimer').textContent = data.disclaimer;
  renderCategoryBreakdown(data.category_breakdown);
  renderReview(data.answer_review);
}

async function submitTest() {
  if (!state.attemptId) return;
  if (state.timerId) clearInterval(state.timerId);
  const durationSeconds = Math.min(7200, Math.floor((Date.now() - state.startTimestamp) / 1000));
  const payload = {
    answers: collectAnswers(),
    duration_seconds: durationSeconds,
  };
  const res = await fetch(`/iq/api/attempts/${state.attemptId}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    alert('提交失败，请重试。');
    return;
  }
  const data = await res.json();
  el('test-section').classList.add('hidden');
  el('result-section').classList.remove('hidden');
  fillResult(data);
}

function restart() {
  window.location.reload();
}

el('start-btn')?.addEventListener('click', startTest);
el('submit-btn')?.addEventListener('click', submitTest);
el('restart-btn')?.addEventListener('click', restart);
