# IQ 测评项目开发文档 V2（产品化改造版）

> 用途：给后续维护、功能扩展、部署排障、结果页优化、评分机制升级与后台增强提供统一说明。

---

## 1. 项目定位

这是一个**面向大众体验的在线智力检测平台**，用于展示：

- 数理推理
- 逻辑推理
- 言语理解
- 空间想象

四个维度下的在线答题、结果报告、后台统计与部署能力。

### 1.1 适用场景

- 网站展示型项目
- 课程设计 / 毕设 / Demo
- 产品原型与轻量测评平台
- 多测评平台的基础模板

### 1.2 不适用场景

本项目**不是**：

- 正式标准化 IQ 量表
- 医疗或心理诊断工具
- 招聘筛选依据
- 学校升学评估工具
- 专业临床认知评估系统

### 1.3 对外表达原则

- 首页可以使用“智力检测 / 脑力测试”等大众化表达吸引用户
- 结果页主标题不直接使用“你的 IQ 是多少”
- 结果页以 **综合认知表现、能力等级、百分位、四维画像** 为主
- “参考 IQ 区间”仅作为附加说明
- 所有结果都应明确说明：**这只是基于站内题库与规则生成的体验型参考结果**

建议首页文案：

> 在线智力检测平台：快速了解你的推理、理解与空间想象表现

建议结果页结论语：

> 本次测评反映的是你在本站题库下的综合认知表现与能力倾向

---

## 2. 新版结果体系

### 2.1 主指标

新版结果页以 **CPI（Cognitive Performance Index，综合认知表现指数）** 作为核心指标。

建议区间：

- 40–59：基础观察区
- 60–74：发展提升区
- 75–89：中等表现区
- 90–109：良好表现区
- 110–124：优秀表现区
- 125+：突出表现区

### 2.2 能力等级

用字母等级替代直接刺激性的单一 IQ 数字：

- E：基础观察
- D：发展提升
- C：中等水平
- B：良好水平
- A：优秀水平
- S：突出水平

### 2.3 站内百分位

示例：

> 你的表现超过了站内 78% 的有效作答用户

### 2.4 四维能力画像

每个维度提供：

- 维度得分
- 维度等级
- 简要解释
- 提升建议

### 2.5 参考 IQ 区间

仅在附加说明中展示：

> 根据本站内部映射规则，你本次表现大致对应参考 IQ 区间 108–114。
>
> 该区间只用于帮助普通用户理解结果所处层级，不等同于正式标准化 IQ 测验结论。

---

## 3. 评分逻辑

新版评分由四部分组成：

### 3.1 正确率得分

```python
accuracy_score = correct_count / answered_count
```

### 3.2 难度加权得分

难度权重建议：

- easy = 1.0
- medium = 1.2
- hard = 1.5

```python
difficulty_score = weighted_correct_sum / weighted_total_sum
```

### 3.3 完整度得分

```python
completion_score = answered_count / delivered_count
```

### 3.4 作答质量得分

参考因素：

- 平均每题作答时长
- 极短时长题目占比
- 重复选择同一选项的比例
- 测评是否完整提交

### 3.5 CPI 公式

```python
final_score_ratio = (
    0.45 * accuracy_score +
    0.30 * difficulty_score +
    0.10 * completion_score +
    0.15 * response_quality_score
)

cpi = round(40 + final_score_ratio * 90)
```

### 3.6 百分位映射

当前版本采用内部临时映射：

- CPI < 60：10–20 百分位
- 60–74：20–40 百分位
- 75–89：40–60 百分位
- 90–109：60–80 百分位
- 110–124：80–92 百分位
- 125+：92–98 百分位

### 3.7 可信度提示

- 高可信度：作答完整、节奏稳定
- 中可信度：存在少量快速作答或节奏波动
- 低可信度：存在较多极短作答或未完整完成

---

## 4. 题库机制

### 4.1 当前结构

