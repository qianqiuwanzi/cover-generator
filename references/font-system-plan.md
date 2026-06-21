# 字体系统 & 花字模板 — 实现方案 v4.0

> 目标：支持抖音/剪映流行字体 + 花字样式模板，让封面文字具有爆款视觉冲击力

---

## 一、现状分析

### 当前字体系统

| 项目 | 当前状态 | 缺陷 |
|------|---------|------|
| 字体发现 | 硬编码路径列表，自动选第一个找到的 | 无 `--font` 参数，用户无法选择 |
| 字体文件 | 只找系统自带字体（微软雅黑/黑体/宋体等） | 不支持自定义 .ttf/.otf，不支持流行字体 |
| 粗体 | 有独立粗体路径列表 | 粗体=换字体文件，而非动态合成 |
| 斜体 | 用 `Image.AFFINE` 矩阵模拟 12° 剪切 | 不是真正的 italic，质量差 |
| 字号 | 全部硬编码 | 无 `--font-size` 系列参数 |
| 行间距 | 硬编码 | 无法调 |

### 当前样式系统（6 种标记）

| 标记 | 底层实现 | 可调参数 |
|------|---------|---------|
| `**text**` | 强调色填充 + 粗体 + 暗底2px阴影描边 | ❌ 无 |
| `__text__` | 次级色 + 12° 仿射斜切 | ❌ 无 |
| `==text==` | 色块底衬 + 粗体 | ❌ 无（padding=8, radius=6 硬编码） |
| `!!text!!` | 外发光（GaussianBlur radius=10） | ❌ 无 |
| `~~text~~` | 空心描边（描边=强调色, 填充=背景色, width=3） | ❌ 无 |
| `` `text` `` | 反色填充 | ❌ 无 |

---

## 二、需要支持的内容

### 2.1 字体库

#### 免费商用字体（优先集成）

| 序号 | 字体 | 风格 | 适用品类 | 字重 | 授权 |
|------|------|------|----------|------|------|
| 1 | **思源黑体** | 现代无衬线 | 全品类通用 | 7 (ExtraLight→Heavy) | SIL OFL |
| 2 | **阿里巴巴普惠体** | 稳重有力 | 电商/科技/商务 | 10 | 阿里免费商用 |
| 3 | **站酷高端黑** | 粗犷冲击 | 科技/潮流 | 1 | CC-署名 |
| 4 | **站酷酷黑** | 硬朗力量 | 电竞/潮流 | 1 | CC-署名 |
| 5 | **站酷快乐体** | 圆润活泼 | 美食/亲子 | 1 | CC-署名 |
| 6 | **站酷文艺体** | 清新艺术 | 时尚/文艺 | 1 | CC-署名 |
| 7 | **OPPO Sans** | 现代舒展 | 科技/商务 | 5 | OPPO免费商用 |
| 8 | **鸿蒙字体** | 轻奢高级 | 时尚/商务 | 9 | 华为开源 |

#### 流行付费字体（引导用户自行安装）

| 序号 | 字体 | 风格 | 来源 |
|------|------|------|------|
| 9 | 汉仪旗黑 | 标题首选 | 汉仪字库 |
| 10 | 方正兰亭黑 | 屏幕阅读舒适 | 方正字库 |
| 11 | 造字工房力黑 | 力量感标题 | 造字工房 |
| 12 | 喜鹊招牌体 | 手写风格 | 喜鹊造字 |

### 2.2 花字模板（12 种）

剪映花字的本质是 **多层文字叠加**。每个花字模板由 N 个渲染层组成：

```
花字模板 = [图层1, 图层2, ..., 图层N]
每个图层 = {偏移(dx,dy), 字体, 字号, 填充色, 描边(颜色,宽度), 投影(颜色,偏移,模糊), 发光(颜色,半径)}
```

#### 模板分类

**A 类：描边系（3 种）—— 最常用，适合标题/数字**

