# -*- coding: utf-8 -*-
"""
字体管理器 v1.1 — 字体发现、注册、缓存、回退、随机选择
支持：系统字体 + 内置 fonts/ 目录 + 用户自定义路径
v1.1: 新增 get_random() 随机字体选择
"""

import os
import glob
import struct
import random
from PIL import ImageFont

# ============================================================
# 字体元数据
# ============================================================

# 中文别名 → 英文 family 名映射（用于文件匹配）
FONT_ALIASES = {
    "思源黑体":    ["Source Han Sans SC", "Source Han Sans CN", "Noto Sans CJK SC",
                  "SourceHanSansSC", "SourceHanSansCN", "NotoSansCJKsc", "NotoSansSC"],
    "思源宋体":    ["Source Han Serif SC", "Source Han Serif CN", "Noto Serif CJK SC",
                  "SourceHanSerifSC", "SourceHanSerifCN", "NotoSerifCJKsc"],
    "阿里巴巴普惠体": ["Alibaba PuHuiTi", "Alibaba Sans", "AlibabaPuHuiTi",
                    "AlibabaSans", "Alibaba PuHuiTi 3.0",
                    "思源黑体"],  # ★ 无字体文件时回退到思源黑体
    "阿里普惠体":  ["Alibaba PuHuiTi", "Alibaba Sans", "AlibabaPuHuiTi",
                  "AlibabaSans", "Alibaba PuHuiTi 3.0",
                  "思源黑体"],  # ★ 回退
    "站酷高端黑":  ["ZCOOL GaoDuanHei", "ZCOOL GaoDuan", "站酷高端黑",
                  "ZCOOLGaoDuanHei", "ZCOOL_GaoDuanHei"],
    "站酷酷黑":    ["ZCOOL KuHei", "ZCOOL KuHeiTi", "站酷酷黑",
                  "ZCOOLKuHei", "ZCOOL_KuHei"],
    "站酷快乐体":  ["ZCOOL KuaiLeTi", "ZCOOL KuaiLe", "站酷快乐体",
                  "ZCOOLKuaiLeTi", "ZCOOL_KuaiLeTi"],
    "站酷文艺体":  ["ZCOOL WenYiTi", "ZCOOL WenYi", "站酷文艺体",
                  "ZCOOLWenYiTi", "ZCOOL_WenYiTi"],
    "站酷庆科黄油体": ["ZCOOL QingKe HuangYouTi", "ZCOOL QingKeHuangYou",
                    "站酷庆科黄油体", "ZCOOL_QingKeHuangYouTi"],
    "OPPO Sans":   ["OPPO Sans", "OPPOSans", "OPPO Sans SC"],
    "鸿蒙字体":    ["HarmonyOS Sans SC", "HarmonyOS Sans", "HarmonyOS_Sans_SC",
                  "HarmonyOSSansSC"],
    "品如手写体":  ["PinRu ShouXie", "PinRuShouXie", "品如手写体"],
    # 系统字体
    "微软雅黑":    ["Microsoft YaHei", "msyh", "Microsoft YaHei UI"],
    "黑体":        ["SimHei", "黑体", "Hei"],
    "宋体":        ["SimSun", "宋体", "Song"],
    "等线":        ["DengXian", "等线"],
    "楷体":        ["KaiTi", "楷体", "Kai"],
}

# 字重解析
WEIGHT_KEYWORDS = {
    "Thin":       100, "Hairline": 100,
    "ExtraLight": 200, "UltraLight": 200,
    "Light":      300,
    "Regular":    400, "Normal": 400, "": 400,
    "Medium":     500,
    "SemiBold":   600, "DemiBold": 600,
    "Bold":       700,
    "ExtraBold":  800, "UltraBold": 800,
    "Heavy":      900, "Black": 900,
}

WEIGHT_CN = {
    100: "Thin", 200: "ExtraLight", 300: "Light",
    400: "Regular", 500: "Medium",
    600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Heavy",
}


