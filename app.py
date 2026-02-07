import streamlit as st
import os
import time
from script_washer import StoryWasher
from history_manager import HistoryManager

# 初始化历史记录管理器
history_mgr = HistoryManager()

try:
    from video_loader import VideoLoader
except ImportError:
    VideoLoader = None

# 设置页面配置
st.set_page_config(
    page_title="AI 漫剧剧本生成智能体",
    page_icon="🎬",
    layout="wide"
)

# 初始化 session state
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None
if 'story_content' not in st.session_state:
    st.session_state.story_content = ""
if 'series_plan' not in st.session_state:
    st.session_state.series_plan = ""
if 'episode_contents' not in st.session_state:
    st.session_state.episode_contents = {} # 存储 {1: content, 2: content...}
if 'next_episode_to_generate' not in st.session_state:
    st.session_state.next_episode_to_generate = 1

def auto_save():
    """自动保存当前状态"""
    if st.session_state.story_content: # 只有当有内容时才保存
        new_id = history_mgr.save_project(st.session_state, st.session_state.current_project_id)
        st.session_state.current_project_id = new_id

def load_project(project_id):
    """加载项目到 session state"""
    data = history_mgr.load_project(project_id)
    if data:
        st.session_state.current_project_id = data['id']
        st.session_state.story_content = data.get('story_content', "")
        st.session_state.series_plan = data.get('series_plan', "")
        st.session_state.episode_contents = data.get('episode_contents', {})
        st.session_state.next_episode_to_generate = data.get('next_episode_to_generate', 1)
        st.rerun()

def new_project():
    """重置状态以开始新项目"""
    st.session_state.current_project_id = None
    st.session_state.story_content = ""
    st.session_state.series_plan = ""
    st.session_state.episode_contents = {}
    st.session_state.next_episode_to_generate = 1
    st.rerun()

