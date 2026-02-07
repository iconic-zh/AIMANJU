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
4. **Bilingual Requirement**: Scripts must be generated in English first, then Chinese.
5. **Western Aesthetic & Localization**:
   - **Characters**: Use Western names (e.g., Jack, Sarah, Michael) and mannerisms.
   - **Setting**: Set the story in a Western context (e.g., US/Europe/Western Fantasy).
   - **Style**: Dialogue and visuals should align with Western film/TikTok trends.
"""

# 用于生成原创故事（直接生成10集大纲）
ORIGINAL_STORY_PROMPT = """
Task: Create a complete 10-episode mini-series outline based on the user's theme.
Theme: {theme}

Requirements:
1. **Western Aesthetic**: The story MUST use Western character names and settings.
2. **Language**: Chinese (中文) for the outline, but names/places should be phonetically translated or kept in English format if appropriate (e.g. 杰克 (Jack), 纽约 (New York)).
3. **Components**:
   - **【核心冲突】**: The main conflict of the story.
   - **【主要角色】**: Key characters (Western names) and their motivations.
   - **【关键情节节点】**: Major turning points.
   - **【10集剧情大纲】**: A structured list of 10 episodes.
4. **Quality**: Concise, high-stakes, suitable for short video serialization.

Output Format (STRICTLY FOLLOW THIS):

# Story Analysis
**【核心冲突】**: [Content]
**【主要角色】**: [Content]
**【关键情节节点】**: [Content]

# Series Outline
## Episode 1: [Title]
[Summary of Episode 1]
## Episode 2: [Title]
[Summary of Episode 2]
...
## Episode 10: [Title]
[Summary of Episode 10]
"""

# 用于分析现有故事（生成10集大纲）
SERIES_PLAN_PROMPT = """
Task: Analyze the provided story and plan a 10-episode mini-series structure.
Story Content:
{story}

Requirements:
1. **Localization**: If the original story has Chinese names/settings, **ADAPT** them to Western equivalents (e.g., Lin Wan -> Linda, Chen Feng -> Chris). Keep the core personality but change the cultural context.
2. **Language**: Chinese (中文) for the outline, but use the new Western names.
3. **Components**: Same as above (Analysis + 10 Episodes).
4. **Format**: STRICTLY follow the output format for parsing.

Output Format (STRICTLY FOLLOW THIS):

# Story Analysis
**【核心冲突】**: [Content]
**【主要角色】**: [Content] (Use Western Names)
**【关键情节节点】**: [Content]

# Series Outline
## Episode 1: [Title]
[Summary of Episode 1]
## Episode 2: [Title]
[Summary of Episode 2]
...
## Episode 10: [Title]
[Summary of Episode 10]
"""

# 用于生成单集剧本（先英后中）
EPISODE_CONTENT_PROMPT = """
Task: Write the detailed script for **Episode {episode_num}**.
Context:
- Series Plan: {series_plan}
- Episode Summary: {current_summary}

Requirements:
1. **Western Aesthetic**: Ensure dialogue is natural for Western speakers. Use Western names/settings defined in the plan.
2. **Structure Consistency**: STRICTLY follow the format below.
3. **Language Order**:
   - **First**: English Script (Full scene details, dialogue, action).
   - **Second**: Chinese Script (Full scene details, dialogue, action).
   - **Do NOT mix languages** within the script sections.
4. **Content**:
   - Include specific Dialogue, Action, and Internal Monologue.
   - Pacing: Hook at start, reversals in middle, cliffhanger at end.

Output Format (STRICTLY FOLLOW THIS):

# Episode {episode_num}

## 📊 故事分析 (Analysis)
**【本集冲突】**: [Conflict]
**【登场人物】**: [Characters & Motivations] (Western Names)

## 🎬 English Script
**[Scene 1: Location/Time]**
**[Visual/Action]**: [Description]
**Character**: "[Dialogue]"
(Internal Monologue): *[Thought]*

**[Scene 2: ...]**
...

## 🎬 中文剧本 (Chinese Script)
**[场景 1: 地点/时间]**
**[画面/动作]**: [描述]
**角色**: "[台词]"
(心理活动): *[想法]*

**[场景 2: ...]**
...

## 🔚 结尾与预告
**【结尾悬念】**: [Cliffhanger Description]
**【下集预告画面】**: [Preview Description]
"""
