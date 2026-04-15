const state = {
  attemptId: null,
  questions: [],
  timerId: null,
  timeLimitSeconds: 25 * 60,
  remainingSeconds: 25 * 60,
  startTimestamp: null,
  submitting: false,
  activeQuestionId: null,
  activeSince: null,
  questionDurations: {},
};

const el = (id) => document.getElementById(id);
const defaultPageTitle = document.title;

function formatTime(seconds) {
  const safeSeconds = Math.max(0, Number(seconds) || 0);
  const minute = String(Math.floor(safeSeconds / 60)).padStart(2, '0');
  const second = String(safeSeconds % 60).padStart(2, '0');
  return `${minute}:${second}`;
}

function formatPercent(ratio) {
  return `${Math.round(Number(ratio || 0) * 100)}%`;
}

function syncActiveTiming() {
  if (!state.activeQuestionId || !state.activeSince) return;
  const now = Date.now();
  const delta = Math.max(0, now - state.activeSince);
  state.questionDurations[state.activeQuestionId] = (state.questionDurations[state.activeQuestionId] || 0) + delta;
  state.activeSince = now;
}

function activateQuestion(questionId) {
  const now = Date.now();
  if (state.activeQuestionId && state.activeSince) {
    const delta = Math.max(0, now - state.activeSince);
    state.questionDurations[state.activeQuestionId] = (state.questionDurations[state.activeQuestionId] || 0) + delta;
  }
  state.activeQuestionId = questionId;
  state.activeSince = now;
}

function attachQuestionTracking() {
  document.querySelectorAll('.question-card').forEach((card) => {
    const questionId = Number(card.dataset.questionId);
    card.addEventListener('click', () => activateQuestion(questionId));
    card.addEventListener('focusin', () => activateQuestion(questionId));
  });
}

function renderQuestions() {
  const form = el('questions-form');
  form.innerHTML = state.questions.map((question) => `
    <article class="question-card" data-question-id="${question.id}">
      <div class="question-head">
        <strong>第 ${question.order_no} 题</strong>
        <span class="badge">${question.category} · ${question.difficulty}</span>
      </div>
      <p class="question-prompt">${question.prompt}</p>
      <div class="option-grid">
        ${Object.entries(question.options).map(([key, value]) => `
          <label class="option-item">
            <input type="radio" name="q_${question.id}" value="${key}" />
            <span class="option-letter">${key}</span>
            <span>${value}</span>
          </label>
        `).join('')}
      </div>
    </article>
  `).join('');
  attachQuestionTracking();
}

function collectAnswers() {
  syncActiveTiming();
  return state.questions.map((question) => {
    const checked = document.querySelector(`input[name="q_${question.id}"]:checked`);
    return {
      question_id: question.id,
      selected_option: checked ? checked.value : null,
      time_spent_seconds: Math.round((state.questionDurations[question.id] || 0) / 1000),
    };
  });
}

function getTimerStatus(seconds) {
  if (seconds <= 60) {
    return {
      tone: 'danger',
      tip: '剩余不足 1 分钟，系统会在时间到后自动交卷。',
    };
  }
  if (seconds <= 5 * 60) {
    return {
      tone: 'warning',
      tip: '剩余不足 5 分钟，建议优先检查未作答题目。',
    };
  }
  return {
    tone: 'normal',
    tip: '倒计时会始终跟随答题进度，时间到后将自动交卷。',
  };
}

function renderTimerState() {
  const safeSeconds = Math.max(0, state.remainingSeconds);
  const timeText = formatTime(safeSeconds);
  const status = getTimerStatus(safeSeconds);
  const progressRatio = state.timeLimitSeconds
    ? Math.max(0, Math.min(1, safeSeconds / state.timeLimitSeconds))
    : 0;

  el('timer').textContent = timeText;

  const floatingValue = el('floating-timer-value');
  const floatingProgress = el('floating-timer-progress');
  const floatingTip = el('floating-timer-tip');
  const timerBox = el('timer-box');
  const floatingPanel = el('floating-timer-panel');

  if (floatingValue) floatingValue.textContent = timeText;
  if (floatingProgress) floatingProgress.style.width = `${progressRatio * 100}%`;
  if (floatingTip) floatingTip.textContent = status.tip;

  [timerBox, floatingPanel].forEach((node) => {
    if (!node) return;
    node.classList.toggle('is-warning', status.tone === 'warning');
    node.classList.toggle('is-danger', status.tone === 'danger');
  });

  document.title = el('test-section')?.classList.contains('hidden')
    ? defaultPageTitle
    : `${timeText} | 在线智力测评平台`;
}

function clearTimer() {
  if (!state.timerId) return;
  window.clearInterval(state.timerId);
  state.timerId = null;
}

function startTimer() {
  clearTimer();
  renderTimerState();
  state.timerId = window.setInterval(() => {
    state.remainingSeconds = Math.max(0, state.remainingSeconds - 1);
    renderTimerState();
    if (state.remainingSeconds <= 0) {
      clearTimer();
      submitTest({ autoSubmitted: true });
    }
  }, 1000);
}

