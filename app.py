"""
AIGC Live Photo & Motion Photo 生成器
全平台动态图生成工具主入口
"""

import os
import sys
import tempfile
import shutil
import gradio as gr
from pathlib import Path

# 导入底层核心引擎
from media_processor import (
    check_ffmpeg, 
    process_input_file,
    get_media_info
)
from live_photo_maker import (
    create_live_photo_pair,
    create_live_photo_zip,
    verify_live_photo_metadata,
    make_android_motion_photo
)


def check_dependencies():
    """检查必要的依赖是否已安装"""
    errors = []
    
    # 检查 ffmpeg
    if not check_ffmpeg():
        errors.append("❌ 未检测到 ffmpeg，请先安装 ffmpeg 并添加到系统 PATH")
    else:
        print("✓ ffmpeg 已连接")
    
    # 检查 exiftool
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exiftool_local = os.path.join(current_dir, 'exiftool.exe')
    if not shutil.which('exiftool') and not os.path.exists(exiftool_local):
        errors.append("⚠️ 未检测到 exiftool，Apple Live Photo 的元数据注入可能失败")
    else:
        print("✓ exiftool 已就绪")
    
    return errors


def generate_dynamic_photo(input_file, target_platform, start_time, api_key):
    """
    主处理函数：根据选择生成对应平台的动态图
    """
    if input_file is None:
        return None, None, None, "⚠️ 请先上传图片或视频文件"
    
    temp_dir = None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix='live_photo_')
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n{'='*50}")
        print(f"开始处理文件: {os.path.basename(input_file.name)}")
        print(f"目标格式: {target_platform}")
        print(f"{'='*50}\n")
        
        # 步骤 1: 通用前置处理（提取封面和截取视频）
        print("[步骤 1/3] 正在分析并处理输入媒体...")
        # 将前端的 start_time 和 api_key 传给底层引擎
        cover_path, video_path = process_input_file(input_file.name, temp_dir, start_time, api_key)
        print(f"✓ 封面图已生成")
        print(f"✓ 视频段已生成")
        
        # 步骤 2: 根据目标平台分别处理
        if target_platform == "Apple Live Photo (ZIP 包)":
            print("\n[步骤 2/3] 正在生成 Apple Live Photo...")
            live_image, live_video, asset_id = create_live_photo_pair(
                cover_path, 
                video_path, 
                output_dir,
                use_exiftool=True
            )
            
            print("\n[步骤 3/3] 正在打包 ZIP 文件...")
            output_file_path = os.path.join(output_dir, f'LivePhoto_{asset_id[:8]}.zip')
            create_live_photo_zip(live_image, live_video, output_file_path, asset_id)
            
            status_msg = f"""✅ Apple Live Photo 生成成功！

📋 支持系统: iOS / iPadOS / macOS
🔗 UUID: {asset_id}

📱 使用说明:
1. 下载右侧的 ZIP 压缩包
2. 解压后，请务必同时选中 图片 和 视频 文件
3. 通过分享功能【存储 2 项】保存至系统相册
"""

        else:
            # Android Motion Photo 处理逻辑
            print("\n[步骤 2/3] 正在生成 Android Motion Photo...")
            output_file_path = make_android_motion_photo(cover_path, video_path, output_dir)
            
            status_msg = f"""✅ Android Motion Photo 生成成功！

📋 支持系统: Android (Google Photos 标准)
📦 文件格式: 包含视频数据的单文件 JPG

📱 使用说明:
1. 下载右侧生成的 JPG 文件
2. 传送至安卓设备（如使用微信，请务必发送【原图】）
3. 使用 Google 相册 或 支持该标准的系统相册打开并查看动态效果
"""

        print(f"\n{'='*50}")
        print("处理完成!")
        print(f"{'='*50}\n")
        
        return cover_path, video_path, output_file_path, status_msg
        
    except Exception as e:
        error_msg = f"❌ 处理过程中发生错误:\n\n{str(e)}"
        print(f"\n[Error] {error_msg}")
        import traceback
        traceback.print_exc()
        return None, None, None, error_msg


