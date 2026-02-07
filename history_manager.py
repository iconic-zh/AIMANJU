import os
import json
import time
from datetime import datetime
import glob

HISTORY_DIR = "saved_projects"

class HistoryManager:
    def __init__(self):
        if not os.path.exists(HISTORY_DIR):
            os.makedirs(HISTORY_DIR)

    def _get_filename(self, project_id, title=""):
        # Sanitize title
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
        safe_title = safe_title[:20] # Limit length
        if not safe_title:
            safe_title = "Untitled"
        return os.path.join(HISTORY_DIR, f"{project_id}_{safe_title}.json")

    def save_project(self, session_state, project_id=None):
        """
        Save the current session state to a JSON file.
        If project_id is None, generate a new one.
        """
        if not project_id:
            project_id = str(int(time.time()))
        
        # Determine title
        title = "Untitled Project"
        story_content = session_state.get('story_content')
        
        if story_content:
            if isinstance(story_content, dict):
                # Try to get title from dictionary
                title = story_content.get("title", "Story Analysis")
                if not title or title == "Story Analysis":
                     # try finding other common keys or just use default
                     title = story_content.get("theme", "Story Analysis")
            elif isinstance(story_content, str):
                # Try to grab first line or first few chars
                content = story_content.strip()
                title = content.split('\n')[0][:30]
            else:
                title = "Story Project"
        
        # Prepare data
        data = {
            "id": project_id,
            "title": title,
            "updated_at": datetime.now().isoformat(),
            "story_content": session_state.get('story_content', ""),
            "series_plan": session_state.get('series_plan', ""),
            "episode_contents": session_state.get('episode_contents', {}),
            "next_episode_to_generate": session_state.get('next_episode_to_generate', 1)
        }

        # Find existing file for this ID to overwrite (in case title changed) or create new
        existing_files = glob.glob(os.path.join(HISTORY_DIR, f"{project_id}_*.json"))
        filename = self._get_filename(project_id, title)
        
        if existing_files:
            # If title changed, we might want to rename, but for simplicity let's just use the ID mapping
            # Actually, to keep filenames clean, let's remove old and write new if title changed
            # But simplest is just write to the ID-based filename.
            # Let's just use the first existing file if ID matches, or create new.
            # To support renaming, let's remove old if different
            old_filename = existing_files[0]
            if old_filename != filename:
                os.remove(old_filename)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return project_id

    def load_project(self, project_id):
        """Load project data by ID"""
        files = glob.glob(os.path.join(HISTORY_DIR, f"{project_id}_*.json"))
        if not files:
            return None
        
        filepath = files[0]
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert episode keys back to integers (JSON dict keys are strings)
                if 'episode_contents' in data:
                    data['episode_contents'] = {int(k): v for k, v in data['episode_contents'].items()}
                return data
        except Exception as e:
            print(f"Error loading project {project_id}: {e}")
            return None

    def get_history_list(self):
        """Return list of projects sorted by update time desc"""
        projects = []
        files = glob.glob(os.path.join(HISTORY_DIR, "*.json"))
        
        for fpath in files:
            try:
                filename = os.path.basename(fpath)
                # Parse ID from filename (format: {id}_{title}.json)
                parts = filename.split('_', 1)
                if len(parts) < 2:
                    continue
                project_id = parts[0]
                
                # Read just enough to get title and date? Or just rely on filename/mtime?
                # Let's read the file to be safe and get nice formatting
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    projects.append({
                        "id": data.get("id"),
                        "title": data.get("title", "Untitled"),
                        "updated_at": data.get("updated_at"),
                        "file_path": fpath
                    })
            except Exception:
                continue
                
        # Sort by updated_at desc
        projects.sort(key=lambda x: x['updated_at'], reverse=True)
        return projects

    def delete_project(self, project_id):
        files = glob.glob(os.path.join(HISTORY_DIR, f"{project_id}_*.json"))
        for f in files:
            os.remove(f)
