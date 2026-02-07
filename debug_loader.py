from video_loader import VideoLoader
import sys

print("=== 开始 VideoLoader 诊断 ===")
# 传入假 key 绕过 OpenAI 初始化检查
loader = VideoLoader(api_key="sk-test-key")

# 测试 URL 提取
test_text = "7.89 复制打开抖音，看看【某某的作品】... https://v.douyin.com/k9k9k9/ ..."
extracted = loader.extract_url(test_text)
print(f"原始文本: {test_text}")
print(f"提取结果: {extracted}")

if extracted == "https://v.douyin.com/k9k9k9/":
    print("✅ URL 提取逻辑正常")
else:
    print("❌ URL 提取逻辑异常")

# 测试音频下载（使用一个简单的测试链接，如果不想真实下载可以跳过）
# 这里我们主要测试 ffmpeg 检测逻辑
import shutil
if shutil.which("ffmpeg"):
    print(f"✅ FFmpeg 已检测到: {shutil.which('ffmpeg')}")
else:
    print("❌ FFmpeg 未被 shutil.which 检测到，尝试运行 download_audio 触发手动检测...")
    # 模拟调用
    try:
        # 传入无效 URL 仅为了触发前面的检查逻辑
        loader.download_audio("http://invalid-url.com", output_dir="test_debug")
    except Exception as e:
        print(f"运行中捕获异常: {e}")

print("=== 诊断结束 ===")
