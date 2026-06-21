# 字体目录

## 快速安装

```bash
# 列出可用字体
python scripts/install_fonts.py --list

# 安装全部免费商用字体
python scripts/install_fonts.py --all

# 安装指定字体
python scripts/install_fonts.py --font "思源黑体"

# 查看安装状态
python scripts/install_fonts.py --status
```

## 可用字体 (10 款)

| # | 字体 | 风格 | 适用品类 | 授权 |
|---|------|------|----------|------|
| 1 | 思源黑体 | 现代无衬线 | 全品类通用 | SIL OFL |
| 2 | 阿里巴巴普惠体 | 稳重有力 | 电商/科技/商务 | 阿里免费商用 |
| 3 | 站酷高端黑 | 粗犷冲击 | 科技/潮流 | CC-署名 |
| 4 | 站酷酷黑 | 硬朗力量 | 电竞/潮流 | CC-署名 |
| 5 | 站酷快乐体 | 圆润活泼 | 美食/亲子 | CC-署名 |
| 6 | 站酷文艺体 | 清新艺术 | 时尚/文艺 | CC-署名 |
| 7 | 站酷庆科黄油体 | 可爱圆润 | 母婴/亲子 | CC-署名 |
| 8 | OPPO Sans | 现代舒展 | 科技/商务 | OPPO免费商用 |
| 9 | 鸿蒙字体 | 轻奢高级 | 时尚/商务 | 华为开源 |
| 10 | 品如手写体 | 手写自然 | 生活/Vlog | 免费商用 |

## 手动安装

将 `.ttf` 或 `.otf` 字体文件放入此目录，脚本会自动发现并注册。

支持的格式: `.ttf` `.otf` `.ttc`

## 版权说明

所有内置字体均为免费商用授权，可用于个人和商业项目（短视频封面、电商主图等）。
部分字体要求署名（如站酷系列 CC-署名协议），请在使用时注意保留版权信息。

## 字体下载官方链接

- 思源黑体: https://github.com/adobe-fonts/source-han-sans
- 阿里巴巴普惠体: https://puhuiti.oss-cn-hangzhou.aliyuncs.com/AlibabaPuHuiTi-3.zip
- 站酷系列: https://www.zcool.com.cn/special/zcoolfonts/
- OPPO Sans: https://open.oppomobile.com/new/developmentDoc/info?id=13193
- 鸿蒙字体: https://developer.huawei.com/consumer/cn/design/resource/