```
┌─────────────────────────────────────────┐
│  A1 经典白描边                           │
│  Layer 3: 深色外描边 6px #333333         │ ← 最外层，最粗
│  Layer 2: 白色中描边 3px #FFFFFF         │ ← 中间层，制造分离感
│  Layer 1: 文字填充（渐变/纯色）           │ ← 最内层，正文
│                                          │
│  A2 荧光撞色                             │
│  Layer 2: 荧光描边 4px #FF00FF           │
│  Layer 1: 文字填充 + 2px 白色内描边      │
│                                          │
│  A3 立体浮雕                             │
│  Layer 3: 深色投影 offset(3,3) blur=4    │
│  Layer 2: 亮色高光描边 2px               │
│  Layer 1: 文字填充                       │
└─────────────────────────────────────────┘
```

**B 类：光影系（3 种）—— 适合强调/数字/价格**

```
┌─────────────────────────────────────────┐
│  B1 霓虹发光                             │
│  Layer 2: 外发光 blur=12 #FF0040 不透明度60%│
│  Layer 1: 文字 #FFFFFF + 内发光          │
│                                          │
│  B2 金属渐变                             │
│  Layer 2: 文字渐变填充（金→浅金→金）      │
│  Layer 1: 1px 深色内阴影                 │
│                                          │
│  B3 氛围光晕                             │
│  Layer 2: 大范围光晕 blur=20             │
│  Layer 1: 文字 + 2px 白色描边            │
└─────────────────────────────────────────┘
```

**C 类：底衬系（3 种）—— 适合标签/角标**

```
┌─────────────────────────────────────────┐
│  C1 圆角标签                             │
│  Layer 2: 圆角矩形底色 + 投影            │
│  Layer 1: 白色粗体文字                   │
│                                          │
│  C2 镂空绶带                             │
│  Layer 2: 倾斜平行四边形色块 + 投影      │
│  Layer 1: 文字                           │
│                                          │
│  C3 爆炸贴纸                             │
│  Layer 2: 不规则多边形底色 + 描边        │
│  Layer 1: 文字                           │
└─────────────────────────────────────────┘
```

**D 类：3D/立体系（3 种）—— 适合主标题/钩子**

```
┌─────────────────────────────────────────┐
│  D1 长投影                               │
│  Layer 8-N: 多层投影 offset(1,1)递增     │
│  Layer 1: 文字填充                       │
│                                          │
│  D2 3D 挤出                               │
│  Layer N: 逐层向下偏移 1px × 10层        │
│  Layer 1: 文字最上层                     │
│                                          │
│  D3 双重曝光                             │
│  Layer 2: 文字副本 offset(4,0) 50%透明度 │
│  Layer 1: 文字本体                       │
└─────────────────────────────────────────┘
```

---

## 三、实现方案

### 3.1 架构总览

```
scripts/
├── generate_cover.py          # 主入口（调用字体/花字模块）
├── font_manager.py            # ★ 新增：字体管理器
├── huazi_engine.py            # ★ 新增：花字渲染引擎
└── huazi_templates.py         # ★ 新增：花字模板库（12种预设）

fonts/                          # ★ 新增：字体目录
├── README.md                   # 字体安装说明 + 下载链接
├── SourceHanSansCN-Bold.otf   # 思源黑体 粗体（内置）
├── AlibabaPuHuiTi-3-85-Bold.otf  # 阿里普惠体 粗体（内置）
└── ...                         # 用户自行安装更多
```

### 3.2 字体管理器 `font_manager.py`

```python
class FontManager:
    """字体发现、注册、缓存、回退"""

    def __init__(self, font_dirs=None):
        # 默认扫描路径
        self.font_dirs = font_dirs or [
            "./fonts/",                          # 技能内置字体
            "C:/Windows/Fonts/",                 # Windows 系统
            "/System/Library/Fonts/",            # macOS
            "/usr/share/fonts/",                 # Linux
        ]
        self._registry = {}   # {font_name: {weight: path}}
        self._cache = {}      # {cache_key: ImageFont}
        self._scan()

    def _scan(self):
        """扫描所有字体目录，建立字体注册表"""
        for d in self.font_dirs:
            for f in glob(d, "*.ttf", "*.otf", "*.ttc"):
                # 解析字体元数据：family, weight, style
                meta = self._parse_font_meta(f)
                self._registry.setdefault(meta.family, {})[meta.weight] = f

    def get(self, family, weight="Regular", size=46):
        """获取 ImageFont 对象（带缓存）"""
        ...

    def list_families(self):
        """列出所有可用字体家族"""
        ...

    def list_weights(self, family):
        """列出某字体所有可用字重"""
        ...

    def download_guide(self):
        """打印字体下载指引（免费商用字体的官方下载链接）"""
        ...

# 全局单例
font_manager = FontManager()
```

