# -*- coding: utf-8 -*-
"""
封面生成器 v3.1 — 多品类模板引擎
基于 6 张真实抖音爆款封面的逐像素分析，提炼为跨品类可复用的设计公式

v3.1:  布局重构 — 文字在上/图片在下（匹配 5/6 爆款封面），新增 4 种排版模式
v3.0:  品类架构（科技/教育/美食/旅游/时尚/财经），一键切换
v2.1:  多图排版引擎（投影/背光/倒影/横评布局）
v2.0:  富文本引擎（**强调** / __斜体__ / ==色块== / !!发光!! / ~~描边~~）

用法:
  # 科技类（默认）
  python generate_cover.py --template dark --title "**跑分150万**的秘密"

  # 教育类
  python generate_cover.py --category education --template academic \
      --title "**3分钟**搞懂区块链" --subtitle "小白也能听明白"

  # 美食类
  python generate_cover.py --category food --template warm_dark \
      --title "**人均50**吃到撑" --image dish.png --image-glow backlight

  # 旅游类
  python generate_cover.py --category travel --template nature \
      --title "**此生必去**的5个地方" --image scenic.png

  # 时尚类
  python generate_cover.py --category fashion --template luxury \
      --title "**2026秋冬**必备单品" --image outfit.png --image-glow both

  # 财经类
  python generate_cover.py --category business --template navy_gold \
      --title "**年化15%**的真相" --specs "收益:15.2%" "风险:中" "门槛:1000"

依赖: pip install Pillow numpy
"""

import argparse
import math
import os
import re
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

# ★ v4.0: 字体管理器 + 花字引擎
from font_manager import get_font_manager, font as _get_font
from huazi_engine import get_huazi_renderer, render_huazi
from huazi_templates import (
    HUAZI_TEMPLATES, DEFAULT_HUAZI, list_huazi,
    resolve_huazi_for_target, resolve_huazi_for_template, HUAZI_TARGET_MAP
)

# ============================================================
# 基础常量
# ============================================================

CANVAS_SIZE = (1200, 1600)  # 3:4 竖屏，高分辨率
SCALE = CANVAS_SIZE[0] / 540  # ≈ 2.222 — 等比缩放因子（原 540×720 → 1200×1600）

def _s(v):
    """等比缩放像素值（540→1200）"""
    return int(v * SCALE)

# ============================================================
# ★ 多品类模板注册表 v3.0
# ============================================================