当前版本已落地为 **32 题固定结构随机抽题**：

- 每个维度 8 题
- 每个维度的难度分布为：
  - easy 2 题
  - medium 4 题
  - hard 2 题

### 4.2 题目字段

题库中每道题建议具备：

- `category`
- `difficulty`
- `difficulty_weight`
- `prompt`
- `options`
- `correct_option`
- `explanation`
- `tags`
- `estimated_seconds`
- `is_active`

### 4.3 后续扩展方向

后续可继续把每个维度扩展到：

- easy 20 题
- medium 20 题
- hard 20 题

四个维度合计 240 题，用于提升复测体验与区分度。

---

## 5. 后台能力

当前后台已支持：

- 管理员登录
- 总体统计概览
- 四维维度正确率
- 作答记录筛选
- 单次详情页
- CSV 导出

单次详情页建议展示：

- 用户昵称 / 标识
- 提交时间
- 总用时
- CPI
- 能力等级
- 百分位
- 参考 IQ 区间
- 四维得分
- 每题作答详情
- 可信度标记

---

## 6. 接口清单

### 6.1 公开接口

- `GET /api/public/info`
- `POST /api/attempts/start`
- `POST /api/attempts/{attempt_id}/submit`
- `GET /api/attempts/{attempt_id}/result`

### 6.2 后台接口

- `POST /api/admin/login`
- `GET /api/admin/dashboard`
- `GET /api/admin/attempts`
- `GET /api/admin/attempts/{attempt_id}`
- `GET /api/admin/attempts/export.csv`

---

## 7. 数据模型

### 7.1 Question

当前重点字段：

- `category`
- `difficulty`
- `difficulty_weight`
- `explanation`
- `tags`
- `estimated_seconds`
- `is_active`

### 7.2 TestAttempt

当前重点字段：

- `cpi_score`
- `ability_level`
- `percentile`
- `iq_range`
- `accuracy_score`
- `difficulty_score`
- `completion_score`
- `response_quality_score`
- `validity_flag`
- `validity_note`
- `math_score`
- `logic_score`
- `verbal_score`
- `spatial_score`

### 7.3 AttemptAnswer

为了保证历史记录可解释，作答记录保存了题目快照：

- `question_dimension`
- `question_difficulty`
- `question_weight`
- `estimated_seconds`
- `prompt_snapshot`
- `selected_option`
- `correct_answer_snapshot`
- `explanation_snapshot`
- `time_spent_seconds`
- `is_correct`

---

## 8. 前端页面结构

### 8.1 前台结果页

建议顺序：

1. 顶部结论卡
2. CPI
3. 能力等级 + 百分位
4. 参考 IQ 区间
5. 四维能力画像
6. 结果解释说明
7. 可信度提示
8. 错题复盘

### 8.2 后台页

当前建议结构：

1. 登录区
2. 统计概览
3. 维度正确率
4. 记录筛选器
5. 记录列表
6. 单次详情页跳转

---

## 9. 部署与兼容性

- 默认部署方案为 SQLite 单容器
- 启动时执行轻量数据库迁移，用于给旧版数据库补齐新增字段
- 如果后续切换 PostgreSQL，建议引入正式迁移工具（如 Alembic）

---

## 10. 后续规划建议

### 第一阶段（已完成）

- 结果命名重构
- 评分逻辑可解释化
- 百分位与可信度展示
- 32 题随机抽题
- 后台详情与导出

### 第二阶段（建议继续）

- 继续扩充题库
- 引入题库管理能力
- 增加真实样本站内百分位校准
- 支持更多筛选统计维度

### 第三阶段（产品化增强）

- 前端组件化
- API 分层
- 数据库升级
- 题库可视化管理

---

## 11. 一句话总结

新版方向不是把它包装成“专业临床 IQ 量表”，而是把它做成一个：

> **更像成品、结果更易懂、解释更自圆其说、对大众更友好的在线智力检测平台**
