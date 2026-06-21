# -*- coding: utf-8 -*-
"""
字体安装器 v1.0 — 一键下载/安装免费商用中文字体到 fonts/ 目录

用法:
  python scripts/install_fonts.py              # 交互式选择
  python scripts/install_fonts.py --all         # 安装全部
  python scripts/install_fonts.py --list        # 列出可用字体
  python scripts/install_fonts.py --font "思源黑体"  # 安装指定字体
"""

import os
import sys
import zipfile
import io
import hashlib
import json
from urllib.request import urlopen, Request, urlretrieve
from urllib.error import URLError

# ============================================================
# 字体目录
# ============================================================

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(SKILL_DIR, "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

# ============================================================
# 字体定义 — 名称 / 下载URL / 文件列表 / 授权
# ============================================================

FONT_REGISTRY = {
    # ── 思源黑体（内置优先下载）──
    "source-han-sans": {
        "name": "思源黑体",
        "name_cn": "思源黑体",
        "description": "Adobe+Google 联合开发，7字重，屏幕显示锐利，全品类通用",
        "license": "SIL OFL (完全免费商用)",
        "priority": 1,
        "downloads": [
            {
                # jsDelivr CDN 镜像 GitHub
                "url": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-han-sans@release/OTF/SimplifiedChinese/SourceHanSansSC-Bold.otf",
                "filename": "SourceHanSansSC-Bold.otf",
                "size_mb": 8.5,
                "required": True,
            },
            {
                "url": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-han-sans@release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf",
                "filename": "SourceHanSansSC-Regular.otf",
                "size_mb": 8.2,
            },
            {
                "url": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-han-sans@release/OTF/SimplifiedChinese/SourceHanSansSC-Heavy.otf",
                "filename": "SourceHanSansSC-Heavy.otf",
                "size_mb": 8.3,
            },
            {
                "url": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-han-sans@release/OTF/SimplifiedChinese/SourceHanSansSC-Medium.otf",
                "filename": "SourceHanSansSC-Medium.otf",
                "size_mb": 8.2,
            },
            {
                "url": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-han-sans@release/OTF/SimplifiedChinese/SourceHanSansSC-Light.otf",
                "filename": "SourceHanSansSC-Light.otf",
                "size_mb": 8.1,
            },
        ],
        "fallback_url": "https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/SourceHanSansSC-Bold.otf",
        "fallback_is_zip": False,
        "manual_url": "https://github.com/adobe-fonts/source-han-sans/releases",
    },

    # ── 阿里巴巴普惠体 ──
    "alibaba-puhuiti": {
        "name": "阿里巴巴普惠体",
        "name_cn": "阿里巴巴普惠体",
        "description": "阿里官方字体，10字重，笔画扎实饱满，电商/品牌封面首选",
        "license": "阿里巴巴免费商用授权",
        "priority": 2,
        "downloads": [
            {
                "url": "https://raw.githubusercontent.com/dohooo/free-fonts/main/AlibabaPuHuiTi-3/AlibabaPuHuiTi-3-85-Bold.otf",
                "filename": "AlibabaPuHuiTi-3-85-Bold.otf",
                "size_mb": 2.4,
                "required": True,
            },
            {
                "url": "https://raw.githubusercontent.com/dohooo/free-fonts/main/AlibabaPuHuiTi-3/AlibabaPuHuiTi-3-55-Regular.otf",
                "filename": "AlibabaPuHuiTi-3-55-Regular.otf",
                "size_mb": 2.3,
            },
            {
                "url": "https://raw.githubusercontent.com/dohooo/free-fonts/main/AlibabaPuHuiTi-3/AlibabaPuHuiTi-3-95-Heavy.otf",
                "filename": "AlibabaPuHuiTi-3-95-Heavy.otf",
                "size_mb": 2.3,
            },
        ],
        "fallback_url": "https://puhuiti.oss-cn-hangzhou.aliyuncs.com/AlibabaPuHuiTi-3.zip",
        "fallback_is_zip": True,
        "manual_url": "https://puhuiti.oss-cn-hangzhou.aliyuncs.com/AlibabaPuHuiTi-3.zip",
    },

    # ── 站酷高端黑 ──
    "zcool-gaoduanhei": {
        "name": "站酷高端黑",
        "name_cn": "站酷高端黑",
        "description": "笔画扎实厚重，结构紧凑，视觉冲击力极强，科技类标题专用",
        "license": "站酷免费商用 (CC-署名)",
        "priority": 3,
        "downloads": [
            {
                "url": "https://raw.githubusercontent.com/jaywcjlove/free-font/main/docs/fonts/%E7%AB%99%E9%85%B7%E9%AB%98%E7%AB%AF%E9%BB%91/ZCOOL_GaoDuanHei.ttf",
                "filename": "ZCOOL_GaoDuanHei.ttf",
                "size_mb": 3.5,
                "required": True,
            },
        ],
        "fallback_url": "https://www.zcool.com.cn/special/zcoolfonts/",
        "fallback_is_zip": False,
        "manual_url": "https://www.zcool.com.cn/special/zcoolfonts/",
    },

    # ── 站酷酷黑 ──
    "zcool-kuhei": {
        "name": "站酷酷黑",
        "name_cn": "站酷酷黑",
        "description": "线条硬朗有力，时尚力量感，电竞/潮流类标题",
        "license": "站酷免费商用 (CC-署名)",
        "priority": 4,
        "downloads": [
            {
                "url": "https://raw.githubusercontent.com/jaywcjlove/free-font/main/docs/fonts/%E7%AB%99%E9%85%B7%E9%85%B7%E9%BB%91/ZCOOL_KuHei.ttf",
                "filename": "ZCOOL_KuHei.ttf",
                "size_mb": 2.8,
                "required": True,
            },
        ],
        "fallback_url": "https://www.zcool.com.cn/special/zcoolfonts/",
        "fallback_is_zip": False,
        "manual_url": "https://www.zcool.com.cn/special/zcoolfonts/",
    },

    # ── 站酷快乐体 ──
    "zcool-kuaileti": {
        "name": "站酷快乐体",
        "name_cn": "站酷快乐体",
        "description": "笔画圆润柔和，轻松活泼氛围感，美食/亲子/趣味类封面",
        "license": "站酷免费商用 (CC-署名)",
        "priority": 5,
        "downloads": [
            {
                "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf",
                "filename": "ZCOOLKuaiLe-Regular.ttf",
                "size_mb": 1.5,
                "required": True,
            },
        ],
        "fallback_url": "https://fonts.google.com/specimen/ZCOOL+KuaiLe",
        "fallback_is_zip": False,
        "manual_url": "https://fonts.google.com/specimen/ZCOOL+KuaiLe",
    },

    # ── 站酷文艺体 ──
    "zcool-wenyiti": {
        "name": "站酷文艺体",
        "name_cn": "站酷文艺体",
        "description": "现代感+艺术气息，文艺/时尚类封面",
        "license": "站酷免费商用 (CC-署名)",
        "priority": 6,
        "downloads": [
            {
                "url": "https://raw.githubusercontent.com/jaywcjlove/free-font/main/docs/fonts/%E7%AB%99%E9%85%B7%E6%96%87%E8%89%BA%E4%BD%93/ZCOOL_WenYiTi.ttf",
                "filename": "ZCOOL_WenYiTi.ttf",
                "size_mb": 2.5,
                "required": True,
            },
        ],
        "fallback_url": "https://www.zcool.com.cn/special/zcoolfonts/",
        "fallback_is_zip": False,
        "manual_url": "https://www.zcool.com.cn/special/zcoolfonts/",
    },

    # ── 站酷庆科黄油体 ──
    "zcool-qingkehuangyouti": {
        "name": "站酷庆科黄油体",
        "name_cn": "站酷庆科黄油体",
        "description": "可爱风格，圆润俏皮，母婴/亲子/可爱风封面",
        "license": "站酷免费商用 (CC-署名)",
        "priority": 7,
        "downloads": [
            {
                "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/zcoolqingkehuangyou/ZCOOLQingKeHuangYou-Regular.ttf",
                "filename": "ZCOOLQingKeHuangYou-Regular.ttf",
                "size_mb": 8.3,
                "required": True,
            },
        ],
        "fallback_url": "https://fonts.google.com/specimen/ZCOOL+QingKe+HuangYou",
        "fallback_is_zip": False,
        "manual_url": "https://fonts.google.com/specimen/ZCOOL+QingKe+HuangYou",
    },

    # ── OPPO Sans ──
    "oppo-sans": {
        "name": "OPPO Sans",
        "name_cn": "OPPO Sans",
        "description": "中宫自然舒适，字形舒展，现代感强，5字重",
        "license": "OPPO免费商用授权",
        "priority": 8,
        "downloads": [
            {
                "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/opposans/OPPOSans-Bold.ttf",
                "filename": "OPPOSans-Bold.ttf",
                "size_mb": 3.0,
                "required": True,
            },
            {
                "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/opposans/OPPOSans-Regular.ttf",
                "filename": "OPPOSans-Regular.ttf",
                "size_mb": 3.0,
            },
        ],
        "fallback_url": "https://www.coloros.com/article/A00000050/",
        "fallback_is_zip": False,
        "manual_url": "https://www.coloros.com/article/A00000050/",
    },

    # ── 鸿蒙字体 ──
    "harmonyos-sans": {
        "name": "鸿蒙字体",
        "name_cn": "鸿蒙字体",
        "description": "华为开源，笔画清晰干净，轻奢高级感，9字重",
        "license": "华为开源 (SIL OFL 等价)",
        "priority": 9,
        "download_type": "npm_zip",
        "npm_package": "harmonyos-sans@1.0.0",
        "zip_url": "https://cdn.jsdelivr.net/npm/harmonyos-sans@1.0.0/HarmonyOS%20Sans.zip",
        "extract_patterns": ["*_SC_Bold*", "*_SC_Regular*"],
        "downloads": [
            {
                "url": "https://cdn.jsdelivr.net/npm/harmonyos-sans@1.0.0/HarmonyOS%20Sans.zip",
                "filename": "HarmonyOS_Sans_SC_Bold.ttf",
                "size_mb": 52.0,
                "required": True,
                "is_zip": True,
                "zip_member": "HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Bold.ttf",
            },
        ],
        "manual_url": "https://developer.huawei.com/consumer/cn/design/resource/",
    },

    # ── 品如手写体 ──
    "pinru-shouxie": {
        "name": "品如手写体",
        "name_cn": "品如手写体",
        "description": "手写风格流畅自然，生活/Vlog/美食类封面",
        "license": "免费商用",
        "priority": 10,
        "downloads": [
            {
                "url": "https://raw.githubusercontent.com/jaywcjlove/free-font/main/docs/fonts/%E5%93%81%E5%A6%82%E6%89%8B%E5%86%99%E4%BD%93/%E5%93%81%E5%A6%82%E6%89%8B%E5%86%99%E4%BD%93.ttf",
                "filename": "PinRuShouXieTi.ttf",
                "size_mb": 4.5,
                "required": True,
            },
        ],
        "fallback_url": "https://www.fonts.net.cn/font-36827597922.html",
        "fallback_is_zip": False,
        "manual_url": "https://www.fonts.net.cn/font-36827597922.html",
    },
}

# ============================================================
# 下载工具
# ============================================================

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def _download_file(url, dest_path, timeout=60):
    """下载单个文件，带进度显示"""
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        print(f"    下载: {os.path.basename(dest_path)} ...", end=" ", flush=True)
        urlretrieve(url, dest_path)
        size_kb = os.path.getsize(dest_path) / 1024
        print(f"[OK] ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"[FAIL] ({e})")
        return False


def _download_and_unzip(url, dest_dir, timeout=120):
    """下载 zip 并解压到目标目录"""
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), f"font_dl_{os.urandom(4).hex()}.zip")
    try:
        print(f"    下载 zip: {url[:80]}...", end=" ", flush=True)
        req = Request(url, headers={"User-Agent": USER_AGENT})
        urlretrieve(url, tmp)
        print("[OK]")
        print(f"    解压到: {dest_dir} ...", end=" ", flush=True)
        with zipfile.ZipFile(tmp, 'r') as zf:
            for member in zf.namelist():
                ext = os.path.splitext(member)[1].lower()
                if ext in ('.ttf', '.otf', '.ttc'):
                    # 解压到 fonts 目录
                    out_name = os.path.basename(member)
                    out_path = os.path.join(dest_dir, out_name)
                    with zf.open(member) as src, open(out_path, 'wb') as dst:
                        dst.write(src.read())
        os.unlink(tmp)
        print("[OK]")
        return True
    except Exception as e:
        print(f"[FAIL] ({e})")
        if os.path.exists(tmp):
            os.unlink(tmp)
        return False


