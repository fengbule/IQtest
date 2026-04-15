# Big Five 性格测试数据库
# 基于国际标准Big Five人格模型改编

# 五大人格维度及其特征
PERSONALITY_DIMENSIONS = {
    "openness": {
        "name": "开放性(Openness)",
        "description": "对新想法、经历和创意的接受程度",
        "high": "富有想象力、创意十足、喜欢探索新事物",
        "low": "传统、实际、偏好已知的事物"
    },
    "conscientiousness": {
        "name": "尽责性(Conscientiousness)",
        "description": "自律、有组织性和责任感",
        "high": "有计划、可靠、自律、追求完美",
        "low": "灵活、随意、不拘小节"
    },
    "extraversion": {
        "name": "外向性(Extraversion)",
        "description": "社交活跃程度和外向程度",
        "high": "热情、爱社交、精力充沛、爱冒险",
        "low": "内敛、独处、深思熟虑"
    },
    "agreeableness": {
        "name": "和善性(Agreeableness)",
        "description": "同情心、合作精神和友善程度",
        "high": "同情、慷慨、温和、配合",
        "low": "竞争、直率、批判"
    },
    "neuroticism": {
        "name": "神经质/情绪稳定性(Neuroticism)",
        "description": "情绪稳定性和压力应对能力",
        "high": "容易焦虑、情绪波动、敏感",
        "low": "稳定、冷静、抗压能力强"
    }
}