# Sidebar 配置
with st.sidebar:
    st.title("🗂️ 项目管理")
    
    # 新建项目按钮
    if st.button("➕ 新建项目", use_container_width=True):
        new_project()
    
    st.divider()
    
    # 历史记录列表
    st.subheader("📜 历史记录")
    history_list = history_mgr.get_history_list()
    
    if not history_list:
        st.info("暂无历史记录")
    else:
        for proj in history_list:
            # 格式化时间显示
            from datetime import datetime
            dt = datetime.fromisoformat(proj['updated_at'])
            date_str = dt.strftime("%m-%d %H:%M")
            
            # 使用按钮作为列表项，点击加载
            # 高亮当前项目
            is_active = (st.session_state.current_project_id == proj['id'])
            label = f"{'📂 ' if is_active else ''}{proj['title']}\nScan: {date_str}"
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(label, key=f"load_{proj['id']}", help="点击加载此项目", use_container_width=True):
                    load_project(proj['id'])
            with col2:
                if st.button("🗑️", key=f"del_{proj['id']}", help="删除"):
                    history_mgr.delete_project(proj['id'])
                    if st.session_state.current_project_id == proj['id']:
                        new_project()
                    else:
                        st.rerun()

    st.divider()
    st.title("⚙️ 配置")

    
    # API 厂商预设
    provider = st.selectbox("API 厂商", ["OpenAI", "DeepSeek", "Moonshot (Kimi)", "自定义"], index=0)
    
    default_base_url = ""
    if provider == "DeepSeek":
        default_base_url = "https://api.deepseek.com"
    elif provider == "Moonshot (Kimi)":
        default_base_url = "https://api.moonshot.cn/v1"
        
    api_key = st.text_input("API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    base_url = st.text_input("Base URL", value=default_base_url or os.getenv("OPENAI_BASE_URL", ""))
    
    # 模型选择
    model_options = [
        "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", 
        "deepseek-chat", "deepseek-coder",
        "moonshot-v1-8k", "moonshot-v1-32k",
        "yi-34b-chat-0205",
        "qwen-turbo"
    ]
    
    selected_model = st.selectbox("Model", model_options + ["自定义输入..."], index=0)
    
    if selected_model == "自定义输入...":
        model = st.text_input("请输入模型名称", value="gpt-4o")
    else:
        model = selected_model
    
    st.divider()
    st.markdown("### 关于")
    st.markdown("本工具可以将普通故事、抖音视频文案改编为适合漫剧制作的结构化剧本。")

# 主界面
st.title("🎬 AI 漫剧剧本生成智能体")

if not api_key:
    st.warning("请先在左侧侧边栏设置 OpenAI API Key。")
    st.stop()

# 初始化 Washer
washer = StoryWasher(api_key=api_key, base_url=base_url if base_url else None, model=model)

# 模式选择
mode = st.radio("选择输入模式", ["💡 原创生成", "📄 本地文件/文本"], horizontal=True)

input_content = ""

if mode == "💡 原创生成":
    theme = st.text_input("输入故事主题或关键词 (如: 赛博朋克、复仇、悬疑)")
    if st.button("生成原创故事"):
            with st.spinner("正在创作故事..."):
                story = washer.generate_story_from_theme(theme)
                st.session_state.story_content = story
                auto_save() # 自动保存
                st.success("原创故事生成成功！")
                st.rerun()
            
    if st.session_state.story_content:
        st.text_area("生成的原创故事", value=st.session_state.story_content, height=200)
        input_content = st.session_state.story_content

elif mode == "📄 本地文件/文本":
    uploaded_file = st.file_uploader("上传文件 (支持 .txt 文本或视频文件)", type=["txt", "mp4", "mov", "avi", "mkv"])
    text_input = st.text_area("或者直接粘贴故事内容", height=200)
    
    if uploaded_file:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext == "txt":
            input_content = uploaded_file.read().decode("utf-8")
        elif file_ext in ["mp4", "mov", "avi", "mkv"]:
            # 处理视频上传
            if VideoLoader is None:
                st.error("无法加载 VideoLoader 模块。请确保已安装 ffmpeg。")
            else:
                with st.spinner("正在处理视频音频..."):
                    # 保存临时文件
                    temp_dir = "temp_uploads"
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 提取文本
                    loader = VideoLoader(api_key=api_key, base_url=base_url if base_url else None)
                    extracted_text = loader.extract_text_from_file(temp_path)
                    
                    # 清理临时文件
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                        
                    if extracted_text.startswith("Error"):
                        st.error(extracted_text)
                    else:
                        st.success("视频文案提取成功！")
                        input_content = extracted_text
                        # 显示提取的文本
                        st.text_area("提取的文案", value=input_content, height=200, disabled=True)

    elif text_input:
        input_content = text_input

# 处理按钮
if input_content and st.button("🚀 开始生成剧本 (连载总纲 + 第1集)", type="primary"):
    st.session_state.story_content = input_content # 确保同步
    auto_save() # 自动保存
    st.session_state.episode_contents = {} # 重置
    st.session_state.next_episode_to_generate = 2 # 重置为第2集 (因为第1集马上生成)
    
    with st.status("正在创作连载剧本...", expanded=True) as status:
        # 步骤 1: 规划
        st.write("📅 正在规划 10 集连载结构...")
        series_plan = washer.plan_series(input_content)
        st.session_state.series_plan = series_plan
        st.write("✅ 连载规划完成")
        
        # 步骤 2: 生成第 1 集
        st.write("✍️ 正在撰写第 1 集 (中英双语)...")
        ep1_content = washer.generate_episode(1, input_content, series_plan, "Episode 1")
        st.session_state.episode_contents[1] = ep1_content
        
        auto_save() # 自动保存
        status.update(label="🎉 基础内容创作完成！", state="complete", expanded=False)

# 结果展示
if st.session_state.series_plan:
    st.divider()
    st.header("📺 生成结果")
    
    # 动态创建 Tab
    # 始终显示总纲 + 已生成的剧集
    generated_episodes = sorted(st.session_state.episode_contents.keys())
    tab_labels = ["📑 总集大纲"] + [f"第 {i} 集" for i in generated_episodes]
    
    tabs = st.tabs(tab_labels)
    
    # 解析总纲中的分集 Summary
    # 假设 series_plan 格式为 "1. Episode 1: Summary..."
    episode_summaries = {}
    try:
        lines = st.session_state.series_plan.split('\n')
        for line in lines:
            line = line.strip()
            # 简单的解析逻辑，匹配 "1. Episode 1:" 或 "Episode 1:"
            if "Episode" in line and ":" in line:
                parts = line.split(":", 1)
                key_part = parts[0]
                summary_part = parts[1].strip()
                # 尝试提取数字
                import re
                match = re.search(r'Episode\s+(\d+)', key_part, re.IGNORECASE)
                if match:
                    ep_num = int(match.group(1))
                    episode_summaries[ep_num] = summary_part
    except Exception as e:
        print(f"Error parsing summaries: {e}")

    # Tab 1: 总纲
    with tabs[0]:
        st.markdown(st.session_state.series_plan)
        st.download_button("下载总纲", st.session_state.series_plan, file_name="0_series_plan.txt")
        
    # Tabs: 分集内容
    for idx, ep_num in enumerate(generated_episodes):
        # tabs[0] is plan, so tabs[idx+1] is the episode
        with tabs[idx + 1]:
            # 展示分集 Summary (如果解析成功)
            if ep_num in episode_summaries:
                st.info(f"**Episode {ep_num} Summary**: {episode_summaries[ep_num]}")
            
            content = st.session_state.episode_contents[ep_num]
            st.markdown(content)
            
            # 底部按钮区域：下载 + 生成下一集
            col1, col2 = st.columns([1, 4])
            with col1:
                st.download_button(f"下载第 {ep_num} 集", content, file_name=f"episode_{ep_num}.md")
            
            # 只有在最新的一集，且不是第10集时，才显示“生成下一集”按钮
            is_latest_generated = (ep_num == max(generated_episodes))
            next_ep_num = ep_num + 1
            
            if is_latest_generated and next_ep_num <= 10:
                with col2:
                    if st.button(f"🎬 生成第 {next_ep_num} 集", key=f"gen_btn_{next_ep_num}", type="primary"):
                        with st.spinner(f"正在撰写第 {next_ep_num} 集..."):
                            ep_content = washer.generate_episode(
                                next_ep_num, 
                                st.session_state.story_content, 
                                st.session_state.series_plan, 
                                f"Episode {next_ep_num}"
                            )
                            st.session_state.episode_contents[next_ep_num] = ep_content
                            st.session_state.next_episode_to_generate = next_ep_num + 1
                            auto_save() # 自动保存
                            st.rerun()
            elif next_ep_num > 10:
                with col2:
                     st.success("🎉 全剧终！")
