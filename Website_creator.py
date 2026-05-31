#!/usr/bin/env python3
"""
简易网站可视化编辑器 - WYSIWYG Website Builder
PPT风格界面，支持文字特效、背景特效，导出HTML文档。
"""

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox, simpledialog
import json
import os
import uuid
import base64
import webbrowser
import tempfile
from dataclasses import dataclass
from typing import Optional

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ============================================================
# 特效 CSS / JS 模板
# ============================================================

TEXT_EFFECTS_CSS = """
/* ------ 文字艺术样式 ------ */
.text-effect-art-gradient {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
}
.text-effect-art-shadow {
  text-shadow: 3px 3px 6px rgba(0,0,0,0.3), 0 0 2px rgba(0,0,0,0.1) !important;
}
.text-effect-art-outline {
  color: transparent !important;
  -webkit-text-stroke: 2px #333 !important;
  text-stroke: 2px #333 !important;
}
.text-effect-art-3d {
  text-shadow: 1px 1px 0 #ccc, 2px 2px 0 #bbb, 3px 3px 0 #aaa, 4px 4px 0 #999, 5px 5px 0 #888, 6px 6px 0 #777 !important;
}
.text-effect-art-neon {
  text-shadow: 0 0 7px #fff, 0 0 10px #fff, 0 0 21px #fff, 0 0 42px #0fa, 0 0 82px #0fa, 0 0 92px #0fa, 0 0 102px #0fa, 0 0 151px #0fa !important;
}

/* ------ 文字动画 ------ */
@keyframes text-shake {
  0%, 100% { transform: translateX(0); }
  10% { transform: translateX(-4px) rotate(-1deg); }
  20% { transform: translateX(4px) rotate(1deg); }
  30% { transform: translateX(-3px) rotate(-0.5deg); }
  40% { transform: translateX(3px) rotate(0.5deg); }
  50% { transform: translateX(-2px); }
  60% { transform: translateX(2px); }
  70% { transform: translateX(-1px); }
  80% { transform: translateX(1px); }
}
.text-effect-anim-shake { display: inline-block; animation: text-shake 0.6s ease-in-out infinite; }

@keyframes text-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}
.text-effect-anim-bounce { display: inline-block; animation: text-bounce 0.8s ease-in-out infinite; }

@keyframes text-glow {
  0%, 100% { text-shadow: 0 0 5px currentColor, 0 0 10px currentColor; }
  50% { text-shadow: 0 0 20px currentColor, 0 0 40px currentColor, 0 0 60px currentColor; }
}
.text-effect-anim-glow { animation: text-glow 1.5s ease-in-out infinite; }

@keyframes text-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
.text-effect-anim-float { display: inline-block; animation: text-float 2.5s ease-in-out infinite; }

@keyframes text-wave-char {
  0%, 100% { transform: translateY(0); color: inherit; }
  50% { transform: translateY(-12px); color: #f5576c; }
}
.text-effect-anim-wave .wave-char { display: inline-block; animation: text-wave-char 1.2s ease-in-out infinite; }

/* typing 用了 JS 模拟，这里只定义光标闪烁 */
@keyframes typing-blink { 50% { border-color: transparent; } }

/* ------ 悬停效果 ------ */
.text-effect-hover-zoom { display: inline-block; transition: transform 0.25s ease; z-index: 1; position: relative; }
.text-effect-hover-zoom:hover { transform: scale(1.35); z-index: 999; }

.text-effect-hover-scale { display: inline-block; transition: transform 0.25s ease; }
.text-effect-hover-scale:hover { transform: scale(1.15); }

.text-effect-hover-rotate { display: inline-block; transition: transform 0.3s ease; }
.text-effect-hover-rotate:hover { transform: rotate(8deg); }

.text-effect-hover-underline { position: relative; display: inline-block; cursor: pointer; }
.text-effect-hover-underline::after {
  content: ''; position: absolute; bottom: -2px; left: 0;
  width: 0; height: 2px; background: currentColor;
  transition: width 0.3s ease;
}
.text-effect-hover-underline:hover::after { width: 100%; }
"""


BG_EFFECTS_CSS = """
/* ------ 背景特效 ------ */

/* 通用固定层 */
.bg-layer { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }

/* 气泡 */
.bg-bubbles .bubble {
  position: absolute; bottom: -80px; border-radius: 50%;
  background: rgba(255,255,255,0.5); pointer-events: none;
  animation: bubble-rise linear infinite;
}
@keyframes bubble-rise {
  0% { transform: translateY(0) scale(1); opacity: 0.4; }
  50% { opacity: 0.7; }
  100% { transform: translateY(-120vh) scale(0.2); opacity: 0; }
}

/* 粒子 */
.bg-particles .particle {
  position: absolute; border-radius: 50%; pointer-events: none;
  animation: particle-drift linear infinite;
}
@keyframes particle-drift {
  0% { transform: translateY(0) translateX(0) scale(1); opacity: 0; }
  15% { opacity: 0.6; }
  85% { opacity: 0.6; }
  100% { transform: translateY(-105vh) translateX(80px) scale(0.2); opacity: 0; }
}

/* 星空 */
.bg-stars .star {
  position: absolute; border-radius: 50%; background: #fff; pointer-events: none;
  animation: star-twinkle ease-in-out infinite alternate;
}
@keyframes star-twinkle {
  0% { opacity: 0.15; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1.3); }
}

/* 动态渐变 */
.bg-gradient-anim { background-size: 400% 400% !important; animation: gradient-move 12s ease infinite; }
@keyframes gradient-move {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 纸屑 */
.bg-confetti .confetti-piece {
  position: absolute; width: 10px; height: 10px; top: -20px; pointer-events: none;
  animation: confetti-fall linear infinite;
}
@keyframes confetti-fall {
  0% { transform: translateY(0) rotate(0deg); opacity: 1; }
  100% { transform: translateY(110vh) rotate(720deg); opacity: 0.2; }
}

/* 飘雪 */
.bg-snow .snowflake {
  position: absolute; top: -20px; color: #fff; font-size: 14px; pointer-events: none;
  animation: snow-fall linear infinite;
}
@keyframes snow-fall {
  0% { transform: translateY(0) translateX(0); opacity: 0.6; }
  50% { transform: translateY(50vh) translateX(25px); opacity: 1; }
  100% { transform: translateY(110vh) translateX(-15px); opacity: 0.2; }
}
"""

