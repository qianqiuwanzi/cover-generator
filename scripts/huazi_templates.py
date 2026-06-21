# -*- coding: utf-8 -*-
"""
花字模板库 v1.0 — 12 种抖音/剪映风格花字预设
每个模板 = 多层渲染指令栈（从底到顶）
"""

HUAZI_TEMPLATES = {

    # ================================================================
    # A 类：描边系（3 种）—— 最常用，适合标题/数字
    # ================================================================

    "stroke-white": {
        "name": "经典白描边",
        "name_cn": "经典白描边",
        "category": "描边系",
        "tags": ["通用", "标题", "数字", "百搭"],
        "description": "暗底封面最通用——深灰外描边+纯白中描边+强调色填充",
        "best_on": "dark",
        "layers": [
            {"type": "stroke", "color": "#1a1a1a", "width": 6},
            {"type": "stroke", "color": "#FFFFFF", "width": 3},
            {"type": "fill",   "color": "accent"},
        ],
    },

    "stroke-neon": {
        "name": "荧光撞色",
        "name_cn": "荧光撞色",
        "category": "描边系",
        "tags": ["潮流", "时尚", "年轻", "撞色"],
        "description": "荧光品红描边+细白内描边，撞色冲击",
        "best_on": "bright",
        "layers": [
            {"type": "stroke", "color": "#FF0088", "width": 4},
            {"type": "stroke", "color": "#FFFFFF", "width": 1},
            {"type": "fill",   "color": "accent"},
        ],
    },

    "stroke-emboss": {
        "name": "立体浮雕",
        "name_cn": "立体浮雕",
        "category": "描边系",
        "tags": ["高端", "质感", "专业", "品牌"],
        "description": "柔和阴影+亮色高光描边，模拟浮雕质感",
        "best_on": "all",
        "layers": [
            {"type": "shadow", "color": "#00000066", "offset": (3, 3), "blur": 4},
            {"type": "stroke", "color": "#FFFFFF44", "width": 2},
            {"type": "fill",   "color": "accent"},
        ],
    },

    # ================================================================
    # B 类：光影系（3 种）—— 适合强调/数字/价格
    # ================================================================

    "glow-neon": {
        "name": "霓虹发光",
        "name_cn": "霓虹发光",
        "category": "光影系",
        "tags": ["科技", "赛博", "强调", "数字"],
        "description": "双层发光（强调色+白色），制造霓虹灯管效果",
        "best_on": "dark",
        "layers": [
            {"type": "glow",   "color": "accent", "radius": 14, "opacity": 140},
            {"type": "glow",   "color": "#FFFFFF", "radius": 5, "opacity": 80},
            {"type": "fill",   "color": "#FFFFFF"},
        ],
    },

    "glow-metal": {
        "name": "金属渐变",
        "name_cn": "金属渐变",
        "category": "光影系",
        "tags": ["高端", "商务", "财经", "奢侈品"],
        "description": "垂直金→浅金→深金渐变+底阴影，模拟金属光泽",
        "best_on": "dark",
        "layers": [
            {"type": "shadow",  "color": "#00000033", "offset": (1, 2), "blur": 3},
            {"type": "stroke",  "color": "#B8860B", "width": 1},
            {"type": "gradient", "colors": ["#FFD700", "#FFF8DC", "#DAA520", "#B8860B"],
             "direction": "vertical"},
        ],
    },

    "glow-ambient": {
        "name": "氛围光晕",
        "name_cn": "氛围光晕",
        "category": "光影系",
        "tags": ["柔和", "暖心", "生活", "Vlog"],
        "description": "大范围柔光+白色薄描边，温暖不刺眼",
        "best_on": "dark",
        "layers": [
            {"type": "glow",   "color": "accent", "radius": 22, "opacity": 120},
            {"type": "stroke", "color": "#FFFFFF66", "width": 2},
            {"type": "fill",   "color": "#FFFFFF"},
        ],
    },

    # ================================================================
    # C 类：底衬系（3 种）—— 适合标签/角标/参数
    # ================================================================

    "badge-rounded": {
        "name": "圆角标签",
        "name_cn": "圆角标签",
        "category": "底衬系",
        "tags": ["标签", "角标", "参数", "规格"],
        "description": "圆角色块+投影，标准抖音标签样式",
        "best_on": "all",
        "layers": [
            {"type": "badge",  "shape": "rounded", "color": "accent",
             "padding_x": 14, "padding_y": 6, "radius": 8},
            {"type": "shadow", "color": "#00000033", "offset": (0, 2), "blur": 6},
            {"type": "fill",   "color": "#FFFFFF"},
        ],
    },

    "badge-ribbon": {
        "name": "镂空绶带",
        "name_cn": "镂空绶带",
        "category": "底衬系",
        "tags": ["促销", "限时", "角标", "首发"],
        "description": "倾斜色块+投影，促销/首发感强烈",
        "best_on": "all",
        "layers": [
            {"type": "badge",  "shape": "ribbon", "color": "accent",
             "padding_x": 16, "padding_y": 8},
            {"type": "shadow", "color": "#00000040", "offset": (2, 2), "blur": 4},
            {"type": "fill",   "color": "#FFFFFF"},
        ],
    },

    "badge-burst": {
        "name": "爆炸贴纸",
        "name_cn": "爆炸贴纸",
        "category": "底衬系",
        "tags": ["强调", "爆炸", "促销", "限时"],
        "description": "大色块+白色粗描边，高冲击力爆炸贴纸效果",
        "best_on": "dark",
        "layers": [
            {"type": "badge",  "shape": "burst", "color": "accent",
             "padding_x": 18, "padding_y": 10, "radius": 6},
            {"type": "stroke", "color": "#FFFFFF", "width": 3},
            {"type": "fill",   "color": "#FFFFFF"},
        ],
    },

    # ================================================================
    # D 类：3D/立体系（3 种）—— 适合主标题/钩子
    # ================================================================

    "3d-long-shadow": {
        "name": "长投影",
        "name_cn": "长投影",
        "category": "3D系",
        "tags": ["科技", "力量", "标题", "扁平"],
        "description": "45° 长投影（12px），扁平化设计经典手法",
        "best_on": "all",
        "layers": [
            {"type": "long_shadow", "color": "#00000088", "length": 12, "angle": 135},
            {"type": "fill",        "color": "accent"},
        ],
    },

    "3d-extrude": {
        "name": "3D挤出",
        "name_cn": "3D挤出",
        "category": "3D系",
        "tags": ["重磅", "冲击", "标题", "3D"],
        "description": "向下挤出 8px 深色层，模拟 3D 厚度",
        "best_on": "all",
        "layers": [
            {"type": "extrude", "color": "darken(accent, 0.4)", "depth": 8},
            {"type": "fill",    "color": "accent"},
        ],
    },

    "3d-double-exposure": {
        "name": "双重曝光",
        "name_cn": "双重曝光",
        "category": "3D系",
        "tags": ["艺术", "时尚", "文艺", "氛围"],
        "description": "文字副本向右偏移+半透明叠加",
        "best_on": "dark",
        "layers": [
            {"type": "copy",   "offset": (5, 0), "opacity": 0.35},
            {"type": "fill",   "color": "accent"},
        ],
    },
}

