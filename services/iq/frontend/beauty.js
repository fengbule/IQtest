const state = {
  gender: 'female',
  file: null,
  previewUrl: '',
  imageStats: null,
  faceAnalysis: null,
  result: null,
};

const FACE_MESH_CDN = 'https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh@0.4';

const DATA = {
  common: {
    faceShapes: {
      oval: { name: '鹅蛋脸倾向', note: '长宽比例均衡，轮廓过渡顺，适配风格范围很广。' },
      round: { name: '圆脸倾向', note: '脸部横向亲和感更明显，适合用发型和角度拉出纵向线条。' },
      squareRound: { name: '方圆脸倾向', note: '下颌存在感较强，适合强调轮廓秩序和肩颈延伸。' },
      long: { name: '长脸倾向', note: '纵向比例更突出，适合增加横向层次与发侧蓬松度。' },
      heart: { name: '心形脸倾向', note: '上庭和额侧存在感更强，适合柔化额头与下巴对比。' },
      diamond: { name: '菱形脸倾向', note: '颧区存在感更强，适合平衡中庭焦点和耳侧层次。' },
    },
    featureFocus: {
      eyes: { name: '眉眼表现力', note: '镜头中优先强化眼神、眉形和眼周清晰度。' },
      center: { name: '鼻唇中轴', note: '保持正面整洁和中轴干净，会更稳定耐看。' },
      jaw: { name: '下颌线与轮廓', note: '拍照时侧转角度、颈肩线和下颌光影更关键。' },
      skin: { name: '皮肤通透感', note: '自然光与均匀底色会明显提升镜头质感。' },
      balance: { name: '五官平衡度', note: '更适合整体协调路线，不必单点过度强化。' },
    },
    palettes: [
      { key: 'coolClean', name: '冷灰蓝 + 奶白', note: '适合清冷、克制、利落型表达。' },
      { key: 'softPink', name: '豆沙粉 + 浅咖', note: '更显柔和、耐看和轻熟。' },
      { key: 'teaBrown', name: '茶棕 + 燕麦', note: '适合日常通勤与低风险搭配。' },
      { key: 'smokeSilver', name: '烟紫 + 银灰', note: '更适合镜头感和精致妆面。' },
      { key: 'apricot', name: '杏桃 + 奶油白', note: '更显元气、健康和亲和。' },
      { key: 'monoBlue', name: '黑白灰 + 深蓝', note: '适合打造干净、理性和利落的第一印象。' },
    ],
    styleProfiles: {
      natural: {
        name: '自然耐看',
        note: '照片更适合低负担、真实肤感和耐看的细节控制。',
        tags: ['耐看型', '自然干净', '松弛感', '低攻击性'],
        suggestions: [
          '强化方向放在干净肤感、自然眉眼和稳定发型轮廓上。',
          '穿搭颜色不必太跳，低饱和色更能突出本人状态。',
          '照片后期保留真实皮肤纹理，会比过强磨皮更高级。',
        ],
      },
      sweet: {
        name: '明媚减龄',
        note: '画面明亮度和亲和感更适合走元气、轻甜或柔和路线。',
        tags: ['元气感', '亲和力', '轻氛围', '明媚感'],
        suggestions: [
          '强化方向可以放在气色、笑容和面中柔和度上。',
          '配色可选择奶杏、浅咖、豆沙和低饱和暖色。',
          '拍照时保留一点动态表情，比完全端正更自然。',
        ],
      },
      clean: {
        name: '清冷利落',
        note: '轮廓、色温或对比度更适合清爽、克制、干净的表达。',
        tags: ['清爽感', '利落感', '克制感', '高级感'],
        suggestions: [
          '强化方向放在眉眼清晰、轮廓边界和服装线条上。',
          '减少碎花、荧光色和过多饰品，画面会更稳。',
          '偏冷或中性色背景更容易放大这条路线的优势。',
        ],
      },
      refined: {
        name: '轻熟精致',
        note: '五官比例和镜头表现更适合做精致、通勤、轻熟感强化。',
        tags: ['精致感', '轻熟感', '通勤友好', '稳定气质'],
        suggestions: [
          '强化方向放在发型整洁度、眉眼边界和衣领质感上。',
          '妆容或修饰保持低饱和，但细节要干净完整。',
          '适合证件照、职业头像和社交主页首图这类高识别场景。',
        ],
      },
    },
    sceneProfiles: {
      daily: { name: '日常自拍', note: '适合自然光、低修饰和真实状态的照片。' },
      social: { name: '社交头像', note: '适合做清晰头像、主页首图和第一印象展示。' },
      dating: { name: '约会氛围', note: '适合柔和光线、浅背景和更有情绪感的构图。' },
      work: { name: '通勤 / 职业照', note: '适合干净背景、稳定表情和利落服装线条。' },
    },
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
  },
  female: {
    reportTitle: '你的 AI 女生向形象报告',
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
    celebrities: [
      { name: '刘亦菲', styles: ['natural', 'sweet'], shapes: ['oval', 'heart'], note: '清透、自然、低攻击性的镜头路线。' },
      { name: '高圆圆', styles: ['natural', 'refined'], shapes: ['oval', 'round'], note: '亲和耐看，适合干净通勤和浅笑头像。' },
      { name: '刘诗诗', styles: ['clean', 'refined'], shapes: ['oval', 'long'], note: '克制、舒展、气质线条稳定。' },
      { name: '倪妮', styles: ['clean', 'refined'], shapes: ['diamond', 'long'], note: '轮廓鲜明，适合高级感和大面积留白。' },
      { name: '赵露思', styles: ['sweet', 'natural'], shapes: ['round', 'oval'], note: '明媚减龄，适合柔和光线和元气表情。' },
      { name: '周也', styles: ['clean', 'sweet'], shapes: ['heart', 'oval'], note: '清冷里带少女感，适合冷感配色和清晰眉眼。' },
      { name: '宋慧乔', styles: ['natural', 'refined'], shapes: ['oval', 'round'], note: '低饱和、轻熟、皮肤质感路线。' },
      { name: '张钧甯', styles: ['clean', 'refined'], shapes: ['long', 'oval'], note: '利落健康，适合职业照和运动清爽感。' },
    ],
  },
  male: {
    reportTitle: '你的 AI 男生向形象报告',
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
    celebrities: [
      { name: '胡歌', styles: ['refined', 'clean'], shapes: ['long', 'oval'], note: '成熟、干净、书卷感和职业头像友好。' },
      { name: '白敬亭', styles: ['clean', 'natural'], shapes: ['oval', 'long'], note: '清爽少年感，适合简洁发型和浅背景。' },
      { name: '许光汉', styles: ['natural', 'sweet'], shapes: ['oval', 'round'], note: '松弛、亲和、适合自然表情和日常光线。' },
      { name: '肖战', styles: ['refined', 'clean'], shapes: ['long', 'heart'], note: '眉眼清晰，适合利落轮廓和精致路线。' },
      { name: '王一博', styles: ['clean', 'refined'], shapes: ['diamond', 'long'], note: '冷感、克制，适合黑白灰与线条感造型。' },
      { name: '彭于晏', styles: ['natural', 'clean'], shapes: ['squareRound', 'oval'], note: '健康、利落，适合运动感和开阔肩颈。' },
      { name: '张若昀', styles: ['refined', 'natural'], shapes: ['long', 'oval'], note: '轻熟通勤，适合低饱和穿搭和稳定表情。' },
      { name: '朱一龙', styles: ['clean', 'refined'], shapes: ['oval', 'heart'], note: '克制精致，适合强化眉眼与中轴干净度。' },
    ],
  },
};

