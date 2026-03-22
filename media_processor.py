"""
媒体处理模块
负责视频抽帧、截取、大模型视频生成等功能
"""

import os
import subprocess
import shutil
import time
import base64
import requests
from pathlib import Path
from typing import Tuple

def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def get_ffmpeg_path() -> str:
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path is None:
        raise RuntimeError("未检测到 ffmpeg，请先安装。")
    return ffmpeg_path

def get_media_info(file_path: str) -> dict:
    info = {
        'path': file_path,
        'format': Path(file_path).suffix.lower(),
        'is_video': False,
        'is_image': False,
        'duration': 0.0,
    }
    
    image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.heic']
    video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv']
    
    if info['format'] in image_exts:
        info['is_image'] = True
    elif info['format'] in video_exts:
        info['is_video'] = True
        
    # 如果是视频，获取时长
    if info['is_video']:
        ffmpeg_path = get_ffmpeg_path()
        import re
        cmd = [ffmpeg_path, '-i', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stderr)
        if duration_match:
            h, m, s = int(duration_match.group(1)), int(duration_match.group(2)), float(duration_match.group(3))
            info['duration'] = h * 3600 + m * 60 + s
            
    return info

def extract_frame_from_video(video_path: str, output_image_path: str, timestamp: float = 0.0) -> str:
    ffmpeg_path = get_ffmpeg_path()
    cmd = [
        ffmpeg_path,
        '-ss', str(timestamp),
        '-i', video_path,
        '-vframes', '1',
        '-q:v', '2',
        '-y',
        output_image_path
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    return output_image_path

def trim_video_to_3s(input_video_path: str, output_video_path: str, start_time: float = 0.0) -> str:
    """截取视频，支持传入开始时间"""
    ffmpeg_path = get_ffmpeg_path()
    cmd = [
        ffmpeg_path,
        '-ss', str(start_time),  # 核心：从指定秒数开始截取
        '-i', input_video_path,
        '-t', '3',               # 往后截 3 秒
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        output_video_path
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    return output_video_path

def dummy_video_generator(image_path: str, output_video_path: str, duration: int = 3) -> str:
    """兜底功能：没填 API 时的本地假视频生成器"""
    print(f"[Dummy API] 未提供 API Key，启动本地基础动效生成...")
    ffmpeg_path = get_ffmpeg_path()
    cmd = [
        ffmpeg_path,
        '-loop', '1',
        '-i', image_path,
        '-t', str(duration),
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-r', '30',
        '-movflags', '+faststart',
        '-y',
        output_video_path
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    return output_video_path

def generate_ai_video(image_path: str, output_video_path: str, api_key: str) -> str:
    """
    核心大模型引擎：调用智谱 CogVideoX 将图片转换为 3 秒视频
    """
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        raise RuntimeError("请先在终端运行：pip install zhipuai")
        
    client = ZhipuAI(api_key=api_key)
    
    with open(image_path, "rb") as f:
        base64_img = base64.b64encode(f.read()).decode('utf-8')
        
    print("[AI] 正在呼叫智谱 CogVideoX 大模型...")
    try:
        response = client.videos.generations(
            model="cogvideox",
            image_url=f"data:image/jpeg;base64,{base64_img}",
            prompt="画面自然连贯地微微移动，保持主体清晰稳定，适合作为实况图的动态背景。"
        )
        task_id = response.id
        
        print(f"[AI] 任务已提交云端 (Task ID: {task_id})，请耐心等待渲染(约1-2分钟)...")
        while True:
            result = client.videos.retrieve_videos_result(id=task_id)
            if result.task_status == "SUCCESS":
                video_url = result.video_result[0].url
                print(f"[AI] 渲染成功！正在下载大模型视频...")
                video_data = requests.get(video_url).content
                with open(output_video_path, "wb") as f:
                    f.write(video_data)
                return output_video_path
            elif result.task_status not in ["PROCESSING", "PENDING"]:
                raise RuntimeError(f"AI 生成失败，状态码: {result.task_status}")
            
            time.sleep(5)
            
    except Exception as e:
        raise RuntimeError(f"大模型调用异常: {str(e)}")

def process_input_file(input_path: str, temp_dir: str, start_time: float = 0.0, api_key: str = "") -> Tuple[str, str]:
    """
    智能路由：根据视频长短决定物理裁剪还是呼叫 AI
    """
    media_info = get_media_info(input_path)
    cover_path = os.path.join(temp_dir, 'cover.jpg')
    video_path = os.path.join(temp_dir, 'video.mov')
    
    if media_info['is_video']:
        duration = media_info.get('duration', 0)
        print(f"[智能路由] 检测到视频输入，总时长: {duration:.2f} 秒")
        
        if duration >= 3.0:
            print(f"[智能路由] 视频长度达标 (≥3秒)，正在从第 {start_time} 秒开始截取...")
            extract_frame_from_video(input_path, cover_path, timestamp=start_time)
            trim_video_to_3s(input_path, video_path, start_time=start_time)
        else:
            print(f"[智能路由] 视频过短 ({duration:.2f}秒)，提取首帧移交大模型图生视频...")
            extract_frame_from_video(input_path, cover_path, timestamp=0.0)
            if api_key.strip():
                generate_ai_video(cover_path, video_path, api_key)
            else:
                dummy_video_generator(cover_path, video_path)
                
    elif media_info['is_image']:
        print("[智能路由] 检测到静态图片...")
        shutil.copy(input_path, cover_path)
        if api_key.strip():
            generate_ai_video(cover_path, video_path, api_key)
        else:
            dummy_video_generator(cover_path, video_path)
            
    else:
        raise ValueError("不支持的文件格式！")
    
    return cover_path, video_path