#### 字体名称映射（中文别名 → 文件匹配）

```python
FONT_ALIASES = {
    # 中文常用名 → 英文 family 名
    "思源黑体":    ["Source Han Sans SC", "Source Han Sans CN", "Noto Sans CJK SC"],
    "思源宋体":    ["Source Han Serif SC", "Source Han Serif CN", "Noto Serif CJK SC"],
    "阿里普惠体":  ["Alibaba PuHuiTi", "Alibaba Sans"],
    "站酷高端黑":  ["ZCOOL GaoDuanHei", "站酷高端黑"],
    "站酷酷黑":    ["ZCOOL KuHei", "站酷酷黑"],
    "站酷快乐体":  ["ZCOOL KuaiLeTi", "站酷快乐体"],
    "站酷文艺体":  ["ZCOOL WenYiTi", "站酷文艺体"],
    "OPPO Sans":  ["OPPO Sans"],
    "鸿蒙字体":    ["HarmonyOS Sans SC", "HarmonyOS Sans"],
    # 系统字体
    "微软雅黑":    ["Microsoft YaHei", "msyh"],
    "黑体":        ["SimHei", "黑体"],
    "宋体":        ["SimSun", "宋体"],
}
```

### 3.3 花字模板系统 `huazi_templates.py`

```python
# 花字模板 = 渲染层栈

HUAZI_TEMPLATES = {
    # ============ A类：描边系 ============
    "stroke-white": {
        "name": "经典白描边",
        "category": "描边系",
        "tags": ["通用", "标题", "数字"],
        "layers": [
            # 从底到顶排列
            {"type": "stroke",   "color": "#222222", "width": 6},           # 底层：深灰厚描边
            {"type": "stroke",   "color": "#FFFFFF", "width": 3},           # 中层：白描边
            {"type": "fill",     "color": "accent"},                        # 顶层：正文（用模板强调色）
        ],
    },

    "stroke-neon": {
        "name": "荧光撞色",
        "category": "描边系",
        "tags": ["潮流", "时尚", "年轻"],
        "layers": [
            {"type": "stroke",   "color": "#FF00AA", "width": 4},
            {"type": "stroke",   "color": "#FFFFFF", "width": 2},
            {"type": "fill",     "color": "accent"},
        ],
    },

    "stroke-emboss": {
        "name": "立体浮雕",
        "category": "描边系",
        "tags": ["高端", "质感"],
        "layers": [
            {"type": "shadow",   "color": "#00000066", "offset": (3, 3), "blur": 4},
            {"type": "stroke",   "color": "#FFFFFF44", "width": 2},
            {"type": "fill",     "color": "accent"},
        ],
    },

    # ============ B类：光影系 ============
    "glow-neon": {
        "name": "霓虹发光",
        "category": "光影系",
        "tags": ["科技", "赛博", "强调"],
        "layers": [
            {"type": "glow",     "color": "accent", "radius": 12, "opacity": 0.6},
            {"type": "glow",     "color": "#FFFFFF", "radius": 4, "opacity": 0.3},
            {"type": "fill",     "color": "#FFFFFF"},
        ],
    },

    "glow-metal": {
        "name": "金属渐变",
        "category": "光影系",
        "tags": ["高端", "商务", "财经"],
        "layers": [
            {"type": "gradient", "colors": ["#FFD700", "#FFF8DC", "#DAA520"], "direction": "vertical"},
            {"type": "shadow",   "color": "#8B691400", "offset": (1, 1), "blur": 0},
            {"type": "stroke",   "color": "#B8860B", "width": 1},
        ],
    },

    "glow-ambient": {
        "name": "氛围光晕",
        "category": "光影系",
        "tags": ["柔和", "暖心", "生活"],
        "layers": [
            {"type": "glow",     "color": "accent", "radius": 20, "opacity": 0.5},
            {"type": "stroke",   "color": "#FFFFFF", "width": 2},
            {"type": "fill",     "color": "accent"},
        ],
    },

    # ============ C类：底衬系 ============
    "badge-rounded": {
        "name": "圆角标签",
        "category": "底衬系",
        "tags": ["标签", "角标", "参数"],
        "layers": [
            {"type": "badge",    "shape": "rounded", "color": "accent", "padding": 12, "radius": 8},
            {"type": "shadow",   "color": "#00000033", "offset": (0, 2), "blur": 6},
            {"type": "fill",     "color": "#FFFFFF"},
        ],
    },

    "badge-ribbon": {
        "name": "镂空绶带",
        "category": "底衬系",
        "tags": ["促销", "限时", "角标"],
        "layers": [
            {"type": "badge",    "shape": "parallelogram", "color": "accent", "padding": 10},
            {"type": "shadow",   "color": "#00000040", "offset": (2, 2), "blur": 4},
            {"type": "fill",     "color": "#FFFFFF"},
        ],
    },

    "badge-burst": {
        "name": "爆炸贴纸",
        "category": "底衬系",
        "tags": ["强调", "爆炸", "促销"],
        "layers": [
            {"type": "badge",    "shape": "burst", "color": "accent", "padding": 16},
            {"type": "stroke",   "color": "#FFFFFF", "width": 3},
            {"type": "fill",     "color": "#FFFFFF"},
        ],
    },

    # ============ D类：3D/立体系 ============
    "3d-long-shadow": {
        "name": "长投影",
        "category": "3D系",
        "tags": ["科技", "力量", "标题"],
        "layers": [
            {"type": "long_shadow", "color": "#00000066", "length": 12, "angle": 135},
            {"type": "fill",       "color": "accent"},
        ],
    },

    "3d-extrude": {
        "name": "3D挤出",
        "category": "3D系",
        "tags": ["重磅", "冲击", "标题"],
        "layers": [
            {"type": "extrude", "color": "darken(accent, 40%)", "depth": 8},
            {"type": "fill",    "color": "accent"},
        ],
    },

    "3d-double-exposure": {
        "name": "双重曝光",
        "category": "3D系",
        "tags": ["艺术", "时尚", "文艺"],
        "layers": [
            {"type": "copy",    "offset": (4, 0), "opacity": 0.4, "blend": "screen"},
            {"type": "fill",    "color": "accent"},
        ],
    },
}
```