const $ = (id) => document.getElementById(id);

function setActiveChip(group, value) {
  document.querySelectorAll(`[data-group="${group}"]`).forEach((el) => {
    el.classList.toggle('active', el.dataset.value === value);
  });
}

function choice(arr, index) {
  return arr[Math.abs(index) % arr.length];
}

function chooseMany(arr, indexes, count) {
  const used = new Set();
  const result = [];
  for (const idx of indexes) {
    const real = Math.abs(idx) % arr.length;
    if (!used.has(real)) {
      used.add(real);
      result.push(arr[real]);
    }
    if (result.length >= count) break;
  }
  return result;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

async function hashFile(file) {
  const buffer = await file.arrayBuffer();
  if (globalThis.crypto?.subtle) {
    const digest = await globalThis.crypto.subtle.digest('SHA-256', buffer);
    return Array.from(new Uint8Array(digest));
  }

  const bytes = new Uint8Array(buffer);
  const hash = new Array(32).fill(0);
  bytes.forEach((byte, index) => {
    hash[index % 32] = (hash[index % 32] + byte + index) % 256;
  });
  return hash;
}

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = state.previewUrl || URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => resolve({ img, url });
    img.onerror = reject;
    img.src = url;
  });
}

function getCanvasStats(img) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  const maxSize = 192;
  const ratio = img.width / img.height;
  canvas.width = ratio >= 1 ? maxSize : Math.max(1, Math.round(maxSize * ratio));
  canvas.height = ratio >= 1 ? Math.max(1, Math.round(maxSize / ratio)) : maxSize;
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);

  let totalLuma = 0;
  let totalLumaSq = 0;
  let warmBias = 0;
  let saturation = 0;
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const luma = 0.299 * r + 0.587 * g + 0.114 * b;
    totalLuma += luma;
    totalLumaSq += luma * luma;
    warmBias += r - b;
    saturation += max === 0 ? 0 : (max - min) / max;
  }

  const px = data.length / 4;
  const avgBrightness = totalLuma / px;
  const variance = Math.max(0, totalLumaSq / px - avgBrightness * avgBrightness);

  return {
    width: img.width,
    height: img.height,
    ratio,
    avgBrightness,
    contrast: Math.sqrt(variance),
    warmth: warmBias / px,
    saturation: saturation / px,
  };
}