# ============================================================
# 安装逻辑
# ============================================================

def _download_zip_member(url, dest_path, zip_member, timeout=120):
    """下载ZIP并提取指定成员文件"""
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), f"font_dl_{os.urandom(4).hex()}.zip")
    try:
        print(f"    下载 ZIP: {os.path.basename(dest_path)} ...", end=" ", flush=True)
        req = Request(url, headers={"User-Agent": USER_AGENT})
        urlretrieve(url, tmp)
        size_mb = os.path.getsize(tmp) / 1024 / 1024
        print(f"[OK] ({size_mb:.1f} MB)")

        print(f"    解压: {zip_member} ...", end=" ", flush=True)
        with zipfile.ZipFile(tmp, 'r') as zf:
            # Try exact match first, then fuzzy match
            found = None
            for name in zf.namelist():
                if zip_member in name and name.lower().endswith(('.ttf', '.otf')):
                    found = name
                    break
            if not found:
                # Fallback: extract all matching SC TTF files
                sc_matches = [n for n in zf.namelist()
                             if 'SC' in n and n.lower().endswith(('.ttf', '.otf'))]
                if sc_matches:
                    for m in sc_matches:
                        out = os.path.join(os.path.dirname(dest_path), os.path.basename(m))
                        if not os.path.exists(out):
                            with zf.open(m) as src, open(out, 'wb') as dst:
                                dst.write(src.read())
                            print(f"\n      提取: {os.path.basename(out)}")
                    os.unlink(tmp)
                    print("[OK]")
                    return True
                else:
                    print(f"[FAIL] 在ZIP中未找到匹配文件")
                    os.unlink(tmp)
                    return False
            with zf.open(found) as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())
        os.unlink(tmp)
        print("[OK]")
        return True
    except Exception as e:
        print(f"[FAIL] ({e})")
        if os.path.exists(tmp):
            os.unlink(tmp)
        return False


