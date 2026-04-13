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
  const res = await fetch('/api/attempts/start', {
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
  const levelText = (data.interpretation.match(/当前大致处于“(.+?)”/) || [])[1] || '结果参考区间';
  const shortSummary = `你的参考 IQ 为 ${data.estimated_iq}，百分位约为 P${data.percentile}。这表示你在本次测验中的整体表现大致处于“${levelText}”。`;
  el('result-level-tag').textContent = levelText;
  el('result-headline').textContent = '你的结果概览';
  el('result-summary').textContent = shortSummary;
  el('interpretation').textContent = data.interpretation;
  el('disclaimer').textContent = data.disclaimer;
  fillReportCards(data, levelText);
  renderCategoryBreakdown(data.category_breakdown);
  renderReview(data.answer_review);
}

function fillReportCards(data, levelText) {
  const iq = Number(data.estimated_iq);
  let rangeTitle = '常见区间';
  let rangeBody = '这表示你的本次表现大致落在较常见的范围内，基础理解和推理能力具有一定稳定性。';

  if (iq >= 125) {
    rangeTitle = '优势表现区';
    rangeBody = '按本测验的内部换算，这通常意味着你在规律发现、信息整合和推理速度上表现较强。';
  } else if (iq >= 110) {
    rangeTitle = '良好表现区';
    rangeBody = '按本测验的内部换算，这说明你的整体表现高于平均水平，在常见推理题上通常更容易找到正确思路。';
  } else if (iq >= 90) {
    rangeTitle = '常模区间';
    rangeBody = '按本测验的内部换算，这属于比较常见的表现区间，说明当前基础能力整体较为正常稳定。';
  } else if (iq >= 75) {
    rangeTitle = '基础发展区';
    rangeBody = '按本测验的内部换算，这说明你当前还有一定提升空间，尤其适合通过复盘和练习来强化薄弱题型。';
  } else {
    rangeTitle = '起步提升区';
    rangeBody = '按本测验的内部换算，这次结果更适合作为一次摸底，不建议直接把它当成固定能力结论。';
  }

  let crowdTitle = '与他人相比';
  let crowdBody = `你的参考百分位约为 P${data.percentile}，也就是在本测验内部换算里，大致位于相应位置。百分位越高，说明本次表现相对越靠前。`;

  if (data.percentile <= 5) {
    crowdBody += ' 但要注意，如果本次没有认真完整作答，这个位置可能会被明显低估。';
  }

  const sortedCategories = Object.entries(data.category_breakdown || {}).sort((a, b) => b[1].accuracy - a[1].accuracy);
  const strongest = sortedCategories[0]?.[0] || '暂无';
  const weakest = sortedCategories[sortedCategories.length - 1]?.[0] || '暂无';

  el('report-overall-title').textContent = `${levelText}`;
  el('report-overall-body').textContent = `从这次结果看，你目前的整体表现可以概括为“${levelText}”。参考 IQ ${iq} 仅代表本站题库下的粗略区间，不是医学或心理诊断。`;

  el('report-range-title').textContent = rangeTitle;
  el('report-range-body').textContent = rangeBody;

  el('report-crowd-title').textContent = crowdTitle;
  el('report-crowd-body').textContent = crowdBody;

  el('report-advice-title').textContent = '下一步怎么提升';
  el('report-advice-body').textContent = `你本次的相对优势在“${strongest}”，优先提升方向是“${weakest}”。建议先把错题重新做一遍，再集中练习同类型题目，这样比单纯重复刷题更有效。`;
}

async function submitTest() {
  if (!state.attemptId) return;
  if (state.timerId) clearInterval(state.timerId);
  const durationSeconds = Math.min(7200, Math.floor((Date.now() - state.startTimestamp) / 1000));
  const payload = {
    answers: collectAnswers(),
    duration_seconds: durationSeconds,
  };
  const res = await fetch(`/api/attempts/${state.attemptId}/submit`, {
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
