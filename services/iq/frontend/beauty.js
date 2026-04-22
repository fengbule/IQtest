const state = {
  gender: 'female',
  style: 'natural',
  scene: 'daily',
  file: null,
  previewUrl: '',
  imageStats: null,
  result: null,
};

const DATA = {
  common: {
    faceShapes: [
      { name: '鹅蛋脸倾向', note: '面部线条较均衡，风格适配范围很广。' },
      { name: '方圆脸倾向', note: '下颌线存在感较明显，适合强调轮廓与纵向比例。' },
      { name: '长脸倾向', note: '面部纵向比例更突出，适合增加横向层次感。' },
      { name: '心形脸倾向', note: '上庭存在感较强，适合柔化额头与下巴对比。' },
      { name: '菱形脸倾向', note: '颧区存在感较强，适合平衡中庭焦点。' },
      { name: '圆脸倾向', note: '整体观感柔和，适合拉长纵向线条。' },
    ],
    palettes: [
      { name: '冷灰蓝 + 奶白', note: '适合清冷、克制、利落型表达。' },
      { name: '豆沙粉 + 浅咖', note: '更显柔和、耐看和轻熟。' },
      { name: '茶棕 + 燕麦', note: '适合日常通勤与低风险搭配。' },
      { name: '烟紫 + 银灰', note: '更适合镜头感和精致妆面。' },
      { name: '橘棕 + 奶杏', note: '更显元气和健康感。' },
      { name: '黑白灰 + 深蓝', note: '适合打造干净和利落的第一印象。' },
    ],
    cameraFocus: [
      { name: '眉眼表现力', note: '镜头中先强化眼神与眉形轮廓。' },
      { name: '鼻唇中轴', note: '更适合保持正面整洁与中轴干净。' },
      { name: '下颌线与轮廓', note: '拍照时注意侧转角度与颈肩延伸。' },
      { name: '皮肤通透感', note: '更适合利用自然光提高质感。' },
      { name: '五官立体度', note: '适合使用轻侧脸与高低光变化。' },
    ],
    tags: ['精致感', '耐看型', '氛围感', '亲和力', '清爽感', '镜头友好', '层次感', '轻熟感', '松弛感', '高级感', '元气感', '克制感'],
    photoTips: [
      '镜头略高于眼睛，更容易显得面部紧致。',
      '自然窗边光比顶光更适合绝大多数人。',
      '微侧 15° 到 30° 往往比完全正面更出片。',
      '肩颈线条打开后，整体气质会更利落。',
      '手机离脸太近会放大中庭，建议适当拉远。',
      '先对焦眼睛，再调整曝光，五官会更清晰。',
      '浅背景更适合突出脸部层次与肤色。',
      '表情不必太满，轻微嘴角上扬更自然。',
      '连续拍几张比单张抓拍更容易选到好角度。',
      '侧身加回头动作，能提升照片故事感。',
    ],
    avoids: [
      '避免过强磨皮，会削弱真实的高级感。',
      '避免复杂背景抢走五官焦点。',
      '避免过低机位，容易压缩颈部与下颌线。',
      '避免颜色过杂的上衣影响面部观感。',
      '避免过重修容或过深阴影，容易显脏。',
      '避免大面积高饱和荧光色贴近脸部。',
      '避免强顶光或室内黄暗光直接拍摄。',
      '避免长时间同一角度自拍，容易形成审美惯性。',
    ],
    features: [
      '中庭视觉存在感适中，更适合平衡而非过度强调。',
      '眉眼区域是你更值得优先优化的焦点。',
      '面部留白感较明显，适合通过发型或配饰增加层次。',
      '鼻唇中轴观感偏顺，可以维持干净路线。',
      '下颌区域存在感较强，适合拉开颈肩比例。',
      '整体轮廓偏柔和，容易营造亲和和减龄氛围。',
      '镜头里更适合立体但克制的修饰方式。',
      '适合走轻氛围而不是堆叠细节的路线。',
      '轮廓与皮肤质感之间的平衡是关键。',
      '五官识别度不错，适合打造个人标签感。',
    ],
  },
  female: {
    styleTypes: [
      '清透甜感', '韩系轻熟', '明媚元气', '清冷精致', '温柔知性', '甜酷轻辣', '氧气自然', '通勤高级'
    ],
    beautyTitle: '妆容建议',
    beautySuggestions: [
      '底妆更适合奶油肌或轻雾面，重点放在均匀肤色而不是厚遮。',
      '眉形建议保持自然平眉或微挑眉，提升干净感。',
      '眼妆更适合低饱和大地色、粉棕或灰粉调，不宜过重晕染。',
      '腮红适合放在苹果肌外侧向太阳穴轻扫，提升面中气色。',
      '唇色优先豆沙、奶咖、裸粉、低饱和红棕，避免过荧光。',
      '高光建议只点在鼻尖、鼻梁中段和颧骨上方，避免全脸发亮。',
      '修容更适合轻度强调轮廓，不建议刻意压缩面部结构。',
      '假睫毛建议以自然束感为主，避免过密抢走气质。',
      '卧蚕和下睫毛轻提亮，会比浓重眼线更显精致。',
      '如果想显成熟感，可以把眼影重点从粉调切到灰棕和茶棕。',
    ],
    hairAccessories: [
      '锁骨层次发更适合拉开面部比例，显得轻盈。',
      '八字刘海或空气感刘海能柔化额头与颧区对比。',
      '低马尾配耳饰适合打造通勤精致感。',
      '卷度不要太碎，保持大弧度更显高级。',
      '耳饰适合细线条、珍珠、小金属感，不建议过于厚重。',
      '发顶适当蓬松，整体会更上镜。',
      '中分更适合强调成熟与轮廓，偏分更适合增加柔和度。',
      '发色推荐茶棕、黑茶、冷棕、亚麻咖，镜头里更稳定。',
    ],
  },
  male: {
    styleTypes: [
      '清爽少年感', '利落通勤感', '冷淡高级感', '稳重成熟感', '干净书卷感', '轻熟痞帅感', '街头层次感', '克制精英感'
    ],
    beautyTitle: '修饰建议',
    beautySuggestions: [
      '眉形优先修整杂毛，保留自然线条，不建议画得过满。',
      '发型重点在顶部蓬松和两侧干净，整体轮廓比复杂造型更重要。',
      '鼻唇区域保持整洁，会明显提升清爽感。',
      '如果胡须较明显，建议统一长度，不要留下散乱边缘。',
      '护肤以清洁、保湿、防晒为核心，比堆叠产品更有效。',
      '可以适当使用润色型防晒或轻薄遮瑕，提升镜头质感。',
      '眼下轻微提亮能改善疲态，但不建议做过强修饰。',
      '镜框更适合偏细、偏利落的形状，避免过宽压脸。',
      '唇部保持润泽度即可，不需要高存在感修饰。',
      '拍证件照或头像时，尽量保持眉骨和鼻梁区域光线清爽。',
    ],
    hairAccessories: [
      '三七分或自然侧分更适合增强利落和成熟感。',
      '顶部纹理不宜过乱，适合干净但有空气感的造型。',
      '两侧可适当推短，能提升整体精神度。',
      '配饰建议优先极简金属、窄边眼镜、质感表链。',
      '黑、深棕、冷棕发色更容易稳定出片。',
      '额头条件允许时，露额会更显精神和轮廓。',
      '不要把发蜡抹得过实，保留自然纹理更高级。',
      '领口、肩线整洁度会直接影响脸部高级感。',
    ],
  },
  styleMap: {
    natural: ['耐看型', '松弛感', '自然干净', '低攻击性'],
    sweet: ['减龄感', '甜酷平衡', '元气感', '轻氛围'],
    clean: ['清冷感', '利落感', '克制感', '高级感'],
    office: ['精致感', '职业感', '成熟度', '通勤友好'],
  },
  sceneMap: {
    daily: ['自然自拍', '松弛状态', '真实肤感'],
    social: ['头像辨识度', '镜头友好', '第一印象'],
    dating: ['氛围感', '柔和线条', '耐看细节'],
    work: ['干净利落', '可信度', '稳定气质'],
  },
};