BG_EFFECTS_JS = """
(function initBgEffects() {
  var body = document.body;
  if (body.classList.contains('bg-bubbles')) {
    var layer = document.createElement('div'); layer.className = 'bg-layer'; body.appendChild(layer);
    for (var i = 0; i < 22; i++) {
      var b = document.createElement('div'); b.className = 'bubble';
      var s = 8 + Math.random() * 55; b.style.width = s+'px'; b.style.height = s+'px';
      b.style.left = Math.random()*100+'%'; b.style.animationDuration = (8+Math.random()*14)+'s';
      b.style.animationDelay = (Math.random()*12)+'s';
      var colors = ['rgba(255,182,193,0.4)','rgba(173,216,230,0.4)','rgba(255,255,255,0.5)','rgba(200,230,255,0.4)','rgba(255,200,220,0.4)'];
      b.style.background = colors[i%colors.length]; layer.appendChild(b);
    }
  }
  if (body.classList.contains('bg-particles')) {
    var layer = document.createElement('div'); layer.className = 'bg-layer'; body.appendChild(layer);
    for (var i = 0; i < 40; i++) {
      var p = document.createElement('div'); p.className = 'particle';
      var s = 2+Math.random()*6; p.style.width = s+'px'; p.style.height = s+'px';
      p.style.left = Math.random()*100+'%'; p.style.animationDuration = (10+Math.random()*20)+'s';
      p.style.animationDelay = (Math.random()*15)+'s';
      var hue = Math.floor(Math.random()*360); p.style.background = 'hsla('+hue+',80%,70%,0.5)';
      layer.appendChild(p);
    }
  }
  if (body.classList.contains('bg-stars')) {
    var layer = document.createElement('div'); layer.className = 'bg-layer'; body.appendChild(layer);
    for (var i = 0; i < 120; i++) {
      var s = document.createElement('div'); s.className = 'star';
      var sz = 1+Math.random()*3; s.style.width = sz+'px'; s.style.height = sz+'px';
      s.style.left = Math.random()*100+'%'; s.style.top = Math.random()*100+'%';
      s.style.animationDuration = (1.5+Math.random()*3)+'s'; s.style.animationDelay = (Math.random()*4)+'s';
      layer.appendChild(s);
    }
  }
  if (body.classList.contains('bg-confetti')) {
    var layer = document.createElement('div'); layer.className = 'bg-layer'; body.appendChild(layer);
    var cols = ['#f8b4c8','#d4b5e8','#b5ead7','#fce38a','#b5d8f7','#ffd5b8','#ff9a9e','#a8edea'];
    for (var i = 0; i < 60; i++) {
      var c = document.createElement('div'); c.className = 'confetti-piece';
      c.style.left = Math.random()*100+'%'; c.style.background = cols[i%cols.length];
      c.style.width = (4+Math.random()*8)+'px'; c.style.height = (4+Math.random()*8)+'px';
      c.style.borderRadius = Math.random()>0.5?'50%':'2px';
      c.style.animationDuration = (2+Math.random()*4)+'s'; c.style.animationDelay = (Math.random()*5)+'s';
      layer.appendChild(c);
    }
  }
  if (body.classList.contains('bg-snow')) {
    var layer = document.createElement('div'); layer.className = 'bg-layer'; body.appendChild(layer);
    for (var i = 0; i < 80; i++) {
      var s = document.createElement('div'); s.className = 'snowflake'; s.textContent = '\\u2744';
      s.style.left = Math.random()*100+'%'; s.style.fontSize = (8+Math.random()*18)+'px';
      s.style.animationDuration = (6+Math.random()*10)+'s'; s.style.animationDelay = (Math.random()*8)+'s';
      layer.appendChild(s);
    }
  }
})();
"""

TEXT_EFFECTS_JS = """
(function initTextEffects() {
  /* 波浪效果：逐字包裹 span */
  document.querySelectorAll('.text-effect-anim-wave').forEach(function(el) {
    var text = el.textContent;
    if (!text || el.querySelector('.wave-char')) return;
    el.innerHTML = '';
    el.style.whiteSpace = 'pre-wrap';
    for (var i = 0; i < text.length; i++) {
      var span = document.createElement('span');
      span.className = 'wave-char';
      span.textContent = text[i] === ' ' ? '\\u00a0' : text[i];
      span.style.animationDelay = (i * 0.07) + 's';
      el.appendChild(span);
    }
  });
  /* 打字机效果 */
  document.querySelectorAll('.text-effect-anim-typing').forEach(function(el) {
    if (el.dataset.typingDone) return;
    var text = el.textContent;
    el.textContent = ''; el.style.display = 'inline-block'; el.style.overflow = 'hidden';
    el.style.whiteSpace = 'nowrap'; el.style.verticalAlign = 'bottom';
    el.style.borderRight = '2px solid '+window.getComputedStyle(el).color;
    var i = 0; var timer = setInterval(function() {
      if (i < text.length) { el.textContent += text[i]; i++; }
      else { clearInterval(timer); el.dataset.typingDone = '1'; }
    }, 90);
  });
})();
"""

# 文字特效名称映射
TEXT_EFFECT_NAMES = {
    "none":            "无特效",
    "art-gradient":    "🌈 艺术渐变",
    "art-shadow":      "💠 阴影效果",
    "art-outline":     "✏️ 描边文字",
    "art-3d":          "📐 3D 立体",
    "art-neon":        "💡 霓虹灯",
    "anim-shake":      "📳 抖动效果",
    "anim-bounce":     "🏀 弹跳效果",
    "anim-wave":       "🌊 波浪效果",
    "anim-typing":     "⌨️ 打字机",
    "anim-glow":       "✨ 呼吸发光",
    "anim-float":      "🎈 漂浮效果",
    "hover-zoom":      "🔍 悬停放大",
    "hover-scale":     "📏 悬停缩放",
    "hover-rotate":    "🔄 悬停旋转",
    "hover-underline": "〰️ 悬停下划线",
}

# 背景特效名称映射
BG_EFFECT_NAMES = {
    "none":         "无特效",
    "gradient":     "🌈 渐变背景",
    "gradient-anim":"✨ 动态渐变",
    "bubbles":      "🫧 气泡升起",
    "particles":    "✨ 粒子漂浮",
    "stars":        "⭐ 闪烁星空",
    "confetti":     "🎊 五彩纸屑",
    "snow":         "❄️ 飘雪效果",
}


