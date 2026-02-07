import os
import sys
import re
import shutil
import yt_dlp
from openai import OpenAI

import subprocess

class VideoLoader:
    def __init__(self, api_key=None, base_url=None):
        """
        初始化 VideoLoader
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _check_ffmpeg(self):
        """检查 ffmpeg 是否可用，尝试添加到 PATH"""
        if shutil.which("ffmpeg"):
            return True
            
        # 尝试查找常见路径
        common_paths = [
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
            "/usr/bin/ffmpeg"
        ]
        for p in common_paths:
            if os.path.exists(p):
                os.environ["PATH"] += os.pathsep + os.path.dirname(p)
                return True
        return False

    def extract_url(self, text):
        """
        从混合文本中提取 HTTP/HTTPS 链接
        """
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
        match = re.search(url_pattern, text)
        if match:
            return match.group(0)
        return text

    def download_audio(self, video_url, output_dir="temp_audio"):
        """
        使用 yt-dlp 下载视频并提取音频
        """
        # 提取真实 URL
        video_url = self.extract_url(video_url)
        print(f"   (Processing URL: {video_url}...)")

        # 检查 ffmpeg 是否安装
        if not self._check_ffmpeg():
            error_msg = "Error: FFmpeg not found. Please install FFmpeg to download and convert audio.\n(Mac: brew install ffmpeg / Win: download from ffmpeg.org)"
            print(error_msg)
            return None

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 设置 yt-dlp 选项
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            # 添加 User-Agent 模拟浏览器
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.douyin.com/',
            # 忽略 SSL 错误（部分代理或网络环境下需要）
            'nocheckcertificate': True,
        }

        print(f"   (Downloading audio from: {video_url}...)")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                # 获取生成的文件路径
                file_id = info['id']
                file_path = os.path.join(output_dir, f"{file_id}.mp3")
                return file_path
        except Exception as e:
            error_msg = f"Error downloading video: {str(e)}"
            print(error_msg)
            # 如果失败，尝试再次以更宽松的配置运行（例如不指定 format）
            return None

    def transcribe_audio(self, audio_path):
        """
        使用 OpenAI Whisper 模型进行语音转文字
        """
        if not audio_path or not os.path.exists(audio_path):
            return None

        print(f"   (Transcribing audio: {audio_path}...)")
        
        # 尝试使用本地 Whisper 库 (如果已安装)
        try:
            import whisper
            print(">>> 检测到本地 whisper 库，正在尝试本地转录 (这可能需要一些时间)...")
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            return result["text"]
        except ImportError:
            print(">>> 未检测到本地 whisper 库 (或加载失败)，回退到 API 转录...")
        except Exception as e:
            print(f">>> 本地转录失败 ({str(e)})，回退到 API 转录...")

        # 回退到 OpenAI API
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            error_msg = f"Error transcribing audio: {str(e)}"
            print(error_msg)
            
            # 智能回退机制：如果是 404/400 或认证错误，且环境变量有 OpenAI Key，尝试用官方 Key 重试
            if "404" in str(e) or "400" in str(e) or "authentication" in str(e).lower():
                env_openai_key = os.getenv("OPENAI_API_KEY")
                # 只有当当前的 key 不是环境变量里的 key 时才重试，避免死循环
                if env_openai_key and env_openai_key != self.api_key:
                    print(">>> 检测到 API 不支持 Whisper，尝试使用环境变量 OPENAI_API_KEY 重试...")
                    try:
                        # 临时创建一个指向 OpenAI 官方的客户端
                        fallback_client = OpenAI(api_key=env_openai_key, base_url="https://api.openai.com/v1")
                        with open(audio_path, "rb") as audio_file:
                            transcript = fallback_client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file
                            )
                        print(">>> 重试成功！")
                        return transcript.text
                    except Exception as retry_e:
                        error_msg += f"\n(自动重试失败: {str(retry_e)})"

            return error_msg
        finally:
            # 清理临时文件
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass

    def extract_text_from_url(self, video_url):
        """
        主入口：URL -> Audio -> Text
        """
        audio_path = self.download_audio(video_url)
        if not audio_path:
            # 再次检查 ffmpeg 提示更友好的错误
            if not self._check_ffmpeg():
                return "Error: FFmpeg 未安装或未在 PATH 中找到。\n尝试运行: brew install ffmpeg"
            return "Error: 下载失败。请检查链接是否有效，或网络是否通畅。\n(建议：复制视频链接而不是分享口令)"
        
        text = self.transcribe_audio(audio_path)
        if not text or text.startswith("Error"):
            return text if text else "Error: Failed to transcribe audio (Unknown error)."
            
        return text

    def extract_audio_from_file(self, local_video_path, output_dir="temp_audio"):
        """
        从本地视频文件提取音频 (使用 ffmpeg)
        """
        if not self._check_ffmpeg():
            print("Error: FFmpeg not found.")
            return None
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 生成输出文件名
        file_name = os.path.splitext(os.path.basename(local_video_path))[0]
        output_path = os.path.join(output_dir, f"{file_name}.mp3")
        
        # 构造 ffmpeg 命令
        # -i input -vn (video none) -acodec libmp3lame -ar 16000 -ac 1 -b:a 64k -y (overwrite)
        # 优化：降采样到 16kHz 单声道，64k 比特率，显著减小文件体积以适应 Whisper 25MB 限制
        cmd = [
            "ffmpeg",
            "-i", local_video_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-ar", "16000",
            "-ac", "1",
            "-b:a", "64k",
            "-y",
            output_path
        ]
        
        print(f"   (Extracting audio from file: {local_video_path}...)")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {e}")
            return None

    def extract_text_from_file(self, local_video_path):
        """
        本地文件主入口：File -> Audio -> Text
        """
        audio_path = self.extract_audio_from_file(local_video_path)
        if not audio_path:
            return "Error: Failed to extract audio from file."
            
        # 检查文件大小
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        if file_size_mb > 24:
            return f"Error: 提取的音频文件过大 ({file_size_mb:.1f}MB)，超过 OpenAI 25MB 限制。\n建议：上传较短的视频片段。"

        text = self.transcribe_audio(audio_path)
        if not text or text.startswith("Error"):
            return text if text else "Error: Failed to transcribe audio (Unknown error)."
            
        return text
