---
name: cover-generator
description: Generate Douyin viral-style video covers (1200x1600, 3:4 portrait) for any content category — tech, education, food, travel, fashion, business. Based on pixel-level analysis of 6 real viral covers. Supports rich text markup, multi-image layouts, product glow/shadow/reflection effects. Use when asked to create a Douyin cover for any content type.
---

# cover-generator — 多品类抖音爆款封面生成器 v3.1

**一句话**：选品类 → 填文案 → 自动生成符合抖音爆款规律的竖屏封面（1200×1600）。

> 基于 6 张真实爆款封面的逐像素分析，提炼为跨品类设计公式 + **富文本引擎** + **多图光影引擎** + **6 品类模板系统**。详见 `references/cover-analysis.md`。

## v3.1：4 种排版布局（文字在上/文字包裹/图片在上/满铺背景）

| 布局 | 参数 | 说明 | 匹配参考 |
|------|------|------|----------|
| **文字在上** ☆默认 | `--cover-layout text-above` | 文字占上方40-55%，图片在下方 | 2/6 爆款 |
| **文字包裹** | `--cover-layout text-surround` | 标题在上 + 图片在中 + 规格在下 | 3/6 爆款 |
| **图片在上** | `--cover-layout image-above` | 图片在上 + 文字在下（旧默认） | 1/6 爆款 |
| **满铺背景** | `--cover-layout full-bg` | 图片铺满全画布 + 半透明蒙层 + 文字叠加 | 图文混合 |

> ★ **默认布局已改为 `text-above`**（文字在上），匹配 5/6 参考封面的真实排版。

## v3.0：6 大品类，一键切换

| 品类 | 参数 | 可用模板 | 设计基调 |
|------|------|----------|----------|
| 科技数码 | `--category tech` | dark / dark_blue / bright / warm_tech | 暗色科技、红金强调、数据驱动 |
| 教育知识 | `--category education` | academic / chalkboard / clean | 干净蓝白、高信任感 |
| 美食餐饮 | `--category food` | warm_dark / bright_eat / rustic | 暖色食欲、橙红棕 |
| 旅游出行 | `--category travel` | nature / sunset / aerial | 自然蓝绿、开阔感 |
| 时尚美妆 | `--category fashion` | luxury / clean_girl / vibrant | 黑金奢华、清冷极简 |
| 财经商业 | `--category business` | navy_gold / white_paper / dark_data | 藏蓝金、数据仪表 |

**向后兼容**：不指定 `--category` 默认为 `tech`，旧命令无需修改。

## 覆盖效果总览

| 功能 | 支持情况 |
|------|---------|
| 富文本标记（6种） | `**强调**` `__斜体__` `==色块==` `!!发光!!` `~~描边~~` ` ``反色`` ` |
| 文字描边/投影 | 暗底自动启用，可调宽度 |
| 多图排版（4种） | 对比2/横评3/品字3/网格4 |
| 抠图光影 | 投影shadow / 背光backlight / 双开both |
| 镜面倒影 | `--image-reflection` |
| 11种产品定位 | top-center/left/right, center/mid-left/mid-right, bottom-center/left/right/fill, full-bg |
| 4种排版布局 | text-above☆ / image-above / text-surround / full-bg |
| 产品标注 | 每图独立标签 |
| 旋转徽章 | `--corner-badge "HOT"` |

## v2.0 已有：富文本标记语法

| 语法 | 效果 | 示例 |
|------|------|------|
| `**text**` | 强调色 + 加粗 | `**跑分150万**的秘密` |
| `__text__` | 次级色 + 斜体 | `深度评测 \| __实至名归？__` |
| `==text==` | 色块底衬 | `==独家首发==` |
| `!!text!!` | 发光效果 | `!!性能怪兽!!` |
| `~~text~~` | 空心描边字 | `~~PRO~~` |
| ` ``text`` ` | 反色文字 | ` ``限时`` ` |

---

## 爆款封面核心公式

经过对 6 张封面的程序化分析（色彩分布、HSV空间、3×3网格亮度、std对比度、文字区密度），总结出以下铁律：

