# -*- coding: utf-8 -*-
"""
花字渲染引擎 v1.0 — 多层文字叠加渲染器
将花字模板描述翻译为 PIL 绘制指令
"""

import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from font_manager import get_font_manager
from huazi_templates import HUAZI_TEMPLATES, DEFAULT_HUAZI

# ============================================================
# 颜色工具
# ============================================================

def _hex_to_rgb(hex_str):
    """#RRGGBB / #RRGGBBAA → (R, G, B) 或 (R, G, B, A)"""
    h = hex_str.lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    elif len(h) == 8:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
    return (255, 255, 255)

def _darken(color, factor=0.4):
    """颜色变暗"""
    if len(color) == 3:
        return tuple(max(0, int(c * (1 - factor))) for c in color)
    if len(color) == 4:
        return tuple([max(0, int(color[0] * (1 - factor))),
                       max(0, int(color[1] * (1 - factor))),
                       max(0, int(color[2] * (1 - factor))),
                       color[3]])
    return color

def _resolve_color(spec, ctx):
    """解析颜色引用 → RGB/RGBA tuple

    ctx = {"accent": (235,40,45), "bg": (10,10,12), "white": (255,255,255), ...}
    spec 可以是 "#FF0000" hex / "accent" 等 key / "darken(accent, 0.4)" / tuple
    """
    if spec is None:
        return ctx.get("white", (255, 255, 255))
    if isinstance(spec, (tuple, list)):
        return tuple(spec)

    spec_str = str(spec)

    # darken(accent, 0.4) 语法
    if spec_str.startswith("darken("):
        inner = spec_str[7:-1]  # "accent, 0.4"
        parts = inner.split(",")
        inner_color = _resolve_color(parts[0].strip(), ctx)
        factor = float(parts[1].strip()) if len(parts) > 1 else 0.3
        return _darken(inner_color, factor)

    # hex
    if spec_str.startswith("#"):
        return _hex_to_rgb(spec_str)

    # ctx key
    if spec_str in ctx:
        return ctx[spec_str]

    # fallback
    return ctx.get("white", (255, 255, 255))


# ============================================================
# 文字测量
# ============================================================

def _text_bbox(text, font):
    """返回 (width, height)"""
    bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


# ============================================================
# 逐层渲染函数
# ============================================================

def _render_fill(base, text, font, x, y, color):
    """简单填充"""
    ImageDraw.Draw(base).text((x, y), text, fill=color, font=font)


def _render_stroke_layer(base, text, font, x, y, color, width):
    """描边图层：在 (x,y) 附近每个像素绘制文字"""
    draw = ImageDraw.Draw(base)
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, fill=color, font=font)


def _render_glow_layer(base, text, font, x, y, color, radius, opacity):
    """发光图层：GaussianBlur + alpha 控制"""
    tw, th = _text_bbox(text, font)
    pad = radius * 3
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    # 多层叠加模拟强发光
    if isinstance(color, tuple) and len(color) == 4:
        glow_color = color
    else:
        glow_color = (color[0], color[1], color[2], min(255, opacity))

    for r_factor in [1.0, 0.6, 0.3]:
        r = int(radius * r_factor)
        glow_c = (glow_color[0], glow_color[1], glow_color[2], min(255, int(opacity * r_factor)))
        ld.text((pad, pad), text, fill=glow_c, font=font)
        if r > 1:
            layer = layer.filter(ImageFilter.GaussianBlur(r))

    base.paste(layer, (x - pad, y - pad), layer)


def _render_shadow_layer(base, text, font, x, y, color, offset, blur):
    """投影图层"""
    tw, th = _text_bbox(text, font)
    pad = blur * 3 + max(abs(offset[0]), abs(offset[1]))
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    sx, sy = pad + offset[0], pad + offset[1]
    if isinstance(color, tuple) and len(color) == 4:
        shadow_color = color
    else:
        shadow_color = (color[0], color[1], color[2], 150)
    ld.text((sx, sy), text, fill=shadow_color, font=font)
    if blur > 0:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.paste(layer, (x - pad, y - pad), layer)