# ============================================================
# 数据模型
# ============================================================
@dataclass
class ProjectSettings:
    """项目（全局）设置"""
    bg_type: str = "none"        # 背景特效类型
    bg_color1: str = "#ffffff"   # 背景主色 / 渐变色1
    bg_color2: str = "#e8f4f8"  # 渐变色2
    page_title: str = "我的网站"

    def to_dict(self) -> dict:
        return {
            "bgType": self.bg_type,
            "bgColor1": self.bg_color1,
            "bgColor2": self.bg_color2,
            "pageTitle": self.page_title,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProjectSettings":
        return cls(
            bg_type=d.get("bgType", "none"),
            bg_color1=d.get("bgColor1", "#ffffff"),
            bg_color2=d.get("bgColor2", "#e8f4f8"),
            page_title=d.get("pageTitle", "我的网站"),
        )


@dataclass
class Element:
    """网页元素数据模型"""
    elem_id: str
    type: str
    x: int
    y: int
    width: int
    height: int
    content: str
    font_family: str = "Microsoft YaHei"
    font_size: int = 20
    color: str = "#333333"
    bold: bool = False
    italic: bool = False
    underline: bool = False
    opacity: float = 1.0
    z_index: int = 0
    border_radius: int = 0
    bg_color: str = "transparent"
    text_align: str = "left"
    text_effect: str = "none"     # 文字特效

    def to_dict(self) -> dict:
        return {
            "id": self.elem_id, "type": self.type,
            "x": self.x, "y": self.y,
            "w": self.width, "h": self.height,
            "content": self.content,
            "fontFamily": self.font_family,
            "fontSize": self.font_size, "color": self.color,
            "bold": self.bold, "italic": self.italic, "underline": self.underline,
            "opacity": self.opacity, "zIndex": self.z_index,
            "borderRadius": self.border_radius, "bgColor": self.bg_color,
            "textAlign": self.text_align, "textEffect": self.text_effect,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Element":
        return cls(
            elem_id=d.get("id", str(uuid.uuid4())[:8]),
            type=d["type"],
            x=d.get("x", 100), y=d.get("y", 100),
            width=d.get("w", 200), height=d.get("h", 100),
            content=d.get("content", ""),
            font_family=d.get("fontFamily", "Microsoft YaHei"),
            font_size=d.get("fontSize", 20),
            color=d.get("color", "#333333"),
            bold=d.get("bold", False), italic=d.get("italic", False),
            underline=d.get("underline", False),
            opacity=d.get("opacity", 1.0), z_index=d.get("zIndex", 0),
            border_radius=d.get("borderRadius", 0),
            bg_color=d.get("bgColor", "transparent"),
            text_align=d.get("textAlign", "left"),
            text_effect=d.get("textEffect", "none"),
        )


# ============================================================
# HTML 生成引擎
# ============================================================

def _build_text_css(elements: list) -> str:
    """收集所有需要的内联 CSS 样式"""
    lines = []
    for el in elements:
        if el.type != "text":
            continue
        sel = f".el-{el.elem_id}"
        s = f"{sel} {{"
        s += f"font-family:'{el.font_family}';font-size:{el.font_size}px;color:{el.color};"
        s += f"text-align:{el.text_align};"
        if el.bold: s += "font-weight:bold;"
        if el.italic: s += "font-style:italic;"
        if el.underline: s += "text-decoration:underline;"
        if el.bg_color != "transparent": s += f"background-color:{el.bg_color};"
        if el.border_radius > 0: s += f"border-radius:{el.border_radius}px;"
        if el.opacity < 1.0: s += f"opacity:{el.opacity};"
        # 有些动画需要 inline-block
        if el.text_effect in ("anim-shake","anim-bounce","anim-float","anim-wave",
                               "anim-typing","hover-zoom","hover-scale","hover-rotate",
                               "hover-underline"):
            s += "display:inline-block;"
        s += "}"
        lines.append(s)
    return "\n".join(lines)


def element_to_html(elem: Element) -> str:
    """将单个元素转换为HTML"""
    style = (
        f"position:absolute;"
        f"left:{elem.x}px;top:{elem.y}px;"
        f"width:{elem.width}px;height:{elem.height}px;"
        f"opacity:{elem.opacity};z-index:{elem.z_index};"
    )

    tag_class = f"el-{elem.elem_id}"
    effect_cls = f" text-effect-{elem.text_effect}" if elem.text_effect != "none" else ""

    if elem.type == "text":
        content_html = elem.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        return f'<div class="{tag_class}{effect_cls}" style="{style}">{content_html}</div>'

    elif elem.type == "image":
        if not elem.content:
            return ""
        img_src = elem.content
        if os.path.isfile(img_src):
            try:
                with open(img_src, "rb") as f:
                    ext = os.path.splitext(img_src)[1].lower().replace(".", "")
                    if ext in ("jpg", "jpeg"): ext = "jpeg"
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                    img_src = f"data:image/{ext};base64,{b64}"
            except Exception:
                pass
        br = f"border-radius:{elem.border_radius}px;" if elem.border_radius > 0 else ""
        return f'<div style="{style}overflow:hidden;"><img src="{img_src}" style="width:100%;height:100%;object-fit:contain;{br}"></div>'

    elif elem.type == "video":
        if not elem.content:
            return ""
        br = f"border-radius:{elem.border_radius}px;" if elem.border_radius > 0 else ""
        return f'<div style="{style}overflow:hidden;"><video src="{elem.content}" controls style="width:100%;height:100%;object-fit:contain;{br}"></video></div>'

    return ""


def generate_html(elements: list, settings: ProjectSettings, title: str = "") -> str:
    """生成完整HTML文档（自包含，CSS/JS全部内嵌）"""
    if not title:
        title = settings.page_title

    # 背景样式
    body_classes = []
    bg_style = ""
    if settings.bg_type == "none":
        bg_style = f"background:{settings.bg_color1};"
    elif settings.bg_type == "gradient":
        bg_style = f"background:linear-gradient(135deg,{settings.bg_color1},{settings.bg_color2});"
    elif settings.bg_type == "gradient-anim":
        bg_style = f"background:linear-gradient(135deg,{settings.bg_color1},{settings.bg_color2});"
        body_classes.append("bg-gradient-anim")
    elif settings.bg_type in ("bubbles","particles","stars","confetti","snow"):
        bg_style = f"background:{settings.bg_color1};"
        body_classes.append(f"bg-{settings.bg_type}")

    # Body CSS
    body_css = (
        f"margin:0;padding:0;"
        f"width:1200px;min-height:800px;"
        f"position:relative;overflow-x:hidden;overflow-y:auto;"
        f"font-family:'Microsoft YaHei',Arial,sans-serif;"
        f"{bg_style}"
    )

    # 收集元素 HTML
    elem_htmls = []
    need_text_css = False
    need_text_js = False
    for el in sorted(elements, key=lambda e: e.z_index):
        h = element_to_html(el)
        if h:
            elem_htmls.append("  " + h)
            if el.type == "text":
                need_text_css = True
                if el.text_effect != "none":
                    need_text_js = True

    has_bg = settings.bg_type not in ("none", "gradient")
    body_class_str = " ".join(body_classes)

    css_parts = []
    if need_text_css:
        css_parts.append(_build_text_css(elements))
    if need_text_js:
        css_parts.append(TEXT_EFFECTS_CSS)
    if has_bg:
        css_parts.append(BG_EFFECTS_CSS)

    css_block = "\n".join(css_parts)

    js_parts = []
    if has_bg:
        js_parts.append(BG_EFFECTS_JS)
    if need_text_js:
        js_parts.append(TEXT_EFFECTS_JS)

    js_block = "\n".join(js_parts)

    body_tag = f'<body class="{body_class_str}" style="{body_css}">' if body_class_str else f'<body style="{body_css}">'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  img {{ max-width:100%; }}
{css_block}
</style>
</head>
{body_tag}
{chr(10).join(elem_htmls)}
<script>
{js_block}
</script>
</body>
</html>"""


def generate_project_folder(elements: list, settings: ProjectSettings, folder_path: str, title: str = "") -> str:
    """导出为项目文件夹（index.html + style.css + script.js），返回 index.html 路径"""
    if not title:
        title = settings.page_title

    # 生成 body classes / styles
    body_classes = []
    bg_style = ""
    if settings.bg_type == "none":
        bg_style = f"background:{settings.bg_color1};"
    elif settings.bg_type == "gradient":
        bg_style = f"background:linear-gradient(135deg,{settings.bg_color1},{settings.bg_color2});"
    elif settings.bg_type == "gradient-anim":
        bg_style = f"background:linear-gradient(135deg,{settings.bg_color1},{settings.bg_color2});"
        body_classes.append("bg-gradient-anim")
    elif settings.bg_type in ("bubbles","particles","stars","confetti","snow"):
        bg_style = f"background:{settings.bg_color1};"
        body_classes.append(f"bg-{settings.bg_type}")

    body_css = (
        f"margin:0;padding:0;"
        f"width:1200px;min-height:800px;"
        f"position:relative;overflow-x:hidden;overflow-y:auto;"
        f"font-family:'Microsoft YaHei',Arial,sans-serif;"
        f"{bg_style}"
    )

    # 元素 HTML
    elem_htmls = []
    need_text_css = False
    need_text_js = False
    for el in sorted(elements, key=lambda e: e.z_index):
        h = element_to_html(el)
        if h:
            elem_htmls.append("  " + h)
            if el.type == "text":
                need_text_css = True
                if el.text_effect != "none":
                    need_text_js = True

    has_bg = settings.bg_type not in ("none", "gradient")

    # ---- style.css ----
    css_parts = [f"/* {title} - 样式表 */"]
    css_parts.append(f"body {{ {body_css} }}")
    css_parts.append("img { max-width:100%; }")
    if need_text_css:
        css_parts.append(_build_text_css(elements))
    if need_text_js:
        css_parts.append(TEXT_EFFECTS_CSS)
    if has_bg:
        css_parts.append(BG_EFFECTS_CSS)
    css_content = "\n\n".join(css_parts)

    os.makedirs(folder_path, exist_ok=True)

    with open(os.path.join(folder_path, "style.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

    # ---- script.js ----
    js_parts = [f"// {title} - 脚本"]
    if has_bg:
        js_parts.append(BG_EFFECTS_JS)
    if need_text_js:
        js_parts.append(TEXT_EFFECTS_JS)
    js_content = "\n\n".join(js_parts)

    with open(os.path.join(folder_path, "script.js"), "w", encoding="utf-8") as f:
        f.write(js_content)

    # ---- index.html ----
    body_class_str = " ".join(body_classes)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
</head>
<body class="{body_class_str}">
{chr(10).join(elem_htmls)}
<script src="script.js"></script>
</body>
</html>"""

    html_path = os.path.join(folder_path, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html_path


# ============================================================
# 画布
# ============================================================
class DesignCanvas(tk.Canvas):
    """PPT风格的画布，用于放置和编辑网页元素"""

    PAGE_W, PAGE_H = 1200, 800
    BG_COLOR = "#e8e8e8"
    PAGE_COLOR = "#ffffff"

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=self.BG_COLOR, highlightthickness=0, **kwargs)
        self.elements: list[Element] = []
        self.settings = ProjectSettings()
        self.selected_id: Optional[str] = None
        self.next_z = 1

        self._drag_data = {"x": 0, "y": 0, "item": None, "type": None}
        self._edit_widget: Optional[tk.Widget] = None
        self._thumb_cache: dict[str, ImageTk.PhotoImage] = {}

        self.offset_x = 50
        self.offset_y = 50
        self.scale_level = 0.6

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Double-Button-1>", self._on_double_click)

        self.after(100, self.redraw)

    # ---- 元素管理 ----
    def add_element(self, elem: Element) -> str:
        elem.z_index = self.next_z
        self.next_z += 1
        self.elements.append(elem)
        self.redraw()
        self.select_element(elem.elem_id)
        return elem.elem_id

    def remove_element(self, elem_id: str):
        self.elements = [e for e in self.elements if e.elem_id != elem_id]
        if self.selected_id == elem_id:
            self.selected_id = None
            self.event_generate("<<SelectionChanged>>")
        self.redraw()

    def get_element(self, elem_id: str) -> Optional[Element]:
        for e in self.elements:
            if e.elem_id == elem_id:
                return e
        return None

    def select_element(self, elem_id: Optional[str]):
        self.selected_id = elem_id
        self.event_generate("<<SelectionChanged>>")
        self.redraw()

    def get_selected(self) -> Optional[Element]:
        return self.get_element(self.selected_id)

    # ---- 渲染 ----
    def redraw(self):
        self.delete("all")
        self._draw_page()
        for elem in sorted(self.elements, key=lambda e: e.z_index):
            self._draw_element(elem)
        self._draw_selection()

    def _draw_page(self):
        x1, y1 = self.offset_x, self.offset_y
        x2 = x1 + int(self.PAGE_W * self.scale_level)
        y2 = y1 + int(self.PAGE_H * self.scale_level)
        # 页面背景
        bg = self.settings.bg_color1
        self.create_rectangle(x1, y1, x2, y2, fill=bg, outline="#cccccc", width=1, tags="page")
        # 如果设置了渐变色2，在画布上简单示意（画一个半透明叠加层）
        if self.settings.bg_type == "gradient" or self.settings.bg_type == "gradient-anim":
            self.create_rectangle(x1, y1, x2, y2, fill=self.settings.bg_color2,
                                  stipple="gray25", outline="", tags="page")
        # 特效标签
        if self.settings.bg_type not in ("none", "gradient", "gradient-anim"):
            label = BG_EFFECT_NAMES.get(self.settings.bg_type, self.settings.bg_type)
            self.create_text(x1 + 10, y1 + 14, text=f"🌐 {label}",
                             anchor="w", font=("Microsoft YaHei", 9), fill="#999999", tags="page")

    def _to_canvas(self, x, y):
        return (self.offset_x + int(x * self.scale_level),
                self.offset_y + int(y * self.scale_level))

    def _to_page(self, cx, cy):
        return (int((cx - self.offset_x) / self.scale_level),
                int((cy - self.offset_y) / self.scale_level))

    def _draw_element(self, elem: Element):
        cx, cy = self._to_canvas(elem.x, elem.y)
        cw = max(int(elem.width * self.scale_level), 20)
        ch = max(int(elem.height * self.scale_level), 20)
        tags = ("element", f"elem_{elem.elem_id}")

        if elem.bg_color != "transparent":
            try:
                self.create_rectangle(cx, cy, cx + cw, cy + ch,
                                      fill=elem.bg_color, outline="", tags=tags)
            except tk.TclError:
                pass

        bw = 2 if elem.elem_id == self.selected_id else 1
        bc = "#0066ff" if elem.elem_id == self.selected_id else "#dddddd"

        if elem.type == "text":
            display_text = elem.content if elem.content else "双击编辑文字"
            max_chars = max(1, cw // 10)
            if len(display_text) > max_chars:
                display_text = display_text[:max_chars - 1] + "…"
            lines = display_text.split("\n")
            if len(lines) > ch // 20:
                lines = lines[:max(1, ch // 20)]
                lines[-1] += "…"
            display_text = "\n".join(lines)
            fs = max(9, int(elem.font_size * self.scale_level))

            # 特效标签
            effect_label = ""
            if elem.text_effect != "none":
                effect_label = TEXT_EFFECT_NAMES.get(elem.text_effect, "")
                effect_label = f" [{effect_label}]"

            item_id = self.create_text(
                cx + cw // 2, cy + ch // 2,
                text=display_text + effect_label,
                font=(elem.font_family, fs,
                      "bold" if elem.bold else "normal",
                      "italic" if elem.italic else "roman"),
                fill=elem.color, width=cw - 10, anchor="center", tags=tags,
            )
            bbox = self.bbox(item_id)
            if bbox:
                tx, ty, tx2, ty2 = bbox
                pad = 4
                bg_item = self.create_rectangle(
                    tx - pad, ty - pad, tx2 + pad, ty2 + pad,
                    fill="", outline="", tags=("bg",) + tags
                )
                self.tag_lower(bg_item, item_id)

            self.create_rectangle(cx, cy, cx + cw, cy + ch,
                                  outline=bc, width=bw, tags=tags)

        elif elem.type == "image":
            self.create_rectangle(cx, cy, cx + cw, cy + ch,
                                  outline=bc, width=bw, fill="#f5f5f5", tags=tags)
            if elem.content and HAS_PIL:
                try:
                    if os.path.isfile(elem.content):
                        pil_img = Image.open(elem.content)
                        pil_img.thumbnail((cw - 8, ch - 8))
                        photo = ImageTk.PhotoImage(pil_img)
                        self._thumb_cache[elem.elem_id] = photo
                        self.create_image(cx + cw // 2, cy + ch // 2,
                                          image=photo, anchor="center", tags=tags)
                except Exception:
                    pass
            if not elem.content or not HAS_PIL or elem.elem_id not in self._thumb_cache:
                self.create_text(cx + cw // 2, cy + ch // 2,
                                 text="🖼️ " + (os.path.basename(elem.content) if elem.content else "图片"),
                                 font=("Microsoft YaHei", 9), fill="#999999",
                                 anchor="center", tags=tags)

        elif elem.type == "video":
            self.create_rectangle(cx, cy, cx + cw, cy + ch,
                                  outline=bc, width=bw, fill="#e8f4f8", tags=tags)
            self.create_text(cx + cw // 2, cy + ch // 2 - 6,
                             text="▶ " + (os.path.basename(elem.content) if elem.content else "视频"),
                             font=("Microsoft YaHei", 9), fill="#666666",
                             anchor="center", tags=tags)
            if not elem.content:
                self.create_text(cx + cw // 2, cy + ch // 2 + 12,
                                 text="点击选择视频文件",
                                 font=("Microsoft YaHei", 7), fill="#999999",
                                 anchor="center", tags=tags)

    def _draw_selection(self):
        if not self.selected_id:
            return
        elem = self.get_element(self.selected_id)
        if not elem:
            return
        cx, cy = self._to_canvas(elem.x, elem.y)
        cw = int(elem.width * self.scale_level)
        ch = int(elem.height * self.scale_level)
        hs = 5
        handles = [
            (cx, cy, "nw"), (cx + cw // 2, cy, "n"),
            (cx + cw, cy, "ne"), (cx + cw, cy + ch // 2, "e"),
            (cx + cw, cy + ch, "se"), (cx + cw // 2, cy + ch, "s"),
            (cx, cy + ch, "sw"), (cx, cy + ch // 2, "w"),
        ]
        for hx, hy, htype in handles:
            self.create_rectangle(hx - hs, hy - hs, hx + hs, hy + hs,
                                  fill="white", outline="#0066ff", width=1.5,
                                  tags=("handle", f"handle_{htype}"))

    # ---- 交互 ----
    def _find_element_at(self, x, y):
        for elem in reversed(sorted(self.elements, key=lambda e: e.z_index)):
            ex, ey = self._to_canvas(elem.x, elem.y)
            ew = int(elem.width * self.scale_level)
            eh = int(elem.height * self.scale_level)
            if ex <= x <= ex + ew and ey <= y <= ey + eh:
                return elem
        return None

    def _on_click(self, event):
        if self._edit_widget:
            self._finish_editing()
        x, y = event.x, event.y
        closest = self.find_closest(x, y)
        tags = self.gettags(closest[0]) if closest else ()
        if any(t.startswith("handle_") for t in tags):
            for t in tags:
                if t.startswith("handle_"):
                    self._drag_data["type"] = f"resize:{t.replace('handle_', '')}"
                    self._drag_data["x"] = x
                    self._drag_data["y"] = y
                    return
        elem = self._find_element_at(x, y)
        if elem:
            self.select_element(elem.elem_id)
            self._drag_data["type"] = "move"
            self._drag_data["x"] = x
            self._drag_data["y"] = y
        else:
            self.select_element(None)

    def _on_drag(self, event):
        if not self.selected_id or not self._drag_data["type"]:
            return
        x, y = event.x, event.y
        dx = x - self._drag_data["x"]
        dy = y - self._drag_data["y"]
        elem = self.get_element(self.selected_id)
        if not elem:
            return
        if self._drag_data["type"] == "move":
            new_x = max(0, elem.x + int(dx / self.scale_level))
            new_y = max(0, elem.y + int(dy / self.scale_level))
            elem.x, elem.y = new_x, new_y
            self.redraw()
            self.event_generate("<<ElementChanged>>")
        elif self._drag_data["type"].startswith("resize:"):
            handle = self._drag_data["type"].split(":")[1]
            dw = int(dx / self.scale_level)
            dh = int(dy / self.scale_level)
            if "e" in handle:
                elem.width = max(30, elem.width + dw)
            if "w" in handle:
                elem.width = max(30, elem.width - dw)
                elem.x += dw if elem.width > 30 else 0
            if "s" in handle:
                elem.height = max(30, elem.height + dh)
            if "n" in handle:
                elem.height = max(30, elem.height - dh)
                elem.y += dh if elem.height > 30 else 0
            self.redraw()
            self.event_generate("<<ElementChanged>>")
        self._drag_data["x"] = x
        self._drag_data["y"] = y

    def _on_release(self, event):
        self._drag_data["type"] = None

    def _on_double_click(self, event):
        x, y = event.x, event.y
        elem = self._find_element_at(x, y)
        if elem and elem.type == "text":
            self.select_element(elem.elem_id)
            self._start_inline_edit(elem)

    # ---- 文字内联编辑 ----
    def _start_inline_edit(self, elem: Element):
        if self._edit_widget:
            self._finish_editing()
        cx, cy = self._to_canvas(elem.x, elem.y)
        cw = max(int(elem.width * self.scale_level), 40)
        ch = max(int(elem.height * self.scale_level), 20)
        self._edit_widget = tk.Text(
            self, wrap="word",
            font=(elem.font_family, max(10, int(elem.font_size * self.scale_level))),
            fg=elem.color,
            bg=elem.bg_color if elem.bg_color != "transparent" else "white",
            relief="solid", borderwidth=1,
            height=max(2, ch // 18), width=max(5, cw // 10),
        )
        self._edit_widget.insert("1.0", elem.content)
        self._edit_widget.place(x=cx, y=cy, width=cw, height=ch)
        self._edit_widget.focus_set()
        self._edit_widget.bind("<Control-Return>", lambda e: self._finish_editing())
        self._edit_widget.bind("<FocusOut>", lambda e: self._finish_editing())
        self._edit_widget.bind("<Escape>", lambda e: self._finish_editing())
        self._edit_widget.tag_add("sel", "1.0", "end")

    def _finish_editing(self):
        if not self._edit_widget:
            return
        try:
            content = self._edit_widget.get("1.0", "end-1c")
            if self.selected_id:
                elem = self.get_element(self.selected_id)
                if elem and elem.type == "text":
                    elem.content = content
                    self.redraw()
                    self.event_generate("<<ElementChanged>>")
        finally:
            self._edit_widget.destroy()
            self._edit_widget = None

    # ---- 右键菜单 ----
    def show_context_menu(self, event):
        x, y = event.x, event.y
        elem = self._find_element_at(x, y)
        if elem:
            self.select_element(elem.elem_id)
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="删除元素", command=lambda: self.remove_element(elem.elem_id))
            menu.add_command(label="上移一层", command=lambda: self._move_up(elem.elem_id))
            menu.add_command(label="下移一层", command=lambda: self._move_down(elem.elem_id))
            menu.tk_popup(event.x_root, event.y_root)

    def _move_up(self, elem_id: str):
        elem = self.get_element(elem_id)
        if elem:
            elem.z_index += 1
            self.next_z = max(self.next_z, elem.z_index + 1)
            self.redraw()

    def _move_down(self, elem_id: str):
        elem = self.get_element(elem_id)
        if elem and elem.z_index > 0:
            elem.z_index -= 1
            self.redraw()

    # ---- 导出 ----
    def to_html(self, title: str = "") -> str:
        return generate_html(self.elements, self.settings, title)


# ============================================================
# 属性面板
# ============================================================
class PropertyPanel(tk.Frame):
    """右侧属性编辑面板"""

    def __init__(self, master, canvas: DesignCanvas, **kwargs):
        super().__init__(master, width=250, bg="#f8f8f8", **kwargs)
        self.canvas = canvas
        self._building = False
        self.pack_propagate(False)

        tk.Label(self, text="⚙ 属性设置", font=("Microsoft YaHei", 12, "bold"),
                 bg="#f8f8f8", anchor="w", padx=10, pady=8).pack(fill="x")

        self._content_frame = tk.Frame(self, bg="#f8f8f8")
        self._content_frame.pack(fill="both", expand=True, padx=8)

        self._scroll_canvas = tk.Canvas(self._content_frame, bg="#f8f8f8",
                                        highlightthickness=0, width=230)
        self._scroll_bar = tk.Scrollbar(self._content_frame, orient="vertical",
                                        command=self._scroll_canvas.yview)
        self._scroll_inner = tk.Frame(self._scroll_canvas, bg="#f8f8f8")

        self._scroll_inner.bind("<Configure>", lambda e: self._scroll_canvas.configure(
            scrollregion=self._scroll_canvas.bbox("all")))
        self._scroll_canvas.create_window((0, 0), window=self._scroll_inner, anchor="nw")
        self._scroll_canvas.configure(yscrollcommand=self._scroll_bar.set)

        self._scroll_canvas.pack(side="left", fill="both", expand=True)
        self._scroll_bar.pack(side="right", fill="y")

        # 鼠标滚轮绑定
        def _on_mousewheel(event):
            self._scroll_canvas.yview_scroll(-1 * (event.delta // 120), "units")
        self._scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel, add="+")

        self.canvas.bind("<<SelectionChanged>>", self._on_selection_changed)

    def _on_selection_changed(self, event=None):
        if self._building:
            return
        for w in self._scroll_inner.winfo_children():
            w.destroy()
        elem = self.canvas.get_selected()
        if elem:
            self._build_element_controls(elem)
        else:
            self._build_project_controls()

    def _build_project_controls(self):
        """无选中元素时显示项目（背景）设置"""
        f = self._scroll_inner
        tk.Label(f, text="🌐 页面背景", font=("Microsoft YaHei", 11, "bold"),
                 bg="#f8f8f8", anchor="w").pack(fill="x", pady=(0, 8))

        s = self.canvas.settings

        # 背景特效
        tk.Label(f, text="背景特效:", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", anchor="w").pack(fill="x")
        bg_names = list(BG_EFFECT_NAMES.keys())
        bg_labels = [BG_EFFECT_NAMES[k] for k in bg_names]
        bg_var = tk.StringVar(value=s.bg_type)
        cb = ttk.Combobox(f, textvariable=bg_var, values=bg_labels, state="readonly", width=22)
        cb.pack(pady=(2, 6))

        # 映射选择到 key
        def on_bg_select(event):
            idx = cb.current()
            if idx >= 0:
                s.bg_type = bg_names[idx]
                self.canvas.redraw()
        cb.bind("<<ComboboxSelected>>", on_bg_select)

        # 颜色1
        self._add_bg_color_row(f, "颜色 1:", s.bg_color1, lambda c: setattr(s, 'bg_color1', c))
        # 颜色2
        self._add_bg_color_row(f, "颜色 2:", s.bg_color2, lambda c: setattr(s, 'bg_color2', c))

        tk.Label(f, text="提示：背景特效仅在导出的HTML中可见",
                 font=("Microsoft YaHei", 7), bg="#f8f8f8", fg="#999999",
                 wraplength=200, anchor="w").pack(fill="x", pady=(6, 0))

    def _add_bg_color_row(self, parent, label, color, setter):
        row = tk.Frame(parent, bg="#f8f8f8")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", width=6, anchor="w").pack(side="left")

        c_frame = tk.Frame(row, bg=color, width=22, height=22,
                           highlightbackground="#cccccc", highlightthickness=1)
        c_frame.pack(side="left", padx=2)

        def pick():
            _, c = colorchooser.askcolor(title="选择颜色", initialcolor=color)
            if c:
                c_frame.configure(bg=c)
                setter(c)
                self.canvas.redraw()

        c_frame.bind("<Button-1>", lambda e: pick())
        tk.Button(row, text="选择", font=("Microsoft YaHei", 8),
                  command=pick).pack(side="left", padx=2)

    def _build_element_controls(self, elem: Element):
        f = self._scroll_inner

        # 元素类型
        type_row = tk.Frame(f, bg="#f8f8f8")
        type_row.pack(fill="x", pady=2)
        type_map = {"text": "文字", "image": "图片", "video": "视频"}
        tk.Label(type_row, text="类型:", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", width=8, anchor="w").pack(side="left")
        tk.Label(type_row, text=type_map.get(elem.type, elem.type),
                 font=("Microsoft YaHei", 9, "bold"),
                 bg="#f8f8f8", fg="#0066ff").pack(side="left")

        # 位置 / 尺寸
        self._add_row("位置 X", elem.x, "x", 0, 2000)
        self._add_row("位置 Y", elem.y, "y", 0, 2000)
        self._add_row("宽度", elem.width, "width", 30, 1200)
        self._add_row("高度", elem.height, "height", 30, 1200)

        sep1 = tk.Frame(f, height=1, bg="#dddddd")
        sep1.pack(fill="x", pady=6)

        if elem.type == "text":
            # ----- 文字特效 -----
            tk.Label(f, text="文字特效:", font=("Microsoft YaHei", 9),
                     bg="#f8f8f8", anchor="w").pack(fill="x")
            eff_keys = list(TEXT_EFFECT_NAMES.keys())
            eff_labels = [TEXT_EFFECT_NAMES[k] for k in eff_keys]
            eff_var = tk.StringVar(value=elem.text_effect)
            eff_cb = ttk.Combobox(f, textvariable=eff_var, values=eff_labels,
                                  state="readonly", width=22)
            eff_cb.pack(pady=(0, 6))

            def on_eff_select(event):
                idx = eff_cb.current()
                if idx >= 0:
                    elem.text_effect = eff_keys[idx]
                    self.canvas.redraw()
            eff_cb.bind("<<ComboboxSelected>>", on_eff_select)

            # 字号
            self._add_row("字号", elem.font_size, "font_size", 8, 200)
            self._build_font_family(elem)

            # 颜色
            self._add_color_picker("文字色", elem.color, "color")
            self._add_bg_picker(elem)

            # 样式按钮
            style_row = tk.Frame(f, bg="#f8f8f8")
            style_row.pack(fill="x", pady=3)

            def tb_bold():
                elem.bold = not elem.bold; self.canvas.redraw()
            def tb_italic():
                elem.italic = not elem.italic; self.canvas.redraw()
            def tb_underline():
                elem.underline = not elem.underline; self.canvas.redraw()

            tk.Button(style_row, text="B", width=3, font=("Arial", 9, "bold"),
                      relief="raised" if elem.bold else "ridge",
                      command=tb_bold).pack(side="left", padx=1)
            tk.Button(style_row, text="I", width=3, font=("Arial", 9, "italic"),
                      relief="raised" if elem.italic else "ridge",
                      command=tb_italic).pack(side="left", padx=1)
            tk.Button(style_row, text="U", width=3, font=("Arial", 9, "underline"),
                      relief="raised" if elem.underline else "ridge",
                      command=tb_underline).pack(side="left", padx=1)

            # 对齐
            align_frame = tk.Frame(f, bg="#f8f8f8")
            align_frame.pack(fill="x", pady=2)
            tk.Label(align_frame, text="对齐:", font=("Microsoft YaHei", 9),
                     bg="#f8f8f8", width=8, anchor="w").pack(side="left")
            align_var = tk.StringVar(value=elem.text_align)
            for val, label in [("left", "左"), ("center", "中"), ("right", "右")]:
                tk.Radiobutton(align_frame, text=label, variable=align_var,
                               value=val, bg="#f8f8f8",
                               command=lambda: self._update_elem(text_align=align_var.get())
                               ).pack(side="left", padx=2)

        elif elem.type == "image":
            self._add_image_controls(elem)
        elif elem.type == "video":
            self._add_video_controls(elem)

        # 圆角 + 不透明度
        sep2 = tk.Frame(f, height=1, bg="#dddddd")
        sep2.pack(fill="x", pady=6)
        self._add_row("圆角", elem.border_radius, "border_radius", 0, 100)
        self._add_opacity_slider(elem)

        # 删除
        btn_frame = tk.Frame(f, bg="#f8f8f8")
        btn_frame.pack(fill="x", pady=8)
        tk.Button(btn_frame, text="🗑 删除元素", fg="red",
                  font=("Microsoft YaHei", 10),
                  command=lambda: self.canvas.remove_element(elem.elem_id)
                  ).pack(fill="x")

    def _add_row(self, label, value, attr, min_v, max_v):
        row = tk.Frame(self._scroll_inner, bg="#f8f8f8")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label + ":", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", width=8, anchor="w").pack(side="left")
        var = tk.StringVar(value=str(value))
        entry = tk.Entry(row, textvariable=var, width=10, font=("Microsoft YaHei", 9))
        entry.pack(side="left", padx=2, ipady=1)

        def on_change(*_):
            if self._building: return
            try:
                val = int(var.get())
                val = max(min_v, min(val, max_v))
                self._update_elem(**{attr: val})
            except ValueError:
                pass
        var.trace_add("write", on_change)

    def _build_font_family(self, elem: Element):
        row = tk.Frame(self._scroll_inner, bg="#f8f8f8")
        row.pack(fill="x", pady=2)
        tk.Label(row, text="字体:", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", width=8, anchor="w").pack(side="left")
        fonts = ["Microsoft YaHei", "SimSun", "SimHei", "KaiTi", "FangSong",
                 "Arial", "Times New Roman", "Courier New", "Georgia", "Verdana"]
        var = tk.StringVar(value=elem.font_family)
        cb = ttk.Combobox(row, textvariable=var, values=fonts, width=15)
        cb.pack(side="left", padx=2)
        cb.bind("<<ComboboxSelected>>", lambda e: self._update_elem(font_family=var.get()))
        cb.bind("<FocusOut>", lambda e: self._update_elem(font_family=var.get()))

    def _add_color_picker(self, label, color, attr):
        row = tk.Frame(self._scroll_inner, bg="#f8f8f8")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label + ":", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", width=8, anchor="w").pack(side="left")
        c_frame = tk.Frame(row, bg=color, width=20, height=20,
                           highlightbackground="#cccccc", highlightthickness=1)
        c_frame.pack(side="left", padx=2)

        def pick_color():
            _, c = colorchooser.askcolor(title="选择颜色", initialcolor=color)
            if c:
                c_frame.configure(bg=c)
                self._update_elem(**{attr: c})
        c_frame.bind("<Button-1>", lambda e: pick_color())
        tk.Button(row, text="选择", font=("Microsoft YaHei", 8),
                  command=pick_color).pack(side="left", padx=2)

    def _add_bg_picker(self, elem: Element):
        row = tk.Frame(self._scroll_inner, bg="#f8f8f8")
        row.pack(fill="x", pady=2)
        tk.Label(row, text="背景色:", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", width=8, anchor="w").pack(side="left")
        bg_col = elem.bg_color if elem.bg_color != "transparent" else "#ffffff"
        c_frame = tk.Frame(row, bg=bg_col, width=20, height=20,
                           highlightbackground="#cccccc", highlightthickness=1)
        c_frame.pack(side="left", padx=2)

        def pick_bg():
            _, c = colorchooser.askcolor(title="选择背景色", initialcolor=bg_col)
            if c:
                c_frame.configure(bg=c)
                self._update_elem(bg_color=c)
            else:
                self._update_elem(bg_color="transparent")
                c_frame.configure(bg="#ffffff")

        c_frame.bind("<Button-1>", lambda e: pick_bg())
        tk.Button(row, text="选择", font=("Microsoft YaHei", 8),
                  command=pick_bg).pack(side="left", padx=1)
        tk.Button(row, text="清除", font=("Microsoft YaHei", 8),
                  command=lambda: (self._update_elem(bg_color="transparent"),
                                   c_frame.configure(bg="#ffffff"))
                  ).pack(side="left", padx=1)

    def _add_image_controls(self, elem: Element):
        f = self._scroll_inner
        path_text = tk.Label(f, text=elem.content if elem.content else "未选择图片",
                             font=("Microsoft YaHei", 8), bg="#f8f8f8", fg="#666666",
                             anchor="w", wraplength=200)
        path_text.pack(fill="x")

        def browse_image():
            path = filedialog.askopenfilename(
                title="选择图片",
                filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
            )
            if path:
                self._update_elem(content=path)
                path_text.config(text=os.path.basename(path))
                self.canvas.redraw()
        tk.Button(f, text="📁 选择图片", font=("Microsoft YaHei", 9),
                  command=browse_image).pack(fill="x", pady=4)

    def _add_video_controls(self, elem: Element):
        f = self._scroll_inner
        path_text = tk.Label(f, text=elem.content if elem.content else "未选择视频",
                             font=("Microsoft YaHei", 8), bg="#f8f8f8", fg="#666666",
                             anchor="w", wraplength=200)
        path_text.pack(fill="x")

        def browse_video():
            path = filedialog.askopenfilename(
                title="选择视频",
                filetypes=[("视频文件", "*.mp4 *.avi *.mov *.wmv *.flv *.webm")]
            )
            if path:
                self._update_elem(content=path)
                path_text.config(text=os.path.basename(path))
                self.canvas.redraw()

        def use_url():
            url = simpledialog.askstring("视频链接", "请输入视频URL地址：")
            if url:
                self._update_elem(content=url)
                path_text.config(text=url[:40] + "..." if len(url) > 40 else url)
                self.canvas.redraw()

        btn_row = tk.Frame(f, bg="#f8f8f8")
        btn_row.pack(fill="x", pady=2)
        tk.Button(btn_row, text="📁 本地文件", font=("Microsoft YaHei", 8),
                  command=browse_video).pack(side="left", fill="x", expand=True, padx=1)
        tk.Button(btn_row, text="🔗 视频链接", font=("Microsoft YaHei", 8),
                  command=use_url).pack(side="left", fill="x", expand=True, padx=1)

    def _add_opacity_slider(self, elem: Element):
        row = tk.Frame(self._scroll_inner, bg="#f8f8f8")
        row.pack(fill="x", pady=2)
        tk.Label(row, text="不透明度:", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", width=8, anchor="w").pack(side="left")
        var = tk.DoubleVar(value=elem.opacity)

        def on_slide(*_):
            val = round(var.get(), 2)
            self._update_elem(opacity=val)

        slider = tk.Scale(row, from_=0.1, to=1.0, resolution=0.05,
                          orient="horizontal", variable=var,
                          bg="#f8f8f8", length=120, showvalue=False)
        slider.pack(side="left", padx=2)
        val_label = tk.Label(row, text=f"{elem.opacity:.1f}",
                             font=("Microsoft YaHei", 8), bg="#f8f8f8", width=3)
        val_label.pack(side="left")
        var.trace_add("write", lambda *_: val_label.config(text=f"{var.get():.1f}"))
        slider.config(command=on_slide)

    def _update_elem(self, **kwargs):
        elem = self.canvas.get_selected()
        if elem:
            for k, v in kwargs.items():
                setattr(elem, k, v)
            self.canvas.redraw()
            self.canvas.event_generate("<<ElementChanged>>")


# ============================================================
# 主窗口
# ============================================================
class MainWindow(tk.Tk):
    """主应用程序窗口"""

    def __init__(self):
        super().__init__()
        self.title("简易网站可视化编辑器 · WYSIWYG Website Builder")
        self.geometry("1400x900")
        self.minsize(1000, 600)
        self.current_file = None
        self._build_ui()
        self._bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # ===== 工具栏 =====
        toolbar = tk.Frame(self, bg="#2c2c2c", height=48)
        toolbar.pack(fill="x", side="top")
        toolbar.pack_propagate(False)

        btn_base = {"font": ("Microsoft YaHei", 10), "fg": "white",
                    "relief": "flat", "padx": 12, "pady": 4, "cursor": "hand2"}
        btn_add = dict(btn_base, bg="#444444")
        btn_act = dict(btn_base, bg="#555555")

        # 添加元素
        tk.Button(toolbar, text="＋ 添加文字", **btn_add,
                  command=self._add_text).pack(side="left", padx=4, pady=8)
        tk.Button(toolbar, text="＋ 添加图片", **btn_add,
                  command=self._add_image).pack(side="left", padx=4, pady=8)
        tk.Button(toolbar, text="＋ 添加视频", **btn_add,
                  command=self._add_video).pack(side="left", padx=4, pady=8)

        tk.Frame(toolbar, width=1, bg="#666666").pack(side="left", fill="y", padx=8)

        # 操作
        tk.Button(toolbar, text="👁 浏览器预览", **btn_act,
                  command=self._preview).pack(side="left", padx=4, pady=8)
        tk.Button(toolbar, text="💾 保存项目", **btn_act,
                  command=self._save_project).pack(side="left", padx=4, pady=8)
        tk.Button(toolbar, text="📂 打开项目", **btn_act,
                  command=self._load_project).pack(side="left", padx=4, pady=8)

        tk.Frame(toolbar, width=1, bg="#666666").pack(side="left", fill="y", padx=8)

        btn_export_html = dict(btn_base, bg="#0066cc")
        btn_export_folder = dict(btn_base, bg="#0077aa")
        tk.Button(toolbar, text="⬇ 导出 HTML", **btn_export_html,
                  command=self._export_html).pack(side="left", padx=4, pady=8)
        tk.Button(toolbar, text="📁 导出项目文件夹", **btn_export_folder,
                  command=self._export_folder).pack(side="left", padx=4, pady=8)

        # 缩放
        scale_frame = tk.Frame(toolbar, bg="#2c2c2c")
        scale_frame.pack(side="right", padx=10)
        tk.Label(scale_frame, text="缩放:", font=("Microsoft YaHei", 9),
                 bg="#2c2c2c", fg="#cccccc").pack(side="left")
        btn_zoom = {"font": ("Arial", 10), "bg": "#444444", "fg": "white",
                    "relief": "flat", "width": 2}
        tk.Button(scale_frame, text="＋", **btn_zoom,
                  command=self._zoom_in).pack(side="left")
        tk.Button(scale_frame, text="－", **btn_zoom,
                  command=self._zoom_out).pack(side="left", padx=2)
        tk.Button(scale_frame, text="100%",
                  font=("Microsoft YaHei", 8), bg="#444444", fg="white", relief="flat",
                  command=self._zoom_reset).pack(side="left")

        self._status_label = tk.Label(toolbar, text=" 就绪",
                                      font=("Microsoft YaHei", 9),
                                      bg="#2c2c2c", fg="#aaaaaa")
        self._status_label.pack(side="right", padx=10)

        # ===== 主体 =====
        main_frame = tk.Frame(self, bg="#e0e0e0")
        main_frame.pack(fill="both", expand=True)

        canvas_container = tk.Frame(main_frame, bg="#e0e0e0")
        canvas_container.pack(side="left", fill="both", expand=True)

        h_scroll = tk.Scrollbar(canvas_container, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        v_scroll = tk.Scrollbar(canvas_container, orient="vertical")
        v_scroll.pack(side="right", fill="y")

        self.canvas = DesignCanvas(canvas_container)
        self.canvas.pack(fill="both", expand=True)
        h_scroll.config(command=self.canvas.xview)
        v_scroll.config(command=self.canvas.yview)
        self.canvas.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        self.canvas.config(scrollregion=(-50, -50, 1300, 1000))

        self.canvas.bind("<Button-2>", self.canvas.show_context_menu)
        self.canvas.bind("<Button-3>", self.canvas.show_context_menu)

        self.property_panel = PropertyPanel(main_frame, self.canvas)
        self.property_panel.pack(side="right", fill="y")

        # ===== 状态栏 =====
        status_bar = tk.Frame(self, bg="#e8e8e8", height=24)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        self._status_bar_label = tk.Label(
            status_bar,
            text="点击工具栏按钮添加元素 · 拖拽移动 · 双击编辑文字 · 右键更多操作",
            font=("Microsoft YaHei", 8), bg="#e8e8e8", fg="#666666", anchor="w", padx=10
        )
        self._status_bar_label.pack(side="left")

        self._elem_count_label = tk.Label(
            status_bar, text="元素: 0", font=("Microsoft YaHei", 8),
            bg="#e8e8e8", fg="#666666", padx=10
        )
        self._elem_count_label.pack(side="right")

        self.canvas.bind("<<ElementChanged>>", self._on_element_changed)

    def _bind_shortcuts(self):
        self.bind_all("<Control-s>", lambda e: self._save_project())
        self.bind_all("<Control-o>", lambda e: self._load_project())
        self.bind_all("<Control-e>", lambda e: self._export_html())
        self.bind_all("Delete", lambda e: self._delete_selected())

    def _on_element_changed(self, event=None):
        count = len(self.canvas.elements)
        self._elem_count_label.config(text=f"元素: {count}")
        elem = self.canvas.get_selected()
        if elem:
            self._status_bar_label.config(
                text=f"选中: {elem.type} ({elem.x},{elem.y}  {elem.width}×{elem.height})"
            )

    def _add_text(self):
        elem = Element(
            elem_id=str(uuid.uuid4())[:8], type="text",
            x=100, y=100, width=220, height=60,
            content="欢迎来到我的网站！", z_index=self.canvas.next_z,
        )
        self.canvas.add_element(elem)
        self._status_label.config(text=" 已添加文字元素")
        self._on_element_changed()

    def _add_image(self):
        path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("所有文件", "*.*")]
        )
        if not path:
            return
        w, h = 300, 200
        if HAS_PIL:
            try:
                img = Image.open(path)
                w, h = img.width, img.height
                max_dim = 400
                if w > max_dim or h > max_dim:
                    ratio = min(max_dim / w, max_dim / h)
                    w, h = int(w * ratio), int(h * ratio)
            except Exception:
                pass
        elem = Element(elem_id=str(uuid.uuid4())[:8], type="image",
                       x=150, y=150, width=w, height=h,
                       content=path, z_index=self.canvas.next_z)
        self.canvas.add_element(elem)
        self._status_label.config(text=" 已添加图片元素")
        self._on_element_changed()

    def _add_video(self):
        dialog = tk.Toplevel(self)
        dialog.title("添加视频")
        dialog.geometry("300x150")
        dialog.configure(bg="#f8f8f8")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        tk.Label(dialog, text="选择视频来源:", font=("Microsoft YaHei", 11),
                 bg="#f8f8f8").pack(pady=15)

        def from_file():
            dialog.destroy()
            path = filedialog.askopenfilename(
                title="选择视频",
                filetypes=[("视频文件", "*.mp4 *.avi *.mov *.wmv *.flv *.webm"), ("所有文件", "*.*")]
            )
            if path:
                self._do_add_video(path)

        def from_url():
            dialog.destroy()
            url = simpledialog.askstring("视频链接", "请输入视频URL地址：")
            if url:
                self._do_add_video(url)

        tk.Button(dialog, text="📁 本地文件", font=("Microsoft YaHei", 10),
                  command=from_file, width=15, pady=4).pack(pady=5)
        tk.Button(dialog, text="🔗 网络链接", font=("Microsoft YaHei", 10),
                  command=from_url, width=15, pady=4).pack(pady=5)

    def _do_add_video(self, path_or_url):
        elem = Element(elem_id=str(uuid.uuid4())[:8], type="video",
                       x=150, y=150, width=400, height=260,
                       content=path_or_url, z_index=self.canvas.next_z)
        self.canvas.add_element(elem)
        self._status_label.config(text=" 已添加视频元素")
        self._on_element_changed()

    def _delete_selected(self):
        elem = self.canvas.get_selected()
        if elem:
            self.canvas.remove_element(elem.elem_id)
            self._status_label.config(text=" 已删除元素")
            self._on_element_changed()

    def _preview(self):
        html = self.canvas.to_html()
        if len(self.canvas.elements) == 0:
            messagebox.showinfo("提示", "画布为空，请先添加一些元素。")
            return
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
            tmp.write(html)
            tmp.close()
            webbrowser.open("file://" + tmp.name)
            self._status_label.config(text=" 正在浏览器中预览...")
        except Exception as e:
            messagebox.showerror("错误", f"预览失败:\n{e}")

    def _export_html(self):
        """导出为单个自包含 HTML 文件"""
        html = self.canvas.to_html()
        if len(self.canvas.elements) == 0:
            messagebox.showinfo("提示", "画布为空，请先添加一些元素。")
            return
        file_path = filedialog.asksaveasfilename(
            title="导出 HTML 文件",
            defaultextension=".html",
            filetypes=[("HTML文件", "*.html"), ("所有文件", "*.*")],
            initialfile="my_website.html"
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            messagebox.showinfo("导出成功", f"自包含HTML已导出到:\n{file_path}\n\n双击即可在浏览器中打开！")
            self._status_label.config(text=f" 已导出: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def _export_folder(self):
        """导出为项目文件夹（含单独的 CSS/JS 文件）"""
        if len(self.canvas.elements) == 0:
            messagebox.showinfo("提示", "画布为空，请先添加一些元素。")
            return
        folder_path = filedialog.askdirectory(title="选择导出文件夹")
        if not folder_path:
            return
        # 创建子目录
        name = simpledialog.askstring("项目名称", "请输入项目名称：", initialvalue="my_website")
        if not name:
            name = "my_website"
        target = os.path.join(folder_path, name)
        try:
            html_path = generate_project_folder(
                self.canvas.elements, self.canvas.settings, target,
                title=self.canvas.settings.page_title
            )
            messagebox.showinfo(
                "导出成功",
                f"项目已导出到文件夹:\n{target}\n\n"
                f"包含文件:\n  index.html  (可双击直接打开)\n  style.css\n  script.js"
            )
            self._status_label.config(text=f" 已导出项目: {name}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def _save_project(self):
        data = {
            "version": 2,
            "settings": self.canvas.settings.to_dict(),
            "elements": [e.to_dict() for e in self.canvas.elements],
        }
        file_path = filedialog.asksaveasfilename(
            title="保存项目",
            defaultextension=".wsweb",
            filetypes=[("网站项目文件", "*.wsweb"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.current_file = file_path
            self._status_label.config(text=f" 项目已保存: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _load_project(self):
        file_path = filedialog.askopenfilename(
            title="打开项目",
            filetypes=[("网站项目文件", "*.wsweb"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 加载项目设置
            sdata = data.get("settings", {})
            self.canvas.settings = ProjectSettings.from_dict(sdata)

            # 加载元素
            elements = []
            max_z = 0
            for ed in data.get("elements", []):
                el = Element.from_dict(ed)
                elements.append(el)
                if el.z_index > max_z:
                    max_z = el.z_index

            self.canvas.elements = elements
            self.canvas.next_z = max_z + 1
            self.canvas.selected_id = None
            self.canvas.redraw()
            self.current_file = file_path
            self._on_element_changed()
            self._status_label.config(text=f" 已加载项目: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开项目文件:\n{e}")

    def _zoom_in(self):
        self.canvas.scale_level = min(2.0, self.canvas.scale_level + 0.1)
        self.canvas.redraw()

    def _zoom_out(self):
        self.canvas.scale_level = max(0.3, self.canvas.scale_level - 0.1)
        self.canvas.redraw()

    def _zoom_reset(self):
        self.canvas.scale_level = 1.0
        self.canvas.redraw()

    def _on_close(self):
        if self.canvas.elements:
            result = messagebox.askyesnocancel("退出确认", "是否保存当前项目后再退出？")
            if result is None:
                return
            if result:
                self._save_project()
        self.destroy()


# ============================================================
# 启动
# ============================================================
def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
