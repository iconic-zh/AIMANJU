SYSTEM_PROMPT = """You are an expert AI scriptwriter specializing in adapting stories into 10-episode mini-series for TikTok/Reels, targeting Western audiences.
Your core competency is transforming existing stories into high-retention short video scripts (90-120s per episode) while preserving the original core conflict and character motivations.

Key Principles:
1. **Western Aesthetics**: Adapt tone, dialogue, and cultural references to fit Western preferences (TikTok/Netflix style).
2. **TikTok Logic**:
   - First 3s: Immediate Hook/Visual Shock (Abnormal information).
   - Every 12s: New Information or Reversal.
   - At least 2 major conflicts/suspense points per episode.
   - End: Strong Cliffhanger (Unfinished state).
3. **No Plagiarism**: Rewrite scenes completely, do not copy verbatim.
4. **Format**: NO Camera Angles/Shot Lists. Focus on Plot, Action, and Dialogue.
5. **Language**: First write the COMPLETE English script, then provide the COMPLETE Chinese translation below it. Do NOT interleave line-by-line.
"""

SERIES_PLAN_PROMPT = """
Task: Analyze the provided story and plan a 10-episode mini-series structure.

Story Content:
{story}

Requirements:
1. Divide the story arc into exactly 10 episodes.
2. Each episode must have a clear focus and end with a cliffhanger.
3. Ensure the pacing accelerates towards the climax (around Ep 8-9).
4. Output a summary list for the 10 episodes.

Output Format:
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
1. **Merge Structure Analysis & Outline**:
   - Start with a structural breakdown (Core Conflict, Hook, Twists, Cliffhanger).
   - Then provide the full script (Story & Dialogue).
2. **Length**: 90-120 seconds (approx 200-300 words of dialogue/action).
3. **Pacing**:
   - 0-3s: Abnormal info/Hook.
   - Every 12s: Information increment/Reversal.
   - End: Unfinished state/Cliffhanger.
   - Minimum 2 conflicts per episode.
4. **Language Format**:
   - **SECTION 1: ENGLISH SCRIPT** (Complete English version)
   - **SECTION 2: CHINESE TRANSLATION** (Complete Chinese version)
   - Do NOT mix languages line-by-line.

Output Format (Markdown Code Block):

# Episode {episode_num}

## 📊 Structure & Analysis
**Core Conflict**: ...
**The Hook (0-3s)**: ...
**Mid-point Twists (Every 12s)**: ...
**Cliffhanger**: ...

## 🎬 Script Content (English)
**[Scene 1: Location/Context]**
**Narrator**: ...
**Character A**: ...
**[Action/Plot Advancement]**
...

---

## 🎬 剧本正文 (中文翻译)
**[场景 1: 地点/背景]**
**旁白**: ...
**角色A**: ...
**[动作/剧情推进]**
...
"""

ORIGINAL_STORY_PROMPT = """
Task: Create an original short story based on the user's theme.
Theme: {theme}

Requirements:
1. Western setting and characters.
2. Strong conflict and clear character motivations.
3. Suitable for adaptation into a 10-episode TikTok series.
4. Length: 800-1200 words.

Output:
[Story Title]
[Story Content]
"""