def install_font(font_key, force=False):
    """安装单个字体（或其必选字重）"""
    info = FONT_REGISTRY.get(font_key)
    if not info:
        print(f"[ERROR] 未知字体: {font_key}")
        return False

    name = info["name_cn"]
    print(f"\n{'='*60}")
    print(f"  安装: {name}  ({info['license']})")
    print(f"  说明: {info['description']}")
    print(f"{'='*60}")

    success_count = 0
    skip_count = 0
    fail_count = 0

    for dl in info.get("downloads", []):
        dest = os.path.join(FONTS_DIR, dl["filename"])

        if os.path.exists(dest) and not force:
            print(f"  [SKIP] 已存在: {dl['filename']}")
            skip_count += 1
            continue

        # Handle ZIP downloads with specific member extraction
        if dl.get("is_zip") and dl.get("zip_member"):
            ok = _download_zip_member(dl["url"], dest, dl["zip_member"])
        else:
            ok = _download_file(dl["url"], dest)

        if ok:
            success_count += 1
        else:
            fail_count += 1
            if dl.get("required"):
                print(f"    [WARN] 必选字重下载失败，尝试备用源...")

    # 如果直接下载全部失败，尝试备用 zip 源
    if success_count == 0 and fail_count > 0:
        fallback = info.get("fallback_url")
        if fallback:
            is_zip = info.get("fallback_is_zip", False)
            if is_zip:
                print(f"    尝试备用 zip 源...")
                ok = _download_and_unzip(fallback, FONTS_DIR)
                if ok:
                    success_count += 1
                    fail_count -= 1

    # 手动下载提示
    if success_count == 0 and skip_count == 0:
        manual = info.get("manual_url")
        if manual:
            print(f"\n  [WARN] 自动下载失败，请手动下载:")
            print(f"     {name}")
            print(f"     官方地址: {manual}")
            print(f"     → 将 .ttf/.otf 文件放入: {FONTS_DIR}")
            return False
    elif success_count > 0:
        print(f"  [OK] {name} 安装完成 ({success_count} 个文件)")

    return success_count > 0 or skip_count > 0


