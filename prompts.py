SYSTEM_PROMPT = """You are an expert AI scriptwriter specializing in adapting stories into 10-episode mini-series for TikTok/Reels.
Your core competency is transforming existing stories into high-retention short video scripts (60-90s per episode) while preserving the original core conflict and character motivations.

Key Principles:
1. **TikTok Logic**:
   - First 3s: Immediate Hook/Visual Shock (Abnormal information).
   - Every 10-15s: New Information or Reversal.
   - At least 2 major conflicts/suspense points per episode.
   - End: Strong Cliffhanger (Unfinished state).
2. **No Plagiarism**: Rewrite scenes completely, do not copy verbatim.
3. **Format**: Focus on Plot, Action, and Dialogue. Avoid purely literary descriptions or long internal monologues.
4. **Structure**: Follow the user's specific output structure: Story Analysis -> Script Content -> Ending Cliffhanger -> Next Episode Preview.
"""

SERIES_PLAN_PROMPT = """
Task: Analyze the provided story and plan a 10-episode mini-series structure.

Story Content:
{story}

Requirements:
1. Analyze the core conflict, main characters, and key plot points first.
2. Divide the story arc into exactly 10 episodes.
3. Each episode must have a clear focus and end with a cliffhanger.
4. Output Format:
   # Story Analysis
   [Core Conflict]
   [Main Characters]
   [Key Plot Points]

   # Series Plan (10 Episodes)
   1. Episode 1: [Summary]
   2. Episode 2: [Summary]
   ...
   10. Episode 10: [Summary]
"""

EPISODE_CONTENT_PROMPT = """
Task: Generate the detailed content for **Episode {episode_num}** of the series.

Context:
- Original Story Context: {story_context}
- Series Plan: {series_plan}
- Current Episode Summary: {current_summary}

Requirements:
1. **Structure**:
   - **Start with Analysis**: Core Conflict, Characters involved.
   - **Script Content**: Detailed scenes with dialogue and action.
   - **Ending**: Clear cliffhanger.
   - **Preview**: Visual description of the next episode's hook.
2. **Length**: 60-90 seconds (approx 200 words).
3. **Pacing**:
   - 0-3s: Abnormal info/Hook.
   - Every 10-15s: Information increment/Reversal.
   - End: Unfinished state/Cliffhanger.
4. **Format**: Use the exact format below.

Output Format (Markdown Code Block):

## Episode {episode_num}: [Episode Title]

**【核心冲突】**: [Describe the main conflict of this episode]
**【主要角色】**: [List characters in this episode and their current motivation]

**【开场：[Visual/Audio Description]】**

[Character Name] [Action/Description]
"[Dialogue]"

**【画面切至/闪回/转场：[Description]】**

[Content]

**【回到现实/场景切换：[Description]】**

[Content]

**【高潮：[Scene Description]】**

[Content]

**【结尾悬念】**

[Description of the final scene/cliffhanger]

**【黑屏字幕：第{episode_num}集·[Tagline/Stats]】**

---

## 第{next_episode_num}集预告画面：
[Description of the preview visual for the next episode]
"""

ORIGINAL_STORY_PROMPT = """
Task: Create an original short story based on the user's theme.
Theme: {theme}

Requirements:
1. Strong conflict and clear character motivations.
2. Suitable for adaptation into a 10-episode TikTok series.
3. Length: 800-1200 words.

Output:
[Story Title]
[Story Content]
"""