async function loadPublicInfo() {
  const response = await fetch('/api/public/info');
  if (!response.ok) return;
  const info = await response.json();
  el('hero-title').textContent = info.title;
  el('hero-question-count').textContent = `${info.question_count} 题`;
  el('hero-time-limit').textContent = `${Math.round(info.time_limit_seconds / 60)} 分钟`;
}

async function startTest() {
  const payload = {
    nickname: el('nickname').value || null,
    email: el('email').value || null,
  };

  const response = await fetch('/api/attempts/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    alert('开始测评失败，请确认后端服务已正常启动。');
    return;
  }

  const data = await response.json();
  state.attemptId = data.attempt_id;
  state.questions = data.questions;
  state.timeLimitSeconds = data.time_limit_seconds;
  state.remainingSeconds = data.time_limit_seconds;
  state.startTimestamp = Date.now();
  state.submitting = false;
  state.questionDurations = {};
  state.activeQuestionId = null;
  state.activeSince = null;

  el('welcome-section').classList.add('hidden');
  el('test-section').classList.remove('hidden');
  el('floating-timer-panel').classList.remove('hidden');
  el('submit-btn').disabled = false;
  el('submit-btn').textContent = '提交并生成报告';
  el('meta-text').textContent = `共 ${data.questions.length} 题，建议在 ${Math.round(data.time_limit_seconds / 60)} 分钟内完成。`;
  renderQuestions();
  startTimer();
}

function renderDimensionBreakdown(items) {
  el('dimension-breakdown').innerHTML = items.map((item) => `
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

function renderReview(answerReview) {
  el('review-list').innerHTML = answerReview.map((item) => `
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

function fillResult(data) {
  el('result-headline').textContent = `你的综合认知表现：${data.ability_label}`;
  el('result-summary').textContent = data.summary;
  el('result-level-tag').textContent = `${data.ability_level} · ${data.ability_label}`;
  el('result-validity-tag').textContent = data.validity_label;

  el('cpi-score').textContent = data.cpi_score;
  el('estimated-iq').textContent = data.estimated_iq;
  el('ability-level').textContent = `${data.ability_level} / ${data.ability_label}`;
  el('percentile').textContent = `P${data.percentile}`;
  el('iq-range').textContent = data.iq_range;
  el('correct-count').textContent = `${data.correct_count}/${data.total_questions}`;
  el('duration').textContent = formatTime(data.duration_seconds);

  el('factor-accuracy').textContent = formatPercent(data.score_factors.accuracy_score);
  el('factor-difficulty').textContent = formatPercent(data.score_factors.difficulty_score);
  el('factor-completion').textContent = formatPercent(data.score_factors.completion_score);
  el('factor-quality').textContent = formatPercent(data.score_factors.response_quality_score);

  el('interpretation').textContent = data.interpretation;
  el('validity-title').textContent = data.validity_label;
  el('validity-note').textContent = data.validity_note;
  el('disclaimer').textContent = data.disclaimer;

  renderDimensionBreakdown(data.dimension_breakdown);
  renderReview(data.answer_review);
}

async function submitTest({ autoSubmitted = false } = {}) {
  if (!state.attemptId || state.submitting) return;
  state.submitting = true;
  syncActiveTiming();
  clearTimer();

  const submitButton = el('submit-btn');
  submitButton.disabled = true;
  submitButton.textContent = autoSubmitted ? '时间到，正在自动交卷…' : '正在生成报告…';
  if (autoSubmitted) {
    const floatingTip = el('floating-timer-tip');
    if (floatingTip) {
      floatingTip.textContent = '时间已到，系统正在自动提交你的试卷。';
    }
  }

  const durationSeconds = Math.min(7200, Math.floor((Date.now() - state.startTimestamp) / 1000));
  const payload = {
    answers: collectAnswers(),
    duration_seconds: durationSeconds,
  };

  let response;
  try {
    response = await fetch(`/api/attempts/${state.attemptId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (_) {
    state.submitting = false;
    submitButton.disabled = false;
    submitButton.textContent = '提交并生成报告';
    renderTimerState();
    if (state.remainingSeconds > 0) startTimer();
    alert('网络异常，提交失败，请稍后重试。');
    return;
  }

  if (!response.ok) {
    state.submitting = false;
    submitButton.disabled = false;
    submitButton.textContent = '提交并生成报告';
    renderTimerState();
    if (state.remainingSeconds > 0) startTimer();
    alert('提交失败，请稍后重试。');
    return;
  }

  const data = await response.json();
  el('floating-timer-panel').classList.add('hidden');
  el('test-section').classList.add('hidden');
  el('result-section').classList.remove('hidden');
  document.title = defaultPageTitle;
  fillResult(data);
}

function restart() {
  window.location.reload();
}

window.addEventListener('blur', () => {
  syncActiveTiming();
  state.activeSince = null;
});

window.addEventListener('focus', () => {
  if (state.activeQuestionId && !state.activeSince) {
    state.activeSince = Date.now();
  }
});

el('start-btn')?.addEventListener('click', startTest);
el('submit-btn')?.addEventListener('click', submitTest);
el('restart-btn')?.addEventListener('click', restart);

loadPublicInfo();