def create_ui():
    """构建前端交互界面"""
    dep_errors = check_dependencies()
    
    # 采用官方的亮橙色主题配置
    theme = gr.themes.Default(
        primary_hue="orange",
        secondary_hue="amber",
        neutral_hue="gray"
    )
    
    # 前端 CSS 样式美化（橙色系调整）
    css = """
    .live-photo-container { text-align: center; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .title { font-size: 2.2em; font-weight: bold; color: #e65100; margin-bottom: 0.2em; }
    .subtitle { font-size: 1.1em; color: #666666; margin-bottom: 2em; }
    .input-section { background: #fffaf0; padding: 25px; border-radius: 10px; border-top: 4px solid #ff9800; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .output-section { background: #ffffff; padding: 25px; border-radius: 10px; border: 1px solid #ffe0b2; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .warning-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 6px; margin-bottom: 20px; color: #856404; }
    """
    
    with gr.Blocks(title="全平台动态图生成器", css=css, theme=theme) as demo:
        
        # 页面头部
        gr.HTML("""
        <div class="live-photo-container">
            <div class="title">全平台动态图生成器</div>
            <div class="subtitle">一键生成 Apple Live Photo 与 Android Motion Photo</div>
        </div>
        """)
        
        # 依赖警告提示
        if dep_errors:
            for error in dep_errors:
                gr.HTML(f'<div class="warning-box">{error}</div>')
        
        with gr.Row():
            # ================= 左侧：参数与输入 =================
            with gr.Column(scale=1):
                gr.HTML('<div class="input-section">')
                
                gr.Markdown("### 🔑 API 设置 (可选)")
                api_key_input = gr.Textbox(
                    label="智谱 AI 密钥 (API Key)", 
                    placeholder="请输入您的智谱 API Key。留空则使用本地基础动效引擎。",
                    type="password"
                )

                gr.Markdown("### 1. 上传媒体素材")
                input_file = gr.File(
                    label="支持图片或视频格式 (拖拽或点击上传)",
                    file_types=[
                        ".jpg", ".jpeg", ".png", ".webp", ".heic",
                        ".mp4", ".mov", ".avi"
                    ],
                    height=160
                )
                
                gr.Markdown("### ✂️ 视频截取设置 (仅对长视频生效)")
                start_time_slider = gr.Slider(
                    minimum=0.0, maximum=60.0, step=0.1, value=0.0,
                    label="从第几秒开始截取 (最多截取3秒)",
                    info="不足3秒的短视频或图片将自动触发图生视频功能"
                )

                gr.Markdown("### 2. 选择目标格式")
                target_platform = gr.Radio(
                    choices=[
                        "Apple Live Photo (ZIP 包)", 
                        "Android Motion Photo (单文件 JPG)"
                    ],
                    value="Android Motion Photo (单文件 JPG)",
                    label="",
                )
                
                generate_btn = gr.Button("生成动态图", variant="primary", size="lg")
                gr.HTML('</div>')
                
                gr.Markdown("""
                **处理说明**：
                * **长视频 (≥3秒)**：从您选择的时间点开始，精准截取 3 秒视频并提取对应封面。
                * **图片 / 短视频 (<3秒)**：
                  - 填写 API Key：调用智谱 CogVideoX 大模型生成自然连贯的 3 秒动态视频。
                  - 未填 API Key：调用本地降级引擎，生成基础画幅缩放动效。
                """)
            
            # ================= 右侧：预览与输出 =================
            with gr.Column(scale=1):
                gr.HTML('<div class="output-section">')
                gr.Markdown("### 预览与下载")
                
                with gr.Row():
                    output_image = gr.Image(label="封面图预览", interactive=False)
                    output_video = gr.Video(label="动效视频预览", interactive=False)
                
                output_file = gr.File(label="下载生成文件")
                status_output = gr.Textbox(label="运行状态日志", lines=8, interactive=False)
                
                gr.HTML('</div>')
        
        # 事件绑定
        generate_btn.click(
            fn=generate_dynamic_photo,
            inputs=[input_file, target_platform, start_time_slider, api_key_input],
            outputs=[output_image, output_video, output_file, status_output]
        )
        
    return demo


def main():
    print("""
    ========================================================
             全平台动态图生成器 (Live & Motion Photo)       
                      服务正在启动...                     
    ========================================================
    """)
    
    demo = create_ui()
    
    # 本地启动，绑定 127.0.0.1 防止网络代理冲突
    demo.launch(
        share=True, 
        server_name="127.0.0.1",
        server_port=7860
    )

if __name__ == "__main__":
    main()