def _parse_font_meta(filepath):
    """从文件名+路径解析字体元数据 (family, weight_num, style)"""
    fname = os.path.splitext(os.path.basename(filepath))[0]

    # 尝试解析 family 和 weight
    family = fname
    weight = 400
    style = "Regular"

    # 按 "-" 分割提取 weight 关键字
    parts = fname.replace("_", "-").replace(" ", "-").split("-")

    # 先检测已知 family 别名
    detected_family = None
    for cn_name, aliases in FONT_ALIASES.items():
        for alias in aliases:
            alias_clean = alias.replace(" ", "").lower()
            fname_clean = fname.replace(" ", "").replace("_", "").replace("-", "").lower()
            if alias_clean in fname_clean:
                detected_family = cn_name
                break
        if detected_family:
            break
    if detected_family:
        family = detected_family

    # 检测字重
    for kw, w in sorted(WEIGHT_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if kw and kw.lower() in fname.lower():
            weight = w
            break

    # 检测斜体
    if "Italic" in fname or "Oblique" in fname:
        style = "Italic"

    return family, weight, style


# ============================================================
# FontManager
# ============================================================

class FontManager:
    """字体管理器 — 发现、注册、缓存、获取"""

    def __init__(self, font_dirs=None):
        self.font_dirs = font_dirs or self._default_dirs()
        self._registry = {}    # {family: {weight_num: (filepath, style)}}
        self._cache = {}       # {(family, weight, size): ImageFont}
        self._file_index = []  # [(filepath, family, weight, style)]
        self._cjk_families = set()  # ★ 支持中文的字体家族
        self._builtin_dir = self.font_dirs[0] if self.font_dirs else ''
        self._scan()

    @staticmethod
    def _default_dirs():
        dirs = []
        # 技能内置 fonts/
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        builtin = os.path.join(skill_dir, "fonts")
        if os.path.isdir(builtin):
            dirs.append(builtin)
        # 系统字体目录
        if os.name == "nt":  # Windows
            windir = os.environ.get("WINDIR", "C:/Windows")
            dirs.append(os.path.join(windir, "Fonts"))
        elif os.uname().sysname == "Darwin":  # macOS
            dirs.extend([
                "/System/Library/Fonts/",
                "/Library/Fonts/",
                os.path.expanduser("~/Library/Fonts/"),
            ])
        else:  # Linux
            dirs.extend([
                "/usr/share/fonts/",
                "/usr/local/share/fonts/",
                os.path.expanduser("~/.fonts/"),
            ])
        return dirs

    def _scan(self):
        """扫描所有字体目录"""
        exts = {".ttf", ".otf", ".ttc"}
        for d in self.font_dirs:
            if not os.path.isdir(d):
                continue
            for root, _dirs, files in os.walk(d):
                for f in files:
                    if os.path.splitext(f)[1].lower() in exts:
                        fp = os.path.join(root, f)
                        family, weight, style = _parse_font_meta(fp)
                        self._file_index.append((fp, family, weight, style))
                        self._registry.setdefault(family, {})[weight] = (fp, style)
                        # ★ 内置字体目录的在建字体全部支持中文
                        if os.path.abspath(d) == os.path.abspath(self._builtin_dir):
                            self._cjk_families.add(family)

    def get(self, family=None, weight="Bold", size=46):
        """
        获取 ImageFont 对象（带缓存）

        family: 字体名（中文或英文），None=自动选第一个
        weight:  字重名称 (Regular/Bold/Heavy 等) 或数值 (400/700/900)
        size:    字号
        """
        # 解析 weight
        if isinstance(weight, str):
            weight_num = WEIGHT_KEYWORDS.get(weight, 400)
        else:
            weight_num = int(weight)

        # 解析 family
        resolved_family = self._resolve_family(family)

        # 查缓存
        cache_key = (resolved_family, weight_num, size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 查找最匹配的字重
        filepath = self._find_best_weight(resolved_family, weight_num)

        if filepath:
            try:
                font = ImageFont.truetype(filepath, size)
            except Exception:
                font = self._fallback_font(size)
        else:
            font = self._fallback_font(size)

        self._cache[cache_key] = font
        return font

    def _resolve_family(self, family):
        """解析字体家族名 → 注册表中的 key"""
        if family is None:
            # 返回第一个可用家族
            if self._registry:
                return list(self._registry.keys())[0]
            return None

        # 直接命中
        if family in self._registry:
            return family

        # 通过别名匹配
        if family in FONT_ALIASES:
            for alias in FONT_ALIASES[family]:
                for reg_family in self._registry:
                    if alias.replace(" ", "").lower() in reg_family.replace(" ", "").lower():
                        return reg_family

        # 模糊匹配
        family_lower = family.lower().replace(" ", "")
        for reg_family in self._registry:
            if family_lower in reg_family.lower().replace(" ", ""):
                return reg_family

        return None

    def _find_best_weight(self, family, target_weight):
        """查找最接近目标字重的字体文件"""
        if family not in self._registry:
            return self._any_file()

        weights = self._registry[family]
        if not weights:
            return self._any_file()

        # 精确匹配
        if target_weight in weights:
            return weights[target_weight][0]

        # 最接近的更高字重
        higher = [w for w in weights if w >= target_weight]
        if higher:
            return weights[min(higher)][0]

        # 最接近的更低的字重
        return weights[max(weights)][0]

    def _any_file(self):
        """返回任意可用字体文件"""
        for entries in self._registry.values():
            for filepath, _style in entries.values():
                return filepath
        return None

    def _fallback_font(self, size):
        """最终回退"""
        try:
            return ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", size)
        except Exception:
            try:
                return ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", size)
            except Exception:
                return ImageFont.load_default()

    # ---- 查询接口 ----

    def list_families(self):
        """列出所有可用字体家族"""
        lines = []
        for family in sorted(self._registry.keys()):
            weights = sorted(self._registry[family].keys())
            weight_str = ", ".join(f"{w}({WEIGHT_CN.get(w, str(w))})" for w in weights)
            lines.append(f"  {family}  →  {weight_str}")
        return lines

    def list_weights(self, family):
        """列出某字体所有可用字重"""
        resolved = self._resolve_family(family)
        if resolved and resolved in self._registry:
            return sorted(self._registry[resolved].keys())
        return []

    def is_available(self, family):
        """检查字体是否可用"""
        return self._resolve_family(family) is not None

    def get_font_path(self, family, weight="Bold"):
        """获取字体文件路径（用于外部使用）"""
        resolved = self._resolve_family(family)
        if isinstance(weight, str):
            weight_num = WEIGHT_KEYWORDS.get(weight, 400)
        else:
            weight_num = int(weight)
        if resolved and resolved in self._registry:
            return self._find_best_weight(resolved, weight_num)
        return self._any_file()

    def list_available(self):
        """列出所有可用字体家族（详细信息）"""
        result = []
        for family in sorted(self._registry.keys()):
            weights = sorted(self._registry[family].keys())
            result.append({
                'family': family,
                'weights': weights,
                'weight_names': [WEIGHT_CN.get(w, str(w)) for w in weights]
            })
        return result

    def get_random(self, weight="Bold", size=46, exclude_families=None):
        """
        随机选择一个支持中文的字体家族并返回字体对象

        weight: 字重名称 (Regular/Bold/Heavy 等) 或数值
        size:   字号
        exclude_families: 排除的字体家族列表

        返回: (ImageFont, family_name)
        """
        exclude_families = exclude_families or []

        # ★ 只从支持中文的字体中随机选择（内置 fonts/ 目录的字体）
        cjk_available = [
            f for f in self._cjk_families
            if f not in exclude_families
        ]

        if not cjk_available:
            # 回退：从全部字体中过滤常见拉丁字体名
            cjk_available = [
                f for f in self._registry.keys()
                if f not in exclude_families
                and 'Arial' not in f and 'Tahoma' not in f and 'Segoe' not in f
                and 'Calibri' not in f and 'Times' not in f and 'Georgia' not in f
                and 'Impact' not in f and 'Verdana' not in f and 'Trebuchet' not in f
                and 'Courier' not in f and 'Comic' not in f and 'Consola' not in f
                and 'Roboto' not in f and 'Corbel' not in f and 'Constantia' not in f
                and 'Cambria' not in f and 'Candara' not in f and 'Palatino' not in f
                and 'Lucida' not in f and 'Microsoft' not in f and 'Malgun' not in f
                and 'Gulim' not in f and 'Batang' not in f and 'Dotum' not in f
                and 'Nirmala' not in f and 'Ebrima' not in f and 'Gadugi' not in f
                and 'Leelawadee' not in f and 'Javanese' not in f and 'Myanmar' not in f
            ]

        if not cjk_available:
            cjk_available = list(self._registry.keys())

        # 随机选择
        family = random.choice(cjk_available)

        # 获取字体
        font = self.get(family=family, weight=weight, size=size)
        return font, family

    @property
    def available_count(self):
        return sum(len(w) for w in self._registry.values())


# ============================================================
# 全局单例
# ============================================================

_font_manager = None

def get_font_manager(font_dirs=None):
    global _font_manager
    if _font_manager is None or font_dirs is not None:
        _font_manager = FontManager(font_dirs)
    return _font_manager

# 便捷函数
def font(size=46, bold=False, family=None, weight=None):
    """获取字体（兼容旧 _font() 接口）"""
    fm = get_font_manager()
    if weight:
        return fm.get(family=family, weight=weight, size=size)
    if bold:
        return fm.get(family=family, weight="Bold", size=size)
    return fm.get(family=family, weight="Regular", size=size)