async function detectFaceLandmarks(img) {
  if (!window.FaceMesh) return null;

  return new Promise((resolve) => {
    let settled = false;
    const finish = (value) => {
      if (settled) return;
      settled = true;
      resolve(value);
    };

    const faceMesh = new window.FaceMesh({
      locateFile: (file) => `${FACE_MESH_CDN}/${file}`,
    });

    faceMesh.setOptions({
      maxNumFaces: 2,
      refineLandmarks: true,
      minDetectionConfidence: 0.55,
      minTrackingConfidence: 0.5,
    });

    faceMesh.onResults((results) => {
      const faces = results.multiFaceLandmarks || [];
      finish({
        landmarks: faces[0] || null,
        faceCount: faces.length,
        method: faces[0] ? 'mediapipe-face-mesh' : 'no-face',
      });
    });

    faceMesh.send({ image: img }).catch(() => finish(null));
    setTimeout(() => finish(null), 8000);
  });
}

function point(landmarks, index, stats) {
  const raw = landmarks[index];
  return {
    x: raw.x * stats.width,
    y: raw.y * stats.height,
  };
}

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function midpoint(a, b) {
  return {
    x: (a.x + b.x) / 2,
    y: (a.y + b.y) / 2,
  };
}

function ratioText(value) {
  return Number.isFinite(value) ? value.toFixed(2) : '-';
}

function classifyFaceShape(metrics) {
  const { faceRatio, jawToFace, foreheadToFace, cheekToJaw, chinToFace } = metrics;

  if (faceRatio > 1.43) return 'long';
  if (cheekToJaw > 1.2 && foreheadToFace < 0.82) return 'diamond';
  if (foreheadToFace > 0.8 && jawToFace < 0.74 && chinToFace < 0.42) return 'heart';
  if (jawToFace > 0.86 && faceRatio < 1.28) return 'round';
  if (jawToFace > 0.82) return 'squareRound';
  return 'oval';
}

