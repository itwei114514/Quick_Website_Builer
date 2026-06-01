#!/usr/bin/env python3
"""
简易网站可视化编辑器 - WYSIWYG Website Builder (v3.0 多页 + 超链接)
PPT风格界面，支持文字特效、背景特效、多页面管理、超链接、导出HTML文档。
"""

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox, simpledialog
import json
import os
import uuid
import base64
import webbrowser
import tempfile
import copy
import html
from dataclasses import dataclass, field
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
/* 可重入的背景特效初始化（每次调用先清除旧层） */
function initBgEffects() {
  var body = document.body;
  /* 清除已有的 bg-layer */
  var oldLayer = document.querySelector('.bg-layer');
  if (oldLayer) oldLayer.remove();
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
}
initBgEffects();
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

# 多页面导航 CSS / JS
PAGE_NAV_CSS = """
/* ===== 多页面导航 ===== */
.presentation {
  width: 100%;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}
.slide {
  width: 100%;
  min-height: 100vh;
  position: absolute;
  top: 0; left: 0;
  opacity: 0;
  transition: opacity 0.6s ease, transform 0.6s ease;
  pointer-events: none;
  overflow-y: auto;
  transform: scale(0.95);
}
.slide.active {
  opacity: 1;
  pointer-events: all;
  transform: scale(1);
  position: relative;
  min-height: 100vh;
}
/* 导航栏 */
.slide-nav {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 8px 18px;
  border-radius: 40px;
  z-index: 9999;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.slide-nav button {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.9);
  font-size: 20px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 20px;
  transition: background 0.2s;
  line-height: 1;
}
.slide-nav button:hover { background: rgba(255,255,255,0.15); }
.slide-nav button:disabled { opacity: 0.3; cursor: default; }
.slide-nav button:disabled:hover { background: transparent; }
.slide-nav .page-indicator {
  color: rgba(255,255,255,0.7);
  font-size: 13px;
  font-family: Arial, sans-serif;
  padding: 0 8px;
  min-width: 50px;
  text-align: center;
  user-select: none;
}
.slide-nav .page-dots {
  display: flex;
  gap: 8px;
  margin: 0 6px;
}
.slide-nav .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.25);
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  padding: 0;
}
.slide-nav .dot:hover { background: rgba(255,255,255,0.5); }
.slide-nav .dot.active {
  background: #ffffff;
  transform: scale(1.3);
  box-shadow: 0 0 8px rgba(255,255,255,0.4);
}
/* 页面底部页码 */
.slide-page-number {
  position: absolute;
  bottom: 80px;
  right: 30px;
  font-size: 14px;
  color: rgba(0,0,0,0.25);
  font-family: Arial, sans-serif;
  pointer-events: none;
}

/* ===== 页面内导航条 ===== */
.slide-inner-nav {
  position: absolute;
  bottom: 60px;
  left: 0;
  right: 0;
  text-align: center;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  font-size: 14px;
  user-select: none;
  pointer-events: none;
}
.slide-inner-nav .sin-inner {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  padding: 6px 16px;
  border-radius: 20px;
}
/* 只有活跃页面的内嵌导航才可点击——非活跃页面的 pointer-events: none 会冒泡到此 */
.slide.active .slide-inner-nav .sin-inner { pointer-events: auto; }
.slide-inner-nav .sin-label {
  color: rgba(255,255,255,0.5);
  font-size: 12px;
  margin-right: 4px;
}
.slide-inner-nav .sin-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 26px;
  border-radius: 50%;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.25s ease;
  cursor: pointer;
}
.slide-inner-nav .sin-num:hover {
  background: rgba(255,255,255,0.15);
  color: #fff;
}
.slide-inner-nav .sin-num.active {
  background: #ffffff;
  color: #222;
  font-weight: bold;
  transform: scale(1.15);
}
.slide-inner-nav .sin-arrow {
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  font-size: 13px;
  padding: 0 4px;
  cursor: pointer;
  transition: color 0.2s;
}
.slide-inner-nav .sin-arrow:hover { color: #fff; }
.slide-inner-nav .sin-arrow.disabled {
  color: rgba(255,255,255,0.2);
  cursor: default;
  pointer-events: none;
}
.slide-inner-nav .sin-ellipsis {
  color: rgba(255,255,255,0.3);
  font-size: 12px;
  padding: 0 2px;
}
"""