def _render_gradient_fill(base, text, font, x, y, colors, direction):
    """渐变填充文字：用渐变图作为文字 mask"""
    tw, th = _text_bbox(text, font)
    pad = 4

    # 创建渐变图
    if direction == "vertical":
        grad = Image.new("RGBA", (tw + pad * 2, th + pad * 2))
        for iy in range(th + pad * 2):
            ratio = iy / max(1, th + pad * 2 - 1)
            c = _interpolate_colors(colors, ratio)
            ImageDraw.Draw(grad).line([(0, iy), (tw + pad * 2, iy)], fill=c)
    elif direction == "horizontal":
        grad = Image.new("RGBA", (tw + pad * 2, th + pad * 2))
        for ix in range(tw + pad * 2):
            ratio = ix / max(1, tw + pad * 2 - 1)
            c = _interpolate_colors(colors, ratio)
            ImageDraw.Draw(grad).line([(ix, 0), (ix, th + pad * 2)], fill=c)
    else:  # diagonal
        grad = Image.new("RGBA", (tw + pad * 2, th + pad * 2))
        for iy in range(th + pad * 2):
            for ix in range(tw + pad * 2):
                ratio = (ix + iy) / max(1, tw + th + pad * 4 - 2)
                c = _interpolate_colors(colors, ratio)
                grad.putpixel((ix, iy), c)

    # 创建文字 mask
    mask = Image.new("L", (tw + pad * 2, th + pad * 2), 0)
    ImageDraw.Draw(mask).text((pad, pad), text, fill=255, font=font)

    # 用 mask 合成渐变到画布
    grad_rgba = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    grad_rgba.paste(grad, (0, 0))
    base.paste(grad_rgba, (x - pad, y - pad), mask)


def _interpolate_colors(colors, ratio):
    """在两个颜色之间插值"""
    if len(colors) == 1:
        return colors[0]
    n = len(colors) - 1
    idx = min(int(ratio * n), n - 1)
    local_ratio = (ratio * n) - idx
    c1, c2 = colors[idx], colors[min(idx + 1, n)]
    return tuple(int(c1[i] + (c2[i] - c1[i]) * local_ratio) for i in range(min(len(c1), len(c2))))


def _render_long_shadow(base, text, font, x, y, color, length, angle):
    """长投影：从 (x,y) 沿 angle 方向逐像素延伸"""
    rad = math.radians(angle)
    dx = math.cos(rad)
    dy = math.sin(rad)
    draw = ImageDraw.Draw(base)
    for i in range(length, 1, -1):
        alpha = int(180 * (1 - i / length))
        if isinstance(color, tuple) and len(color) == 4:
            c = color[:3] + (min(255, alpha),)
        else:
            c = (color[0], color[1], color[2], alpha)
        sx = x + int(dx * i)
        sy = y + int(dy * i)
        draw.text((sx, sy), text, fill=c, font=font)


def _render_extrude(base, text, font, x, y, color, depth):
    """3D 挤出：向下逐层偏移"""
    draw = ImageDraw.Draw(base)
    for i in range(depth, 0, -1):
        alpha = int(200 * (1 - i / depth))
        if isinstance(color, tuple) and len(color) == 4:
            c = color[:3] + (min(255, alpha),)
        else:
            c = (color[0], color[1], color[2], alpha)
        draw.text((x, y + i), text, fill=c, font=font)


def _render_copy_layer(base, text, font, x, y, color, offset, opacity):
    """偏移半透明副本"""
    ox, oy = offset
    tw, th = _text_bbox(text, font)
    pad = max(abs(ox), abs(oy)) + 4
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    if isinstance(color, tuple) and len(color) == 4:
        c = color
    else:
        c = (color[0], color[1], color[2], int(255 * opacity))
    ld.text((pad + ox, pad + oy), text, fill=c, font=font)
    base.paste(layer, (x - pad, y - pad), layer)