# ================================================================
# 智能匹配：模板背景 → 推荐花字
# ================================================================

TEMPLATE_HUAZI_MAP = {
    "dark":        "stroke-white",
    "dark_blue":   "glow-neon",
    "bright":      "stroke-neon",
    "warm_tech":   "glow-metal",
    "academic":    "stroke-emboss",
    "chalkboard":  "stroke-white",
    "clean":       "stroke-emboss",
    "warm_dark":   "glow-ambient",
    "bright_eat":  "stroke-neon",
    "rustic":      "glow-ambient",
    "nature":      "stroke-emboss",
    "sunset":      "glow-ambient",
    "aerial":      "stroke-emboss",
    "luxury":      "glow-metal",
    "clean_girl":  "stroke-emboss",
    "vibrant":     "stroke-neon",
    "navy_gold":   "stroke-white",
    "white_paper": "stroke-emboss",
    "dark_data":   "glow-neon",
}

# 默认花字
DEFAULT_HUAZI = "stroke-white"

# 花字适用目标映射
HUAZI_TARGET_MAP = {
    "title":    "stroke-white",    # 标题默认白描边
    "subtitle": "stroke-emboss",   # 副标题默认浮雕
    "price":    "glow-neon",       # 价格默认发光
    "badge":    "badge-rounded",   # 角标默认圆角标签
    "tags":     "badge-rounded",   # 标签默认圆角标签
    "specs_val":"glow-neon",       # 规格数值默认发光
}

# ============================================================
# 花字查询
# ============================================================

def list_huazi():
    """列出所有花字模板"""
    lines = []
    for key, tmpl in sorted(HUAZI_TEMPLATES.items()):
        cat = tmpl.get("category", "")
        name = tmpl.get("name_cn", tmpl.get("name", key))
        desc = tmpl.get("description", "")
        tags = ", ".join(tmpl.get("tags", []))
        lines.append(f"  [{cat}] {key:25s} {name:12s}  {desc}")
        lines.append(f"  {' ' * 40}标签: {tags}")
    return lines

def get_huazi(name):
    """获取花字模板"""
    return HUAZI_TEMPLATES.get(name)

def resolve_huazi_for_target(target, user_choice=None):
    """解析目标元素的花字"""
    if user_choice:
        return user_choice
    return HUAZI_TARGET_MAP.get(target, DEFAULT_HUAZI)

def resolve_huazi_for_template(template_name):
    """根据封面模板推荐花字"""
    return TEMPLATE_HUAZI_MAP.get(template_name, DEFAULT_HUAZI)
