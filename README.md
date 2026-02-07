# AI 漫剧剧本生成智能体 (AI Manga Script Generator)

这是一个基于 AI 的漫剧剧本生成工具，旨在帮助创作者将普通故事或视频文案改编为适合短视频平台（如 TikTok、抖音）的结构化漫剧剧本。

## ✨ 主要功能

*   **多模式输入**：支持原创故事生成、本地文本上传、以及视频文件字幕提取。
*   **智能洗稿**：保持核心冲突和角色动机，避免抄袭风险。
*   **结构化输出**：自动生成 10 集连载规划，并提供中英双语对照的剧本内容。
*   **西方审美适配**：专为 TikTok 全球发布优化，对白和设定符合西方审美。
*   **本地化处理**：支持使用本地 Whisper 模型进行视频字幕提取，无需消耗 API token。
*   **交互式生成**：分集生成，支持实时预览和下载。

## 🛠️ 安装与运行

### 前置要求

*   Python 3.8+
*   OpenAI API Key (或其他兼容 OpenAI 格式的 API Key，如 DeepSeek, Moonshot)
*   FFmpeg (用于视频处理)

### 安装步骤

1.  克隆仓库：
    ```bash
    git clone <your-repo-url>
    cd AIMANJU
    ```

2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

3.  配置环境变量：
    复制 `.env.example` 为 `.env`，并填入你的 API Key：
    ```bash
    cp .env.example .env
    ```
    或者在启动应用后在侧边栏输入。

### 启动应用

运行启动脚本：
```bash
bash start_app.sh
```
或者直接运行：
```bash
streamlit run app.py
```

## 📝 许可证

MIT License