PAGE_NAV_JS = """
(function initPageNav() {
  var slides = document.querySelectorAll('.slide');
  var dots = document.querySelectorAll('.dot');
  var prevBtn = document.querySelector('.nav-prev');
  var nextBtn = document.querySelector('.nav-next');
  var indicator = document.querySelector('.page-indicator');
  var current = 0;

  function showSlide(index) {
    if (index < 0 || index >= slides.length) return;
    slides.forEach(function(s) { s.classList.remove('active'); });
    dots.forEach(function(d) { d.classList.remove('active'); });
    slides[index].classList.add('active');
    if (dots[index]) dots[index].classList.add('active');
    current = index;
    if (indicator) {
      indicator.textContent = (current + 1) + ' / ' + slides.length;
    }
    if (prevBtn) prevBtn.disabled = (current === 0);
    if (nextBtn) nextBtn.disabled = (current === slides.length - 1);
    /* 更新页面内导航条的高亮 */
    document.querySelectorAll('.sin-num').forEach(function(n) { n.classList.remove('active'); });
    var activeNums = slides[index].querySelectorAll('.sin-num');
    activeNums.forEach(function(n) { n.classList.add('active'); });

    /* 同步 body 的 bg 特效类 → 使 BG_EFFECTS_JS 能正确取到当前页的特效 */
    var oldBgs = document.body.className.match(/\bbg-[\w-]+\b/g);
    if (oldBgs) oldBgs.forEach(function(c) { document.body.classList.remove(c); });
    var slideClasses = slides[index].className.match(/\bbg-[\w-]+\b/g);
    if (slideClasses) slideClasses.forEach(function(c) { document.body.classList.add(c); });
    /* 重入背景特效（函数已设计为可重入——先清除旧层再重建） */
    if (typeof initBgEffects === 'function') initBgEffects();
  }

  if (prevBtn) prevBtn.addEventListener('click', function() {
    if (current > 0) showSlide(current - 1);
  });
  if (nextBtn) nextBtn.addEventListener('click', function() {
    if (current < slides.length - 1) showSlide(current + 1);
  });
  dots.forEach(function(dot, i) {
    dot.addEventListener('click', function() { showSlide(i); });
  });
  /* 页面内导航条点击 */
  document.querySelectorAll('.sin-num').forEach(function(num) {
    num.addEventListener('click', function(e) {
      e.stopPropagation();
      showSlide(parseInt(num.getAttribute('data-page')));
    });
  });
  document.querySelectorAll('.sin-arrow').forEach(function(arr) {
    arr.addEventListener('click', function(e) {
      e.stopPropagation();
      var target = parseInt(arr.getAttribute('data-target'));
      if (!isNaN(target) && target >= 0 && target < slides.length) showSlide(target);
    });
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      if (current < slides.length - 1) showSlide(current + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (current > 0) showSlide(current - 1);
    }
  });
  showSlide(0);
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
    nav_style: str = "floating"  # 页面导航风格: "floating"(底部浮动栏) / "inline"(页面内嵌)

    def to_dict(self) -> dict:
        return {
            "bgType": self.bg_type,
            "bgColor1": self.bg_color1,
            "bgColor2": self.bg_color2,
            "pageTitle": self.page_title,
            "navStyle": self.nav_style,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProjectSettings":
        return cls(
            bg_type=d.get("bgType", "none"),
            bg_color1=d.get("bgColor1", "#ffffff"),
            bg_color2=d.get("bgColor2", "#e8f4f8"),
            page_title=d.get("pageTitle", "我的网站"),
            nav_style=d.get("navStyle", "floating"),
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
    link_url: str = ""            # 超链接 URL
    link_target: str = "_blank"   # 链接目标 (_blank / _self)

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
            "linkUrl": self.link_url, "linkTarget": self.link_target,
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
            link_url=d.get("linkUrl", ""),
            link_target=d.get("linkTarget", "_blank"),
        )


@dataclass
class Page:
    """页面数据模型——仿 PPT 的独立页面"""
    page_id: str
    name: str
    elements: list[Element] = field(default_factory=list)
    settings: Optional[ProjectSettings] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = ProjectSettings()

    def to_dict(self) -> dict:
        return {
            "id": self.page_id,
            "name": self.name,
            "settings": self.settings.to_dict(),
            "elements": [e.to_dict() for e in self.elements],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Page":
        return cls(
            page_id=d.get("id", str(uuid.uuid4())[:8]),
            name=d.get("name", "未命名页面"),
            elements=[Element.from_dict(ed) for ed in d.get("elements", [])],
            settings=ProjectSettings.from_dict(d.get("settings", {})),
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
        if el.text_effect in ("anim-shake","anim-bounce","anim-float","anim-wave",
                               "anim-typing","hover-zoom","hover-scale","hover-rotate",
                               "hover-underline"):
            s += "display:inline-block;"
        s += "}"
        lines.append(s)
    return "\n".join(lines)


def _normalize_url(url: str) -> str:
    """标准化外部链接 URL：
    - 自动补全缺失的 https:// 协议
    - 本地文件路径转为 file:/// 协议
    - HTML 转义防止 XSS / 属性截断
    """
    if not url:
        return url
    url = url.strip()
    # 已有协议 → 直接 HTML 转义后返回
    for prefix in ("http://", "https://", "ftp://", "file:///", "mailto:", "tel:", "data:"):
        if url.startswith(prefix):
            return html.escape(url, quote=True)
    # 本地文件路径（反斜杠或盘符开头）
    if "\\" in url or (len(url) > 1 and url[1] == ":"):
        url = url.replace("\\", "/")
        if len(url) > 1 and url[1] == ":":
            url = f"file:///{url}"
        return html.escape(url, quote=True)
    # 以 # 开头 → 锚点链接，直接返回
    if url.startswith("#"):
        return url
    # 其余的（www.xxx.com / baidu.com 等）→ 补 https://
    return html.escape(f"https://{url}", quote=True)


def _normalize_media_src(src: str) -> str:
    """标准化媒体资源 URL（图片/视频的 src）：
    - 远程 URL 补协议
    - 本地文件保持原样（由调用方做 base64 内联）
    """
    if not src:
        return src
    src = src.strip()
    for prefix in ("http://", "https://", "data:"):
        if src.startswith(prefix):
            return src
    if "\\" in src or (len(src) > 1 and src[1] == ":"):
        return src  # 本地路径，由调用方做 base64 内联
    if src.startswith("//"):
        return f"https:{src}"
    # 看起来像个域名 → 补协议
    if "." in src.split("/")[0]:
        return f"https://{src}"
    return src


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

    inner_html = ""
    if elem.type == "text":
        content_html = elem.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        inner_html = f'<div class="{tag_class}{effect_cls}" style="{style}">{content_html}</div>'

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
        else:
            # 远程 URL → 补全协议
            img_src = _normalize_media_src(img_src)
        br = f"border-radius:{elem.border_radius}px;" if elem.border_radius > 0 else ""
        inner_html = f'<div class="{tag_class}" style="{style}overflow:hidden;"><img src="{img_src}" style="width:100%;height:100%;object-fit:contain;{br}"></div>'

    elif elem.type == "video":
        if not elem.content:
            return ""
        video_src = elem.content
        if not os.path.isfile(video_src):
            video_src = _normalize_media_src(video_src)
        br = f"border-radius:{elem.border_radius}px;" if elem.border_radius > 0 else ""
        inner_html = f'<div class="{tag_class}" style="{style}overflow:hidden;"><video src="{video_src}" controls style="width:100%;height:100%;object-fit:contain;{br}"></video></div>'

    if not inner_html:
        return ""

    # 如果有超链接，包裹 <a> 标签
    if elem.link_url:
        normalized_url = _normalize_url(elem.link_url)
        target = elem.link_target if elem.link_target else "_blank"
        return f'<a href="{normalized_url}" target="{target}" style="text-decoration:none;color:inherit;">{inner_html}</a>'

    return inner_html


def _build_inner_nav_html(page_index: int, total_pages: int) -> str:
    """生成页面内导航条 HTML——只显示附近几页"""
    if total_pages <= 1:
        return ""

    RANGE = 2  # 当前页前后各显示几页

    # 上一页 / 下一页箭头
    prev_html = ""
    if page_index > 0:
        prev_html = f'<span class="sin-arrow" role="button" tabindex="0" data-target="{page_index - 1}">◀ 上一页</span>'
    else:
        prev_html = '<span class="sin-arrow disabled">已经是第一页了</span>'

    next_html = ""
    if page_index < total_pages - 1:
        next_html = f'<span class="sin-arrow" role="button" tabindex="0" data-target="{page_index + 1}">下一页 ▶</span>'
    else:
        next_html = '<span class="sin-arrow disabled">已经是最后一页了</span>'

    # 页码按钮 —— 只显示附近几页
    start_page = max(0, page_index - RANGE)
    end_page = min(total_pages - 1, page_index + RANGE)

    # 保证至少显示 5 页（不足时向两边扩展）
    while end_page - start_page < 4 and total_pages > 5:
        if start_page > 0:
            start_page -= 1
        elif end_page < total_pages - 1:
            end_page += 1
        else:
            break
    start_page = max(0, start_page)
    end_page = min(total_pages - 1, end_page)

    num_html = ""
    # 首页 + 省略号
    if start_page > 0:
        num_html += f'<span class="sin-num" role="button" tabindex="0" data-page="0">1</span>'
        if start_page > 1:
            num_html += '<span class="sin-ellipsis">…</span>'
    # 中间页码
    for i in range(start_page, end_page + 1):
        active = " active" if i == page_index else ""
        num_html += f'<span class="sin-num{active}" role="button" tabindex="0" data-page="{i}">{i + 1}</span>'
    # 省略号 + 末页
    if end_page < total_pages - 1:
        if end_page < total_pages - 2:
            num_html += '<span class="sin-ellipsis">…</span>'
        num_html += f'<span class="sin-num" role="button" tabindex="0" data-page="{total_pages - 1}">{total_pages}</span>'

    return (
        f'<div class="slide-inner-nav">'
        f'<div class="sin-inner">'
        f'{prev_html}'
        f'{num_html}'
        f'{next_html}'
        f'</div></div>'
    )


def _build_page_html(page: Page, page_index: int, total_pages: int, nav_style: str = "floating") -> str:
    """生成单个页面的 HTML"""
    body_classes = []
    bg_style = ""
    s = page.settings
    if s.bg_type == "none":
        bg_style = f"background:{s.bg_color1};"
    elif s.bg_type == "gradient":
        bg_style = f"background:linear-gradient(135deg,{s.bg_color1},{s.bg_color2});"
    elif s.bg_type == "gradient-anim":
        bg_style = f"background:linear-gradient(135deg,{s.bg_color1},{s.bg_color2});"
        body_classes.append("bg-gradient-anim")
    elif s.bg_type in ("bubbles","particles","stars","confetti","snow"):
        bg_style = f"background:{s.bg_color1};"
        body_classes.append(f"bg-{s.bg_type}")

    bg_class_str = " ".join(body_classes)
    slide_class = f"slide{' active' if page_index == 0 else ''}"
    if bg_class_str:
        slide_class += " " + bg_class_str

    slide_style = f"{bg_style}"

    elem_htmls = []
    need_bg_js = s.bg_type not in ("none", "gradient")
    all_need_text_js = False

    for el in sorted(page.elements, key=lambda e: e.z_index):
        h = element_to_html(el)
        if h:
            elem_htmls.append("  " + h)
            if el.type == "text" and el.text_effect != "none":
                all_need_text_js = True

    html = f'<div class="{slide_class}" style="{slide_style}">\n'
    html += '\n'.join(elem_htmls)
    html += f'\n  <div class="slide-page-number">{page_index + 1} / {total_pages}</div>'
    # 页面内导航（仅 inline 模式）
    if nav_style == "inline":
        inner_nav = _build_inner_nav_html(page_index, total_pages)
        if inner_nav:
            html += f'\n  {inner_nav}'
    html += '\n</div>'

    return html, need_bg_js, all_need_text_js


def generate_html(pages: list[Page], global_title: str = "", nav_style: str = "floating") -> str:
    """生成完整多页HTML文档"""
    if not pages:
        return ""
    title = global_title or pages[0].settings.page_title

    # 收集所有页面的 CSS/JS 需求
    all_elements = []
    need_text_css = False
    need_text_js = False
    has_bg = False

    page_htmls = []
    for i, page in enumerate(pages):
        ph, bg_need, txt_need = _build_page_html(page, i, len(pages), nav_style)
        page_htmls.append(ph)
        if bg_need:
            has_bg = True
        if txt_need:
            need_text_js = True
        for el in page.elements:
            if el.type == "text":
                need_text_css = True
            all_elements.append(el)

    # CSS 收集
    css_parts = []
    if need_text_css:
        css_parts.append(_build_text_css(all_elements))
    if need_text_js:
        css_parts.append(TEXT_EFFECTS_CSS)
    if has_bg:
        css_parts.append(BG_EFFECTS_CSS)
    css_parts.append(PAGE_NAV_CSS)
    css_block = "\n".join(css_parts)

    # JS 收集
    js_parts = []
    if has_bg:
        js_parts.append(BG_EFFECTS_JS)
    if need_text_js:
        js_parts.append(TEXT_EFFECTS_JS)
    js_parts.append(PAGE_NAV_JS)
    js_block = "\n".join(js_parts)

    # 第一个页面的 bg class 同步到 body（供 BG_EFFECTS_JS 初始检测）
    first_bg_classes = ""
    if pages:
        p0 = pages[0]
        if p0.settings.bg_type in ("bubbles","particles","stars","confetti","snow"):
            first_bg_classes = f' class="bg-{p0.settings.bg_type}"'

    # 导航栏 HTML（仅 floating 模式）
    nav_html = ""
    if nav_style == "floating":
        dots_html = ""
        for i in range(len(pages)):
            cls = "dot active" if i == 0 else "dot"
            dots_html += f'<button class="{cls}" data-page="{i}"></button>'
        nav_html = f"""<div class="slide-nav">
  <button class="nav-prev" disabled>◀</button>
  <span class="page-indicator">1 / {len(pages)}</span>
  <div class="page-dots">{dots_html}</div>
  <button class="nav-next"{' disabled' if len(pages) <= 1 else ''}>▶</button>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  img {{ max-width:100%; }}
  body {{ font-family:'Microsoft YaHei',Arial,sans-serif; }}
{css_block}
</style>
</head>
<body{first_bg_classes}>
<div class="presentation">
{chr(10).join(page_htmls)}
</div>
{nav_html}
<script>
{js_block}
</script>
</body>
</html>"""


def _build_page_html_static(page: Page, page_index: int, total_pages: int, elements: list,
                             nav_style: str = "floating") -> str:
    """生成单页 HTML (用于静态文件导出，复用已有 elements 列表)"""
    body_classes = []
    bg_style = ""
    s = page.settings
    if s.bg_type == "none":
        bg_style = f"background:{s.bg_color1};"
    elif s.bg_type == "gradient":
        bg_style = f"background:linear-gradient(135deg,{s.bg_color1},{s.bg_color2});"
    elif s.bg_type == "gradient-anim":
        bg_style = f"background:linear-gradient(135deg,{s.bg_color1},{s.bg_color2});"
        body_classes.append("bg-gradient-anim")
    elif s.bg_type in ("bubbles","particles","stars","confetti","snow"):
        bg_style = f"background:{s.bg_color1};"
        body_classes.append(f"bg-{s.bg_type}")

    bg_class_str = " ".join(body_classes)
    slide_class = f"slide{' active' if page_index == 0 else ''}"
    if bg_class_str:
        slide_class += " " + bg_class_str

    slide_style = f"{bg_style}"

    elem_htmls = []
    for el in sorted(elements, key=lambda e: e.z_index):
        h = element_to_html(el)
        if h:
            elem_htmls.append("  " + h)

    html = f'<div class="{slide_class}" style="{slide_style}">\n'
    html += '\n'.join(elem_htmls)
    html += f'\n  <div class="slide-page-number">{page_index + 1} / {total_pages}</div>'
    if nav_style == "inline":
        inner_nav = _build_inner_nav_html(page_index, total_pages)
        if inner_nav:
            html += f'\n  {inner_nav}'
    html += '\n</div>'
    return html


def generate_project_folder(pages: list[Page], folder_path: str, title: str = "", nav_style: str = "floating") -> str:
    """导出为项目文件夹（index.html + style.css + script.js），返回 index.html 路径"""
    if not pages:
        return ""
    if not title:
        title = pages[0].settings.page_title

    # 收集全局元素
    all_elements = []
    need_text_css = False
    need_text_js = False
    has_bg = False

    for page in pages:
        for el in page.elements:
            all_elements.append(el)
            if el.type == "text":
                need_text_css = True
                if el.text_effect != "none":
                    need_text_js = True
        if page.settings.bg_type not in ("none", "gradient"):
            has_bg = True

    # ---- style.css ----
    css_parts = [f"/* {title} - 样式表 */"]
    css_parts.append("body { margin:0; padding:0; font-family:'Microsoft YaHei',Arial,sans-serif; }")
    css_parts.append("img { max-width:100%; }")
    if need_text_css:
        css_parts.append(_build_text_css(all_elements))
    if need_text_js:
        css_parts.append(TEXT_EFFECTS_CSS)
    if has_bg:
        css_parts.append(BG_EFFECTS_CSS)
    css_parts.append(PAGE_NAV_CSS)
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
    js_parts.append(PAGE_NAV_JS)
    js_content = "\n\n".join(js_parts)

    with open(os.path.join(folder_path, "script.js"), "w", encoding="utf-8") as f:
        f.write(js_content)

    # ---- index.html ----
    page_htmls = []
    for i, page in enumerate(pages):
        ph = _build_page_html_static(page, i, len(pages), page.elements, nav_style)
        page_htmls.append(ph)

    # body bg class（供 BG_EFFECTS_JS 初始检测）
    first_bg_classes = ""
    p0 = pages[0]
    if p0.settings.bg_type in ("bubbles","particles","stars","confetti","snow"):
        first_bg_classes = f' class="bg-{p0.settings.bg_type}"'

    # 导航栏（仅 floating 模式）
    nav_html = ""
    if nav_style == "floating":
        dots_html = ""
        for i in range(len(pages)):
            cls = "dot active" if i == 0 else "dot"
            dots_html += f'<button class="{cls}" data-page="{i}"></button>'
        nav_html = f"""<nav class="slide-nav">
  <button class="nav-prev" disabled>◀</button>
  <span class="page-indicator">1 / {len(pages)}</span>
  <div class="page-dots">{dots_html}</div>
  <button class="nav-next"{' disabled' if len(pages) <= 1 else ''}>▶</button>