function classifyFeatureFocus(metrics, stats) {
  if (metrics.eyeToFace > 0.23) return 'eyes';
  if (metrics.jawToFace > 0.84) return 'jaw';
  if (stats.avgBrightness > 138 && stats.contrast < 54) return 'skin';
  if (metrics.mouthToFace > 0.36 || metrics.noseToFace > 0.21) return 'center';
  return 'balance';
}

function analyzeLandmarks(faceResult, stats) {
  if (!faceResult?.landmarks) return null;

  const landmarks = faceResult.landmarks;
  const top = point(landmarks, 10, stats);
  const chin = point(landmarks, 152, stats);
  const leftCheek = point(landmarks, 234, stats);
  const rightCheek = point(landmarks, 454, stats);
  const leftJaw = point(landmarks, 172, stats);
  const rightJaw = point(landmarks, 397, stats);
  const leftForehead = point(landmarks, 103, stats);
  const rightForehead = point(landmarks, 332, stats);
  const leftChin = point(landmarks, 148, stats);
  const rightChin = point(landmarks, 378, stats);
  const leftEyeOuter = point(landmarks, 33, stats);
  const leftEyeInner = point(landmarks, 133, stats);
  const rightEyeInner = point(landmarks, 362, stats);
  const rightEyeOuter = point(landmarks, 263, stats);
  const mouthLeft = point(landmarks, 61, stats);
  const mouthRight = point(landmarks, 291, stats);
  const noseLeft = point(landmarks, 129, stats);
  const noseRight = point(landmarks, 358, stats);
  const noseTip = point(landmarks, 1, stats);
  const browCenter = midpoint(point(landmarks, 105, stats), point(landmarks, 334, stats));

  const faceHeight = Math.max(1, distance(top, chin));
  const faceWidth = Math.max(1, distance(leftCheek, rightCheek));
  const jawWidth = distance(leftJaw, rightJaw);
  const foreheadWidth = distance(leftForehead, rightForehead);
  const chinWidth = distance(leftChin, rightChin);
  const leftEyeWidth = distance(leftEyeOuter, leftEyeInner);
  const rightEyeWidth = distance(rightEyeInner, rightEyeOuter);
  const eyeWidth = (leftEyeWidth + rightEyeWidth) / 2;
  const mouthWidth = distance(mouthLeft, mouthRight);
  const noseWidth = distance(noseLeft, noseRight);
  const upperThird = distance(top, browCenter) / faceHeight;
  const midThird = distance(browCenter, noseTip) / faceHeight;
  const lowerThird = distance(noseTip, chin) / faceHeight;

  const metrics = {
    faceRatio: faceHeight / faceWidth,
    jawToFace: jawWidth / faceWidth,
    foreheadToFace: foreheadWidth / faceWidth,
    cheekToJaw: faceWidth / Math.max(1, jawWidth),
    chinToFace: chinWidth / faceWidth,
    eyeToFace: eyeWidth / faceWidth,
    mouthToFace: mouthWidth / faceWidth,
    noseToFace: noseWidth / faceWidth,
    upperThird,
    midThird,
    lowerThird,
    symmetry: 1 - Math.min(0.4, Math.abs(leftEyeWidth - rightEyeWidth) / Math.max(1, eyeWidth)),
  };

  const faceShapeKey = classifyFaceShape(metrics);
  const featureFocusKey = classifyFeatureFocus(metrics, stats);
  const observations = [
    `脸部长宽比约 ${ratioText(metrics.faceRatio)}，当前更接近“${DATA.common.faceShapes[faceShapeKey].name}”。`,
    `下颌宽度约为脸宽的 ${(metrics.jawToFace * 100).toFixed(0)}%，适合据此调整发型和拍照角度。`,
    `平均眼裂宽度约为脸宽的 ${(metrics.eyeToFace * 100).toFixed(0)}%，眉眼清晰度会直接影响上镜稳定性。`,
    `鼻翼与唇部横向比例分别约为 ${(metrics.noseToFace * 100).toFixed(0)}% / ${(metrics.mouthToFace * 100).toFixed(0)}%，建议保持中轴干净。`,
    `三庭分布约为 ${(metrics.upperThird * 100).toFixed(0)}% / ${(metrics.midThird * 100).toFixed(0)}% / ${(metrics.lowerThird * 100).toFixed(0)}%，报告建议会优先平衡比例。`,
  ];

  if (faceResult.faceCount > 1) {
    observations.unshift('检测到多张人脸，报告优先分析画面中模型返回的第一张脸。');
  }

  return {
    method: 'cv',
    faceCount: faceResult.faceCount,
    confidence: Math.round((0.78 + Math.min(metrics.symmetry, 1) * 0.16) * 100),
    faceShapeKey,
    featureFocusKey,
    metrics,
    observations,
  };
}