| 要素 | 规则 |
|------|------|
| **尺寸** | 1200×1600（3:4竖屏），填满整个空间 |
| **背景** | 暗底（60-80%画面）或暖亮底（20-40%画面），纯色/极简 |
| **对比度** | 必须 HIGH（整体 std > 70），这是抓眼球的前提 |
| **强调色** | ≤10% 画面，红/金/橙/青，饱和拉满 |
| **文字** | 3-4 级层级（钩子标题 → 副标题 → 规格参数 → 标签） |
| **构图** | 不对称！左右亮度差 ≥10，产品偏左或居中 |
| **信息密度** | 文字覆盖 40-60% 画面 |

---

## 四种模板速查

| 模板 | 背景 | 强调色 | 适用场景 |
|------|------|--------|----------|
| `dark` | 纯黑 #0A0A0C | 红色 #EB282D | 产品评测、新品首发、性能怪兽 |
| `dark_blue` | 深蓝黑 #080A1C | 金色 #FFC328 | 芯片/显卡、跑分对比、技术解读 |
| `bright` | 奶油白 #F8F4EC | 红橙 #E43A20 | 横评推荐、性价比榜单、避坑指南 |
| `warm_tech` | 暗暖黑 #1A161C | 暖橙 #FF8E1E | 摄影器材、影音设备、设计产品 |

---

## 使用方法

### 方式 1：命令行直接生成

```bash
cd <workspace>/skills/tech-cover-generator

# === 科技类（默认，向后兼容）===

# 暗黑产品评测风 — 关键词高亮
python scripts/generate_cover.py \
    --template dark --title "**跑分150万**的秘密" \
    --specs "跑分:150万" "芯片:A18 Pro" "功耗:6.2W" \
    --tags "旗舰横评" "首发评测" --corner-badge "HOT"

# === 教育类 ===

python scripts/generate_cover.py --category education --template academic \
    --title "**3分钟**搞懂区块链" --subtitle "小白也能听明白"

# === 美食类 ===

python scripts/generate_cover.py --category food --template warm_dark \
    --title "**人均50**吃到撑" --image dish.png --image-glow backlight \
    --specs "口味:9.2" "环境:8.5" "服务:9.0" --tags "探店" "必吃"

# === 旅游类 ===

python scripts/generate_cover.py --category travel --template sunset \
    --title "**此生必去**的5个地方" --image scenic.png --image-glow both

# === 时尚类 ===

python scripts/generate_cover.py --category fashion --template luxury \
    --title "**2026秋冬**必备单品" --image outfit.png --image-glow both \
    --corner-badge "NEW"

# === 财经类 ===

python scripts/generate_cover.py --category business --template navy_gold \
    --title "**年化15%**的真相" \
    --specs "收益:15.2%" "风险:中等" "门槛:1000" \
    --price "¥1000起"

# === 多产品横评（通用）===

python scripts/generate_cover.py --category food --template bright_eat \
    --title "**3款**网红螺蛳粉横评" \
    --image a.png --image b.png --image c.png \
    --image-layout compare-3h --image-labels "A款" "B款" "C款"
```

### 方式 2：对话式生成（推荐）

直接用自然语言描述需求，我来调用脚本生成：

> "帮我做一个暗黑风的科技封面，标题是'RTX 5090深度评测'，副标题是'性能提升300%？实测数据全公开'，标签用'显卡' '评测' '首发'"

> "生成一个亮色横评封面，对比8款千元机，标题是'2026千元机推荐'"

---

