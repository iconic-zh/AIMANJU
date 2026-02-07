import os
import sys
import time
from prompts import SYSTEM_PROMPT, SERIES_PLAN_PROMPT, EPISODE_CONTENT_PROMPT, ORIGINAL_STORY_PROMPT

# 尝试导入 dotenv 以加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)

# 尝试导入 VideoLoader
try:
    from video_loader import VideoLoader
except ImportError:
    VideoLoader = None

class StoryWasher:
    def __init__(self, api_key=None, base_url=None, model="gpt-4o"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    def call_llm(self, prompt, temperature=0.7):
        """调用 LLM 生成内容"""
        try:
            print(f"   (Calling LLM with model: {self.model}...)")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {e}"

    def generate_story_from_theme(self, theme):
        """从零生成故事"""
        print(f"\n>>> [0/3] 正在根据主题创作原创故事...")
        prompt = ORIGINAL_STORY_PROMPT.format(theme=theme)
        story = self.call_llm(prompt, temperature=0.8) # 稍微提高创造性
        print(">>> 原创故事生成完成：")
        print(story[:200] + "..." if len(story) > 200 else story)
        print("-" * 50)
        return story

    def plan_series(self, story_content):
        """步骤 1: 生成10集连载规划"""
        print("\n>>> [1/2] 正在规划 10 集连载结构...")
        prompt = SERIES_PLAN_PROMPT.format(story=story_content)
        series_plan = self.call_llm(prompt)
        print(">>> 连载规划完成")
        return series_plan

    def generate_episode(self, episode_num, story_context, series_plan, current_summary):
        """步骤 2: 生成单集详细内容 (合并分析与剧本)"""
        print(f"\n>>> [2/2] 正在生成第 {episode_num} 集内容 (CN/EN)...")
        prompt = EPISODE_CONTENT_PROMPT.format(
            episode_num=episode_num,
            story_context=story_context,
            series_plan=series_plan,
            current_summary=current_summary
        )
        content = self.call_llm(prompt)
        print(f">>> 第 {episode_num} 集生成完成")
        return content

    def process_story(self, story_content):
        """CLI 模式下的处理流程"""
        results = {}
        
        # 步骤 1: 规划
        series_plan = self.plan_series(story_content)
        results['series_plan'] = series_plan
        print(series_plan)
        print("-" * 50)

        # 步骤 2: 逐集生成 (仅生成第1集作为示例，CLI模式下)
        # 在 Web 模式下，我们会循环生成所有
        ep1_content = self.generate_episode(1, story_content, series_plan, "Episode 1 Summary (See Plan)")
        results['episode_1'] = ep1_content
        print(ep1_content[:200] + "...")
        print("-" * 50)
        
        return results

    def save_results(self, results, output_dir="output", original_story=None):
        """保存结果到文件"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 如果有原创故事，也保存下来
        if original_story:
            with open(os.path.join(output_dir, "0_original_story.txt"), "w", encoding="utf-8") as f:
                f.write(original_story)

        with open(os.path.join(output_dir, "1_series_plan.txt"), "w", encoding="utf-8") as f:
            f.write(results.get("series_plan", ""))
            
        # 保存各集内容
        for key, value in results.items():
            if key.startswith("episode_"):
                with open(os.path.join(output_dir, f"{key}.md"), "w", encoding="utf-8") as f:
                    f.write(value)
            
        print(f"\nAll results saved to {output_dir}/ directory.")

def print_menu():
    print("\n请选择输入模式：")
    print("1. 本地文件 (txt)")
    print("2. 抖音视频链接 (自动提取文案)")
    print("3. 原创生成 (输入主题/关键词)")
    print("q. 退出")

if __name__ == "__main__":
    # 配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL") 
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    print("=== AI 漫剧洗剧本智能体 v2.0 ===")
    
    if not api_key:
        print("\n[Warning] OPENAI_API_KEY environment variable not found.")
        input_key = input("Please enter your API Key: ").strip()
        if input_key:
            api_key = input_key
        else:
            sys.exit(1)

    washer = StoryWasher(api_key=api_key, base_url=base_url, model=model)
    
    while True:
        print_menu()
        choice = input("\n请输入选项 (1/2/3/q): ").strip().lower()
        
        if choice == 'q':
            break
            
        story_content = ""
        original_story_content = None # 用于保存生成的原创故事
        
        if choice == '1':
            file_path = input("请输入文件路径 (默认 sample_story.txt): ").strip()
            if not file_path:
                file_path = "sample_story.txt"
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    story_content = f.read()
            else:
                print("错误：文件不存在")
                continue
                
        elif choice == '2':
            if VideoLoader is None:
                print("错误：无法加载 VideoLoader 模块。请确保已安装 yt-dlp。")
                continue
                
            url = input("请输入抖音/TikTok视频链接: ").strip()
            if not url:
                continue
            
            print(">>> 正在处理视频链接 (下载音频 -> 语音转文字)...")
            loader = VideoLoader(api_key=api_key, base_url=base_url)
            story_content = loader.extract_text_from_url(url)
            
            if story_content.startswith("Error"):
                print(story_content)
                continue
            else:
                print(f"\n提取到的文案:\n{story_content[:200]}...\n")
                
        elif choice == '3':
            theme = input("请输入故事主题或关键词 (如: 赛博朋克、复仇、悬疑): ").strip()
            if not theme:
                continue
            story_content = washer.generate_story_from_theme(theme)
            original_story_content = story_content
            
        else:
            print("无效选项")
            continue
            
        if story_content:
            results = washer.process_story(story_content)
            washer.save_results(results, original_story=original_story_content)
            print("\n处理完成！")