### 3.4 花字渲染引擎 `huazi_engine.py`

```python
class HuaziRenderer:
    """花字多层渲染器 —— 将模板描述翻译为 PIL 绘制指令"""

    def __init__(self, font_manager):
        self.fm = font_manager

    def render(self, base, text, template_name, x, y,
               font_family=None, font_size=46,
               accent_color=None, bg_color=None, t=None):
        """
        在 base 画布上渲染花字

        参数:
          base: PIL Image (RGBA) 画布
          text: 文字内容
          template_name: 花字模板名 (如 "stroke-white")
          x, y: 文字左上角坐标
          font_family: 字体家族（None=使用当前模板默认）
          font_size: 字号
          accent_color: 覆盖模板中的 "accent" 颜色引用
          bg_color: 覆盖背景色引用
          t: 模板配置对象（用于获取强调色等）
        """
        template = HUAZI_TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"未知花字模板: {template_name}")

        # 解析颜色引用
        color_ctx = {
            "accent": accent_color or (235, 40, 45),
            "bg": bg_color or (10, 10, 12),
            "white": (255, 255, 255),
        }

        # 获取字体
        font = self.fm.get(font_family or "思源黑体", "Bold", font_size)

        # 逐层渲染（从底到顶）
        for layer in template["layers"]:
            self._render_layer(base, text, font, x, y, layer, color_ctx)

        return base

    def _render_layer(self, base, text, font, x, y, layer, color_ctx):
        """渲染单个图层"""
        ltype = layer["type"]
        color = self._resolve_color(layer.get("color"), color_ctx)

        if ltype == "fill":
            ImageDraw.Draw(base).text((x, y), text, fill=color, font=font)

        elif ltype == "stroke":
            width = layer.get("width", 3)
            self._render_stroke_layer(base, text, font, x, y, color, width)

        elif ltype == "glow":
            radius = layer.get("radius", 8)
            opacity = layer.get("opacity", 0.6)
            self._render_glow_layer(base, text, font, x, y, color, radius, opacity)

        elif ltype == "shadow":
            offset = layer.get("offset", (2, 2))
            blur = layer.get("blur", 4)
            self._render_shadow_layer(base, text, font, x, y, color, offset, blur)

        elif ltype == "gradient":
            colors = [self._resolve_color(c, color_ctx) for c in layer.get("colors", [])]
            direction = layer.get("direction", "vertical")
            self._render_gradient_fill(base, text, font, x, y, colors, direction)

        elif ltype == "long_shadow":
            length = layer.get("length", 10)
            angle = layer.get("angle", 135)
            self._render_long_shadow(base, text, font, x, y, color, length, angle)

        elif ltype == "extrude":
            depth = layer.get("depth", 6)
            self._render_extrude(base, text, font, x, y, color, depth)

        elif ltype == "copy":
            offset = layer.get("offset", (4, 0))
            opacity = layer.get("opacity", 0.5)
            self._render_copy_layer(base, text, font, x, y, color, offset, opacity)

        elif ltype == "badge":
            shape = layer.get("shape", "rounded")
            padding = layer.get("padding", 10)
            radius = layer.get("radius", 8)
            self._render_badge_bg(base, text, font, x, y, color, shape, padding, radius)

    def _resolve_color(self, color_spec, ctx):
        """解析颜色引用 → RGB/RGBA tuple"""
        if isinstance(color_spec, (tuple, list)):
            return tuple(color_spec)
        if color_spec is None:
            return (255, 255, 255)
        if color_spec.startswith("#"):
            return self._hex_to_rgb(color_spec)
        if color_spec in ctx:
            return ctx[color_spec]
        return (255, 255, 255)  # fallback
```