## 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--template` | 否 | 模板风格 (dark/dark_blue/bright/warm_tech) | `--template dark` |
| `--title` | **是** | L1 钩子标题，3-12字，建议疑问句/数字开头 | `--title "跑分150万的秘密"` |
| `--subtitle` | 推荐 | L2 副标题，6-20字 | `--subtitle "深度评测 | 性能怪兽"` |
| `--specs` | 推荐 | 规格参数，格式 `"标签:数值"`，2-4组 | `--specs "跑分:150万" "功耗:6.2W"` |
| `--tags` | 推荐 | 底部标签，2-5个 | `--tags "旗舰" "评测" "首发"` |
| `--price` | 否 | 右下角价格徽章 | `--price "¥8999"` |
| `--image` | 推荐 | 产品图，可多次使用（抠图用PNG） | `--image a.png --image b.png` |
| `--image-layout` | 否 | 多图布局 (single/compare-2/compare-3h/compare-3v/grid-4) | `--image-layout compare-3h` |
| `--image-position` | 否 | 单图定位 (top-center/left/right, center/mid-left/right, bottom-center/left/right/fill, full-bg) | `--image-position bottom-center` |
| `--image-glow` | 推荐 | 抠图光影 (none/shadow/backlight/both) | `--image-glow both` |
| `--image-reflection` | 否 | 启用镜面倒影 | `--image-reflection` |
| `--image-labels` | 否 | 每张产品图的标注文字 | `--image-labels "A机" "B机" "C机"` |
| `--cover-layout` | 否 | 排版布局 (text-above☆/image-above/text-surround/full-bg) | `--cover-layout text-surround` |
| `--accent-bar` | 否 | 强调色条旁文字（支持富文本） | `--accent-bar "**独家首发**"` |
| `--corner-badge` | 否 | 右上角旋转徽章 (如 HOT/NEW/PRO) | `--corner-badge "HOT"` |
| `--output` / `-o` | 否 | 输出路径 (default: cover.png) | `-o my_cover.png` |

> **多图示例**：`--image phone1.png --image phone2.png --image phone3.png --image-layout compare-3h`
> **富文本可混排**：`"**跑分**150万的__真相__"` = 跑分(红粗)150万的真相(灰斜)

---

## 标题文案技巧（提升点击率）

基于 6 张爆款封面的文案模式分析：

| 类型 | 模板 | 示例 |
|------|------|------|
| **疑问悬念** | "为什么XX...？" | "为什么旗舰机越卖越贵" |
| **数字冲击** | "N款/N元/N倍..." | "500元以内最强TWS" |
| **对比冲突** | "XX vs XX" | "A18 Pro vs 骁龙8 — 差距有多大？" |
| **排行榜** | "TOP5 / 榜单" | "2026千元机性能榜TOP5" |
| **揭露真相** | "真相/秘密/内幕" | "跑分造假的秘密" |

**最佳实践**：标题 5-10 字，包含数字或疑问词，制造信息缺口。

---

## 色彩搭配参考

```
暗底公式 (4/6爆款使用):
┌────────────────────────────────────┐
│ 背景 60-80%  │ #000000 / #080A1C / #0A0A0C │
│ 文字 15-25%  │ #F0F0F5 (亮白) + #AAB4C8 (次级灰) │
│ 强调 5-10%   │ #EB282D (红) / #FFC328 (金) / #FF8E1E (橙) │
│ 辅助 1-3%    │ #3CC850 (绿/跑分) / #32B9E1 (青/温度) │
└────────────────────────────────────┘

亮底公式 (2/6爆款使用):
┌────────────────────────────────────┐
│ 背景 60-80%  │ #F8F4EC / #E0E0C0 (奶油/米色) │
│ 文字 15-25%  │ #121216 (深黑) + #6E6964 (灰棕) │
│ 强调 5-10%   │ #E43A20 (红橙) / #128EB9 (蓝绿) │
└────────────────────────────────────┘
```

---

## 依赖安装

```bash
pip install Pillow
```

中文字体：脚本会自动检测系统字体（Windows/macOS/Linux），无需额外配置。

---

## 任务隔离

所有生成的封面输出到用户指定的路径，不会污染技能目录。

```
正确 ✅:
  python scripts/generate_cover.py --output "D:/workspace/项目/cover.png"

错误 ❌:
  python scripts/generate_cover.py --output cover.png  (散落在技能目录)
```

---

## 参考

- `references/cover-analysis.md` — 6 张爆款封面的完整数据化分析（色彩、构图、排版、心理触发机制）
- `scripts/generate_cover.py` — 核心生成脚本
