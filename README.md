<div align="center">
  <h1>🎨 Website Builder 1.1</h1>
  <p><strong>PPT 风格的可视化网站编辑器 — 拖拽生成多页 HTML 网站，无需写一行代码</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python">
    <img src="https://img.shields.io/badge/UI-Tkinter-orange">
    <img src="https://img.shields.io/badge/license-MIT-green">
    <img src="https://img.shields.io/badge/status-stable-brightgreen">
  </p>
  <br>
</div>

---

## ✨ 亮点速览

| 功能 | 说明 |
|------|------|
| 🖱️ **拖拽编辑** | 像 PPT 一样在画布上随意拖放、缩放元素 |
| 📄 **多页面管理** | 支持多页面，左侧缩略图面板，一键切换、复制、排序 |
| 🎭 **16 种文字特效** | 渐变、霓虹灯、3D 立体、波浪、打字机、悬停放大… |
| 🌌 **8 种背景特效** | 气泡、粒子、星空、纸屑、飘雪、动态渐变… |
| 🔗 **超链接支持** | 外部链接、本地文件、任意 URL 自动补全协议 |
| 🖼️ **图片/视频嵌入** | 支持本地文件自动转 base64 内联，也支持远程 URL |
| 📤 **一键导出 HTML** | 生成可直接运行的完整 HTML 文档，所有特效和交互都在 |
| ⌨️ **键盘导航** | 左右箭头键切换页面，原生般的浏览体验 |

---

## 🚀 快速开始

### 方式 1：直接运行 exe（推荐）

下载 `WebsiteBuilder1.1.exe`，双击运行即可，无需任何环境配置。

### 方式 2：源码运行

```bash
# 克隆仓库
git clone https://github.com/your-username/WebsiteBuilder1.1.git
cd WebsiteBuilder1.1

# 安装依赖（可选，仅图片需要 Pillow）
pip install Pillow

# 运行
python solution.py
```

> **依赖说明**：图片功能和部分美化依赖 `Pillow`，如有报错 `pip install Pillow` 即可。核心编辑功能无需任何额外依赖。

---

## 📸 界面预览

```
┌─────────────────────────────────────────────────────┐
│  📄 页面              🎨 Website Builder 1.1    ⚙ 属性 │
│  ┌──────┐  ┌──────────────────────────────┐  ┌────┐ │
│  │ 首页  │  │                              │  │背景│ │
│  │      │  │    ☀️ 欢迎来到我的网站          │  │特效│ │
│  │ 第2页 │  │                              │  │链接│ │
│  │      │  │    🖱️ 拖拽编辑，双击修改文字    │  │... │ │
│  │ 第3页 │  │                              │  └────┘ │
│  └──────┘  └──────────────────────────────┘         │
│              ◀ 1 / 3 ▶                              │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 核心功能介绍

### 🖱️ 所见即所得编辑器
- **拖拽移动**：选中元素直接拖拽
- **缩放调整**：8 个控制手柄，任意方向调整尺寸
- **双击编辑**：双击文字元素进入内联编辑模式
- **右键菜单**：删除、上移/下移图层

### 📄 多页面管理（PPT 风格）
- 左侧缩略图面板直观展示所有页面
- 右键页面可：**重命名 / 复制 / 删除 / 左右移动**
- 支持两种导航风格：
  - **浮动导航栏** → 底部固定黑条，带圆点指示器
  - **页面内嵌导航** → 每页底部显示页码条

### 🎭 文字特效丰富
```
📐 3D 立体    💡 霓虹灯    🌈 渐变文字    ✏️ 描边文字
📳 抖动       🏀 弹跳      🌊 波浪        ⌨️ 打字机
✨ 呼吸发光    🎈 漂浮      🔍 悬停放大    🔄 悬停旋转
```

### 🌌 沉浸式背景特效
```css
✨ 动态渐变    🫧 气泡升起    🌟 闪烁星空
🎊 五彩纸屑    ❄️ 飘雪效果    ✨ 粒子漂浮
```

### 🔗 智能链接处理
- 自动补全 `https://` 协议 — 输入 `baidu.com` 即可用
- 本地文件路径自动识别 — `C:\page.html` → `file:///`
- HTML 转义保护 — 防止特殊字符破坏页面

---

## 📦 生成 HTML 示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>我的网站</title>
    <!-- 所有 CSS 内置，无需额外加载 -->
</head>
<body>
    <!-- 多页幻灯片结构 + 交互 JS -->
    <div class="presentation">
        <div class="slide active">...</div>
        <div class="slide">...</div>
    </div>
    <script>
        // 键盘导航、页面切换、特效动画
    </script>
</body>
</html>
```

> 导出的 HTML 是一个**自包含文件** — 所有 CSS 样式、JavaScript 交互都打包在里面，放到任何 Web 服务器或本地打开都能直接运行。

---

## 🧰 技术栈

| 技术 | 用途 |
|------|------|
| **Python 3.10** | 核心语言 |
| **Tkinter** | GUI 桌面界面 |
| **Pillow** | 图片处理（可选） |
| **PyInstaller** | 打包为独立 exe |
| **CSS3 Animations** | 前端特效动画 |
| **Vanilla JS** | 页面交互逻辑 |

---

## 📁 项目结构

```
WebsiteBuilder1.1/
├── solution.py          # 主程序（单文件）
├── WebsiteBuilder1.1.exe # 打包好的可执行文件
├── README.md            # 本文件
└── LICENSE              # 开源许可证
```

> **单文件设计**：整个编辑器只有 1 个 Python 文件，方便阅读、修改和分发。

---

## 📜 开源协议

本项目采用 MIT 协议开源 — 你可以自由使用、修改和分发。

---

<div align="center">
  <sub>如果觉得有用，别忘了 ⭐ Star 支持一下！</sub>
  <br>
  <sub>Made with ❤️ by a passionate developer</sub>
</div>