const $ = (id) => document.getElementById(id);

function setActiveChip(group, value) {
  document.querySelectorAll(`[data-group="${group}"]`).forEach((el) => {
    el.classList.toggle('active', el.dataset.value === value);
  });
}

function choice(arr, index) {
  return arr[index % arr.length];
}

function chooseMany(arr, indexes, count) {
  const used = new Set();
  const result = [];
  for (const idx of indexes) {
    const real = idx % arr.length;
    if (!used.has(real)) {
      used.add(real);
      result.push(arr[real]);
    }
    if (result.length >= count) break;
  }
  return result;
}

async function hashFile(file) {
  const buffer = await file.arrayBuffer();
  const digest = await crypto.subtle.digest('SHA-256', buffer);
  return Array.from(new Uint8Array(digest));
}

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => resolve({ img, url });
    img.onerror = reject;
    img.src = url;
  });
}

async function analyzeImage(file) {
  const { img, url } = await loadImage(file);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  const maxSize = 160;
  const ratio = img.width / img.height;
  canvas.width = ratio >= 1 ? maxSize : Math.max(1, Math.round(maxSize * ratio));
  canvas.height = ratio >= 1 ? Math.max(1, Math.round(maxSize / ratio)) : maxSize;
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);

  let totalLuma = 0;
  let warmBias = 0;
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    totalLuma += 0.299 * r + 0.587 * g + 0.114 * b;
    warmBias += (r - b);
  }

  const px = data.length / 4;
  return {
    width: img.width,
    height: img.height,
    ratio,
    avgBrightness: totalLuma / px,
    warmth: warmBias / px,
    previewUrl: url,
  };
}