function fallbackFaceAnalysis(hash, stats) {
  const faceShapeKeys = ['oval', 'round', 'squareRound', 'long', 'heart', 'diamond'];
  const featureKeys = ['eyes', 'center', 'jaw', 'skin', 'balance'];
  const faceShapeKey = stats.ratio < 0.82 ? 'long' : choice(faceShapeKeys, hash[3] + Math.round(stats.ratio * 10));
  const featureFocusKey = stats.avgBrightness > 136 ? 'skin' : choice(featureKeys, hash[4] + Math.round(stats.warmth));

  return {
    method: 'fallback',
    faceCount: 0,
    confidence: 42,
    faceShapeKey,
    featureFocusKey,
    metrics: {
      faceRatio: stats.ratio < 1 ? 1.34 : 1.18,
      jawToFace: 0.78,
      eyeToFace: 0.2,
      mouthToFace: 0.34,
      noseToFace: 0.19,
    },
    observations: [
      '未获取到稳定的人脸关键点，已切换为图片比例、亮度、色温与构图的兜底分析。',
      `照片亮度约 ${stats.avgBrightness.toFixed(0)}，色温偏差约 ${stats.warmth.toFixed(0)}，会影响配色与上镜建议。`,
      '建议换一张正脸、无遮挡、光线更均匀的照片，可得到更接近 CV 关键点模型级别的结果。',
    ],
  };
}

async function analyzeImage(file, hash) {
  const { img } = await loadImage(file);
  const stats = getCanvasStats(img);
  const faceResult = await detectFaceLandmarks(img);
  const faceAnalysis = analyzeLandmarks(faceResult, stats) || fallbackFaceAnalysis(hash, stats);

  return { stats, faceAnalysis };
}

function pickPalette(stats, styleKey, hash) {
  if (styleKey === 'clean' && stats.warmth < 6) return DATA.common.palettes[0];
  if (styleKey === 'refined' && stats.contrast > 46) return DATA.common.palettes[3];
  if (stats.warmth > 14 && stats.avgBrightness > 118) return DATA.common.palettes[4];
  if (stats.warmth > 4) return DATA.common.palettes[2];
  if (stats.avgBrightness < 94) return DATA.common.palettes[5];
  return choice(DATA.common.palettes, hash[5] + Math.round(stats.saturation * 100));
}

function pickStyle(stats, faceAnalysis, gender, hash) {
  const { faceShapeKey, featureFocusKey, metrics } = faceAnalysis;

  if (featureFocusKey === 'jaw' || faceShapeKey === 'diamond' || stats.contrast > 58) return 'clean';
  if (stats.avgBrightness > 132 && stats.saturation > 0.22 && gender === 'female') return 'sweet';
  if (faceShapeKey === 'long' || metrics.faceRatio > 1.35 || stats.contrast > 46) return 'refined';
  if (stats.avgBrightness > 128 && gender === 'male' && featureFocusKey === 'eyes') return 'clean';
  return choice(['natural', 'natural', 'refined', 'clean'], hash[7]);
}