def install_all(force=False):
    """安装所有字体"""
    total = len(FONT_REGISTRY)
    ok = 0
    # 按优先级排序
    items = sorted(FONT_REGISTRY.items(), key=lambda x: x[1].get("priority", 99))
    for key, info in items:
        if install_font(key, force=force):
            ok += 1
        else:
            print(f"  [WARN] {info['name_cn']} 需要手动安装")

    print(f"\n{'='*60}")
    print(f"  安装完成: {ok}/{total} 个字体家族")
    print(f"  字体目录: {FONTS_DIR}")
    print(f"{'='*60}")
    return ok


def list_fonts():
    """列出可用字体"""
    print(f"\n{'='*70}")
    print(f"  免费商用中文字体列表 ({len(FONT_REGISTRY)} 款)")
    print(f"{'='*70}\n")
    for key, info in sorted(FONT_REGISTRY.items(), key=lambda x: x[1].get("priority", 99)):
        installed = any(
            os.path.exists(os.path.join(FONTS_DIR, dl["filename"]))
            for dl in info.get("downloads", [])
        )
        status = "[OK] 已安装" if installed else "[  ] 未安装"
        print(f"  [{info['priority']:2d}] {info['name_cn']:16s}  {status}")
        print(f"       {info['description']}")
        print(f"       授权: {info['license']}")
        if not installed:
            manual = info.get("manual_url", "")
            if manual:
                print(f"       手动下载: {manual}")
        print()