CATEGORIES = {
    "tech": {
        "label": "科技数码",
        "description": "暗色科技感、红/金强调、数据驱动",
        "templates": {
            "dark": {
                "name": "极致暗黑 — 产品首发",
                "bg_color": (10, 10, 12),
                "bg_accent": (28, 28, 38),
                "text_primary": (240, 240, 245),
                "text_secondary": (170, 170, 180),
                "accent": (235, 42, 46),
                "accent_alt": (55, 200, 80),
                "tag_bg": (38, 38, 48),
                "tag_text": (215, 215, 225),
                "divider": (55, 55, 65),
                "glow_color": (235, 40, 45),
                "stroke_color": (0, 0, 0),
                "block_bg": (42, 15, 18),
                "block_text": (255, 200, 200),
                "shadow_color": (0, 0, 0),
                "backlight_color": (235, 40, 45),
                "is_dark": True,
            },
            "dark_blue": {
                "name": "暗蓝冷调 — 芯片/技术",
                "bg_color": (8, 10, 28),
                "bg_accent": (18, 22, 50),
                "text_primary": (235, 240, 250),
                "text_secondary": (155, 170, 200),
                "accent": (255, 195, 40),
                "accent_alt": (50, 185, 225),
                "tag_bg": (22, 28, 55),
                "tag_text": (195, 205, 235),
                "divider": (38, 42, 68),
                "glow_color": (255, 195, 40),
                "stroke_color": (0, 0, 10),
                "block_bg": (40, 35, 15),
                "block_text": (255, 235, 180),
                "shadow_color": (0, 0, 8),
                "backlight_color": (255, 195, 40),
                "is_dark": True,
            },
            "bright": {
                "name": "清新亮色 — 横评推荐",
                "bg_color": (248, 244, 236),
                "bg_accent": (255, 252, 245),
                "text_primary": (18, 18, 22),
                "text_secondary": (110, 105, 100),
                "accent": (228, 58, 32),
                "accent_alt": (18, 142, 185),
                "tag_bg": (232, 226, 216),
                "tag_text": (65, 60, 55),
                "divider": (210, 204, 194),
                "glow_color": (228, 58, 32),
                "stroke_color": (255, 255, 255),
                "block_bg": (255, 235, 225),
                "block_text": (180, 40, 20),
                "shadow_color": (180, 175, 170),
                "backlight_color": (228, 58, 32),
                "is_dark": False,
            },
            "warm_tech": {
                "name": "暖色横评 — 器材/影音",
                "bg_color": (26, 22, 28),
                "bg_accent": (36, 30, 40),
                "text_primary": (245, 240, 230),
                "text_secondary": (185, 175, 165),
                "accent": (255, 142, 30),
                "accent_alt": (255, 200, 60),
                "tag_bg": (48, 40, 46),
                "tag_text": (215, 205, 195),
                "divider": (52, 46, 50),
                "glow_color": (255, 142, 30),
                "stroke_color": (10, 5, 5),
                "block_bg": (55, 30, 15),
                "block_text": (255, 210, 170),
                "shadow_color": (8, 5, 3),
                "backlight_color": (255, 142, 30),
                "is_dark": True,
            },
        },
    },

    "education": {
        "label": "教育知识",
        "description": "干净明亮、蓝/白学术调、高信任感",
        "templates": {
            "academic": {
                "name": "学术蓝白 — 知识科普",
                "bg_color": (245, 248, 252),
                "bg_accent": (235, 242, 252),
                "text_primary": (15, 25, 45),
                "text_secondary": (90, 105, 130),
                "accent": (30, 100, 200),
                "accent_alt": (255, 140, 30),
                "tag_bg": (225, 235, 248),
                "tag_text": (40, 70, 130),
                "divider": (200, 210, 225),
                "glow_color": (30, 100, 200),
                "stroke_color": (255, 255, 255),
                "block_bg": (220, 235, 255),
                "block_text": (20, 65, 160),
                "shadow_color": (180, 185, 195),
                "backlight_color": (30, 100, 200),
                "is_dark": False,
            },
            "chalkboard": {
                "name": "黑板粉笔 — 教学讲解",
                "bg_color": (25, 35, 28),
                "bg_accent": (32, 44, 34),
                "text_primary": (235, 240, 225),
                "text_secondary": (170, 180, 160),
                "accent": (255, 220, 80),
                "accent_alt": (255, 150, 60),
                "tag_bg": (38, 52, 40),
                "tag_text": (210, 225, 195),
                "divider": (55, 70, 58),
                "glow_color": (255, 220, 80),
                "stroke_color": (15, 22, 18),
                "block_bg": (50, 65, 42),
                "block_text": (240, 250, 220),
                "shadow_color": (10, 15, 12),
                "backlight_color": (255, 220, 80),
                "is_dark": True,
            },
            "clean": {
                "name": "极简白 — 干货分享",
                "bg_color": (252, 252, 250),
                "bg_accent": (248, 248, 244),
                "text_primary": (20, 20, 22),
                "text_secondary": (130, 130, 125),
                "accent": (220, 60, 40),
                "accent_alt": (40, 150, 120),
                "tag_bg": (240, 240, 235),
                "tag_text": (80, 80, 75),
                "divider": (225, 225, 220),
                "glow_color": (220, 60, 40),
                "stroke_color": (255, 255, 255),
                "block_bg": (255, 240, 235),
                "block_text": (180, 45, 30),
                "shadow_color": (200, 200, 195),
                "backlight_color": (220, 60, 40),
                "is_dark": False,
            },
        },
    },

    "food": {
        "label": "美食餐饮",
        "description": "暖色食欲、橙红棕、烟火气",
        "templates": {
            "warm_dark": {
                "name": "暖暗食欲 — 探店打卡",
                "bg_color": (22, 16, 12),
                "bg_accent": (35, 25, 18),
                "text_primary": (250, 240, 225),
                "text_secondary": (200, 180, 160),
                "accent": (255, 120, 30),
                "accent_alt": (255, 200, 50),
                "tag_bg": (45, 32, 22),
                "tag_text": (230, 210, 185),
                "divider": (60, 45, 32),
                "glow_color": (255, 120, 30),
                "stroke_color": (10, 5, 3),
                "block_bg": (60, 30, 15),
                "block_text": (255, 220, 180),
                "shadow_color": (5, 3, 2),
                "backlight_color": (255, 120, 30),
                "is_dark": True,
            },
            "bright_eat": {
                "name": "明亮食欲 — 教程菜谱",
                "bg_color": (255, 250, 242),
                "bg_accent": (255, 248, 235),
                "text_primary": (35, 22, 15),
                "text_secondary": (140, 110, 90),
                "accent": (235, 80, 25),
                "accent_alt": (50, 170, 90),
                "tag_bg": (255, 240, 225),
                "tag_text": (120, 70, 40),
                "divider": (235, 220, 205),
                "glow_color": (235, 80, 25),
                "stroke_color": (255, 255, 255),
                "block_bg": (255, 225, 200),
                "block_text": (200, 60, 20),
                "shadow_color": (210, 195, 180),
                "backlight_color": (235, 80, 25),
                "is_dark": False,
            },
            "rustic": {
                "name": "复古暖调 — 传统美食",
                "bg_color": (40, 28, 18),
                "bg_accent": (52, 36, 24),
                "text_primary": (245, 235, 215),
                "text_secondary": (195, 175, 150),
                "accent": (220, 140, 40),
                "accent_alt": (180, 80, 30),
                "tag_bg": (58, 40, 26),
                "tag_text": (225, 205, 175),
                "divider": (70, 50, 34),
                "glow_color": (220, 140, 40),
                "stroke_color": (18, 10, 5),
                "block_bg": (70, 38, 18),
                "block_text": (255, 220, 170),
                "shadow_color": (10, 6, 3),
                "backlight_color": (220, 140, 40),
                "is_dark": True,
            },
        },
    },

    "travel": {
        "label": "旅游出行",
        "description": "自然蓝绿、日落暖橙、开阔感",
        "templates": {
            "nature": {
                "name": "自然风光 — 景点推荐",
                "bg_color": (235, 245, 240),
                "bg_accent": (225, 242, 235),
                "text_primary": (15, 40, 30),
                "text_secondary": (90, 120, 105),
                "accent": (20, 150, 100),
                "accent_alt": (255, 160, 40),
                "tag_bg": (215, 235, 222),
                "tag_text": (40, 90, 65),
                "divider": (195, 215, 200),
                "glow_color": (20, 150, 100),
                "stroke_color": (255, 255, 255),
                "block_bg": (210, 240, 220),
                "block_text": (15, 110, 70),
                "shadow_color": (195, 205, 198),
                "backlight_color": (20, 150, 100),
                "is_dark": False,
            },
            "sunset": {
                "name": "日落暖橙 — 旅行Vlog",
                "bg_color": (30, 22, 18),
                "bg_accent": (42, 30, 24),
                "text_primary": (248, 238, 220),
                "text_secondary": (200, 180, 155),
                "accent": (255, 155, 50),
                "accent_alt": (255, 100, 80),
                "tag_bg": (48, 34, 26),
                "tag_text": (225, 200, 170),
                "divider": (62, 46, 36),
                "glow_color": (255, 155, 50),
                "stroke_color": (12, 8, 5),
                "block_bg": (60, 35, 18),
                "block_text": (255, 210, 160),
                "shadow_color": (8, 5, 3),
                "backlight_color": (255, 155, 50),
                "is_dark": True,
            },
            "aerial": {
                "name": "航拍蓝白 — 攻略合集",
                "bg_color": (240, 246, 252),
                "bg_accent": (232, 242, 250),
                "text_primary": (18, 35, 55),
                "text_secondary": (100, 125, 150),
                "accent": (15, 130, 200),
                "accent_alt": (255, 180, 30),
                "tag_bg": (222, 238, 250),
                "tag_text": (35, 80, 140),
                "divider": (200, 218, 235),
                "glow_color": (15, 130, 200),
                "stroke_color": (255, 255, 255),
                "block_bg": (215, 235, 252),
                "block_text": (12, 95, 170),
                "shadow_color": (190, 200, 215),
                "backlight_color": (15, 130, 200),
                "is_dark": False,
            },
        },
    },

    "fashion": {
        "label": "时尚美妆",
        "description": "奢华黑金、清冷极简、活力撞色",
        "templates": {
            "luxury": {
                "name": "奢华黑金 — 穿搭/奢侈品",
                "bg_color": (12, 10, 14),
                "bg_accent": (28, 24, 32),
                "text_primary": (242, 238, 230),
                "text_secondary": (180, 170, 160),
                "accent": (215, 175, 65),
                "accent_alt": (200, 160, 100),
                "tag_bg": (35, 30, 38),
                "tag_text": (225, 215, 195),
                "divider": (52, 46, 55),
                "glow_color": (215, 175, 65),
                "stroke_color": (5, 3, 6),
                "block_bg": (50, 38, 22),
                "block_text": (240, 215, 150),
                "shadow_color": (3, 2, 4),
                "backlight_color": (215, 175, 65),
                "is_dark": True,
            },
            "clean_girl": {
                "name": "清冷极简 — 美妆护肤",
                "bg_color": (248, 246, 244),
                "bg_accent": (252, 250, 248),
                "text_primary": (30, 28, 32),
                "text_secondary": (155, 150, 148),
                "accent": (200, 130, 160),
                "accent_alt": (160, 180, 200),
                "tag_bg": (240, 236, 234),
                "tag_text": (100, 90, 95),
                "divider": (225, 222, 220),
                "glow_color": (200, 130, 160),
                "stroke_color": (255, 255, 255),
                "block_bg": (248, 235, 242),
                "block_text": (170, 90, 130),
                "shadow_color": (210, 205, 203),
                "backlight_color": (200, 130, 160),
                "is_dark": False,
            },
            "vibrant": {
                "name": "活力撞色 — 潮流/探店",
                "bg_color": (245, 240, 250),
                "bg_accent": (250, 242, 252),
                "text_primary": (25, 15, 35),
                "text_secondary": (130, 115, 135),
                "accent": (240, 60, 120),
                "accent_alt": (120, 40, 200),
                "tag_bg": (238, 230, 245),
                "tag_text": (90, 60, 120),
                "divider": (220, 212, 230),
                "glow_color": (240, 60, 120),
                "stroke_color": (255, 255, 255),
                "block_bg": (250, 225, 240),
                "block_text": (200, 40, 100),
                "shadow_color": (210, 200, 215),
                "backlight_color": (240, 60, 120),
                "is_dark": False,
            },
        },
    },

    "business": {
        "label": "财经商业",
        "description": "藏蓝金、数据仪表、专业权威",
        "templates": {
            "navy_gold": {
                "name": "藏蓝金 — 投资理财",
                "bg_color": (10, 15, 30),
                "bg_accent": (18, 25, 48),
                "text_primary": (238, 242, 250),
                "text_secondary": (155, 170, 200),
                "accent": (220, 180, 45),
                "accent_alt": (50, 200, 180),
                "tag_bg": (22, 30, 55),
                "tag_text": (200, 210, 235),
                "divider": (38, 46, 70),
                "glow_color": (220, 180, 45),
                "stroke_color": (3, 5, 12),
                "block_bg": (35, 30, 15),
                "block_text": (240, 215, 150),
                "shadow_color": (2, 4, 10),
                "backlight_color": (220, 180, 45),
                "is_dark": True,
            },
            "white_paper": {
                "name": "白皮书 — 行业分析",
                "bg_color": (250, 251, 252),
                "bg_accent": (245, 248, 252),
                "text_primary": (18, 22, 35),
                "text_secondary": (110, 118, 135),
                "accent": (25, 85, 180),
                "accent_alt": (220, 150, 30),
                "tag_bg": (235, 240, 248),
                "tag_text": (40, 65, 120),
                "divider": (215, 220, 230),
                "glow_color": (25, 85, 180),
                "stroke_color": (255, 255, 255),
                "block_bg": (228, 238, 252),
                "block_text": (18, 60, 150),
                "shadow_color": (195, 200, 210),
                "backlight_color": (25, 85, 180),
                "is_dark": False,
            },
            "dark_data": {
                "name": "暗色数据 — 财报解读",
                "bg_color": (8, 10, 18),
                "bg_accent": (16, 20, 35),
                "text_primary": (235, 238, 245),
                "text_secondary": (150, 160, 185),
                "accent": (60, 210, 150),
                "accent_alt": (255, 190, 40),
                "tag_bg": (20, 26, 42),
                "tag_text": (195, 205, 225),
                "divider": (35, 40, 60),
                "glow_color": (60, 210, 150),
                "stroke_color": (2, 3, 8),
                "block_bg": (18, 40, 28),
                "block_text": (180, 240, 200),
                "shadow_color": (2, 2, 5),
                "backlight_color": (60, 210, 150),
                "is_dark": True,
            },
        },
    },
}

# 向后兼容别名
TEMPLATE_ALIASES = {
    "dark": ("tech", "dark"),
    "dark_blue": ("tech", "dark_blue"),
    "bright": ("tech", "bright"),
    "warm_tech": ("tech", "warm_tech"),
}


def resolve_template(category, template_name):
    """解析品类+模板名 → 模板配置"""
    # 别名优先
    if template_name in TEMPLATE_ALIASES and category == "tech":
        cat, tname = TEMPLATE_ALIASES[template_name]
        return CATEGORIES[cat]["templates"][tname], cat, tname

    if category in CATEGORIES:
        cat_templates = CATEGORIES[category]["templates"]
        if template_name in cat_templates:
            return cat_templates[template_name], category, template_name
        # 如果没找到，返回该类别的第一个模板
        first = next(iter(cat_templates.values()))
        print(f"[WARN] 模板 '{template_name}' 在 '{category}' 中不存在，使用默认模板")
        return first, category, next(iter(cat_templates.keys()))

    # 完全回退
    print(f"[WARN] 品类 '{category}' 不存在，回退到 tech.dark")
    return CATEGORIES["tech"]["templates"]["dark"], "tech", "dark"


# ============================================================
# 字体发现
# ============================================================

FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/STZHONGS.TTF",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

BOLD_FONT_PATHS = [
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
] + FONT_PATHS