function pickScene(stats, faceAnalysis, styleKey) {
  if (styleKey === 'refined' || (stats.contrast > 48 && stats.avgBrightness > 105)) return 'work';
  if (faceAnalysis.featureFocusKey === 'eyes' || stats.ratio < 0.95) return 'social';
  if (styleKey === 'sweet' || stats.warmth > 12) return 'dating';
  return 'daily';
}

function scoreFrom(hash, stats, faceAnalysis) {
  const base = 79 + (hash[0] % 12);
  const lightBonus = stats.avgBrightness > 132 ? 3 : stats.avgBrightness < 88 ? -3 : 1;
  const contrastBonus = stats.contrast > 42 ? 2 : 0;
  const cvBonus = faceAnalysis.method === 'cv' ? 3 : -1;
  const confidenceBonus = faceAnalysis.confidence > 88 ? 2 : 0;
  return Math.max(72, Math.min(98, base + lightBonus + contrastBonus + cvBonus + confidenceBonus));
}

function buildFeaturePool(faceAnalysis, stats) {
  const faceShape = DATA.common.faceShapes[faceAnalysis.faceShapeKey];
  const featureFocus = DATA.common.featureFocus[faceAnalysis.featureFocusKey];
  const pool = [...faceAnalysis.observations];

  pool.push(`${faceShape.name}适合围绕轮廓比例做发型和拍照角度优化。`);
  pool.push(`${featureFocus.name}是这张照片里更值得优先强化的上镜抓手。`);
  if (stats.avgBrightness > 128) pool.push('整体照片明亮度不错，更适合突出干净与通透路线。');
  if (stats.avgBrightness < 95) pool.push('照片偏暗时会压住皮肤和轮廓，建议优先修正光线。');
  if (stats.warmth > 10) pool.push('暖调环境下，柔和色系会比冷硬配色更自然。');
  if (stats.warmth < -8) pool.push('偏冷的画面环境更适合增强清爽和克制感。');
  if (stats.ratio < 0.92) pool.push('竖幅自拍更适合突出脸部与肩颈延伸。');
  if (stats.ratio > 1.18) pool.push('横幅照片会放大背景存在感，建议控制脸部占比。');
  return pool;
}

function buildBeautyPool(genderData, styleKey, sceneKey, faceAnalysis) {
  const pool = [...genderData.beautySuggestions];
  if (styleKey === 'sweet') {
    pool.push(state.gender === 'female'
      ? '可以适度提高腮红与唇色的甜感，但保持低饱和更耐看。'
      : '可以保留一点少年感和松弛感，不必把造型做得过于成熟。');
  }
  if (styleKey === 'clean') {
    pool.push(state.gender === 'female'
      ? '把色彩重心放在眉眼轮廓，会比强烈唇色更显高级。'
      : '尽量减少过多花哨元素，清爽干净会更贴合你的路线。');
  }
  if (sceneKey === 'work') {
    pool.push(state.gender === 'female'
      ? '通勤场景建议减少闪片与亮泽面积，保持稳重精致。'
      : '职业照建议强化眉眼清晰度和衣领整洁度，可信度会更高。');
  }
  if (faceAnalysis.featureFocusKey === 'skin') {
    pool.push('优先保证肤色均匀和光线干净，比增加复杂修饰更有效。');
  }
  return pool;
}

function buildHairPool(genderData, sceneKey, faceAnalysis, stats) {
  const pool = [...genderData.hairAccessories];
  if (faceAnalysis.faceShapeKey === 'long') pool.push('长脸倾向建议增加脸侧层次，减少发顶过度增高。');
  if (faceAnalysis.faceShapeKey === 'round') pool.push('圆脸倾向建议保留顶部轻蓬松和侧脸纵向线条。');
  if (faceAnalysis.faceShapeKey === 'diamond') pool.push('菱形脸倾向适合在颧骨附近用发丝或配饰做柔化。');
  if (sceneKey === 'social') pool.push('头像场景下，耳周和额前的整洁度会直接影响辨识度。');
  if (sceneKey === 'dating') pool.push('约会氛围照更适合柔和一点的发丝线条和配饰点缀。');
  if (stats.ratio > 1.1) pool.push('横幅照片里，发型轮廓会被放大，建议减少凌乱毛躁感。');
  return pool;
}

