import streamlit as st
import os
import time
import json
import re
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
        
    # 持久化存储 API Key
    if 'saved_api_key' not in st.session_state:
        st.session_state.saved_api_key = os.getenv("OPENAI_API_KEY", "")

    def update_api_key():
        st.session_state.saved_api_key = st.session_state.api_key_input

    api_key = st.text_input("API Key", type="password", 
                           value=st.session_state.saved_api_key, 
                           key="api_key_input",
                           on_change=update_api_key)

    # Base URL 处理 (仅在自定义时显示，其他情况自动设置)
    if provider == "自定义":
        base_url = st.text_input("Base URL", value=os.getenv("OPENAI_BASE_URL", ""))
    else:
        # 如果有环境变量且没有特定默认值，也可以尝试使用环境变量，但通常厂商有固定 URL
        base_url = default_base_url if default_base_url else os.getenv("OPENAI_BASE_URL", "")
    
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
        if isinstance(st.session_state.story_content, dict):
             st.json(st.session_state.story_content)
             input_content = st.session_state.story_content
        else:
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
if input_content and st.button("🚀 开始生成剧本 (连载总纲)", type="primary"):
    st.session_state.story_content = input_content # 确保同步
    auto_save() # 自动保存
    st.session_state.episode_contents = {} # 重置
    st.session_state.next_episode_to_generate = 1 # 重置为第1集
    
    with st.status("正在创作连载剧本...", expanded=True) as status:
        # 步骤 1: 规划
        st.write("📅 正在规划 10 集连载结构...")
        # 如果是原创故事，story_content 已经是生成好的大纲，不需要再 plan_series
        # 但为了逻辑统一，我们假设 input_content 只是素材
        # 如果 input_content 已经是格式化的原创大纲（包含 # Series Outline 或 JSON key），直接使用
        is_ready_made = False
        if isinstance(input_content, dict) and "series_outline" in input_content:
             is_ready_made = True
        elif isinstance(input_content, str) and "# Series Outline" in input_content:
             is_ready_made = True
             
        if is_ready_made:
             series_plan = input_content
             st.write("✅ 使用已生成的原创大纲")
        else:
             series_plan = washer.plan_series(input_content)
             st.write("✅ 连载规划完成")
             
        st.session_state.series_plan = series_plan
        auto_save() # 自动保存
        status.update(label="🎉 总纲规划完成！请点击下方标签页开始生成分集。", state="complete", expanded=False)
        st.rerun()

# 结果展示
if st.session_state.series_plan:
    st.divider()
    st.header("📺 生成结果")
    
    # 解析总纲中的分集 Summary
    episode_summaries = {}
    series_plan_data = st.session_state.series_plan
    
    # 尝试解析 JSON 字符串
    if isinstance(series_plan_data, str) and series_plan_data.strip().startswith('{'):
        try:
            series_plan_data = json.loads(series_plan_data)
        except:
            pass
            
    if isinstance(series_plan_data, dict):
        # JSON 模式
        outline = series_plan_data.get("series_outline", [])
        for ep in outline:
            ep_num = ep.get("episode_number")
            if ep_num:
                episode_summaries[ep_num] = ep.get("summary", "")
    else:
        # 兼容旧版 Markdown 模式
        try:
            # 匹配 "## Episode X: Title" 及其后的内容，直到下一个 "## Episode"
            pattern = re.compile(r'## Episode (\d+):[^\n]*\n(.*?)(?=## Episode \d+|$)', re.DOTALL)
            matches = pattern.findall(series_plan_data)
            for ep_num_str, summary in matches:
                ep_num = int(ep_num_str)
                episode_summaries[ep_num] = summary.strip()
        except Exception as e:
            print(f"Error parsing summaries: {e}")

    # 动态创建 Tab (固定 10 集 + 总纲)
    tab_labels = ["📑 总集大纲"] + [f"第 {i} 集" for i in range(1, 11)]
    tabs = st.tabs(tab_labels)
    
    # Tab 1: 总纲
    with tabs[0]:
        if isinstance(series_plan_data, dict):
            st.json(series_plan_data)
            json_str = json.dumps(series_plan_data, ensure_ascii=False, indent=2)
            st.download_button("下载总纲 (JSON)", json_str, file_name="series_plan.json")
        else:
            st.markdown(series_plan_data)
            st.download_button("下载总纲", series_plan_data, file_name="0_series_plan.txt")
        
    # Tabs: 分集内容 (1-10)
    for i in range(1, 11):
        with tabs[i]:
            ep_num = i
            
            # 1. 显示摘要 (来自总纲)
            if ep_num in episode_summaries:
                with st.expander(f"📖 第 {ep_num} 集剧情概要", expanded=False):
                    st.markdown(episode_summaries[ep_num])
            else:
                st.warning("未能从总纲中解析出本集概要")

            # 2. 显示剧本内容 (如果已生成)
            if ep_num in st.session_state.episode_contents:
                content = st.session_state.episode_contents[ep_num]
                
                if isinstance(content, dict):
                    st.json(content)
                    
                    # 简易阅读视图
                    st.markdown("---")
                    st.subheader("剧本预览")
                    
                    scripts = content.get("scripts", {})
                    st.markdown("### 🇬🇧 English Script")
                    st.markdown(scripts.get("english", ""))
                    st.markdown("### 🇨🇳 Chinese Script")
                    st.markdown(scripts.get("chinese", ""))
                    
                    json_str = json.dumps(content, ensure_ascii=False, indent=2)
                    st.download_button(f"下载第 {ep_num} 集 (JSON)", json_str, file_name=f"episode_{ep_num}.json")
                else:
                    st.markdown(content)
                    st.download_button(f"下载第 {ep_num} 集", content, file_name=f"episode_{ep_num}.md")
            
            # 3. 生成按钮 (如果未生成)
            else:
                # 检查前一集是否完成 (强制按顺序生成，或者允许跳跃? 用户说"稳定"，按顺序较好，但跳跃也无妨)
                # 为了上下文连贯，最好按顺序。但这里允许用户点击任意集，
                # 只是生成时 Context 可能需要依赖前一集。
                # 简化逻辑：只依赖总纲和本集摘要。如果需要上下文，可以获取前一集的生成内容。
                
                if st.button(f"🎬 生成第 {ep_num} 集剧本", key=f"gen_btn_{ep_num}", type="primary"):
                    with st.spinner(f"正在撰写第 {ep_num} 集 (英 -> 中)..."):
                        # 获取摘要
                        current_summary = episode_summaries.get(ep_num, "Summary not found")
                        
                        # 调用生成
                        content = washer.generate_episode(
                            episode_num=ep_num,
                            story_context=st.session_state.series_plan, # 使用总纲作为上下文
                            series_plan=st.session_state.series_plan,
                            current_summary=current_summary
                        )
                        
                        # 保存
                        st.session_state.episode_contents[ep_num] = content
                        auto_save()
                        st.rerun()