def _find_font(bold=False):
    for p in (BOLD_FONT_PATHS if bold else FONT_PATHS):
        if os.path.exists(p):
            return p
    return None


def _font(size, bold=False, family=None, weight=None):
    """获取字体 — v4.0: 通过字体管理器（支持多字体家族+字重）"""
    fm = get_font_manager()
    if weight:
        return fm.get(family=family, weight=weight, size=size)
    if bold:
        return fm.get(family=family, weight="Bold", size=size)
    return fm.get(family=family, weight="Regular", size=size)


# ★ v4.0: 全局字体配置（可在 generate_cover 中覆盖）
_FONT_FAMILY = None       # 默认字体家族
_FONT_WEIGHT_TITLE = "Bold"
_FONT_WEIGHT_BODY = "Regular"
_TITLE_SIZE = int(46 * SCALE)     # ≈ 102
_SUBTITLE_SIZE = int(26 * SCALE)  # ≈ 58

# ★ v4.0: 全局花字配置
_HUAZI_TITLE = None      # None=自动匹配模板
_HUAZI_SUBTITLE = None
_HUAZI_PRICE = None
_HUAZI_BADGE = None
_HUAZI_TAGS = None
_HUAZI_SPECS_VAL = None


# ============================================================
# 富文本解析器
# ============================================================

TOKEN_PATTERN = re.compile(
    r'(\*\*(.+?)\*\*|'
    r'__(.+?)__|'
    r'==(.+?)==|'
    r'!!(.+?)!!|'
    r'~~(.+?)~~|'
    r'``(.+?)``)'
)


def parse_rich_text(text):
    if not text:
        return []
    segments, last_end = [], 0
    for m in TOKEN_PATTERN.finditer(text):
        if m.start() > last_end:
            plain = text[last_end:m.start()]
            if plain:
                segments.append((plain, {}))
        if m.group(2):
            segments.append((m.group(2), {'accent': True, 'bold': True}))
        elif m.group(3):
            segments.append((m.group(3), {'secondary': True, 'slant': True}))
        elif m.group(4):
            segments.append((m.group(4), {'block': True, 'bold': True}))
        elif m.group(5):
            segments.append((m.group(5), {'glow': True, 'bold': True}))
        elif m.group(6):
            segments.append((m.group(6), {'stroke_only': True, 'bold': True}))
        elif m.group(7):
            segments.append((m.group(7), {'invert': True}))
        last_end = m.end()
    if last_end < len(text):
        segments.append((text[last_end:], {}))
    return segments if segments else [(text, {})]


# ============================================================
# 文字渲染引擎
# ============================================================

def _text_size(text, font):
    bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _render_text_stroke(base, xy, text, font, fill_color, stroke_color, stroke_width=None):
    if stroke_width is None:
        stroke_width = int(3 * SCALE)
    x, y = xy
    draw = ImageDraw.Draw(base)
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, fill=stroke_color, font=font)
    draw.text((x, y), text, fill=fill_color, font=font)


def _render_text_glow(base, xy, text, font, fill_color, glow_color, glow_radius=None):
    if glow_radius is None:
        glow_radius = _s(8)
    x, y = xy
    tw, th = _text_size(text, font)
    pad = glow_radius * 2
    glow_layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(glow_layer).text((pad, pad), text, fill=glow_color, font=font)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(glow_radius))
    base.paste(glow_layer, (x - pad, y - pad), glow_layer)
    ImageDraw.Draw(base).text((x, y), text, fill=fill_color, font=font)


def _render_text_slant(base, xy, text, font, fill_color, angle=12):
    x, y = xy
    tw, th = _text_size(text, font)
    pad = abs(int(th * math.tan(math.radians(angle)))) + 5
    text_layer = Image.new("RGBA", (tw + pad, th + 10), (0, 0, 0, 0))
    ImageDraw.Draw(text_layer).text((0, 0), text, fill=fill_color, font=font)
    sheared = text_layer.transform(
        (text_layer.width, text_layer.height),
        Image.AFFINE, (1, math.tan(math.radians(angle)), 0, 0, 1, 0), Image.BICUBIC)
    base.paste(sheared, (x, y), sheared)