### 3.5 CLI 扩展

```bash
# ======== 字体选择 ========

# 列出可用字体
python scripts/generate_cover.py --list-fonts

# 指定字体家族
python scripts/generate_cover.py \
    --font-family "思源黑体" --font-weight Bold \
    --title "**RTX 5090**深度评测"

# 指定自定义字体文件
python scripts/generate_cover.py \
    --font-file "D:/fonts/zhanku-gaoduanhei.ttf" \
    --title "性能怪兽"

# ======== 字号 ========
python scripts/generate_cover.py \
    --title-size 52 --subtitle-size 28 --specs-size 32

# ======== 花字模板 ========

# 列出所有花字模板
python scripts/generate_cover.py --list-huazi

# 标题使用花字
python scripts/generate_cover.py \
    --title "**RTX 5090**深度评测" \
    --title-huazi stroke-white     # ★ 标题套用花字模板

# 数字/价格使用花字
python scripts/generate_cover.py \
    --price "¥8999" \
    --price-huazi glow-neon        # ★ 价格套用花字模板

# 角标使用花字
python scripts/generate_cover.py \
    --corner-badge "HOT" \
    --badge-huazi badge-burst

# 标签使用花字
python scripts/generate_cover.py \
    --tags "显卡" "评测" "首发" \
    --tags-huazi badge-rounded

# ======== 全局花字 ========
python scripts/generate_cover.py \
    --title "性能怪兽" \
    --huazi-preset stroke-white    # ★ 整个封面统一花字预设
```

### 3.6 富文本 × 花字 结合

在富文本标记中直接指定花字模板：

```
扩展语法：
  **text**              → 使用默认花字（当前模板默认）
  **text|stroke-white** → 使用指定花字模板
  !!price|glow-neon!!   → 发光花字
  ==tag|badge-rounded== → 底衬花字
```

