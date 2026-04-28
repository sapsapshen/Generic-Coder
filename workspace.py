import os, sys, json, time, threading, fnmatch
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable

_CONFIG_DIR = Path.home() / '.genericagent'
_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
_WORKSPACE_CONFIG_PATH = _CONFIG_DIR / 'workspace_config.json'

DEFAULT_EXCLUDE_PATTERNS = [
    '.git', '__pycache__', '*.pyc', '.DS_Store', 'node_modules',
    '.venv', 'venv', '.env', '*.egg-info', '.idea', '.vscode',
    '*.o', '*.so', '*.dylib', '*.dll', '*.exe', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', 'dist', 'build', '.tox',
]

def load_workspace_config() -> dict:
    if _WORKSPACE_CONFIG_PATH.exists():
        try:
            with open(_WORKSPACE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {'workspaces': [], 'recent_folders': [], 'active_workspace': ''}

def save_workspace_config(config: dict):
    with open(_WORKSPACE_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


class FileTreeBuilder:
    def __init__(self, exclude_patterns: Optional[List[str]] = None):
        self.exclude_patterns = exclude_patterns or DEFAULT_EXCLUDE_PATTERNS
        self._gitignore_patterns: Dict[str, List[str]] = {}

    def _load_gitignore(self, folder_path: str) -> List[str]:
        if folder_path in self._gitignore_patterns:
            return self._gitignore_patterns[folder_path]
        patterns = []
        gitignore_path = os.path.join(folder_path, '.gitignore')
        if os.path.isfile(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception:
                pass
        self._gitignore_patterns[folder_path] = patterns
        return patterns

    def _is_excluded(self, name: str, parent: str) -> bool:
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        gitignore = self._load_gitignore(parent)
        for pattern in gitignore:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    def build_tree(self, root_path: str, max_depth: int = 5,
                   current_depth: int = 0, max_items: int = 500) -> dict:
        root_path = os.path.abspath(root_path)
        if not os.path.isdir(root_path):
            return {
                'name': os.path.basename(root_path),
                'path': root_path,
                'type': 'file',
                'children': []
            }

        entry = {
            'name': os.path.basename(root_path) or root_path,
            'path': root_path,
            'type': 'directory',
            'children': []
        }

        if current_depth >= max_depth:
            entry['truncated'] = True
            return entry

        try:
            items = sorted(os.listdir(root_path), key=lambda x: (
                not os.path.isdir(os.path.join(root_path, x)), x.lower()))
        except PermissionError:
            entry['error'] = 'Permission denied'
            return entry
        except OSError as e:
            entry['error'] = str(e)
            return entry

        count = 0
        for item in items:
            if count >= max_items:
                entry['truncated'] = True
                break
            if item.startswith('.'):
                if item not in ('.gitignore', '.env.example', '.editorconfig'):
                    if not item.startswith('.env'):
                        continue
            if self._is_excluded(item, root_path):
                continue

            item_path = os.path.join(root_path, item)
            is_dir = os.path.isdir(item_path)

            if is_dir:
                child = self.build_tree(item_path, max_depth=max_depth,
                                       current_depth=current_depth + 1,
                                       max_items=max(50, max_items // 4))
                if child.get('children') or not child.get('error'):
                    entry['children'].append(child)
                    count += 1
            else:
                try:
                    size = os.path.getsize(item_path)
                except OSError:
                    size = 0
                entry['children'].append({
                    'name': item,
                    'path': item_path,
                    'type': 'file',
                    'size': size
                })
                count += 1

        return entry

    def build_flat_list(self, root_path: str, pattern: str = '*',
                        max_items: int = 500) -> List[dict]:
        root_path = os.path.abspath(root_path)
        results = []

        try:
            for entry in os.scandir(root_path):
                if len(results) >= max_items:
                    break
                if self._is_excluded(entry.name, root_path):
                    continue
                if pattern != '*' and not fnmatch.fnmatch(entry.name, pattern):
                    continue
                try:
                    size = entry.stat().st_size if entry.is_file() else 0
                except OSError:
                    size = 0
                results.append({
                    'name': entry.name,
                    'path': entry.path,
                    'type': 'directory' if entry.is_dir() else 'file',
                    'size': size
                })
        except PermissionError:
            pass
        except OSError:
            pass

        results.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        return results


class WorkspaceWatcher:
    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self._watched_paths: Dict[str, dict] = {}
        self._callbacks: List[Callable] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_watch(self, path: str, recursive: bool = True):
        path = os.path.abspath(path)
        self._watched_paths[path] = {
            'recursive': recursive,
            'snapshot': self._snapshot_dir(path, recursive)
        }

    def remove_watch(self, path: str):
        path = os.path.abspath(path)
        self._watched_paths.pop(path, None)

    def on_change(self, callback: Callable):
        self._callbacks.append(callback)

    def _snapshot_dir(self, path: str, recursive: bool = True) -> Dict[str, float]:
        snapshot = {}
        try:
            if recursive:
                for root, dirs, files in os.walk(path):
                    for name in files:
                        fp = os.path.join(root, name)
                        try:
                            snapshot[fp] = os.path.getmtime(fp)
                        except OSError:
                            pass
            else:
                for entry in os.scandir(path):
                    if entry.is_file():
                        try:
                            snapshot[entry.path] = entry.stat().st_mtime
                        except OSError:
                            pass
        except PermissionError:
            pass
        return snapshot

    def _check_changes(self):
        for path, config in list(self._watched_paths.items()):
            if not os.path.exists(path):
                continue
            new_snapshot = self._snapshot_dir(path, config['recursive'])
            old_snapshot = config['snapshot']

            added = set(new_snapshot.keys()) - set(old_snapshot.keys())
            removed = set(old_snapshot.keys()) - set(new_snapshot.keys())
            modified = {
                fp for fp in set(new_snapshot.keys()) & set(old_snapshot.keys())
                if new_snapshot[fp] != old_snapshot[fp]
            }

            if added or removed or modified:
                config['snapshot'] = new_snapshot
                changes = {
                    'path': path,
                    'added': list(added),
                    'removed': list(removed),
                    'modified': list(modified)
                }
                for cb in self._callbacks:
                    try:
                        cb(changes)
                    except Exception:
                        pass

    def start(self):
        if self._running:
            return
        self._running = True

        def _loop():
            while self._running:
                try:
                    self._check_changes()
                except Exception:
                    pass
                time.sleep(self.interval)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None


class WorkspaceManager:
    def __init__(self):
        self._active_workspace: str = ''
        self._workspaces: Dict[str, dict] = {}
        self._tree_builder = FileTreeBuilder()
        self._watcher = WorkspaceWatcher()
        self._lock = threading.Lock()
        self._load_state()

    def _load_state(self):
        config = load_workspace_config()
        for ws in config.get('workspaces', []):
            name = ws.get('name', '')
            path = ws.get('path', '')
            if name and path and os.path.isdir(path):
                self._workspaces[name] = {'path': path, 'exclude': ws.get('exclude', [])}
        active = config.get('active_workspace', '')
        if active and active in self._workspaces:
            self._active_workspace = active

    def _save_state(self):
        config = {
            'workspaces': [
                {'name': name, 'path': ws['path'], 'exclude': ws.get('exclude', [])}
                for name, ws in self._workspaces.items()
            ],
            'recent_folders': [w['path'] for w in self._workspaces.values()][-20:],
            'active_workspace': self._active_workspace
        }
        save_workspace_config(config)

    def open_folder(self, path: str, name: str = '') -> dict:
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return {'status': 'error', 'msg': f'Folder not found: {path}'}

        name = name or os.path.basename(path)
        with self._lock:
            self._workspaces[name] = {'path': path, 'exclude': []}
            self._active_workspace = name

        self._save_state()
        self._watcher.add_watch(path)
        if not self._watcher._running:
            self._watcher.start()

        return {
            'status': 'success',
            'name': name,
            'path': path,
            'tree': self._tree_builder.build_tree(path, max_depth=3)
        }

    def close_workspace(self, name: str = '') -> dict:
        with self._lock:
            target = name or self._active_workspace
            if target not in self._workspaces:
                return {'status': 'error', 'msg': f'Workspace "{target}" not open'}

            path = self._workspaces[target]['path']
            self._watcher.remove_watch(path)
            self._workspaces.pop(target, None)

            if self._active_workspace == target:
                self._active_workspace = next(iter(self._workspaces.keys()), '')
            self._save_state()

        return {'status': 'success', 'name': target}

    def switch_workspace(self, name: str) -> dict:
        with self._lock:
            if name not in self._workspaces:
                return {'status': 'error', 'msg': f'Workspace "{name}" not found'}
            self._active_workspace = name
            self._save_state()
        return {
            'status': 'success',
            'name': name,
            'path': self._workspaces[name]['path']
        }

    def get_active_workspace(self) -> dict:
        with self._lock:
            if not self._active_workspace or self._active_workspace not in self._workspaces:
                return {'status': 'error', 'msg': 'No active workspace'}
            ws = self._workspaces[self._active_workspace]
            return {
                'status': 'success',
                'name': self._active_workspace,
                'path': ws['path']
            }

    def list_workspaces(self) -> List[dict]:
        with self._lock:
            return [
                {
                    'name': name,
                    'path': ws['path'],
                    'active': name == self._active_workspace
                }
                for name, ws in self._workspaces.items()
            ]

    def get_tree(self, path: str = '', max_depth: int = 5) -> dict:
        if not path:
            active = self.get_active_workspace()
            if active.get('status') != 'success':
                return active
            path = active['path']

        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return {'status': 'error', 'msg': f'Not a directory: {path}'}

        return {
            'status': 'success',
            'tree': self._tree_builder.build_tree(path, max_depth=max_depth)
        }

    def list_files(self, path: str = '', pattern: str = '*') -> dict:
        if not path:
            active = self.get_active_workspace()
            if active.get('status') != 'success':
                return active
            path = active['path']

        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return {'status': 'error', 'msg': f'Not a directory: {path}'}

        files = self._tree_builder.build_flat_list(path, pattern=pattern)
        return {'status': 'success', 'files': files, 'path': path}

    def get_relative_path(self, absolute_path: str) -> str:
        active = self.get_active_workspace()
        if active.get('status') != 'success':
            return absolute_path
        ws_path = active['path']
        try:
            return os.path.relpath(absolute_path, ws_path)
        except ValueError:
            return absolute_path

    def is_within_workspace(self, path: str) -> bool:
        active = self.get_active_workspace()
        if active.get('status') != 'success':
            return False
        ws_path = active['path']
        try:
            rel = os.path.relpath(os.path.abspath(path), ws_path)
            return not rel.startswith('..')
        except ValueError:
            return False

    def create_folder(self, path: str) -> dict:
        os.makedirs(os.path.abspath(path), exist_ok=True)
        return {'status': 'success', 'path': os.path.abspath(path)}

    def delete_item(self, path: str) -> dict:
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return {'status': 'error', 'msg': f'Path not found: {path}'}

        try:
            if os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            else:
                os.remove(path)
            return {'status': 'success', 'path': path}
        except OSError as e:
            return {'status': 'error', 'msg': str(e)}

    def move_item(self, src: str, dst: str) -> dict:
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)
        if not os.path.exists(src):
            return {'status': 'error', 'msg': f'Source not found: {src}'}

        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            import shutil
            shutil.move(src, dst)
            return {'status': 'success', 'source': src, 'destination': dst}
        except OSError as e:
            return {'status': 'error', 'msg': str(e)}

    def search_files(self, query: str, path: str = '',
                     max_results: int = 50) -> dict:
        if not path:
            active = self.get_active_workspace()
            if active.get('status') != 'success':
                return active
            path = active['path']

        path = os.path.abspath(path)
        results = []
        query_lower = query.lower()

        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not self._tree_builder._is_excluded(d, root)]
                for f in files:
                    if self._tree_builder._is_excluded(f, root):
                        continue
                    if query_lower in f.lower():
                        fp = os.path.join(root, f)
                        try:
                            size = os.path.getsize(fp)
                        except OSError:
                            size = 0
                        results.append({
                            'name': f,
                            'path': fp,
                            'size': size,
                            'relative': self.get_relative_path(fp)
                        })
                        if len(results) >= max_results:
                            return {'status': 'success', 'results': results, 'path': path}
        except PermissionError:
            pass
        except OSError:
            pass

        return {'status': 'success', 'results': results, 'path': path}

    def on_file_changed(self, callback: Callable):
        self._watcher.on_change(callback)

    def __del__(self):
        self._watcher.stop()