function scoreFrom(hash, stats, gender) {
  const base = 78 + (hash[0] % 13);
  const lightBonus = stats.avgBrightness > 132 ? 3 : stats.avgBrightness < 88 ? -2 : 1;
  const portraitBonus = stats.ratio < 0.95 ? 2 : 0;
  const genderBonus = gender === 'female' ? hash[1] % 3 : hash[2] % 3;
  return Math.max(75, Math.min(96, base + lightBonus + portraitBonus + genderBonus));
}

function buildResult(hash, stats) {
  const genderData = DATA[state.gender];
  const faceShape = choice(DATA.common.faceShapes, hash[3] + Math.round(stats.ratio * 10));
  const styleType = choice(genderData.styleTypes, hash[4] + hash[8]);
  const palette = choice(DATA.common.palettes, hash[5] + Math.round(stats.avgBrightness));
  const cameraFocus = choice(DATA.common.cameraFocus, hash[6] + Math.round(stats.warmth + 20));
  const score = scoreFrom(hash, stats, state.gender);

  const styleTags = [
    ...chooseMany(DATA.common.tags, hash.slice(7, 16), 3),
    ...DATA.styleMap[state.style],
    ...DATA.sceneMap[state.scene],
  ].slice(0, 8);

  const featurePool = [...DATA.common.features];
  if (stats.avgBrightness > 128) featurePool.push('整体照片明亮度不错，更适合突出干净与通透路线。');
  if (stats.avgBrightness < 95) featurePool.push('照片偏暗时会压住皮肤和轮廓，建议优先修正光线。');
  if (stats.warmth > 10) featurePool.push('暖调环境下，柔和色系会比冷硬配色更自然。');
  if (stats.warmth < -8) featurePool.push('偏冷的画面环境更适合增强清爽和克制感。');
  if (stats.ratio < 0.92) featurePool.push('你上传的是偏竖幅的自拍，更适合突出脸部与肩颈延伸。');

  const beautyPool = [...genderData.beautySuggestions];
  if (state.style === 'sweet') beautyPool.push(state.gender === 'female' ? '可以适度提高腮红与唇色的甜感，但保持低饱和更耐看。' : '可以保留一点少年感和松弛感，不必把造型做得过于成熟。');
  if (state.style === 'clean') beautyPool.push(state.gender === 'female' ? '把色彩重心放在眉眼轮廓，会比强烈唇色更显高级。' : '尽量减少过多花哨元素，清爽干净会更贴合你的路线。');
  if (state.scene === 'work') beautyPool.push(state.gender === 'female' ? '通勤场景建议减少闪片与亮泽面积，保持稳重精致。' : '职业照建议强化眉眼清晰度和衣领整洁度，可信度会更高。');

  const hairPool = [...genderData.hairAccessories];
  if (state.scene === 'social') hairPool.push('头像场景下，耳周和额前的整洁度会直接影响辨识度。');
  if (state.scene === 'dating') hairPool.push('约会氛围照更适合柔和一点的发丝线条和耳饰/配饰点缀。');
  if (stats.ratio > 1.1) hairPool.push('横幅照片里，发型的轮廓会被放大，建议减少凌乱毛躁感。');

  const photoTips = [...chooseMany(DATA.common.photoTips, hash.slice(16, 25), 4)];
  const avoids = [...chooseMany(DATA.common.avoids, hash.slice(25, 33), 4)];
  const features = [...chooseMany(featurePool, hash.slice(9, 20), 5)];
  const beautySuggestions = [...chooseMany(beautyPool, hash.slice(18, 30), 5)];
  const hairAccessories = [...chooseMany(hairPool, hash.slice(4, 17), 5)];

  const vibeCore = choice(DATA.styleMap[state.style], hash[10]);
  const summary = `你这次的报告更偏向 ${styleType} 与 ${vibeCore} 路线。整体建议不是走“堆很多细节”的方向，而是抓住 ${cameraFocus.name}、${palette.name} 和 ${faceShape.name} 这三个主轴，把个人辨识度做得更稳定。`;

  return {
    score,
    faceShape,
    styleType,
    palette,
    cameraFocus,
    summary,
    styleTags,
    features,
    beautySuggestions,
    hairAccessories,
    photoTips,
    avoids,
    beautyTitle: genderData.beautyTitle,
    vibe: vibeCore,
  };
}