# 历史人物库 (每个维度0-100分)
HISTORICAL_FIGURES = [
    {
        "id": 1,
        "name": "孙子",
        "dynasty": "春秋时期",
        "title": "兵法家、战略家",
        "description": "《孙子兵法》作者，是中国古代伟大的军事理论家。他思想深邃、计算精密、注重谋略与秩序，但为人低调、自律严格。他的兵学思想强调\"道天地将法\"的系统性，展现出高度的战略思维和组织能力。孙子虽生活在战乱年代，但始终保持理性冷静，通过\"上兵伐谋\"等智慧超越纯粹的武力对抗，是历史上最具影响力的思想家之一。",
        "openness": 85,           # 创新战术
        "conscientiousness": 95,   # 极度自律
        "extraversion": 35,         # 低调、内向
        "agreeableness": 60,        # 中等
        "neuroticism": 20,          # 情绪稳定
    },
    {
        "id": 2,
        "name": "李白",
        "dynasty": "唐代",
        "title": "诗人、浪漫主义者",
        "description": "唐代伟大诗人，\"诗仙\"美誉享誉千古。李白热爱自由、富有想象力、创意无限，他的诗歌奔放、大胆、充满浪漫色彩。他性格外向、豪放不羁，喜欢冒险和新奇的经历，在酒肆与朋友谈天论地。虽然才华横溢，但有时缺乏约束，情绪波动较大，容易受环境影响。他代表了对自由和理想的永恒追求，是中国文化中最具个性的典范。",
        "openness": 100,          # 极度开放、创意
        "conscientiousness": 40,   # 不拘小节
        "extraversion": 90,        # 极度外向
        "agreeableness": 75,       # 友善豪爽
        "neuroticism": 65,         # 情绪波动
    },
    {
        "id": 3,
        "name": "诸葛亮",
        "dynasty": "三国时期",
        "title": "智者、谋士",
        "description": "三国时期最杰出的政治家和军事家。诸葛亮智慧超群、思虑周密、计划周全，其\"空城计\"等故事流传千古。他虽然具有高度的创新精神，但更看重秩序和法则，是极致的完美主义者。诸葛亮性格内敛、专注、克己奉公，为了蜀汉的事业鞠躬尽瘁。他的一生展现了理性、责任和坚持，虽然情绪相对稳定，但为实现理想付出了巨大代价。",
        "openness": 80,           # 创新战术
        "conscientiousness": 100,  # 完美主义
        "extraversion": 25,        # 内敛
        "agreeableness": 85,       # 克己奉公
        "neuroticism": 25,         # 极度稳定
    },
    {
        "id": 4,
        "name": "项羽",
        "dynasty": "秦末",
        "title": "楚霸王、猛将",
        "description": "秦末最强悍的武装力量领导者。项羽力大无穷、勇猛无敌、性格直率豪放。他热血沸腾、爱冒险、行动迅速，但缺乏耐心和深远谋划。项羽的性格中自信过头，有时显得傲慢，容易被激怒，情绪波动大。他代表了勇气和热血，但也反映了仅有武力而缺乏智慧的局限。虽然英勇无敌，但最终败给了更具策略的对手，成为古代\"力不如智\"的典范。",
        "openness": 55,           # 中等创新
        "conscientiousness": 45,   # 计划性不足
        "extraversion": 95,        # 极度外向
        "agreeableness": 50,       # 中等友善
        "neuroticism": 80,         # 情绪易波动
    },
    {
        "id": 5,
        "name": "班昭",
        "dynasty": "汉代",
        "title": "女性学者、教育家",
        "description": "中国历史上最著名的女性学者。班昭博学多才、温和善良、极具耐心和同情心。她虽然处于男性主导的社会，但通过勤学和努力获得了尊重。班昭的一生充满理性和教育精神，她著《女诫》教导女性修养，体现了高度的社会责任感和道德情操。她的性格中兼有开放的思想和传统的价值观，既有创新精神又重视秩序，是古代女性知识分子的杰出代表。",
        "openness": 75,           # 学者的开放心态
        "conscientiousness": 90,   # 严谨治学
        "extraversion": 45,        # 偏内向
        "agreeableness": 95,       # 极度和善
        "neuroticism": 30,         # 稳定理性
    },
    {
        "id": 6,
        "name": "唐太宗",
        "dynasty": "唐代",
        "title": "皇帝、治国家",
        "description": "唐朝伟大的皇帝，\"贞观之治\"的缔造者。唐太宗雄心勃勃、具有远见卓识，同时兼具开放包容的心态，善于采纳意见。他性格外向、果断、充满能量，但有时过于自信。唐太宗的治国理念体现了对秩序和效率的重视，他能够听取魏征的直言，展现了高度的理性和自我反思能力。他的一生是权力、智慧和人格的完美结合，是中国历史上最成功的统治者之一。",
        "openness": 85,           # 开放包容
        "conscientiousness": 85,   # 有秩序感
        "extraversion": 85,        # 外向果断
        "agreeableness": 75,       # 虚心纳谏
        "neuroticism": 35,         # 相对稳定
    },
    {
        "id": 7,
        "name": "苏轼",
        "dynasty": "北宋",
        "title": "文人、诗人",
        "description": "北宋最著名的文人，诗、词、书、画样样精通。苏轼性格旷达、充满幽默感、热爱生活和自然。他虽然才华横溢，但为人豁达、不刻意追求利禄，反而多次因为直言敢谏而遭贬。苏轼的开放思想和对新事物的接受度很高，但他的理想主义有时与现实产生冲突。他的一生充满波折，却始终保持乐观和创意，用笔尖书写人生的悲欢离合，代表了文人的洒脱和坚持。",
        "openness": 95,           # 极度开放
        "conscientiousness": 55,   # 不拘小节
        "extraversion": 75,        # 外向社交
        "agreeableness": 80,       # 同情他人
        "neuroticism": 55,         # 中等敏感
    },
    {
        "id": 8,
        "name": "曾国藩",
        "dynasty": "清代",
        "title": "政治家、将军",
        "description": "晚清最重要的政治和军事人物。曾国藩性格坚毅、自律极强，其\"修身齐家治国平天下\"的理想贯穿一生。他做事有计划、讲求秩序、追求完美，虽然缺乏天才式的灵感，但通过持之以恒的努力获得成功。曾国藩的一生充满理性和责任感，他对部下严格，对自己更严格，代表了传统士人的最高精神境界。他虽然属于保守派，但在乱世中展现了稳定和秩序的价值，是自律精神的典范。",
        "openness": 50,           # 相对保守
        "conscientiousness": 100,  # 完美主义
        "extraversion": 50,        # 中等外向
        "agreeableness": 70,       # 有原则
        "neuroticism": 25,         # 极度稳定
    },
]