def _render_text_block(base, xy, text, font, fill_color, block_color, padding=None):
    if padding is None:
        padding = _s(8)
    x, y = xy
    tw, th = _text_size(text, font)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(
        [x - padding, y - padding // 2, x + tw + padding, y + th + padding // 2],
        radius=_s(6), fill=block_color)
    draw.text((x, y), text, fill=fill_color, font=font)


def _text_with_shadow(draw, xy, text, font, fill, shadow_color=(0, 0, 0), offset=None):
    if offset is None:
        offset = _s(2)
    x, y = xy
    draw.text((x + offset, y + offset), text, fill=shadow_color, font=font)
    draw.text((x, y), text, fill=fill, font=font)


def _render_rich_line(base, t, segments, x, y, base_font_size=None, line_spacing=None):
    if base_font_size is None:
        base_font_size = _s(46)
    if line_spacing is None:
        line_spacing = _s(56)
    draw = ImageDraw.Draw(base)
    cx = x
    for text, style in segments:
        if not text:
            continue
        accent = style.get('accent', False)
        secondary = style.get('secondary', False)
        bold = style.get('bold', False)
        slant = style.get('slant', False)
        block = style.get('block', False)
        glow = style.get('glow', False)
        stroke_only = style.get('stroke_only', False)
        invert = style.get('invert', False)

        size = base_font_size + (_s(2) if stroke_only else 0)
        font = _font(size, bold=bold or accent or glow)

        if accent:       fg = t["accent"]
        elif secondary:  fg = t["text_secondary"]
        elif invert:     fg = t["bg_color"]
        else:            fg = t["text_primary"]

        if glow:
            _render_text_glow(base, (cx, y), text, font, fg,
                            (*t["glow_color"], 180), glow_radius=_s(10))
            cx += _text_size(text, font)[0] + _s(6)
        elif stroke_only:
            _render_text_stroke(base, (cx, y), text, font, t["bg_color"],
                              t["accent"], stroke_width=_s(3))
            cx += _text_size(text, font)[0] + _s(6)
        elif block:
            _render_text_block(base, (cx, y), text, font,
                             t.get("block_text", (255, 255, 255)),
                             t.get("block_bg", t["accent"]), padding=_s(8))
            cx += _text_size(text, font)[0] + _s(16) + _s(6)
        elif slant:
            _render_text_slant(base, (cx, y), text, font, fg, angle=12)
            tw = _text_size(text, font)[0]
            th = _text_size(text, font)[1]
            pad = abs(int(th * math.tan(math.radians(12)))) + _s(5)
            cx += tw + pad + _s(4)
        else:
            if t.get("is_dark", True):
                if accent or secondary:
                    _render_text_stroke(base, (cx, y), text, font, fg,
                                      t["stroke_color"], stroke_width=_s(2))
                else:
                    _text_with_shadow(draw, (cx, y), text, font, fg,
                                    shadow_color=t["stroke_color"], offset=_s(2))
            else:
                draw.text((cx, y), text, fill=fg, font=font)
            cx += _text_size(text, font)[0] + _s(4)
    return cx


def _render_rich_title(draw, base, t, rich_title, y_start, huazi=None, font_family=None, font_size=None, align="left"):
    """渲染标题（v4.0: 支持花字）"""
    if font_size is None:
        font_size = _TITLE_SIZE
    if not rich_title:
        return y_start

    # ★ v4.3: 按 \n 拆分，每行独立 parse + textwrap
    raw_lines = rich_title.split('\n')
    all_rendered_lines = []  # [(line_text, list_of_segments), ...]
    for raw_line in raw_lines:
        if not raw_line.strip():
            continue
        segs = parse_rich_text(raw_line)
        line_text = ''.join(s[0] for s in segs)
        wrapped = textwrap.wrap(line_text, width=15) if line_text else ['']
        # 把 segs 分配到每个 wrapped 子行
        seg_idx = 0
        for wline in wrapped:
            wsegs, rem = [], len(wline)
            while rem > 0 and seg_idx < len(segs):
                st, ss = segs[seg_idx]
                if len(st) <= rem:
                    wsegs.append((st, ss)); rem -= len(st); seg_idx += 1
                else:
                    wsegs.append((st[:rem], ss)); segs[seg_idx] = (st[rem:], ss); rem = 0
            if wsegs:
                all_rendered_lines.append((wline, wsegs))

    # 确定花字
    effective_huazi = huazi or _HUAZI_TITLE
    if effective_huazi is None:
        effective_huazi = None

    cy = y_start
    for line_text, line_segs in all_rendered_lines:
        if not line_text.strip():
            continue

        has_bold = any(ss.get('accent') or ss.get('bold') or ss.get('glow') for _, ss in line_segs)
        use_huazi = effective_huazi and HUAZI_TEMPLATES.get(effective_huazi)

        if align == "center":
            if use_huazi:
                # ★ 方案B：花字先渲染到临时层，实测像素宽度，再居中
                tmp_w = base.width
                tmp_h = int(font_size * 2.5)
                tmp = Image.new("RGBA", (tmp_w, tmp_h), (0, 0, 0, 0))
                try:
                    hr = get_huazi_renderer()
                    hr.render(tmp, line_text, effective_huazi,
                             0, int(font_size * 0.3),
                             font_family=font_family or _FONT_FAMILY,
                             font_weight="Bold", font_size=font_size,
                             accent_color=t.get("accent"),
                             bg_color=t.get("bg_color"))
                    # 检测实际渲染像素的右边界
                    tmp_arr = np.array(tmp)
                    alpha = tmp_arr[:, :, 3]
                    col_alpha = np.max(alpha, axis=0)
                    nonzero = np.where(col_alpha > 10)[0]
                    actual_w = nonzero[-1] + 1 if len(nonzero) > 0 else tmp_w
                    line_x = max(0, (base.width - actual_w) // 2)
                except Exception:
                    tw = _text_size(line_text, _font(font_size, bold=has_bold, family=font_family))[0]
                    line_x = (base.width - tw) // 2
            else:
                # 非花字：_text_size 测量准确
                tw = _text_size(line_text, _font(font_size, bold=has_bold, family=font_family))[0]
                line_x = (base.width - tw) // 2
        else:
            line_x = _s(28)

        if use_huazi:
            try:
                hr = get_huazi_renderer()
                hr.render(base, line_text, effective_huazi,
                         line_x, cy,
                         font_family=font_family or _FONT_FAMILY,
                         font_weight="Bold" if has_bold else "Regular",
                         font_size=font_size,
                         accent_color=t.get("accent"),
                         bg_color=t.get("bg_color"))
            except Exception:
                _render_rich_line(base, t, line_segs, line_x, cy,
                                base_font_size=font_size)
        else:
            _render_rich_line(base, t, line_segs, line_x, cy,
                            base_font_size=font_size)

        cy += max(_s(56), int(font_size * 1.2))
    return cy + _s(12)


def _render_rich_subtitle(draw, base, t, rich_subtitle, y_start, huazi=None, font_family=None, font_size=None, align="left"):
    """渲染副标题（v4.0: 支持花字）"""
    if font_size is None:
        font_size = _SUBTITLE_SIZE
    if not rich_subtitle:
        return y_start

    # ★ v4.3: 按 \n 拆分，每行独立 parse + textwrap
    raw_lines = rich_subtitle.split('\n')
    all_rendered_lines = []
    for raw_line in raw_lines:
        if not raw_line.strip():
            continue
        segs = parse_rich_text(raw_line)
        line_text = ''.join(s[0] for s in segs)
        wrapped = textwrap.wrap(line_text, width=15) if line_text else ['']
        seg_idx = 0
        for wline in wrapped:
            wsegs, rem = [], len(wline)
            while rem > 0 and seg_idx < len(segs):
                st, ss = segs[seg_idx]
                if len(st) <= rem:
                    wsegs.append((st, ss)); rem -= len(st); seg_idx += 1
                else:
                    wsegs.append((st[:rem], ss)); segs[seg_idx] = (st[rem:], ss); rem = 0
            if wsegs:
                all_rendered_lines.append((wline, wsegs))
    cy = y_start

    effective_huazi = huazi or _HUAZI_SUBTITLE

    for line_text, line_segs in all_rendered_lines:
        if not line_text.strip():
            continue
        tw_line = _text_size(line_text, _font(font_size))[0]  # 不用 family，与花字一致
        if align == "center":
            line_x = (base.width - tw_line) // 2
        else:
            line_x = _s(28)

        if effective_huazi and HUAZI_TEMPLATES.get(effective_huazi):
            try:
                hr = get_huazi_renderer()
                hr.render(base, line_text, effective_huazi,
                         line_x, cy,
                         font_family=font_family or _FONT_FAMILY,
                         font_weight="Regular", font_size=font_size,
                         accent_color=t.get("text_secondary"),
                         bg_color=t.get("bg_color"))
            except Exception:
                _render_rich_line(base, t, line_segs, line_x, cy,
                                base_font_size=font_size)
        else:
            _render_rich_line(base, t, line_segs, line_x, cy,
                            base_font_size=font_size)

        cy += max(_s(36), int(font_size * 1.4))
    return cy + _s(10)


# ============================================================
# 装饰元素
# ============================================================

def _draw_glow_orb(draw, base, t, cx, cy, radius):
    glow = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    r, g, b = t["glow_color"]
    for i in range(5):
        ri = radius - i * (radius // 6)
        gd.ellipse([cx - ri, cy - ri, cx + ri, cy + ri],
                    fill=(r, g, b, max(0, 20 - i * 3)))
    base.paste(glow, (0, 0), glow)


def _draw_deco_ring(draw, base, t, cx, cy, r):
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([cx - r, cy - r, cx + r, cy + r],
               fill=(t["accent"][0], t["accent"][1], t["accent"][2], 12),
               outline=(t["accent"][0], t["accent"][1], t["accent"][2], 60), width=2)
    base.paste(overlay, (0, 0), overlay)


def _draw_accent_bar(draw, t, x, y, w, h=4):
    draw.rectangle([x, y, x + w, y + h], fill=t["accent"])


def _draw_rotated_badge(base, t, text, x, y, font_size=None, rotation=-15, huazi=None, font_family=None):
    if font_size is None:
        font_size = _s(18)
    font = _font(font_size, bold=True, family=font_family)
    bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = _s(12)
    badge = Image.new("RGBA", (tw + pad * 4, th + pad * 4), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)

    badge_huazi = huazi or _HUAZI_BADGE
    if badge_huazi and HUAZI_TEMPLATES.get(badge_huazi):
        try:
            hr = get_huazi_renderer()
            hr.render(badge, text, badge_huazi, pad * 2, pad * 2,
                     font_family=font_family or _FONT_FAMILY,
                     font_weight="Bold", font_size=font_size,
                     accent_color=(255, 255, 255),
                     bg_color=t["accent"])
        except Exception:
            bd.rounded_rectangle([pad, pad, tw + pad * 3, th + pad * 3],
                                 radius=_s(8), fill=t["accent"])
            bd.text((pad * 2, pad * 2), text, fill=(255, 255, 255), font=font)
    else:
        bd.rounded_rectangle([pad, pad, tw + pad * 3, th + pad * 3],
                             radius=_s(8), fill=t["accent"])
        bd.text((pad * 2, pad * 2), text, fill=(255, 255, 255), font=font)

    rotated = badge.rotate(rotation, expand=True, resample=Image.BICUBIC,
                           fillcolor=(0, 0, 0, 0))
    base.paste(rotated, (x - rotated.width // 2, y - rotated.height // 2), rotated)


# ============================================================
# 图片引擎 (v2.1)
# ============================================================

def _extract_alpha_mask(product):
    if product.mode == 'RGBA':
        return product.split()[3]
    return Image.new("L", product.size, 255)


def _add_product_shadow(base, product, pos, alpha_mask, t, shadow_opacity=120):
    pw, ph = product.size
    sox, soy = int(pw * 0.02), int(ph * 0.04)
    shadow = alpha_mask.copy()
    shadow_img = Image.new("L", (pw + abs(sox) * 2, ph + abs(soy) * 2), 0)
    shadow_img.paste(shadow, (abs(sox), abs(soy)))
    blur_r = max(pw, ph) // 40
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(blur_r))
    cm = blur_r * 2
    shadow_img = shadow_img.crop((max(0, abs(sox) - cm), max(0, abs(soy) - cm),
                                   min(shadow_img.width, pw + abs(sox) + cm),
                                   min(shadow_img.height, ph + abs(soy) + cm)))
    sc = t["shadow_color"]
    shadow_rgba = Image.new("RGBA", shadow_img.size, (0, 0, 0, 0))
    spx = shadow_rgba.load(); slx = shadow_img.load()
    for sy in range(shadow_img.height):
        for sx in range(shadow_img.width):
            a = min(slx[sx, sy], shadow_opacity)
            if a > 0:
                spx[sx, sy] = (sc[0], sc[1], sc[2], a)
    base.paste(shadow_rgba,
               (pos[0] - (shadow_img.width - pw) // 2 + sox,
                pos[1] - (shadow_img.height - ph) // 2 + soy), shadow_rgba)


def _add_product_backlight(base, product, pos, alpha_mask, t, intensity=80):
    pw, ph = product.size
    dr = max(_s(3), max(pw, ph) // 60)
    dilated = alpha_mask.filter(ImageFilter.MaxFilter(dr * 2 + 1))
    blur_r = max(pw, ph) // 25
    bl1 = dilated.filter(ImageFilter.GaussianBlur(blur_r))
    dilated2 = alpha_mask.filter(ImageFilter.MaxFilter(dr * 4 + 1))
    bl2 = dilated2.filter(ImageFilter.GaussianBlur(blur_r * 2))
    margin = blur_r * 3
    bl_w, bl_h = pw + margin * 2, ph + margin * 2
    bl_rgba = Image.new("RGBA", (bl_w, bl_h), (0, 0, 0, 0))
    bl_px = bl_rgba.load(); bl1_lx = bl1.load(); bl2_lx = bl2.load()
    bc = t["backlight_color"]
    for by in range(bl_h):
        for bx in range(bl_w):
            lx, ly = bx - margin, by - margin
            a1 = bl1_lx[lx, ly] if (0 <= lx < pw and 0 <= ly < ph) else 0
            a2 = bl2_lx[lx, ly] if (0 <= lx < pw and 0 <= ly < ph) else 0
            a = min(a1 * intensity // 255 + a2 * intensity // 510, 120)
            if a > 2:
                bl_px[bx, by] = (bc[0], bc[1], bc[2], a)
    base.paste(bl_rgba, (pos[0] - margin, pos[1] - margin), bl_rgba)


def _add_product_reflection(base, product, pos, alpha_mask):
    pw, ph = product.size
    reflect_h = ph // 3
    reflected = product.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, pw, reflect_h))
    reflect_alpha = alpha_mask.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, pw, reflect_h))
    gradient = Image.new("L", (pw, reflect_h), 0)
    gd = ImageDraw.Draw(gradient)
    for i in range(reflect_h):
        gd.line([(0, i), (pw, i)], fill=int(100 * (1 - i / reflect_h)))
    combined = Image.new("L", (pw, reflect_h), 0)
    cm_px = combined.load(); ra_px = reflect_alpha.load(); gd_px = gradient.load()
    for ry in range(reflect_h):
        for rx in range(pw):
            cm_px[rx, ry] = min(ra_px[rx, ry], gd_px[rx, ry])
    base.paste(reflected, (pos[0], pos[1] + ph), combined)


def _product_label(draw, base, t, text, x, y):
    font = _font(_s(15))
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = _s(6)
    draw.rounded_rectangle([x - pad, y - pad, x + tw + pad, y + th + pad],
                           radius=_s(4), fill=t["accent"])
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    dot_r = _s(3)
    draw.ellipse([x - dot_r + tw // 2, y - _s(15),
                  x + dot_r + tw // 2, y - _s(15) + dot_r * 2], fill=t["accent"])
    draw.line([(x + tw // 2, y - _s(15) + dot_r * 2),
               (x + tw // 2, y - pad)], fill=t["accent"], width=_s(1))


def _resize_product(product, target_w, target_h):
    """缩放图片以完全适配目标区域（contain 模式，不裁剪）。
    返回 (resized_image, new_w, new_h)，图片保持原始宽高比，不裁剪。
    """
    pw, ph = product.size
    scale = min(target_w / pw, target_h / ph)  # min = contain（不裁剪）
    nw, nh = int(pw * scale), int(ph * scale)
    product = product.resize((nw, nh), Image.LANCZOS)
    return product, nw, nh


def _place_single_product(base, t, image_path, position, glow_mode, reflection, label,
                          cover_layout="text-above", text_bottom=0):
    w, h = CANVAS_SIZE
    try:
        product = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"[WARN] 无法打开产品图 {image_path}: {e}")
        return None

    # 单图定位网格 — 6行×3列（上中下 × 左中右）+ 铺满背景
    pos_cfg = {
        # ---- 上方（image-above 模式）----
        "top-center":    (0.75, 0.34, "center", 0.05),
        "top-left":      (0.52, 0.34, "left", 0.05),
        "top-right":     (0.50, 0.36, "right", 0.04),
        # ---- 中部（text-surround 模式）----
        "center":        (0.65, 0.42, "center", 0.25),
        "mid-left":      (0.50, 0.42, "left", 0.28),
        "mid-right":     (0.50, 0.42, "right", 0.28),
        # ---- 下方（text-above 模式，文字在上图片在下）----
        "bottom-center": (0.78, 0.38, "center", 0.55),
        "bottom-left":   (0.52, 0.38, "left", 0.53),
        "bottom-right":  (0.52, 0.38, "right", 0.53),
        "bottom-fill":   (0.88, 0.42, "center", 0.50),
        # ---- 铺满背景 ----
        "full-bg":       (1.0, 1.0, "center", 0.0),
    }
    cfg = pos_cfg.get(position, pos_cfg["bottom-center"])
    rw, rh, align, tr = cfg
    tw, th = int(w * rw), int(h * rh)
    if align == "center":   x0 = (w - tw) // 2
    elif align == "left":   x0 = _s(20)
    else:                   x0 = w - tw - _s(20)
    y0 = int(h * tr)

    # text-above 模式下，图片紧跟文字底部，不等固定比例
    if cover_layout == "text-above" and text_bottom > 0:
        y0 = text_bottom + _s(12)
        # 如果超出画布，缩小图片高度
        available_h = h - y0 - _s(60)  # 留60px给底部标签等
        if available_h < th:
            th = max(int(h * 0.15), available_h)

    # 统一执行 alpha 提取 + 缩放（contain 模式，不裁剪）
    alpha_mask = _extract_alpha_mask(product)
    product, actual_w, actual_h = _resize_product(product, tw, th)
    alpha_mask, _, _ = _resize_product(alpha_mask.convert("RGBA"), tw, th)
    alpha_mask = alpha_mask.split()[0]

    # 将实际图片居中放置在目标区域内（contain 模式下实际尺寸 ≤ 目标尺寸）
    px = x0 + (tw - actual_w) // 2
    py = y0 + (th - actual_h) // 2

    if glow_mode in ("backlight", "both"):
        _add_product_backlight(base, product, (px, py), alpha_mask, t)
    if glow_mode in ("shadow", "both"):
        _add_product_shadow(base, product, (px, py), alpha_mask, t)
    base.paste(product, (px, py), alpha_mask)
    if reflection:
        _add_product_reflection(base, product, (px, py), alpha_mask)
    if label:
        draw = ImageDraw.Draw(base)
        lx = x0 + tw // 2 - _text_size(label, _font(15))[0] // 2
        _product_label(draw, base, t, label, lx, y0 + th + 12)

    return (x0, y0, x0 + tw, y0 + th)


def _place_multi_products(base, t, image_paths, layout, glow_mode, labels,
                          y_offset=0, max_y=None, placement="top"):
    """多产品排版引擎
    y_offset: 最小Y起始（px），用于text-above模式下图片跟随文字
    max_y:    最大Y限制（px），防止溢出
    placement: "top" | "bottom" — 决定 slot 定位在上半区还是下半区
    """
    w, h = CANVAS_SIZE
    layout_cfg = {
        # 所有布局使用原始定义（上方定位），placement="bottom" 时自动下移
        "compare-2":  [(0.08, 0.08, 0.40, 0.30), (0.52, 0.08, 0.40, 0.30)],
        "compare-3h": [(0.03, 0.06, 0.30, 0.28), (0.35, 0.06, 0.30, 0.28), (0.67, 0.06, 0.30, 0.28)],
        "compare-3v": [(0.15, 0.03, 0.70, 0.24), (0.08, 0.30, 0.40, 0.18), (0.52, 0.30, 0.40, 0.18)],
        "grid-4":     [(0.05, 0.05, 0.43, 0.22), (0.52, 0.05, 0.43, 0.22),
                       (0.05, 0.30, 0.43, 0.22), (0.52, 0.30, 0.43, 0.22)],
    }
    slots = layout_cfg.get(layout, layout_cfg["compare-2"])
    boxes = []

    # 计算实际使用的区域
    for i, img_path in enumerate(image_paths):
        if i >= len(slots):
            break
        try:
            product = Image.open(img_path).convert("RGBA")
        except Exception as e:
            print(f"[WARN] 无法打开产品图 {img_path}: {e}")
            continue
        sx, sy, sw, sh = slots[i]

        # ---- 位置计算 ----
        if placement == "bottom" or y_offset > 0:
            # 下移模式：整体平移，保持 slot 间相对位置
            if placement == "bottom" and y_offset <= 0:
                # 无具体 y_offset，整体下移 44%
                shift = 0.44
            else:
                # 有 y_offset：第一个 slot 移到 y_offset，其余保持相对间距
                first_sy = slots[0][1]
                shift = y_offset / h + 0.02 - first_sy
            new_sy = sy + shift

            # 确保不超出画布
            effective_bottom = (max_y or (h - _s(60))) / h
            if new_sy + sh > effective_bottom:
                sh = max(0.15, effective_bottom - new_sy - 0.02)

            sy = new_sy

        tw, th = int(w * sw), int(h * sh)
        x0, y0 = int(w * sx), int(h * sy)

        alpha_mask = _extract_alpha_mask(product)
        product, actual_w, actual_h = _resize_product(product, tw, th)
        alpha_mask, _, _ = _resize_product(alpha_mask.convert("RGBA"), tw, th)
        alpha_mask = alpha_mask.split()[0]

        # 将实际图片居中放置在目标区域内（contain 模式下实际尺寸 ≤ 目标尺寸）
        px = x0 + (tw - actual_w) // 2
        py = y0 + (th - actual_h) // 2

        if glow_mode in ("backlight", "both"):
            _add_product_backlight(base, product, (px, py), alpha_mask, t, intensity=50)
        if glow_mode in ("shadow", "both"):
            _add_product_shadow(base, product, (px, py), alpha_mask, t, shadow_opacity=80)
        base.paste(product, (px, py), alpha_mask)
        if labels and i < len(labels) and labels[i]:
            draw = ImageDraw.Draw(base)
            label = labels[i]
            lx = x0 + tw // 2 - _text_size(label, _font(13))[0] // 2
            _product_label(draw, base, t, label, lx, y0 + th + 6)
        boxes.append((x0, y0, x0 + tw, y0 + th))
    if not boxes:
        return None
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


# ============================================================
# 文字区域渲染
# ============================================================

def _render_accent_line(draw, base, t, text, y_start):
    font_a = _font(_s(16))
    _draw_accent_bar(draw, t, _s(28), y_start + _s(8), _s(70), 4)
    if text:
        segs = parse_rich_text(text)
        _render_rich_line(base, t, segs, _s(110), y_start, base_font_size=_s(16))
    return y_start + _s(28)


def _render_specs_bar(draw, base, t, specs, y_start, huazi_val=None, font_family=None):
    w, _ = CANVAS_SIZE
    f_label, f_value = _font(_s(14), family=font_family), _font(_s(30), bold=True, family=font_family)
    n = len(specs)
    if n == 0:
        return y_start
    bar_w, bar_h = w - _s(56), _s(82)
    item_w, x0 = bar_w // n, _s(28)
    draw.rounded_rectangle([x0, y_start, x0 + bar_w, y_start + bar_h],
                           radius=_s(8), fill=t["bg_accent"], outline=t["divider"], width=_s(1))
    for i, spec in enumerate(specs):
        cx = x0 + i * item_w + item_w // 2
        label = spec.get("label", "")
        if label:
            draw.text((cx, y_start + _s(8)), label, fill=t["text_secondary"], font=f_label, anchor="mt")
        val = str(spec.get("value", ""))

        val_huazi = huazi_val or _HUAZI_SPECS_VAL
        if i == 0 and val_huazi and HUAZI_TEMPLATES.get(val_huazi):
            tw_val = _text_size(val, _font(_s(30), bold=True, family=font_family))[0]
            try:
                hr = get_huazi_renderer()
                hr.render(base, val, val_huazi,
                         cx - tw_val // 2, y_start + _s(32),
                         font_family=font_family or _FONT_FAMILY,
                         font_weight="Bold", font_size=_s(30),
                         accent_color=t.get("accent_alt"),
                         bg_color=t.get("bg_color"))
            except Exception:
                fg = t["accent_alt"]
                _render_text_glow(base, (cx - _text_size(val, f_value)[0] // 2, y_start + _s(32)),
                                val, f_value, fg, (*fg, 120), glow_radius=_s(6))
        elif i == 0:
            fg = t["accent_alt"]
            _render_text_glow(base, (cx - _text_size(val, f_value)[0] // 2, y_start + _s(32)),
                            val, f_value, fg, (*fg, 120), glow_radius=_s(6))
        else:
            draw.text((cx, y_start + _s(38)), val, fill=t["text_primary"], font=f_value, anchor="mt")
        if i < n - 1:
            sx = x0 + (i + 1) * item_w
            draw.line([(sx, y_start + _s(12)), (sx, y_start + bar_h - _s(12))], fill=t["divider"], width=_s(1))
    return y_start + bar_h + _s(16)


def _render_tags(draw, base, t, tags, y_start, huazi=None, font_family=None):
    f_tag = _font(_s(17), family=font_family)
    x, th = _s(28), _s(34)
    tag_huazi = huazi or _HUAZI_TAGS
    for i, tag_text in enumerate(tags):
        bbox = draw.textbbox((0, 0), tag_text, font=f_tag)
        tw = bbox[2] - bbox[0] + _s(22)
        if i == 0:
            bg, fg, outline = t["accent"], (255, 255, 255), None
        else:
            bg, fg, outline = t["tag_bg"], t["tag_text"], t["divider"]

        if i == 0 and tag_huazi and HUAZI_TEMPLATES.get(tag_huazi):
            # 第一个标签用花字
            draw.rounded_rectangle([x, y_start, x + tw, y_start + th],
                                   radius=_s(7), fill=bg, outline=outline, width=_s(1) if outline else 0)
            try:
                hr = get_huazi_renderer()
                hr.render(base, tag_text, tag_huazi, x + _s(11), y_start + _s(5),
                         font_family=font_family or _FONT_FAMILY,
                         font_weight="Bold", font_size=_s(17),
                         accent_color=fg, bg_color=bg)
            except Exception:
                draw.text((x + _s(11), y_start + _s(5)), tag_text, fill=fg, font=f_tag)
        else:
            draw.rounded_rectangle([x, y_start, x + tw, y_start + th],
                                   radius=_s(7), fill=bg, outline=outline, width=_s(1) if outline else 0)
            draw.text((x + _s(11), y_start + _s(5)), tag_text, fill=fg, font=f_tag)
        x += tw + _s(10)
        if x > CANVAS_SIZE[0] - _s(60):
            break
    return y_start + _s(48)


def _render_price_badge(draw, base, t, price_text, x, y, huazi=None, font_family=None):
    f = _font(_s(36), bold=True, family=font_family)
    bbox = draw.textbbox((0, 0), price_text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = _s(16)
    glow = Image.new("RGBA", (tw + pad * 4, th + pad * 4), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([pad, pad, tw + pad * 3, th + pad * 3],
                                           radius=_s(12), fill=t["accent"])
    glow = glow.filter(ImageFilter.GaussianBlur(_s(4)))
    base.paste(glow, (x - pad - pad, y - pad - pad), glow)
    draw.rounded_rectangle([x - pad, y - pad, x + tw + pad, y + th + pad],
                           radius=_s(12), fill=t["accent"])

    price_huazi = huazi or _HUAZI_PRICE
    if price_huazi and HUAZI_TEMPLATES.get(price_huazi):
        try:
            hr = get_huazi_renderer()
            hr.render(base, price_text, price_huazi, x, y,
                     font_family=font_family or _FONT_FAMILY,
                     font_weight="Bold", font_size=_s(36),
                     accent_color=(255, 255, 255),
                     bg_color=t["accent"])
        except Exception:
            draw.text((x, y), price_text, fill=(255, 255, 255), font=f)
    else:
        draw.text((x, y), price_text, fill=(255, 255, 255), font=f)


def _render_watermark_line(draw, t):
    w, h = CANVAS_SIZE
    f = _font(_s(11))
    draw.line([(_s(24), h - _s(42)), (w - _s(24), h - _s(42))], fill=t["divider"], width=_s(1))
    draw.text((_s(30), h - _s(34)), "@CREATOR", fill=t["text_secondary"], font=f)


def _render_frame(draw, t):
    w, h = CANVAS_SIZE
    draw.rectangle([_s(1), _s(1), w - _s(2), h - _s(2)], outline=t["divider"], width=_s(1))


# ============================================================
# ★ 主入口
# ============================================================

def generate_cover(
    category="tech",
    template="dark",
    title="",
    subtitle="",
    specs=None,
    tags=None,
    image_paths=None,
    image_layout="single",
    image_position="bottom-center",
    image_glow="none",
    image_reflection=False,
    image_labels=None,
    price_text=None,
    accent_line_text=None,
    corner_badge=None,
    cover_layout="text-above",
    output_path="cover.png",
    # ★ v4.0: 字体 & 花字
    font_family=None,
    font_weight_title="Bold",
    font_weight_body="Regular",
    title_huazi=None,
    subtitle_huazi=None,
    price_huazi=None,
    badge_huazi=None,
    tags_huazi=None,
    specs_huazi=None,
    title_size=None,
    subtitle_size=None,
):
    """
    cover_layout 模式:
      - "text-above":    文字在上方（40-55%），图片在下方 ← ★ 新默认，匹配爆款
      - "image-above":   图片在上方，文字在下方（旧默认，向后兼容）
      - "text-surround": 文字上下 + 图片中间
      - "full-bg":       图片铺满背景，文字叠加

    v4.0 字体 & 花字:
      --font-family "思源黑体"  指定字体家族
      --title-huazi stroke-white 标题花字模板
    """
    # ★ v4.0: 设置全局字体/花字配置
    global _FONT_FAMILY, _FONT_WEIGHT_TITLE, _FONT_WEIGHT_BODY
    global _TITLE_SIZE, _SUBTITLE_SIZE
    global _HUAZI_TITLE, _HUAZI_SUBTITLE, _HUAZI_PRICE, _HUAZI_BADGE, _HUAZI_TAGS, _HUAZI_SPECS_VAL
    _FONT_FAMILY = font_family
    _FONT_WEIGHT_TITLE = font_weight_title
    _FONT_WEIGHT_BODY = font_weight_body

    # ★ v5.1: 自动计算标题字号（垂直+水平双约束）
    if title_size is None:
        raw = title or ''
        title_lines = max(1, len(raw.split('\n')))
        # 垂直约束：文字区 44% 画布高 / (行数 × 1.25)
        avail_h = int(CANVAS_SIZE[1] * 0.44)
        size_by_h = avail_h // (title_lines * 1.25)
        # 水平约束：最长行字数不超画布 85% 宽
        stripped = raw
        for ch in '*_=!~`': stripped = stripped.replace(ch, '')
        longest = max((len(l) for l in stripped.split('\n')), default=1)
        avail_w = int(CANVAS_SIZE[0] * 0.85)
        size_by_w = avail_w // max(1, longest) if longest > 0 else avail_w
        title_size = int(min(size_by_h, size_by_w))
        title_size = max(120, min(320, title_size))
    if subtitle_size is None:
        subtitle_size = int(title_size * 0.55)

    _TITLE_SIZE = title_size
    _SUBTITLE_SIZE = subtitle_size
    # 花字：如果没指定则自动匹配模板
    _HUAZI_TITLE = title_huazi or resolve_huazi_for_template(resolve_template(category, template)[2])
    _HUAZI_SUBTITLE = subtitle_huazi
    _HUAZI_PRICE = price_huazi or HUAZI_TARGET_MAP.get("price")
    _HUAZI_BADGE = badge_huazi or HUAZI_TARGET_MAP.get("badge")
    _HUAZI_TAGS = tags_huazi
    _HUAZI_SPECS_VAL = specs_huazi or HUAZI_TARGET_MAP.get("specs_val")

    # 解析模板
    t, resolved_cat, resolved_tmpl = resolve_template(category, template)
    cat_label = CATEGORIES.get(resolved_cat, {}).get("label", resolved_cat)

    base = Image.new("RGBA", CANVAS_SIZE, t["bg_color"] + (255,))
    draw = ImageDraw.Draw(base)
    w, h = CANVAS_SIZE

    has_multi = (image_layout and image_layout != "single" and
                 image_paths and len(image_paths) > 1)

    # ======== 0. 全背景模式 — 图片铺满，叠加半透明蒙层 ========
    if cover_layout == "full-bg" and image_paths:
        try:
            bg_img = Image.open(image_paths[0]).convert("RGBA")
            bg_img = bg_img.resize(CANVAS_SIZE, Image.LANCZOS)
            base.paste(bg_img, (0, 0))
            # 深色蒙层保证文字可读
            overlay_alpha = 160 if t.get("is_dark", True) else 90
            overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, overlay_alpha))
            base.paste(overlay, (0, 0), overlay)
        except Exception as e:
            print(f"[WARN] 无法打开背景图 {image_paths[0]}: {e}，回退到纯色背景")
            base = Image.new("RGBA", CANVAS_SIZE, t["bg_color"] + (255,))
            draw = ImageDraw.Draw(base)

    # ======== 1. 背景装饰 ========
    if t.get("is_dark", True):
        _draw_glow_orb(draw, base, t, w - _s(50), _s(70), _s(190))
        _draw_deco_ring(draw, base, t, w - _s(45), _s(45), _s(55))
    else:
        _draw_glow_orb(draw, base, t, w - _s(40), _s(50), _s(150))
    _draw_accent_bar(draw, t, _s(24), _s(16), _s(50), 3)

    if corner_badge:
        _draw_rotated_badge(base, t, corner_badge, w - _s(50), _s(55), rotation=-15)

    # ================================================================
    # ★ 布局分发
    # ================================================================

    if cover_layout == "full-bg":
        # ---- 满铺背景：文字垂直居中于全画布 ----
        _layout_full_bg(base, draw, t, w, h,
                        image_paths, has_multi, image_layout, image_position,
                        image_glow, image_reflection, image_labels,
                        title, subtitle, specs, tags, price_text, accent_line_text)

    elif cover_layout == "image-above":
        _layout_image_above(base, draw, t, w, h,
                            image_paths, has_multi, image_layout, image_position,
                            image_glow, image_reflection, image_labels,
                            title, subtitle, specs, tags, price_text, accent_line_text)

    elif cover_layout == "text-surround":
        _layout_text_surround(base, draw, t, w, h,
                              image_paths, has_multi, image_layout, image_position,
                              image_glow, image_reflection, image_labels,
                              title, subtitle, specs, tags, price_text, accent_line_text)

    else:
        # ---- 默认 text-above：文字在上 → 图片在下 ----
        _layout_text_above(base, draw, t, w, h,
                           image_paths, has_multi, image_layout, image_position,
                           image_glow, image_reflection, image_labels,
                           title, subtitle, specs, tags, price_text, accent_line_text)

    # _render_watermark_line(draw, t)  # v4.1: 移除硬编码 @CREATOR 水印
    _render_frame(draw, t)

    final = base.convert("RGB")
    final.save(output_path, quality=95)

    n_imgs = len(image_paths) if image_paths else 0
    print(f"[OK] 封面已生成: {output_path}")
    print(f"     品类: {cat_label}  |  模板: {t['name']}  |  尺寸: {w}x{h}  |  产品图: {n_imgs}张  |  布局: {cover_layout}  |  v4.0")
    return output_path


# ============================================================
# 布局子函数
# ============================================================

def _layout_full_bg(base, draw, t, w, h,
                     image_paths, has_multi, image_layout, image_position,
                     image_glow, image_reflection, image_labels,
                     title, subtitle, specs, tags, price_text, accent_line_text):
    """★ v5.1 满铺背景：文字垂直居中于全画布"""
    MARGIN = int(h * 0.05)

    # 先测量文字总高度
    tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tmp_draw = ImageDraw.Draw(tmp)
    tmp_cy = 0
    if title:
        tmp_cy = _render_rich_title(tmp_draw, tmp, t, title, tmp_cy, align="center")
    if subtitle:
        tmp_cy = _render_rich_subtitle(tmp_draw, tmp, t, subtitle, tmp_cy, align="center")
    text_h = tmp_cy

    # 垂直居中
    cy = (h - text_h) // 2
    if cy < MARGIN:
        cy = MARGIN
    if title:
        cy = _render_rich_title(draw, base, t, title, cy, align="center")
    if subtitle:
        cy = _render_rich_subtitle(draw, base, t, subtitle, cy, align="center")


def _layout_image_above(base, draw, t, w, h,
                        image_paths, has_multi, image_layout, image_position,
                        image_glow, image_reflection, image_labels,
                        title, subtitle, specs, tags, price_text, accent_line_text):
    """★ v5.0 图片在上一半 → 文字在下一半，纯比例驱动"""
    HALF = int(h * 0.50)
    MARGIN = int(h * 0.03)

    # ---- 上半：图片 ----
    if image_paths:
        if has_multi:
            _place_multi_products(base, t, image_paths, image_layout, image_glow, image_labels,
                                  y_offset=MARGIN, max_y=HALF - MARGIN)
        else:
            # 图片填满上半区 (MARGIN, MARGIN) ~ (w-MARGIN, HALF-MARGIN)
            _place_single_product(base, t, image_paths[0], "top-center", image_glow,
                                  image_reflection, image_labels[0] if image_labels else None,
                                  cover_layout="image-above")

    # ---- 下半：文字（居中）----
    cy = HALF + MARGIN
    if title:
        cy = _render_rich_title(draw, base, t, title, cy, align="center")
    if subtitle:
        cy = _render_rich_subtitle(draw, base, t, subtitle, cy, align="center")
    if tags and len(tags) > 0:
        _render_tags(draw, base, t, tags, h - MARGIN - int(h * 0.04))


def _layout_text_above(base, draw, t, w, h,
                       image_paths, has_multi, image_layout, image_position,
                       image_glow, image_reflection, image_labels,
                       title, subtitle, specs, tags, price_text, accent_line_text):
    """★ v5.0 文字上一半 → 图片下一半，纯比例驱动"""
    HALF = int(h * 0.50)
    MARGIN = int(h * 0.03)

    # ---- 上半：文字（居中）----
    cy = MARGIN
    if title:
        cy = _render_rich_title(draw, base, t, title, cy, align="center")
    if subtitle:
        cy = _render_rich_subtitle(draw, base, t, subtitle, cy, align="center")

    # ---- 下半：图片 ----
    if image_paths:
        img_start = max(HALF + MARGIN, cy + MARGIN)  # 确保不重叠
        if has_multi:
            _place_multi_products(base, t, image_paths, image_layout, image_glow, image_labels,
                                  y_offset=img_start, max_y=h - MARGIN, placement="bottom")
        else:
            _place_single_product(base, t, image_paths[0], "bottom-center", image_glow,
                                  image_reflection, image_labels[0] if image_labels else None,
                                  cover_layout="text-above", text_bottom=img_start)

    if tags and len(tags) > 0:
        _render_tags(draw, base, t, tags, h - MARGIN - int(h * 0.04))


def _layout_text_surround(base, draw, t, w, h,
                          image_paths, has_multi, image_layout, image_position,
                          image_glow, image_reflection, image_labels,
                          title, subtitle, specs, tags, price_text, accent_line_text):
    """★ v5.1 文字上下包裹：上文字 | 等距 | 图片 | 等距 | 下文字"""
    title_lines = title.split('\n') if title else []
    title_top = title_lines[0] if len(title_lines) > 0 else ''
    title_bottom = title_lines[1] if len(title_lines) > 1 else ''

    MARGIN = int(h * 0.05)  # 5% 补偿光晕/花字扩展

    # ---- 上区：顶部标题 ----
    cy = MARGIN
    if title_top:
        cy = _render_rich_title(draw, base, t, title_top, cy, align="center")
    top_end = cy

    # ---- 下区文字预测量 ----
    tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tmp_draw = ImageDraw.Draw(tmp)
    bot_h = 0
    if title_bottom:
        bot_h = _render_rich_title(tmp_draw, tmp, t, title_bottom, 0, align="center")

    # ---- 中区：图片在上下文字之间，等距 ----
    img_start = top_end + MARGIN
    img_end = h - bot_h - MARGIN
    image_box = None
    if image_paths and img_end > img_start:
        if has_multi:
            image_box = _place_multi_products(base, t, image_paths, image_layout, image_glow, image_labels,
                                              y_offset=img_start, max_y=img_end)
        else:
            product = Image.open(image_paths[0]).convert("RGBA")
            pw, ph = product.size
            # 图片最多占可用空间的 65%，留呼吸感
            avail_w = (w - MARGIN * 2) * 0.65
            avail_h = (img_end - img_start) * 0.65
            if pw > 0 and ph > 0 and avail_h > 0:
                scale = min(avail_w / pw, avail_h / ph)
                nw, nh = int(pw * scale), int(ph * scale)
                product = product.resize((nw, nh), Image.LANCZOS)
                x0 = (w - nw) // 2
                y0 = img_start  # 贴顶：gap1=MARGIN, gap2=img_bottom+MARGIN
                alpha_mask = _extract_alpha_mask(product)
                if image_glow in ("backlight", "both"):
                    _add_product_backlight(base, product, (x0, y0), alpha_mask, t)
                if image_glow in ("shadow", "both"):
                    _add_product_shadow(base, product, (x0, y0), alpha_mask, t)
                base.paste(product, (x0, y0), alpha_mask if product.mode == 'RGBA' else None)
                image_box = (x0, y0, x0 + nw, y0 + nh)

    # ---- 下区：底部标题（图片实际底部 + MARGIN）----
    img_bottom = image_box[3] if image_box else img_end
    bot_start = img_bottom + MARGIN + int(h * 0.03)  # +3% 补偿阴影向下延伸
    if title_bottom:
        _render_rich_title(draw, base, t, title_bottom, bot_start, align="center")
    if tags and len(tags) > 0:
        _render_tags(draw, base, t, tags, h - MARGIN - int(h * 0.04))


# ============================================================
# CLI
# ============================================================

def main():
    # 动态生成品类选择列表
    cat_choices = list(CATEGORIES.keys())
    cat_help = " / ".join(f"{k}({v['label']})" for k, v in CATEGORIES.items())

    parser = argparse.ArgumentParser(
        description="封面生成器 v3.0 — 多品类模板引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
品类与模板:
  {cat_help}

  科技(tech):     dark / dark_blue / bright / warm_tech
  教育(education): academic / chalkboard / clean
  美食(food):      warm_dark / bright_eat / rustic
  旅游(travel):    nature / sunset / aerial
  时尚(fashion):   luxury / clean_girl / vibrant
  财经(business):  navy_gold / white_paper / dark_data

富文本标记:  **强调**  __斜体__  ==色块==  !!发光!!  ~~描边~~  ``反色``

示例:
  # 科技类（向后兼容，默认品类）
  %(prog)s --template dark --title "**跑分150万**的秘密" --specs "跑分:150万" "芯片:A18"

  # 教育类
  %(prog)s --category education --template academic \\
      --title "**3分钟**搞懂区块链" --subtitle "小白也能听明白"

  # 美食类
  %(prog)s --category food --template warm_dark \\
      --title "**人均50**吃到撑" --image dish.png --image-glow backlight

  # 带产品图
  %(prog)s --category fashion --template luxury \\
      --title "**2026秋冬**必备单品" --image outfit.png --image-glow both
        """
    )

    # 品类 & 模板
    parser.add_argument("--category", "-c", default="tech", choices=cat_choices,
                        help=f"内容品类 (default: tech)")
    parser.add_argument("--template", "-t", default="dark",
                        help="模板名称（见上方列表，default: dark）")

    # 文字
    parser.add_argument("--title", default="", help="L1 钩子标题，支持富文本标记")
    parser.add_argument("--subtitle", default="", help="L2 副标题，支持富文本标记")
    parser.add_argument("--specs", nargs="*", default=[],
                        help='规格参数，格式: "标签:数值" (2-4组)')
    parser.add_argument("--tags", nargs="*", default=[], help="底部标签 (2-5个)")
    parser.add_argument("--price", default="", help="价格徽章文字")
    parser.add_argument("--accent-bar", default="", help="强调色条文字，支持富文本")
    parser.add_argument("--corner-badge", default="", help="右上角旋转徽章 (HOT/NEW/PRO)")

    # 图片
    parser.add_argument("--image", action="append", default=[], dest="image_paths",
                        help="产品图路径，可多次使用")
    parser.add_argument("--image-layout", default="single",
                        choices=["single", "compare-2", "compare-3h", "compare-3v", "grid-4"],
                        help="多图布局模式 (default: single)")
    parser.add_argument("--image-position", default="bottom-center",
                        choices=["top-center", "top-left", "top-right",
                                 "center", "mid-left", "mid-right",
                                 "bottom-center", "bottom-left", "bottom-right",
                                 "bottom-fill", "full-bg"],
                        help="单图定位 (default: bottom-center)")
    parser.add_argument("--image-glow", default="none",
                        choices=["none", "shadow", "backlight", "both"],
                        help="抠图光影效果 (default: none)")
    parser.add_argument("--image-reflection", action="store_true", help="启用镜面倒影")
    parser.add_argument("--image-labels", nargs="*", default=[], help="每张产品图的标注文字")

    # 布局模式
    parser.add_argument("--cover-layout", default="text-above",
                        choices=["text-above", "image-above", "text-surround", "full-bg"],
                        help="排版布局模式（default: text-above 文字在上图片在下）")

    # ★ v4.0: 字体
    parser.add_argument("--font-family", default=None,
                        help="字体家族（如: 思源黑体, 站酷高端黑, 阿里普惠体）")
    parser.add_argument("--font-weight-title", default="Bold",
                        help="标题字重 (default: Bold)")
    parser.add_argument("--font-weight-body", default="Regular",
                        help="正文字重 (default: Regular)")
    parser.add_argument("--title-size", type=int, default=None,
                        help="标题字号 (default: 自动计算)")
    parser.add_argument("--subtitle-size", type=int, default=None,
                        help="副标题字号 (default: 自动计算)")

    # ★ v4.0: 花字
    parser.add_argument("--list-fonts", action="store_true",
                        help="列出所有可用字体")
    parser.add_argument("--list-huazi", action="store_true",
                        help="列出所有花字模板")
    parser.add_argument("--title-huazi", default=None,
                        help="标题花字模板名")
    parser.add_argument("--subtitle-huazi", default=None,
                        help="副标题花字模板名")
    parser.add_argument("--price-huazi", default=None,
                        help="价格花字模板名")
    parser.add_argument("--badge-huazi", default=None,
                        help="角标花字模板名")
    parser.add_argument("--tags-huazi", default=None,
                        help="标签花字模板名")
    parser.add_argument("--specs-huazi", default=None,
                        help="规格数值花字模板名")

    # 输出
    parser.add_argument("--output", "-o", default="cover.png", help="输出文件路径")

    args = parser.parse_args()

    # --list-fonts
    if args.list_fonts:
        fm = get_font_manager()
        families = fm.list_families()
        print(f"\n  可用字体 ({fm.available_count} 个文件, {len(families)} 个家族):\n")
        for line in families:
            print(line)
        print(f"\n  内置字体目录: {os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')}")
        print(f"  运行 python scripts/install_fonts.py --all 安装更多免费商用字体")
        sys.exit(0)

    # --list-huazi
    if args.list_huazi:
        print(f"\n  花字模板 ({len(HUAZI_TEMPLATES)} 种):\n")
        for line in list_huazi():
            print(line)
        sys.exit(0)

    # 处理回退模板名
    template = args.template
    if template in TEMPLATE_ALIASES and args.category == "tech":
        pass  # 使用别名
    elif args.category in CATEGORIES and template not in CATEGORIES[args.category]["templates"]:
        available = list(CATEGORIES[args.category]["templates"].keys())
        print(f"[WARN] '{template}' 不在 {args.category} 品类中，可用: {available}")
        # 尝试全局别名
        if template in TEMPLATE_ALIASES:
            cat_alt, tmpl_alt = TEMPLATE_ALIASES[template]
            print(f"[INFO] 使用别名映射: {template} → {cat_alt}.{tmpl_alt}")
            args.category = cat_alt
            template = tmpl_alt
        else:
            template = available[0]
            print(f"[INFO] 使用默认模板: {template}")

    specs_list = []
    for s in args.specs:
        if ":" in s:
            label, value = s.split(":", 1)
            specs_list.append({"label": label.strip(), "value": value.strip()})
        else:
            specs_list.append({"label": "", "value": s.strip()})

    # v4.0: 字体信息
    fm = get_font_manager()
    n_families = len(fm.list_families())
    active_family = args.font_family or (fm.list_families()[0].split("  →")[0].strip() if fm.list_families() else "系统默认")
    print(f"[INFO] 字体: {active_family} ({n_families} 个家族可用)")
    if args.title_huazi or _HUAZI_TITLE:
        print(f"[INFO] 花字: 标题={args.title_huazi or '自动'}")

    output = generate_cover(
        category=args.category,
        template=template,
        title=args.title,
        subtitle=args.subtitle,
        specs=specs_list if specs_list else None,
        tags=args.tags if args.tags else None,
        image_paths=args.image_paths if args.image_paths else None,
        image_layout=args.image_layout,
        image_position=args.image_position,
        image_glow=args.image_glow,
        image_reflection=args.image_reflection,
        image_labels=args.image_labels if args.image_labels else None,
        price_text=args.price if args.price else None,
        accent_line_text=args.accent_bar if args.accent_bar else None,
        corner_badge=args.corner_badge if args.corner_badge else None,
        cover_layout=args.cover_layout,
        output_path=args.output,
        # ★ v4.0
        font_family=args.font_family,
        font_weight_title=args.font_weight_title,
        font_weight_body=args.font_weight_body,
        title_huazi=args.title_huazi,
        subtitle_huazi=args.subtitle_huazi,
        price_huazi=args.price_huazi,
        badge_huazi=args.badge_huazi,
        tags_huazi=args.tags_huazi,
        specs_huazi=args.specs_huazi,
        title_size=args.title_size,
        subtitle_size=args.subtitle_size,
    )
    print(f"[DONE] {output}")


if __name__ == "__main__":
    main()