function renderResult(result) {
  $('report-title').textContent = state.gender === 'female' ? '你的 AI 女生向形象报告' : '你的 AI 男生向形象报告';
  $('report-summary').textContent = result.summary;
  $('report-score').textContent = `上镜指数 ${result.score}`;
  $('report-vibe').textContent = `风格标签 ${result.vibe}`;

  $('face-shape').textContent = result.faceShape.name;
  $('face-shape-note').textContent = result.faceShape.note;
  $('style-type').textContent = result.styleType;
  $('style-type-note').textContent = '这条风格线最适合你当前照片表现出来的状态。';
  $('color-palette').textContent = result.palette.name;
  $('color-palette-note').textContent = result.palette.note;
  $('camera-focus').textContent = result.cameraFocus.name;
  $('camera-focus-note').textContent = result.cameraFocus.note;

  $('feature-list').innerHTML = result.features.map((item) => `<li>${item}</li>`).join('');
  $('tag-cloud').innerHTML = result.styleTags.map((item) => `<span>${item}</span>`).join('');
  $('beauty-section-title').textContent = result.beautyTitle;
  $('beauty-suggestion-list').innerHTML = result.beautySuggestions.map((item) => `<li>${item}</li>`).join('');
  $('hair-accessory-list').innerHTML = result.hairAccessories.map((item) => `<li>${item}</li>`).join('');
  $('photo-tip-list').innerHTML = result.photoTips.map((item) => `<li>${item}</li>`).join('');
  $('avoid-list').innerHTML = result.avoids.map((item) => `<li>${item}</li>`).join('');
}

function simulateLoading(messages, done) {
  $('analysis-card').classList.remove('hidden');
  let step = 0;
  const bar = $('loading-bar');
  const text = $('loading-text');
  const timer = setInterval(() => {
    step += 1;
    text.textContent = messages[Math.min(step - 1, messages.length - 1)];
    bar.style.width = `${Math.min(step * 22, 96)}%`;
    if (step >= messages.length) {
      clearInterval(timer);
      bar.style.width = '100%';
      setTimeout(done, 250);
    }
  }, 420);
}

async function handleAnalyze() {
  if (!state.file) {
    alert('请先上传一张照片。');
    return;
  }

  const btn = $('analyze-btn');
  btn.disabled = true;
  btn.textContent = '分析中...';

  try {
    const [hash, stats] = await Promise.all([hashFile(state.file), analyzeImage(state.file)]);
    state.imageStats = stats;
    state.result = buildResult(hash, stats);

    simulateLoading([
      '正在读取图片基础特征...',
      '正在生成脸型与风格倾向...',
      state.gender === 'female' ? '正在生成妆容与发型建议...' : '正在生成修饰与发型建议...',
      '正在整理拍照与配色建议...',
    ], () => {
      renderResult(state.result);
      $('result-section').classList.remove('hidden');
      $('analysis-card').classList.add('hidden');
      btn.disabled = false;
      btn.textContent = '重新生成精美报告';
      window.scrollTo({ top: $('result-section').offsetTop - 20, behavior: 'smooth' });
    });
  } catch (error) {
    console.error(error);
    btn.disabled = false;
    btn.textContent = '开始生成精美报告';
    $('analysis-card').classList.add('hidden');
    alert('图片分析失败，请换一张清晰照片重试。');
  }
}

function bindChoices() {
  document.querySelectorAll('.choice-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const { group, value } = chip.dataset;
      state[group] = value;
      setActiveChip(group, value);
    });
  });
}

function bindUpload() {
  $('photo-input').addEventListener('change', async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    state.file = file;
    if (state.previewUrl) URL.revokeObjectURL(state.previewUrl);
    state.previewUrl = URL.createObjectURL(file);
    $('photo-preview').src = state.previewUrl;
    $('preview-wrap').classList.remove('hidden');
    $('upload-empty').classList.add('hidden');
  });
}

async function saveReport() {
  const report = $('report-board');
  const canvas = await html2canvas(report, {
    backgroundColor: '#ffffff',
    scale: 2,
    useCORS: true,
    logging: false,
  });
  const link = document.createElement('a');
  link.download = `AI颜值测试报告-${new Date().toISOString().slice(0, 10)}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

function restart() {
  window.location.reload();
}

bindChoices();
bindUpload();
$('analyze-btn').addEventListener('click', handleAnalyze);
$('save-report-btn').addEventListener('click', saveReport);
$('restart-btn').addEventListener('click', restart);