或者通过命令行参数更简洁地控制：

```bash
# 标题的 **强调** 部分用撞色花字
python scripts/generate_cover.py \
    --title "**RTX 5090|stroke-neon**深度评测" \
    --default-huazi stroke-white
```

---

## 四、实现阶段

### Phase 1：字体管理器（优先级：高）

**文件**：`scripts/font_manager.py`

- [ ] 字体目录扫描（内置 `fonts/` + 系统目录）
- [ ] 字体元数据解析（family, weight, style）
- [ ] 字体注册表 `{family: {weight: path}}`
- [ ] `--list-fonts` CLI 命令
- [ ] `--font-family` / `--font-weight` / `--font-file` CLI 参数
- [ ] 字体缓存（避免重复加载）
- [ ] 下载指引文档 `fonts/README.md`

**内置字体**（2 款，打包进技能目录）：
- 思源黑体 Bold（标题首选，26MB）
- 阿里巴巴普惠体 Bold（副标题/正文，11MB）

### Phase 2：花字引擎（优先级：高）

**文件**：`scripts/huazi_templates.py` + `scripts/huazi_engine.py`

- [ ] 12 种花字模板定义（A1-D3）
- [ ] 多层渲染引擎（fill / stroke / glow / shadow / gradient / badge / extrude / long_shadow / copy）
- [ ] 颜色引用解析（accent / bg / white / #hex → RGB）
- [ ] `--list-huazi` CLI 命令
- [ ] `--title-huazi` / `--price-huazi` / `--tags-huazi` / `--badge-huazi` CLI 参数

### Phase 3：集成（优先级：中）

- [ ] 富文本标记扩展（`**text|huazi**` 语法）
- [ ] `--huazi-preset` 全局预设
- [ ] 花字自动适配模板（暗底模板自动启用 white-stroke，亮底自动适配 dark-stroke）
- [ ] `generate_cover()` 集成

### Phase 4：字体下载工具（优先级：低）

- [ ] `python scripts/install_fonts.py` 交互式字体下载器
- [ ] 一键下载免费商用字体（从官方源）
- [ ] 字体管理界面

---

## 五、花字智能匹配规则

根据封面模板自动选择花字：

| 模板背景 | 推荐花字 |
|----------|---------|
| dark（暗黑） | `stroke-white` — 白描边在暗底最清晰 |
| dark_blue（暗蓝） | `glow-neon` — 霓虹发光与科技感匹配 |
| bright（亮色） | `stroke-neon` — 撞色描边在亮底突出 |
| warm_tech（暖暗） | `glow-metal` — 金属渐变与暖色协调 |
| luxury（奢华黑金） | `glow-metal` — 金色金属渐变 |
| academic（学术蓝白） | `stroke-emboss` — 浮雕干净专业 |
| navy_gold（藏蓝金） | `stroke-white` 或 `glow-metal` |

---

## 六、与现有系统的兼容

| 现有功能 | 兼容方式 |
|----------|---------|
| 富文本 `**text**` | 内部自动桥接到花字引擎的默认模板 |
| `_render_rich_title()` | 逐段调用花字引擎（每段可独立指定模板） |
| `_render_text_stroke()` | 被花字引擎的 `stroke` 图层替代 |
| `_render_text_glow()` | 被花字引擎的 `glow` 图层替代 |
| `_render_text_block()` | 被花字引擎的 `badge` 图层替代 |
| 现有 CLI 参数 | 完全保留，花字参数为可选增量 |

---

## 七、风险评估

| 风险 | 缓解措施 |
|------|---------|
| 字体文件体积大（思源黑体 26MB） | 只内置 Bold 字重，其余引导用户安装 |
| 花字渲染性能 | 缓存渲染层，避免重复创建临时 Image |
| 字体版权 | 仅内置 SIL OFL / 明确免费商用字体 |
| 向后兼容 | 所有新参数可选，旧命令无需修改 |
| 中文字符缺失（部分字体缺字） | 自动回退到思源黑体（全覆盖） |
