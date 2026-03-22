# 📸 AIGC -live photo跨平台动态图生成器
### Live & Motion Photo Maker

> 基于 Python 与 Gradio 构建的全平台动态图生成工具，深度融合 AIGC 视频大模型，让静态图片获得动态灵魂。

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-UI-FF7C00?style=flat-square&logo=gradio&logoColor=white)](https://gradio.app/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Media_Engine-007808?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![ExifTool](https://img.shields.io/badge/ExifTool-Metadata-F5A623?style=flat-square)](https://exiftool.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 📖 项目简介

本项目是一款覆盖 **Apple** 与 **Android** 双平台的原生动态照片生成工具。无需任何专业软件，只需上传图片（或短视频），即可一键生成可直接导入系统相册、支持长按播放的 Live Photo / Motion Photo 文件。

更进一步，项目内置 **智谱 CogVideoX 图生视频大模型**，当素材为纯静态图片时，AI 将自动为其生成平滑自然的 3 秒动态背景——让每一张照片都"活"起来。



# 演示视频

https://github.com/hacoresapling/AIGC-LivePhoto-Maker/issues/1#issue-4116147182



# 生成结果展示

输入静态图，输出长视频转换为实况图：

https://github.com/hacoresapling/AIGC-LivePhoto-Maker/issues/2#issue-4116163054

进一步下载生成文件至手机端，生成live实况图：

https://github.com/hacoresapling/AIGC-LivePhoto-Maker/issues/3#issue-4116183584

---

## ✨ 核心亮点

### 🍏 Apple Live Photo — 原生级元数据注入
突破 iOS 闭环生态壁垒，使用 **ExifTool** 精准注入符合 Apple 规范的 **36 位带连字符 UUID**，实现图片与配对视频的强绑定。生成的文件导入系统相册后，原生支持长按播放，与手机直拍 Live Photo 体验完全一致。

### 🤖 Android Motion Photo — 底层二进制拼接
完美兼容 Google Photos 动态图标准。采用 **Binary Appending** 技术，将 MP4 数据流直接物理追加至 JPG 文件尾部，并注入 **XMP 元数据**，实现单文件传输、零动效损失，开箱即用。

### 🧠 AIGC 视频大模型赋能
内置智能路由引擎，自动识别输入素材类型：
- 输入为**静态图片**或**不足 3 秒的短视频**时 → 自动调用 **智谱 CogVideoX** 图生视频模型，生成 3 秒动态背景
- 输入为**合规视频素材**时 → 直接进入格式转换流程，跳过 AI 调用，节省成本与时间

### ⚙️ 降级兜底机制
当用户未配置 AI 大模型 API Key 时，系统自动降级至本地 **FFmpeg 引擎**，生成基础的缩放/平移动效，确保业务流程 **100% 闭环**，不因缺少外部服务而中断。

---

## 🏗️ 技术架构

```
用户输入 (图片 / 视频)
       │
       ▼
┌─────────────────────────────┐
│        app.py               │  ← Gradio Web UI 前端，交互与逻辑分发
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│     media_processor.py      │  ← 媒体处理中枢
│  ┌─────────────────────┐    │
│  │   智能路由引擎       │    │  判断素材类型
│  └────────┬────────────┘    │
│           ├── 静态图/短视频 ──→ CogVideoX API (AI 生成)
│           └── 合规视频 ─────→ FFmpeg 本地处理
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│     live_photo_maker.py     │  ← 核心封装引擎
│  ┌──────────┐ ┌──────────┐  │
│  │ iOS 模式 │ │Android 模式│ │
│  │UUID注入  │ │二进制拼接│  │
│  └──────────┘ └──────────┘  │
└─────────────────────────────┘
             │
             ▼
     输出动态照片文件
  (.jpg Live Photo / Motion Photo)
```

---

## 📂 目录结构

```text
AIGC_LivePhoto_Maker/
├── app.py                 # Gradio Web 前端主入口，负责交互与逻辑分发
├── media_processor.py     # 媒体处理中枢：FFmpeg 抽帧/裁剪、智能路由、AI 大模型调用
├── live_photo_maker.py    # 核心封装引擎：UUID 生成、Metadata 注入、二进制拼接
├── exiftool.exe           # (需用户自行下载) 元数据处理底层依赖
├── requirements.txt       # Python 依赖包列表
└── README.md              # 项目说明文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- FFmpeg（已加入系统 PATH）
- ExifTool（已加入系统 PATH 或放置于项目根目录）

### 安装步骤

**1. 克隆项目**
```bash
git clone https://github.com/your-username/AIGC_LivePhoto_Maker.git
cd AIGC_LivePhoto_Maker
```

**2. 安装 Python 依赖**
```bash
pip install -r requirements.txt
```

**3. 安装外部依赖**

- **FFmpeg**：从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载并加入系统 PATH
- **ExifTool**：从 [exiftool.org](https://exiftool.org/) 下载，将 `exiftool.exe`（Windows）放置于项目根目录，或加入系统 PATH

**4. 配置 AI 大模型（可选）**

若需使用 AIGC 图生视频功能，在项目根目录创建 `.env` 文件：
```env
ZHIPU_API_KEY=your_zhipu_api_key_here
```
> 未配置时系统自动降级为 FFmpeg 本地动效，不影响基础功能使用。

**5. 启动应用**
```bash
python app.py
```

浏览器访问 `http://localhost:7860` 即可使用。

---

## 📱 使用说明

| 步骤 | 操作 |
|------|------|
| ① | 上传一张静态图片或一段短视频作为素材 |
| ② | 选择目标平台：**Apple Live Photo** 或 **Android Motion Photo** |
| ③ | 点击生成，等待处理完成（AI 生成约需 30-60 秒） |
| ④ | 下载输出文件，通过数据线或 AirDrop 导入系统相册 |
| ⑤ | 在相册中长按图片，即可看到动态效果 🎉 |

---

## 🔧 核心技术解析

### Apple Live Photo 实现原理
Apple Live Photo 的本质是一张 JPEG 与一段 MOV 视频的强绑定组合。绑定的关键在于两个文件的 EXIF 元数据中必须写入**完全相同的 UUID**（格式为标准 36 位带连字符的十六进制字符串）。

本项目通过 ExifTool 命令行接口，向图片注入 `MediaGroupUUID` 字段，实现对 iOS 原生识别逻辑的精准匹配。

```python
# 核心注入逻辑示意
uuid_str = str(uuid.uuid4()).upper()  # 生成标准 UUID
# 使用 ExifTool 将 UUID 写入 JPEG 元数据
subprocess.run([
    "exiftool",
    f"-MediaGroupUUID={uuid_str}",
    image_path
])
```

### Android Motion Photo 实现原理
Android Motion Photo 采用单文件方案：将 MP4 视频数据**追加至 JPEG 文件末尾**，并在 JPEG 的 XMP 元数据中写入视频数据的偏移量（Offset）。Google Photos 通过读取该偏移量，从文件尾部精准截取视频流并播放。

```python
# 核心拼接逻辑示意
with open(output_path, 'wb') as out:
    out.write(jpeg_data)        # 写入原始 JPEG
    out.write(mp4_data)         # 追加 MP4 数据流
# 同时注入 XMP 元数据标记视频偏移量
```

---

## 🌐 AIGC 模型接入

本项目接入 **智谱 CogVideoX** 图生视频模型，支持从单张静态图片生成流畅的动态视频片段。

- **模型**：CogVideoX（图生视频）
- **输出时长**：5秒
- **调用方式**：REST API，异步轮询任务状态
- **降级策略**：API Key 缺失或调用失败时，自动切换为 FFmpeg 本地缩放动效

---

## 📦 依赖列表

```
gradio
requests
Pillow
python-dotenv
zhipuai
```

---

## 🗺️ Roadmap

- [ ] 支持批量图片处理
- [ ] 接入更多 AI 视频生成模型（如 Kling、Wan）
- [ ] 增加视频时长与动效风格自定义选项
- [ ] 支持 Web 在线部署（Hugging Face Spaces）
- [ ] 开发命令行 CLI 模式

---

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- [ExifTool](https://exiftool.org/) — 强大的元数据处理工具
- [FFmpeg](https://ffmpeg.org/) — 开源媒体处理框架
- [Gradio](https://gradio.app/) — 快速构建 ML Demo 的利器
- [智谱 AI CogVideoX](https://open.bigmodel.cn/) — AIGC 视频生成能力支持

---

<div align="center">

**如果这个项目对你有帮助，欢迎点个 ⭐ Star！**

</div>
