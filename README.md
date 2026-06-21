# cover-generator v3.0

多品类抖音爆款封面一键生成器。

基于 6 张真实爆款封面（1200×1600）的逐像素分析，提炼为 **6 品类 × 18 模板** 的设计系统。

## 快速开始

```bash
pip install Pillow

# 科技类（默认，向后兼容）
python scripts/generate_cover.py --template dark --title "**跑分150万**的秘密"

# 教育类
python scripts/generate_cover.py --category education --template academic --title "**3分钟**搞懂区块链"

# 美食类
python scripts/generate_cover.py --category food --template warm_dark --title "**人均50**吃到撑"

# 旅游类
python scripts/generate_cover.py --category travel --template sunset --title "**此生必去**的5个地方"

# 时尚类
python scripts/generate_cover.py --category fashion --template luxury --title "**2026秋冬**必备单品"

# 财经类
python scripts/generate_cover.py --category business --template navy_gold --title "**年化15%**的真相"
```

## 6 大品类

| 品类 | --category | 模板数 | 设计基调 |
|------|-----------|--------|----------|
| 科技数码 | tech | 4 | 暗色科技、红金强调 |
| 教育知识 | education | 3 | 干净蓝白、高信任感 |
| 美食餐饮 | food | 3 | 暖色食欲、橙红棕 |
| 旅游出行 | travel | 3 | 自然蓝绿、开阔感 |
| 时尚美妆 | fashion | 3 | 黑金奢华、清冷极简 |
| 财经商业 | business | 3 | 藏蓝金、数据仪表 |

## 功能覆盖

- **富文本**：`**强调**` `__斜体__` `==色块==` `!!发光!!` `~~描边~~` ` ``反色`` `
- **多图**：横评/对比/网格 4 种布局
- **光影**：投影 shadow / 背光 backlight / 倒影 reflection
- **定位**：5 种产品位置 + 自定义占比

## 详细文档

- `SKILL.md` — 完整技能文档
- `references/cover-analysis.md` — 6 张爆款封面的深度分析