function selectCelebrities(genderData, styleKey, faceShapeKey, hash) {
  return genderData.celebrities
    .map((item, index) => {
      const styleScore = item.styles.includes(styleKey) ? 48 : 18;
      const shapeScore = item.shapes.includes(faceShapeKey) ? 34 : 10;
      const stableNoise = hash[(index + 11) % hash.length] / 12;
      return { ...item, similarity: Math.round(Math.min(96, styleScore + shapeScore + stableNoise)) };
    })
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, 3);
}

function buildResult(hash, stats, faceAnalysis) {
  const genderData = DATA[state.gender];
  const faceShape = DATA.common.faceShapes[faceAnalysis.faceShapeKey];
  const featureFocus = DATA.common.featureFocus[faceAnalysis.featureFocusKey];
  const styleKey = pickStyle(stats, faceAnalysis, state.gender, hash);
  const sceneKey = pickScene(stats, faceAnalysis, styleKey);
  const styleProfile = DATA.common.styleProfiles[styleKey];
  const sceneProfile = DATA.common.sceneProfiles[sceneKey];
  const palette = pickPalette(stats, styleKey, hash);
  const score = scoreFrom(hash, stats, faceAnalysis);
  const celebrities = selectCelebrities(genderData, styleKey, faceAnalysis.faceShapeKey, hash);

  const styleTags = [
    ...styleProfile.tags,
    faceShape.name,
    featureFocus.name,
    sceneProfile.name,
    palette.name,
  ].slice(0, 9);

  const features = chooseMany(buildFeaturePool(faceAnalysis, stats), hash.slice(8, 24), 6);
  const beautySuggestions = chooseMany(buildBeautyPool(genderData, styleKey, sceneKey, faceAnalysis), hash.slice(18, 32), 5);
  const hairAccessories = chooseMany(buildHairPool(genderData, sceneKey, faceAnalysis, stats), hash.slice(4, 20), 5);
  const photoTips = chooseMany(DATA.common.photoTips, hash.slice(16, 30), 4);
  const avoids = chooseMany(DATA.common.avoids, hash.slice(24, 40), 4);

  const summary = `这张照片更适合强化「${styleProfile.name}」路线，主要使用场景建议放在「${sceneProfile.name}」。CV 分析显示当前重点是 ${faceShape.name}、${featureFocus.name} 和 ${palette.name}，建议围绕这三点提升上镜稳定度。`;

  return {
    score,
    faceShape,
    featureFocus,
    styleProfile,
    sceneProfile,
    palette,
    summary,
    styleTags,
    styleSuggestions: styleProfile.suggestions,
    features,
    beautySuggestions,
    hairAccessories,
    photoTips,
    avoids,
    celebrities,
    beautyTitle: genderData.beautyTitle,
    reportTitle: genderData.reportTitle,
    modelLabel: faceAnalysis.method === 'cv'
      ? `CV 关键点 ${faceAnalysis.confidence}%`
      : `兜底分析 ${faceAnalysis.confidence}%`,
  };
}

function renderList(id, items) {
  $(id).innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
}