</nav>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
</head>
<body{first_bg_classes}>
<div class="presentation">
{chr(10).join(page_htmls)}
</div>
{nav_html}
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
    """PPT风格的画布，用于放置和编辑网页元素（支持多页面）"""

    PAGE_W, PAGE_H = 1200, 800
    BG_COLOR = "#e8e8e8"
    PAGE_COLOR = "#ffffff"

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=self.BG_COLOR, highlightthickness=0, **kwargs)
        self.pages: list[Page] = []
        self.current_page_index = 0
        self.selected_id: Optional[str] = None

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

    # ---- 页面代理属性 ----
    @property
    def current_page(self) -> Optional[Page]:
        if 0 <= self.current_page_index < len(self.pages):
            return self.pages[self.current_page_index]
        return None

    @property
    def elements(self) -> list[Element]:
        p = self.current_page
        return p.elements if p else []

    @elements.setter
    def elements(self, value):
        p = self.current_page
        if p:
            p.elements = value

    @property
    def settings(self) -> ProjectSettings:
        p = self.current_page
        return p.settings if p else ProjectSettings()

    @settings.setter
    def settings(self, value):
        p = self.current_page
        if p:
            p.settings = value

    def _calc_next_z(self) -> int:
        max_z = max((e.z_index for e in self.elements), default=0)
        return max_z + 1

    # ---- 页面管理 ----
    def init_default_page(self):
        """初始化一个默认页面"""
        self.pages = [Page(page_id=str(uuid.uuid4())[:8], name="首页")]
        self.current_page_index = 0
        self.selected_id = None
        self.after(100, self.redraw)

    def add_new_page(self, name: str = None) -> str:
        """添加新页面"""
        if name is None:
            name = f"第 {len(self.pages) + 1} 页"
        page = Page(page_id=str(uuid.uuid4())[:8], name=name)
        self.pages.append(page)
        self.switch_to_page(len(self.pages) - 1)
        return page.page_id

    def delete_page(self, page_index: int) -> bool:
        """删除指定页面（至少保留一页）"""
        if len(self.pages) <= 1:
            return False
        self.pages.pop(page_index)
        if self.current_page_index >= len(self.pages):
            self.current_page_index = len(self.pages) - 1
        elif self.current_page_index == page_index:
            self.current_page_index = min(page_index, len(self.pages) - 1)
        self.selected_id = None
        self.redraw()
        self.event_generate("<<PageChanged>>")
        self.event_generate("<<SelectionChanged>>")
        return True

    def switch_to_page(self, index: int):
        """切换到指定页面"""
        if 0 <= index < len(self.pages):
            if self._edit_widget:
                self._finish_editing()
            self.current_page_index = index
            self.selected_id = None
            self.redraw()
            self.event_generate("<<PageChanged>>")
            self.event_generate("<<SelectionChanged>>")

    def move_page(self, from_idx: int, to_idx: int):
        """移动页面顺序"""
        if 0 <= from_idx < len(self.pages) and 0 <= to_idx < len(self.pages):
            page = self.pages.pop(from_idx)
            self.pages.insert(to_idx, page)
            self.current_page_index = to_idx
            self.redraw()
            self.event_generate("<<PageChanged>>")

    def rename_page(self, page_index: int, new_name: str):
        """重命名页面"""
        if 0 <= page_index < len(self.pages) and new_name:
            self.pages[page_index].name = new_name
            self.event_generate("<<PageChanged>>")

    # ---- 元素管理 ----
    def add_element(self, elem: Element) -> str:
        elem.z_index = self._calc_next_z()
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
        bg = self.settings.bg_color1
        self.create_rectangle(x1, y1, x2, y2, fill=bg, outline="#cccccc", width=1, tags="page")
        if self.settings.bg_type in ("gradient", "gradient-anim"):
            self.create_rectangle(x1, y1, x2, y2, fill=self.settings.bg_color2,
                                  stipple="gray25", outline="", tags="page")
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

        # 超链接指示器
        has_link = bool(elem.link_url)

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

            effect_label = ""
            if elem.text_effect != "none":
                effect_label = TEXT_EFFECT_NAMES.get(elem.text_effect, "")
                effect_label = f" [{effect_label}]"

            link_tag = " 🔗" if has_link else ""

            item_id = self.create_text(
                cx + cw // 2, cy + ch // 2,
                text=display_text + effect_label + link_tag,
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
                img_label = os.path.basename(elem.content) if elem.content else "图片"
                extra = " 🔗" if has_link else ""
                self.create_text(cx + cw // 2, cy + ch // 2,
                                 text=f"🖼️ {img_label}{extra}",
                                 font=("Microsoft YaHei", 9), fill="#999999",
                                 anchor="center", tags=tags)

        elif elem.type == "video":
            self.create_rectangle(cx, cy, cx + cw, cy + ch,
                                  outline=bc, width=bw, fill="#e8f4f8", tags=tags)
            vlabel = os.path.basename(elem.content) if elem.content else "视频"
            extra = " 🔗" if has_link else ""
            self.create_text(cx + cw // 2, cy + ch // 2 - 6,
                             text=f"▶ {vlabel}{extra}",
                             font=("Microsoft YaHei", 9), fill="#666666",
                             anchor="center", tags=tags)
            if not elem.content:
                self.create_text(cx + cw // 2, cy + ch // 2 + 12,
                                 text="点击选择视频文件",
                                 font=("Microsoft YaHei", 7), fill="#999999",
                                 anchor="center", tags=tags)

        # 超链接下划线装饰
        if has_link:
            self.create_line(cx + 4, cy + ch - 2, cx + cw - 4, cy + ch - 2,
                             fill="#0066ff", width=1, tags=("link_line",) + tags)

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
            self.redraw()

    def _move_down(self, elem_id: str):
        elem = self.get_element(elem_id)
        if elem and elem.z_index > 0:
            elem.z_index -= 1
            self.redraw()

    # ---- 导出 ----
    def to_html(self, title: str = "") -> str:
        nav_style = self.pages[0].settings.nav_style if self.pages else "floating"
        return generate_html(self.pages, title, nav_style)


# ============================================================
# 页面缩略图侧边栏
# ============================================================
class PageThumbnailPanel(tk.Frame):
    """左侧页面缩略图面板——仿 PPT 的页面浏览"""

    THUMB_W = 160
    THUMB_H = 100
    PANEL_W = 190

    def __init__(self, master, canvas: DesignCanvas, **kwargs):
        super().__init__(master, width=self.PANEL_W, bg="#2d2d2d", **kwargs)
        self.canvas = canvas
        self._thumb_widgets: list[tk.Widget] = []
        self.pack_propagate(False)

        # 标题
        header = tk.Frame(self, bg="#2d2d2d")
        header.pack(fill="x", padx=6, pady=6)
        tk.Label(header, text="📄 页面", font=("Microsoft YaHei", 11, "bold"),
                 bg="#2d2d2d", fg="#ffffff").pack(side="left")
        tk.Button(header, text="＋", font=("Arial", 12, "bold"),
                  bg="#444444", fg="white", relief="flat", width=3, cursor="hand2",
                  command=self._add_page).pack(side="right")

        # 滚动区域
        self._scroll_canvas = tk.Canvas(self, bg="#2d2d2d", highlightthickness=0,
                                        width=self.PANEL_W - 6)
        self._scroll_bar = tk.Scrollbar(self, orient="vertical",
                                        command=self._scroll_canvas.yview)
        self._scroll_inner = tk.Frame(self._scroll_canvas, bg="#2d2d2d")

        self._scroll_inner.bind("<Configure>", lambda e: self._scroll_canvas.configure(
            scrollregion=self._scroll_canvas.bbox("all")))
        self._scroll_canvas.create_window((0, 0), window=self._scroll_inner, anchor="n",
                                          width=self.PANEL_W - 16)
        self._scroll_canvas.configure(yscrollcommand=self._scroll_bar.set)

        self._scroll_canvas.pack(side="left", fill="both", expand=True, padx=(3, 0))
        self._scroll_bar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self._scroll_canvas.yview_scroll(-1 * (event.delta // 120), "units")
        self._scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel, add="+")

        self.canvas.bind("<<PageChanged>>", lambda e: self.refresh())
        self.canvas.bind("<<ElementChanged>>", lambda e: self.refresh())

    def refresh(self):
        """刷新缩略图列表"""
        for w in self._thumb_widgets:
            w.destroy()
        self._thumb_widgets = []

        for i, page in enumerate(self.canvas.pages):
            tw = self._build_thumbnail(page, i)
            tw.pack(fill="x", padx=6, pady=3)
            self._thumb_widgets.append(tw)

    def _build_thumbnail(self, page: Page, index: int) -> tk.Frame:
        """构建单个页面缩略图"""
        is_active = index == self.canvas.current_page_index
        bg_color = "#3a3a4a" if is_active else "#353535"
        border_color = "#0066ff" if is_active else "#555555"

        frame = tk.Frame(self._scroll_inner, bg=bg_color,
                         highlightbackground=border_color,
                         highlightthickness=2 if is_active else 1,
                         cursor="hand2")

        # 缩略图画布
        thumb_canvas = tk.Canvas(frame, width=self.THUMB_W, height=self.THUMB_H,
                                 bg=page.settings.bg_color1,
                                 highlightthickness=0)
        thumb_canvas.pack(padx=4, pady=(4, 0))

        # 简化的元素预览
        self._draw_thumb_preview(thumb_canvas, page.elements)

        # 页面名称（可编辑）
        name_frame = tk.Frame(frame, bg=bg_color)
        name_frame.pack(fill="x", padx=4, pady=(2, 4))

        page_num_label = tk.Label(name_frame, text=f"{index + 1}",
                                  font=("Arial", 8), bg=bg_color,
                                  fg="#888888", width=2)
        page_num_label.pack(side="left")

        name_label = tk.Label(name_frame, text=page.name,
                              font=("Microsoft YaHei", 9), bg=bg_color,
                              fg="#ffffff" if is_active else "#cccccc",
                              anchor="w", padx=2)
        name_label.pack(side="left", fill="x", expand=True)

        # 点击切换到该页面
        def on_click(e, idx=index):
            self.canvas.switch_to_page(idx)
            self.refresh()

        for widget in (frame, thumb_canvas, name_label, page_num_label):
            widget.bind("<Button-1>", on_click)

        # 右键菜单
        def on_right_click(e, idx=index):
            menu = tk.Menu(self, tearoff=0, bg="#444444", fg="white")
            menu.add_command(label="重命名", command=lambda: self._rename_page(idx))
            menu.add_command(label="复制页面", command=lambda: self._duplicate_page(idx))
            if len(self.canvas.pages) > 1:
                menu.add_command(label=f"删除「{page.name}」", command=lambda: self._delete_page(idx))
            if idx > 0:
                menu.add_command(label="⬆ 左移", command=lambda: self._move_page(idx, idx - 1))
            if idx < len(self.canvas.pages) - 1:
                menu.add_command(label="⬇ 右移", command=lambda: self._move_page(idx, idx + 1))
            menu.tk_popup(e.x_root, e.y_root)

        frame.bind("<Button-3>", on_right_click)
        thumb_canvas.bind("<Button-3>", on_right_click)
        name_label.bind("<Button-3>", on_right_click)

        return frame

    def _draw_thumb_preview(self, canvas: tk.Canvas, elements: list[Element]):
        """在缩略图画布上绘制简化的元素预览"""
        if not elements:
            cx, cy = self.THUMB_W // 2, self.THUMB_H // 2
            canvas.create_text(cx, cy, text="空页面", font=("Microsoft YaHei", 8),
                               fill="#999999", anchor="center")
            return

        scale_x = self.THUMB_W / 1200
        scale_y = self.THUMB_H / 800
        scale = min(scale_x, scale_y) * 0.85
        offset_x = (self.THUMB_W - 1200 * scale) / 2
        offset_y = (self.THUMB_H - 800 * scale) / 2

        for elem in sorted(elements, key=lambda e: e.z_index):
            x1 = offset_x + elem.x * scale
            y1 = offset_y + elem.y * scale
            x2 = x1 + elem.width * scale
            y2 = y1 + elem.height * scale

            # 尺寸过滤——太小就不画了
            if x2 - x1 < 4 or y2 - y1 < 3:
                continue

            if elem.type == "text":
                color = elem.color if elem.color != "transparent" else "#333"
                canvas.create_rectangle(x1, y1, x2, y2,
                                        outline=color, fill="",
                                        width=1)
                # 文字行示意
                line_y = y1 + (y2 - y1) * 0.3
                text_w = (x2 - x1) * 0.8
                canvas.create_line(x1 + 3, line_y, x1 + 3 + text_w, line_y,
                                   fill=color, width=1)
                if y2 - y1 > 12:
                    canvas.create_line(x1 + 3, line_y + 4, x1 + 3 + text_w * 0.6, line_y + 4,
                                       fill=color, width=1)

            elif elem.type == "image":
                canvas.create_rectangle(x1, y1, x2, y2,
                                        fill="#e0e0e0", outline="#aaaaaa", width=1)
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                canvas.create_text(mx, my, text="🖼", font=("Arial", max(6, int((x2-x1)/6))),
                                   fill="#888888", anchor="center")

            elif elem.type == "video":
                canvas.create_rectangle(x1, y1, x2, y2,
                                        fill="#d0e8f4", outline="#88bbdd", width=1)
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                canvas.create_text(mx, my, text="▶", font=("Arial", max(6, int((x2-x1)/6))),
                                   fill="#5588aa", anchor="center")

    def _add_page(self):
        self.canvas.add_new_page()
        self.refresh()

    def _delete_page(self, index: int):
        name = self.canvas.pages[index].name
        if messagebox.askyesno("删除页面", f"确定要删除「{name}」吗？\n该页面上的所有元素将被删除。"):
            self.canvas.delete_page(index)
            self.refresh()

    def _rename_page(self, index: int):
        old_name = self.canvas.pages[index].name
        new_name = simpledialog.askstring("重命名页面", "请输入新名称：",
                                          initialvalue=old_name)
        if new_name:
            self.canvas.rename_page(index, new_name)
            self.refresh()

    def _duplicate_page(self, index: int):
        """复制页面"""
        src = self.canvas.pages[index]
        new_elements = []
        for el in src.elements:
            new_el = copy.deepcopy(el)
            new_el.elem_id = str(uuid.uuid4())[:8]
            new_elements.append(new_el)

        new_page = Page(
            page_id=str(uuid.uuid4())[:8],
            name=f"{src.name} (副本)",
            elements=new_elements,
            settings=copy.deepcopy(src.settings),
        )
        self.canvas.pages.insert(index + 1, new_page)
        self.canvas.switch_to_page(index + 1)
        self.refresh()

    def _move_page(self, from_idx: int, to_idx: int):
        self.canvas.move_page(from_idx, to_idx)
        self.refresh()


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

        def _on_mousewheel(event):
            self._scroll_canvas.yview_scroll(-1 * (event.delta // 120), "units")
        self._scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel, add="+")

        self.canvas.bind("<<SelectionChanged>>", self._on_selection_changed)
        # 页面切换时也刷新属性面板
        self.canvas.bind("<<PageChanged>>", self._on_page_changed)

        # 首次初始化时显示项目控制面板
        self.after(200, self._on_selection_changed)

    def _on_page_changed(self, event=None):
        """页面切换时强制刷新属性面板"""
        self._on_selection_changed()

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
        """无选中元素时显示项目/背景设置"""
        f = self._scroll_inner
        s = self.canvas.settings

        # ---- 页面背景 ----
        tk.Label(f, text="🌐 页面背景", font=("Microsoft YaHei", 11, "bold"),
                 bg="#f8f8f8", anchor="w").pack(fill="x", pady=(0, 8))

        # 背景特效
        tk.Label(f, text="背景特效:", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", anchor="w").pack(fill="x")
        bg_names = list(BG_EFFECT_NAMES.keys())
        bg_labels = [BG_EFFECT_NAMES[k] for k in bg_names]
        initial_label = BG_EFFECT_NAMES.get(s.bg_type, s.bg_type)
        bg_var = tk.StringVar(value=initial_label)
        cb = ttk.Combobox(f, textvariable=bg_var, values=bg_labels,
                          state="readonly", width=22)
        cb.pack(pady=(2, 6))

        # 颜色标签动态更新
        def _get_color_labels(bg_key: str):
            if bg_key in ("gradient", "gradient-anim"):
                return "渐变色 1:", "渐变色 2:"
            elif bg_key == "none":
                return "背景色:", None
            else:  # bubbles / stars / snow ...
                return "背景色:", None

        color_row_frame = tk.Frame(f, bg="#f8f8f8")
        color_row_frame.pack(fill="x")

        label1, label2 = _get_color_labels(s.bg_type)
        self._add_bg_color_row(color_row_frame, label1, s.bg_color1,
                               lambda c: setattr(s, 'bg_color1', c))

        # 颜色2 容器（根据需要显示/隐藏）
        self._color2_frame = tk.Frame(color_row_frame, bg="#f8f8f8")
        self._color2_frame.pack(fill="x")
        if label2:
            self._add_bg_color_row(self._color2_frame, label2, s.bg_color2,
                                   lambda c: setattr(s, 'bg_color2', c))
        else:
            self._color2_frame.pack_forget()

        def on_bg_select(event):
            idx = cb.current()
            if idx >= 0:
                s.bg_type = bg_names[idx]
                # 刷新颜色标签
                for w in color_row_frame.winfo_children():
                    w.destroy()
                l1, l2 = _get_color_labels(s.bg_type)
                self._add_bg_color_row(color_row_frame, l1, s.bg_color1,
                                       lambda c: setattr(s, 'bg_color1', c))
                if l2:
                    self._color2_frame = tk.Frame(color_row_frame, bg="#f8f8f8")
                    self._color2_frame.pack(fill="x")
                    self._add_bg_color_row(self._color2_frame, l2, s.bg_color2,
                                           lambda c: setattr(s, 'bg_color2', c))
                self.canvas.redraw()
        cb.bind("<<ComboboxSelected>>", on_bg_select)

        # 颜色说明提示
        hint_map = {
            "none": "仅使用「背景色」填充页面",
            "gradient": "两种渐变色从上到下混合过渡",
            "gradient-anim": "两种渐变色动态流动",
            "bubbles": "半透明气泡从底部升起（背景色上方）",
            "particles": "彩色粒子漂浮飘散",
            "stars": "白色星星闪烁",
            "confetti": "彩色纸屑飘落",
            "snow": "雪花缓缓飘落",
        }
        hint_text = hint_map.get(s.bg_type, "")
        hint_label = tk.Label(f, text=hint_text,
                              font=("Microsoft YaHei", 7), bg="#f8f8f8", fg="#888888",
                              wraplength=200, anchor="w", justify="left")
        hint_label.pack(fill="x", pady=(2, 0))

        # 特效提示随选择变化
        def update_hint(event=None):
            idx = cb.current()
            if idx >= 0:
                key = bg_names[idx]
                hint_label.config(text=hint_map.get(key, ""))
        cb.bind("<<ComboboxSelected>>", update_hint, add="+")

        sep1 = tk.Frame(f, height=1, bg="#dddddd")
        sep1.pack(fill="x", pady=8)

        # ---- 页面导航风格 ----
        tk.Label(f, text="📄 页面导航风格", font=("Microsoft YaHei", 11, "bold"),
                 bg="#f8f8f8", anchor="w").pack(fill="x", pady=(0, 6))

        nav_style_var = tk.StringVar(value=s.nav_style)
        nav_floating = tk.Radiobutton(
            f, text="浮动导航栏  — 底部固定黑条，◀ 页码 ●●● ▶",
            variable=nav_style_var, value="floating",
            bg="#f8f8f8", font=("Microsoft YaHei", 8),
            anchor="w", wraplength=220, justify="left",
            command=lambda: self._update_nav_style(nav_style_var.get()))
        nav_floating.pack(fill="x", pady=1)

        nav_inline = tk.Radiobutton(
            f, text="页面内嵌导航 — 每页底部显示页码条，可点击切换",
            variable=nav_style_var, value="inline",
            bg="#f8f8f8", font=("Microsoft YaHei", 8),
            anchor="w", wraplength=220, justify="left",
            command=lambda: self._update_nav_style(nav_style_var.get()))
        nav_inline.pack(fill="x", pady=1)

        tk.Label(f, text="提示：两种导航均支持键盘← →翻页",
                 font=("Microsoft YaHei", 7), bg="#f8f8f8", fg="#999999",
                 wraplength=200, anchor="w").pack(fill="x", pady=(2, 0))

    def _update_nav_style(self, style: str):
        """更新所有页面的导航风格为统一设置"""
        for page in self.canvas.pages:
            page.settings.nav_style = style
        self.canvas.redraw()

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

        # ===== 超链接设置（所有元素通用） =====
        link_header = tk.Frame(f, bg="#f8f8f8")
        link_header.pack(fill="x", pady=2)
        tk.Label(link_header, text="🔗 超链接", font=("Microsoft YaHei", 10, "bold"),
                 bg="#f8f8f8", anchor="w").pack(fill="x")

        # 链接 URL
        tk.Label(f, text="链接地址:", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", anchor="w").pack(fill="x")
        link_url_var = tk.StringVar(value=elem.link_url)
        link_url_entry = tk.Entry(f, textvariable=link_url_var,
                                  font=("Microsoft YaHei", 9))
        link_url_entry.pack(fill="x", pady=(0, 2), ipady=1)

        def on_link_url_change(*_):
            self._update_elem(link_url=link_url_var.get())
        link_url_var.trace_add("write", on_link_url_change)

        # 链接目标
        target_row = tk.Frame(f, bg="#f8f8f8")
        target_row.pack(fill="x", pady=2)
        tk.Label(target_row, text="打开方式:", font=("Microsoft YaHei", 9),
                 bg="#f8f8f8", width=8, anchor="w").pack(side="left")
        link_target_var = tk.StringVar(value=elem.link_target)
        target_cb = ttk.Combobox(target_row, textvariable=link_target_var,
                                 values=["_blank (新窗口)", "_self (当前窗口)", "_parent", "_top"],
                                 state="readonly", width=16)
        target_cb.pack(side="left", padx=2)
        target_map = {
            "_blank (新窗口)": "_blank",
            "_self (当前窗口)": "_self",
            "_parent": "_parent",
            "_top": "_top",
        }

        def on_target_select(event):
            label = target_cb.get()
            if label in target_map:
                self._update_elem(link_target=target_map[label])
        target_cb.bind("<<ComboboxSelected>>", on_target_select)

        # 设置初始选中值
        for k, v in target_map.items():
            if v == elem.link_target:
                target_cb.set(k)
                break

        # 清除链接按钮
        tk.Button(f, text="清除链接", font=("Microsoft YaHei", 8),
                  fg="#cc3333",
                  command=lambda: (link_url_var.set(""),
                                   self._update_elem(link_url=""))
                  ).pack(anchor="w", pady=(0, 4))

        sep_link = tk.Frame(f, height=1, bg="#dddddd")
        sep_link.pack(fill="x", pady=6)

        if elem.type == "text":
            # ----- 文字特效 -----
            tk.Label(f, text="文字特效:", font=("Microsoft YaHei", 9),
                     bg="#f8f8f8", anchor="w").pack(fill="x")
            eff_keys = list(TEXT_EFFECT_NAMES.keys())
            eff_labels = [TEXT_EFFECT_NAMES[k] for k in eff_keys]
            # 用 label 而非 key 作为初始显示值
            initial_eff = TEXT_EFFECT_NAMES.get(elem.text_effect, elem.text_effect)
            eff_var = tk.StringVar(value=initial_eff)
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
        self.title("简易网站可视化编辑器 · WYSIWYG Website Builder (多页+超链接)")
        self.geometry("1400x900")
        self.minsize(1100, 600)
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

        # 中间：画布容器 (先创建画布，后续面板需要引用它)
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

        # 左侧：页面缩略图
        self.page_thumb_panel = PageThumbnailPanel(main_frame, self.canvas)
        self.page_thumb_panel.pack(side="left", fill="y")

        self.property_panel = PropertyPanel(main_frame, self.canvas)
        self.property_panel.pack(side="right", fill="y")

        # 初始化默认页面
        self.canvas.init_default_page()
        self.page_thumb_panel.refresh()

        # ===== 状态栏 =====
        status_bar = tk.Frame(self, bg="#e8e8e8", height=24)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        self._status_bar_label = tk.Label(
            status_bar,
            text="点击工具栏按钮添加元素 · 拖拽移动 · 双击编辑文字 · 左侧切换页面",
            font=("Microsoft YaHei", 8), bg="#e8e8e8", fg="#666666", anchor="w", padx=10
        )
        self._status_bar_label.pack(side="left")

        self._elem_count_label = tk.Label(
            status_bar, text="元素: 0", font=("Microsoft YaHei", 8),
            bg="#e8e8e8", fg="#666666", padx=10
        )
        self._elem_count_label.pack(side="right")

        self._page_count_label = tk.Label(
            status_bar, text="页面: 1", font=("Microsoft YaHei", 8),
            bg="#e8e8e8", fg="#666666", padx=10
        )
        self._page_count_label.pack(side="right")

        self.canvas.bind("<<ElementChanged>>", self._on_element_changed)
        self.canvas.bind("<<PageChanged>>", self._on_page_changed)

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
                + (f" 🔗{elem.link_url}" if elem.link_url else "")
            )

    def _on_page_changed(self, event=None):
        page_count = len(self.canvas.pages)
        current = self.canvas.current_page_index + 1
        self._page_count_label.config(text=f"页面: {page_count}")
        self._status_bar_label.config(
            text=f"当前: 第 {current}/{page_count} 页「{self.canvas.current_page.name}」"
        )
        self._on_element_changed()

    def _add_text(self):
        elem = Element(
            elem_id=str(uuid.uuid4())[:8], type="text",
            x=100, y=100, width=220, height=60,
            content="欢迎来到我的网站！",
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
                       content=path)
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
                       content=path_or_url)
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
        total_elems = sum(len(p.elements) for p in self.canvas.pages)
        if total_elems == 0:
            messagebox.showinfo("提示", "所有页面均为空，请先添加一些元素。")
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
        total_elems = sum(len(p.elements) for p in self.canvas.pages)
        if total_elems == 0:
            messagebox.showinfo("提示", "所有页面均为空，请先添加一些元素。")
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
            messagebox.showinfo("导出成功",
                                f"多页HTML已导出到:\n{file_path}\n\n"
                                f"共 {len(self.canvas.pages)} 页，支持键盘箭头翻页！")
            self._status_label.config(text=f" 已导出: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def _export_folder(self):
        """导出为项目文件夹（含单独的 CSS/JS 文件）"""
        total_elems = sum(len(p.elements) for p in self.canvas.pages)
        if total_elems == 0:
            messagebox.showinfo("提示", "所有页面均为空，请先添加一些元素。")
            return
        folder_path = filedialog.askdirectory(title="选择导出文件夹")
        if not folder_path:
            return
        name = simpledialog.askstring("项目名称", "请输入项目名称：", initialvalue="my_website")
        if not name:
            name = "my_website"
        target = os.path.join(folder_path, name)
        try:
            title = self.canvas.pages[0].settings.page_title if self.canvas.pages else "我的网站"
            nav_style = self.canvas.pages[0].settings.nav_style if self.canvas.pages else "floating"
            html_path = generate_project_folder(
                self.canvas.pages, target, title=title, nav_style=nav_style
            )
            messagebox.showinfo(
                "导出成功",
                f"项目已导出到文件夹:\n{target}\n\n"
                f"共 {len(self.canvas.pages)} 页\n"
                f"包含文件:\n  index.html\n  style.css\n  script.js"
            )
            self._status_label.config(text=f" 已导出项目: {name}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def _save_project(self):
        data = {
            "version": 3,
            "pageTitle": self.canvas.pages[0].settings.page_title if self.canvas.pages else "我的网站",
            "currentPage": self.canvas.current_page_index,
            "pages": [p.to_dict() for p in self.canvas.pages],
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

            ver = data.get("version", 1)

            if ver >= 3:
                # v3 格式：多页面
                pages = [Page.from_dict(pd) for pd in data.get("pages", [])]
                if not pages:
                    pages = [Page(page_id=str(uuid.uuid4())[:8], name="首页")]
                self.canvas.pages = pages
                self.canvas.current_page_index = data.get("currentPage", 0)
                if self.canvas.current_page_index >= len(pages):
                    self.canvas.current_page_index = 0

            elif ver == 2:
                # v2 格式：单页，兼容转换为多页
                sdata = data.get("settings", {})
                settings = ProjectSettings.from_dict(sdata)
                elements = [Element.from_dict(ed) for ed in data.get("elements", [])]
                page = Page(
                    page_id=str(uuid.uuid4())[:8],
                    name="首页",
                    elements=elements,
                    settings=settings,
                )
                self.canvas.pages = [page]
                self.canvas.current_page_index = 0

            else:
                messagebox.showerror("打开失败", f"未知的项目版本: v{ver}")
                return

            self.canvas.selected_id = None
            self.canvas.redraw()
            self.current_file = file_path
            self.page_thumb_panel.refresh()
            self._on_page_changed()
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
        if any(len(p.elements) > 0 for p in self.canvas.pages):
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