# 50道Big Five性格测试题目
# 每题采用李克特5点量表：1=强烈不同意, 5=强烈同意
# is_reverse: True表示需要反向计分
PERSONALITY_QUESTIONS = [
    # openness维度（10题）
    {
        "id": 1,
        "dimension": "openness",
        "question": "我想象力丰富，经常能想到创新的点子",
        "is_reverse": False,
        "position": 1
    },
    {
        "id": 2,
        "dimension": "openness",
        "question": "我喜欢尝试新的事物和不同的经历",
        "is_reverse": False,
        "position": 2
    },
    {
        "id": 3,
        "dimension": "openness",
        "question": "我对艺术、音乐和文学很感兴趣",
        "is_reverse": False,
        "position": 3
    },
    {
        "id": 4,
        "dimension": "openness",
        "question": "我倾向于思考抽象的观点和想法",
        "is_reverse": False,
        "position": 4
    },
    {
        "id": 5,
        "dimension": "openness",
        "question": "我的工作方式倾向于常规和既定的方法",
        "is_reverse": True,
        "position": 5
    },
    {
        "id": 6,
        "dimension": "openness",
        "question": "我喜欢发现新知识和学习新事物",
        "is_reverse": False,
        "position": 6
    },
    {
        "id": 7,
        "dimension": "openness",
        "question": "我更喜欢安定的、可预见的生活",
        "is_reverse": True,
        "position": 7
    },
    {
        "id": 8,
        "dimension": "openness",
        "question": "我在创意和创新方面有相当的能力",
        "is_reverse": False,
        "position": 8
    },
    {
        "id": 9,
        "dimension": "openness",
        "question": "我对哲学和理论问题很感兴趣",
        "is_reverse": False,
        "position": 9
    },
    {
        "id": 10,
        "dimension": "openness",
        "question": "我倾向于保守和传统的价值观",
        "is_reverse": True,
        "position": 10
    },

    # conscientiousness维度（10题）
    {
        "id": 11,
        "dimension": "conscientiousness",
        "question": "我做事情总是有计划，井井有条",
        "is_reverse": False,
        "position": 11
    },
    {
        "id": 12,
        "dimension": "conscientiousness",
        "question": "我是一个可靠和值得信任的人",
        "is_reverse": False,
        "position": 12
    },
    {
        "id": 13,
        "dimension": "conscientiousness",
        "question": "我的工作质量总是很高",
        "is_reverse": False,
        "position": 13
    },
    {
        "id": 14,
        "dimension": "conscientiousness",
        "question": "我很自律，很少拖延",
        "is_reverse": False,
        "position": 14
    },
    {
        "id": 15,
        "dimension": "conscientiousness",
        "question": "我的生活方式有些散乱，不太有条理",
        "is_reverse": True,
        "position": 15
    },
    {
        "id": 16,
        "dimension": "conscientiousness",
        "question": "我对细节要求很高，追求完美",
        "is_reverse": False,
        "position": 16
    },
    {
        "id": 17,
        "dimension": "conscientiousness",
        "question": "我经常忘记东西或遗漏重要的细节",
        "is_reverse": True,
        "position": 17
    },
    {
        "id": 18,
        "dimension": "conscientiousness",
        "question": "我责任感强，总是力求做到最好",
        "is_reverse": False,
        "position": 18
    },
    {
        "id": 19,
        "dimension": "conscientiousness",
        "question": "我做计划时很周全，考虑周到",
        "is_reverse": False,
        "position": 19
    },
    {
        "id": 20,
        "dimension": "conscientiousness",
        "question": "我不太在意事情是否完美",
        "is_reverse": True,
        "position": 20
    },

    # extraversion维度（10题）
    {
        "id": 21,
        "dimension": "extraversion",
        "question": "我是一个外向的人，喜欢社交",
        "is_reverse": False,
        "position": 21
    },
    {
        "id": 22,
        "dimension": "extraversion",
        "question": "我喜欢参加各种社交活动和聚会",
        "is_reverse": False,
        "position": 22
    },
    {
        "id": 23,
        "dimension": "extraversion",
        "question": "我是话题中心，总是吸引他人的注意",
        "is_reverse": False,
        "position": 23
    },
    {
        "id": 24,
        "dimension": "extraversion",
        "question": "我有很多朋友，社交圈很广",
        "is_reverse": False,
        "position": 24
    },
    {
        "id": 25,
        "dimension": "extraversion",
        "question": "我更喜欢独处而不是和别人在一起",
        "is_reverse": True,
        "position": 25
    },
    {
        "id": 26,
        "dimension": "extraversion",
        "question": "我做事充满精力和热情",
        "is_reverse": False,
        "position": 26
    },
    {
        "id": 27,
        "dimension": "extraversion",
        "question": "我是一个比较文静和内向的人",
        "is_reverse": True,
        "position": 27
    },
    {
        "id": 28,
        "dimension": "extraversion",
        "question": "我主动和陌生人交谈，不会感到尴尬",
        "is_reverse": False,
        "position": 28
    },
    {
        "id": 29,
        "dimension": "extraversion",
        "question": "我爱冒险，喜欢刺激的经历",
        "is_reverse": False,
        "position": 29
    },
    {
        "id": 30,
        "dimension": "extraversion",
        "question": "我在大群体中感到不舒服",
        "is_reverse": True,
        "position": 30
    },

    # agreeableness维度（10题）
    {
        "id": 31,
        "dimension": "agreeableness",
        "question": "我是一个同情心强的人，容易理解他人",
        "is_reverse": False,
        "position": 31
    },
    {
        "id": 32,
        "dimension": "agreeableness",
        "question": "我总是尽力帮助需要帮助的人",
        "is_reverse": False,
        "position": 32
    },
    {
        "id": 33,
        "dimension": "agreeableness",
        "question": "我愿意为了和睦而做出妥协",
        "is_reverse": False,
        "position": 33
    },
    {
        "id": 34,
        "dimension": "agreeableness",
        "question": "我觉得他人的感受很重要",
        "is_reverse": False,
        "position": 34
    },
    {
        "id": 35,
        "dimension": "agreeableness",
        "question": "我有时候比较冷淡，缺乏同情心",
        "is_reverse": True,
        "position": 35
    },
    {
        "id": 36,
        "dimension": "agreeableness",
        "question": "我喜欢合作，更愿意与人合作而不是竞争",
        "is_reverse": False,
        "position": 36
    },
    {
        "id": 37,
        "dimension": "agreeableness",
        "question": "我的想法往往与他人发生冲突",
        "is_reverse": True,
        "position": 37
    },
    {
        "id": 38,
        "dimension": "agreeableness",
        "question": "我是一个温和、和善的人",
        "is_reverse": False,
        "position": 38
    },
    {
        "id": 39,
        "dimension": "agreeableness",
        "question": "我关心他人的福利和幸福",
        "is_reverse": False,
        "position": 39
    },
    {
        "id": 40,
        "dimension": "agreeableness",
        "question": "我更在意自己的利益，而不太关心他人",
        "is_reverse": True,
        "position": 40
    },

    # neuroticism维度（10题）
    {
        "id": 41,
        "dimension": "neuroticism",
        "question": "我容易感到焦虑和担忧",
        "is_reverse": False,
        "position": 41
    },
    {
        "id": 42,
        "dimension": "neuroticism",
        "question": "我的情绪波动比较大",
        "is_reverse": False,
        "position": 42
    },
    {
        "id": 43,
        "dimension": "neuroticism",
        "question": "我对压力反应敏感，容易感到不适",
        "is_reverse": False,
        "position": 43
    },
    {
        "id": 44,
        "dimension": "neuroticism",
        "question": "我经常感到沮丧或悲伤",
        "is_reverse": False,
        "position": 44
    },
    {
        "id": 45,
        "dimension": "neuroticism",
        "question": "我很少感到压力或紧张",
        "is_reverse": True,
        "position": 45
    },
    {
        "id": 46,
        "dimension": "neuroticism",
        "question": "我很容易生气或烦躁",
        "is_reverse": False,
        "position": 46
    },
    {
        "id": 47,
        "dimension": "neuroticism",
        "question": "我通常保持冷静和镇定",
        "is_reverse": True,
        "position": 47
    },
    {
        "id": 48,
        "dimension": "neuroticism",
        "question": "我容易自我怀疑，缺乏自信",
        "is_reverse": False,
        "position": 48
    },
    {
        "id": 49,
        "dimension": "neuroticism",
        "question": "我经常感到不安和不舒适",
        "is_reverse": False,
        "position": 49
    },
    {
        "id": 50,
        "dimension": "neuroticism",
        "question": "我是一个情绪稳定的人",
        "is_reverse": True,
        "position": 50
    },
]