function renderResult(result) {
  $('report-title').textContent = result.reportTitle;
  $('report-summary').textContent = result.summary;
  $('report-score').textContent = `上镜指数 ${result.score}`;
  $('model-status').textContent = result.modelLabel;
  $('report-photo').src = state.previewUrl;

  $('face-shape').textContent = result.faceShape.name;
  $('face-shape-note').textContent = result.faceShape.note;
  $('feature-focus').textContent = result.featureFocus.name;
  $('feature-focus-note').textContent = result.featureFocus.note;
  $('style-type').textContent = result.styleProfile.name;
  $('style-type-note').textContent = result.styleProfile.note;
  $('scene-fit').textContent = result.sceneProfile.name;
  $('scene-fit-note').textContent = result.sceneProfile.note;
  $('color-palette').textContent = result.palette.name;
  $('color-palette-note').textContent = result.palette.note;
  $('camera-focus').textContent = result.featureFocus.name;
  $('camera-focus-note').textContent = result.featureFocus.note;

  renderList('feature-list', result.features);
  $('tag-cloud').innerHTML = result.styleTags.map((item) => `<span>${escapeHtml(item)}</span>`).join('');
  renderList('style-suggestion-list', result.styleSuggestions);
  $('celebrity-list').innerHTML = result.celebrities.map((item) => `
    <div class="celebrity-card">
      <div class="celebrity-avatar">${escapeHtml(item.name.slice(0, 1))}</div>
      <div>
        <strong>${escapeHtml(item.name)}</strong>
        <span>风格相似度 ${item.similarity}%</span>
        <p>${escapeHtml(item.note)}</p>
      </div>
    </div>
  `).join('');
  $('beauty-section-title').textContent = result.beautyTitle;
  renderList('beauty-suggestion-list', result.beautySuggestions);
  renderList('hair-accessory-list', result.hairAccessories);
  renderList('photo-tip-list', result.photoTips);
  renderList('avoid-list', result.avoids);
}

function simulateLoading(messages, done) {
  $('analysis-card').classList.remove('hidden');
  let step = 0;
  const bar = $('loading-bar');
  const text = $('loading-text');
  bar.style.width = '0%';
  text.textContent = messages[0];

  const timer = setInterval(() => {
    step += 1;
    text.textContent = messages[Math.min(step, messages.length - 1)];
    bar.style.width = `${Math.min((step + 1) * 20, 96)}%`;
    if (step >= messages.length - 1) {
      clearInterval(timer);
      bar.style.width = '100%';
      setTimeout(done, 260);
    }
  }, 430);
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
    const hash = await hashFile(state.file);
    const imageAnalysisPromise = analyzeImage(state.file, hash);

    simulateLoading([
      '正在读取图片基础特征...',
      '正在调用 CV 人脸关键点模型...',
      '正在判断脸型、五官比例和上镜重点...',
      '正在归纳强化风格与使用场景...',
      '正在匹配明星风格参考并整理报告...',
    ], () => {
      imageAnalysisPromise
        .then(({ stats, faceAnalysis }) => {
          state.imageStats = stats;
          state.faceAnalysis = faceAnalysis;
          state.result = buildResult(hash, stats, faceAnalysis);
          renderResult(state.result);
          $('result-section').classList.remove('hidden');
          $('analysis-card').classList.add('hidden');
          btn.disabled = false;
          btn.textContent = '重新生成形象报告';
          window.scrollTo({ top: $('result-section').offsetTop - 20, behavior: 'smooth' });
        })
        .catch((error) => {
          console.error(error);
          btn.disabled = false;
          btn.textContent = '生成形象报告';
          $('analysis-card').classList.add('hidden');
          alert('图片分析失败，请换一张清晰照片重试。');
        });
    });
  } catch (error) {
    console.error(error);
    btn.disabled = false;
    btn.textContent = '生成形象报告';
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
  $('photo-input').addEventListener('change', (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    state.file = file;
    state.result = null;
    if (state.previewUrl) URL.revokeObjectURL(state.previewUrl);
    state.previewUrl = URL.createObjectURL(file);
    $('photo-preview').src = state.previewUrl;
    $('preview-wrap').classList.remove('hidden');
    $('upload-empty').classList.add('hidden');
    $('result-section').classList.add('hidden');
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
  link.download = `AI形象分析报告-${new Date().toISOString().slice(0, 10)}.png`;
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