def show_status():
    """显示安装状态"""
    installed_families = []
    for key, info in FONT_REGISTRY.items():
        installed_files = []
        for dl in info.get("downloads", []):
            fp = os.path.join(FONTS_DIR, dl["filename"])
            if os.path.exists(fp):
                installed_files.append(dl["filename"])
        if installed_files:
            installed_families.append((info["name_cn"], installed_files))

    print(f"\n  字体目录: {FONTS_DIR}")
    if installed_families:
        print(f"  已安装 {len(installed_families)}/{len(FONT_REGISTRY)} 个字体家族:\n")
        for name, files in installed_families:
            print(f"    [OK] {name} ({len(files)} 个文件)")
    else:
        print(f"  [WARN] 尚未安装任何字体，运行 install_fonts.py --all 开始安装")


# ============================================================
# CLI
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="字体安装器 — 下载免费商用中文字体到 fonts/ 目录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --list            列出所有可用字体及状态
  %(prog)s --all              安装全部字体
  %(prog)s --font "思源黑体"  安装指定字体
  %(prog)s --status           查看安装状态
  %(prog)s --all --force      强制重新下载全部
        """
    )
    parser.add_argument("--list", action="store_true", help="列出所有可用字体")
    parser.add_argument("--all", action="store_true", help="安装全部字体")
    parser.add_argument("--font", type=str, help="安装指定字体名称")
    parser.add_argument("--force", action="store_true", help="强制覆盖已存在的文件")
    parser.add_argument("--status", action="store_true", help="显示安装状态")

    args = parser.parse_args()

    if args.list:
        list_fonts()
    elif args.status:
        show_status()
    elif args.all:
        install_all(force=args.force)
    elif args.font:
        # 模糊匹配字体名
        matched = None
        for key, info in FONT_REGISTRY.items():
            if args.font in info["name_cn"] or args.font in info["name"] or args.font == key:
                matched = key
                break
        if matched:
            install_font(matched, force=args.force)
        else:
            print(f"[ERROR] 未找到字体: {args.font}")
            print(f"可用字体: {', '.join(info['name_cn'] for info in FONT_REGISTRY.values())}")
    else:
        # 默认：交互式
        list_fonts()
        print("用法:")
        print("  python scripts/install_fonts.py --all     # 安装全部")
        print("  python scripts/install_fonts.py --list    # 列出字体")
        print("  python scripts/install_fonts.py --status  # 查看状态")
        print("  python scripts/install_fonts.py --font \"思源黑体\"  # 安装指定")


if __name__ == "__main__":
    main()