def _render_badge_bg(base, text, font, x, y, color, shape, padding_x, padding_y, radius):
    """底衬背景"""
    tw, th = _text_bbox(text, font)
    bw = tw + padding_x * 2
    bh = th + padding_y * 2
    bx = x - padding_x
    by = y - padding_y
    draw = ImageDraw.Draw(base)

    if shape == "rounded":
        draw.rounded_rectangle([bx, by, bx + bw, by + bh],
                               radius=radius, fill=color)
    elif shape == "ribbon":
        # 平行四边形绶带
        skew = 12
        pts = [(bx + skew, by), (bx + bw, by),
               (bx + bw - skew, by + bh), (bx, by + bh)]
        draw.polygon(pts, fill=color)
    elif shape == "burst":
        # 爆炸贴纸：圆角矩形 + 锯齿边缘（简化版用大圆角+粗描边近似）
        draw.rounded_rectangle([bx, by, bx + bw, by + bh],
                               radius=max(radius, 12), fill=color)
        # 添加锯齿小三角装饰
        for side_x in [bx + bw//4, bx + bw*3//4]:
            tri = [(side_x - 8, by - 8), (side_x + 8, by - 8), (side_x, by)]
            draw.polygon(tri, fill=color)


# ============================================================
# HuaziRenderer
# ============================================================

class HuaziRenderer:
    """花字多层渲染器"""

    def __init__(self, font_manager=None):
        self.fm = font_manager or get_font_manager()

    def render(self, base, text, template_name, x, y,
               font_family=None, font_weight="Bold", font_size=46,
               accent_color=None, bg_color=None, custom_colors=None):
        """
        在 base 画布上渲染花字

        参数:
          base:           PIL Image (RGBA) 画布
          text:           文字内容
          template_name:  花字模板名 (如 "stroke-white")
          x, y:           文字左上角坐标
          font_family:    字体家族（None=自动选择）
          font_weight:    字重
          font_size:      字号
          accent_color:   覆盖强调色 (R,G,B)
          bg_color:       覆盖背景色 (R,G,B)
          custom_colors:  自定义颜色 dict {"accent": (R,G,B), ...}

        返回:
          (width, height) 文字包围盒
        """
        template = HUAZI_TEMPLATES.get(template_name)
        if not template:
            template = HUAZI_TEMPLATES.get(DEFAULT_HUAZI)
        if not template:
            return _text_bbox(text, self.fm.get(weight="Bold", size=font_size))

        # 构建颜色上下文
        color_ctx = {
            "accent": accent_color or (235, 40, 45),
            "bg":     bg_color or (10, 10, 12),
            "white":  (255, 255, 255),
        }
        if custom_colors:
            color_ctx.update(custom_colors)

        # 获取字体
        font = self.fm.get(family=font_family, weight=font_weight, size=font_size)

        # 逐层渲染（从底到顶）
        for layer in template.get("layers", []):
            self._render_layer(base, text, font, x, y, layer, color_ctx)

        return _text_bbox(text, font)

    def _render_layer(self, base, text, font, x, y, layer, ctx):
        """渲染单个图层"""
        ltype = layer.get("type")
        color_spec = layer.get("color")
        color = _resolve_color(color_spec, ctx)

        if ltype == "fill":
            _render_fill(base, text, font, x, y, color)

        elif ltype == "stroke":
            width = layer.get("width", 3)
            _render_stroke_layer(base, text, font, x, y, color, width)

        elif ltype == "glow":
            radius = layer.get("radius", 8)
            opacity = layer.get("opacity", 150)
            _render_glow_layer(base, text, font, x, y, color, radius, opacity)

        elif ltype == "shadow":
            offset = layer.get("offset", (2, 2))
            blur = layer.get("blur", 4)
            _render_shadow_layer(base, text, font, x, y, color, offset, blur)

        elif ltype == "gradient":
            colors = [_resolve_color(c, ctx) for c in layer.get("colors", [])]
            direction = layer.get("direction", "vertical")
            _render_gradient_fill(base, text, font, x, y, colors, direction)

        elif ltype == "long_shadow":
            length = layer.get("length", 10)
            angle = layer.get("angle", 135)
            _render_long_shadow(base, text, font, x, y, color, length, angle)

        elif ltype == "extrude":
            depth = layer.get("depth", 6)
            _render_extrude(base, text, font, x, y, color, depth)

        elif ltype == "copy":
            offset = layer.get("offset", (4, 0))
            opacity = layer.get("opacity", 0.5)
            _render_copy_layer(base, text, font, x, y, color, offset, opacity)

        elif ltype == "badge":
            shape = layer.get("shape", "rounded")
            px = layer.get("padding_x", 10)
            py = layer.get("padding_y", 6)
            radius = layer.get("radius", 8)
            _render_badge_bg(base, text, font, x, y, color, shape, px, py, radius)

    def render_simple(self, base, text, x, y, font_size=46,
                      font_family=None, font_weight="Bold",
                      fill_color=None, stroke_color=None, stroke_width=0,
                      glow_color=None, glow_radius=8, glow_opacity=150,
                      shadow_color=None, shadow_offset=(2, 2), shadow_blur=4):
        """简化 API：直接指定效果参数，不依赖模板"""
        color_ctx = {
            "accent": fill_color or (255, 255, 255),
            "white": (255, 255, 255),
            "bg": (0, 0, 0),
        }
        font = self.fm.get(family=font_family, weight=font_weight, size=font_size)

        if shadow_color:
            _render_shadow_layer(base, text, font, x, y,
                                _resolve_color(shadow_color, color_ctx),
                                shadow_offset, shadow_blur)
        if glow_color:
            _render_glow_layer(base, text, font, x, y,
                              _resolve_color(glow_color, color_ctx),
                              glow_radius, glow_opacity)
        if stroke_width > 0 and stroke_color:
            _render_stroke_layer(base, text, font, x, y,
                                _resolve_color(stroke_color, color_ctx),
                                stroke_width)
        _render_fill(base, text, font, x, y,
                    _resolve_color(fill_color, color_ctx))

        return _text_bbox(text, font)


# ============================================================
# 全局单例
# ============================================================

_huazi_renderer = None

def get_huazi_renderer(font_manager=None):
    global _huazi_renderer
    if _huazi_renderer is None or font_manager is not None:
        _huazi_renderer = HuaziRenderer(font_manager)
    return _huazi_renderer


def render_huazi(base, text, template_name, x, y, **kwargs):
    """便捷函数"""
    hr = get_huazi_renderer()
    return hr.render(base, text, template_name, x, y, **kwargs)
