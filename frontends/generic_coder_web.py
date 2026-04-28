#!/usr/bin/env python3
"""Generic Coder custom web UI without Streamlit."""

from __future__ import annotations

import json
import os
import queue
import re
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List
from wsgiref.simple_server import WSGIRequestHandler, make_server

from bottle import Bottle, HTTPResponse, request, response, static_file

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from agentmain import GeneraticAgent
import chatapp_common  # noqa: F401  Activate /continue patch on GeneraticAgent.
from frontends.chatapp_common import build_done_text
from frontends.continue_cmd import extract_ui_messages, handle_frontend_command, list_sessions, reset_conversation
from remoteserver import RemoteServerManager, add_server_config
from workspace import WorkspaceManager, load_workspace_config

APP_NAME = "Generic Coder"
APP_SUBTITLE = "Autonomous development cockpit"
DEFAULT_THEME = "solarflare"
SUPPORTED_THEMES = {"solarflare", "graphite", "neonwave", "daybreak", "ember"}
STATIC_DIR = BASE_DIR / "assets" / "generic_coder"
INDEX_HTML = STATIC_DIR / "index.html"
MAX_SESSIONS = 20
CONFIG_DIR = Path.home() / ".genericagent"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_STATE_PATH = CONFIG_DIR / "generic_coder_frontend.json"
UI_LLM_CONFIG_PATH = CONFIG_DIR / "ui_llm_config.json"


def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else dict(default)
    except Exception:
        return dict(default)


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def default_frontend_state() -> Dict[str, Any]:
    return {
        "workspace": {"path": "", "name": ""},
        "remote": {
            "enabled": False,
            "server_name": "",
            "name": "",
            "host": "",
            "port": 22,
            "username": "root",
            "password": "",
            "key_path": "",
            "cwd": "",
        },
    }


def infer_session_type(key: str) -> str:
    lower = key.lower()
    if "native" in lower and "claude" in lower:
        return "native_claude"
    if "native" in lower and "oai" in lower:
        return "native_oai"
    if "claude" in lower:
        return "claude"
    return "oai"


def load_managed_llm_form() -> Dict[str, str]:
    payload = load_json(UI_LLM_CONFIG_PATH, {})
    if not payload:
        return {
            "entry_key": "generic_coder_native_oai_config",
            "session_type": "native_oai",
            "protocol_preset": "custom",
            "api_mode": "chat_completions",
            "provider": "",
            "name": "",
            "apikey": "",
            "apibase": "",
            "model": "",
        }
    key, cfg = next(iter(payload.items()))
    cfg = cfg if isinstance(cfg, dict) else {}
    return {
        "entry_key": key,
        "session_type": infer_session_type(key),
        "protocol_preset": str(cfg.get("protocol_preset", "custom")),
        "api_mode": str(cfg.get("api_mode", "chat_completions")),
        "provider": str(cfg.get("provider", "")),
        "name": str(cfg.get("name", "")),
        "apikey": str(cfg.get("apikey", "")),
        "apibase": str(cfg.get("apibase", "")),
        "model": str(cfg.get("model", "")),
    }


def save_managed_llm_form(payload: Dict[str, Any]) -> Dict[str, str]:
    session_type = str(payload.get("session_type", "native_oai")).strip() or "native_oai"
    protocol_preset = str(payload.get("protocol_preset", "custom")).strip() or "custom"
    api_mode = str(payload.get("api_mode", "chat_completions")).strip().lower().replace("-", "_") or "chat_completions"
    provider = str(payload.get("provider", "")).strip()
    name = str(payload.get("name", "")).strip()
    apikey = str(payload.get("apikey", "")).strip()
    apibase = str(payload.get("apibase", "")).strip()
    model = str(payload.get("model", "")).strip()
    if not all((apikey, apibase, model)):
        raise ValueError("API key, base URL, and model are required.")

    entry_key = f"generic_coder_{session_type}_config"
    cfg = {
        "protocol_preset": protocol_preset,
        "api_mode": "responses" if api_mode == "responses" else "chat_completions",
        "provider": provider,
        "name": name or (provider if provider else model),
        "apikey": apikey,
        "apibase": apibase,
        "model": model,
    }
    save_json(UI_LLM_CONFIG_PATH, {entry_key: cfg})
    return {
        "entry_key": entry_key,
        "session_type": session_type,
        "protocol_preset": cfg["protocol_preset"],
        "api_mode": cfg["api_mode"],
        "provider": provider,
        "name": cfg["name"],
        "apikey": apikey,
        "apibase": apibase,
        "model": model,
    }


def normalize_assistant_text(raw_text: str, streaming: bool = False) -> str:
    text = build_done_text(raw_text) if raw_text else ""
    text = re.sub(r"(?m)^\**LLM Running \(Turn \d+\) \.\.\.\**\s*$", "", text)
    text = re.sub(r"(?m)^\[Info\] Final response to user\.\s*$", "", text)
    text = re.sub(r"(?ms)\n?`{3,}\s*\n(?:\s*\n)*`{3,}\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if text:
        return text
    return "Synthesizing response..." if streaming else "..."


def relative_time(mtime: float) -> str:
    delta = max(0, int(time.time() - mtime))
    if delta < 60:
        return f"{delta}s ago"
    if delta < 3600:
        return f"{delta // 60}m ago"
    if delta < 86400:
        return f"{delta // 3600}h ago"
    return f"{delta // 86400}d ago"


def model_label_for_client(client) -> str:
    if isinstance(client, dict):
        return "Unavailable"
    backend = getattr(client, "backend", None)
    model = getattr(backend, "model", None)
    if isinstance(model, str) and model.strip():
        return model.strip()
    name = getattr(backend, "name", None)
    if isinstance(name, str) and name.strip():
        return name.strip()
    return type(backend).__name__ if backend is not None else "Unknown"


class GenericCoderState:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.agent = GeneraticAgent()
        self.workspace_manager = WorkspaceManager()
        self.remote_manager = RemoteServerManager()
        self.frontend_state = load_json(FRONTEND_STATE_PATH, default_frontend_state())
        if getattr(self.agent, "llmclient", None) is not None:
            threading.Thread(target=self.agent.run, daemon=True).start()
        self.theme = DEFAULT_THEME
        self.messages: List[Dict[str, str]] = []
        self.pending: Dict[str, Dict[str, object]] = {}
        self.last_reply_time = int(time.time())

    def bootstrap_payload(self) -> Dict[str, object]:
        with self.lock:
            return {
                "app_name": APP_NAME,
                "subtitle": APP_SUBTITLE,
                "theme": self.theme,
                "messages": list(self.messages),
                "is_running": bool(getattr(self.agent, "is_running", False)),
                "model": self.current_model_label(),
                "model_index": getattr(self.agent, "llm_no", 0),
                "workspace": self.workspace_payload(),
                "remote": self.remote_payload(),
                "llm_form": self.llm_form_payload(),
                "last_reply_time": self.last_reply_time,
            }

    def _save_frontend_state(self) -> None:
        save_json(FRONTEND_STATE_PATH, self.frontend_state)

    def llm_form_payload(self) -> Dict[str, str]:
        return load_managed_llm_form()

    def save_llm_form(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        form = save_managed_llm_form(payload)
        self.agent.load_llm_sessions()
        if getattr(self.agent, "llmclients", None):
            self.agent.next_llm(len(self.agent.llmclients) - 1)
        return {
            "form": form,
            "model": self.current_model_label(),
            "model_index": getattr(self.agent, "llm_no", 0),
            "models": self.models_payload()["models"],
        }

    def workspace_payload(self) -> Dict[str, Any]:
        active = self.workspace_manager.get_active_workspace()
        cfg = load_workspace_config()
        return {
            "active": active if active.get("status") == "success" else None,
            "workspaces": self.workspace_manager.list_workspaces(),
            "recent_folders": cfg.get("recent_folders", []),
        }

    def set_workspace(self, path: str, name: str = "") -> Dict[str, Any]:
        result = self.workspace_manager.open_folder(path, name=name)
        if result.get("status") != "success":
            raise RuntimeError(result.get("msg", "Failed to open workspace."))
        self.frontend_state["workspace"] = {"path": result["path"], "name": result["name"]}
        self._save_frontend_state()
        return self.workspace_payload()

    def remote_payload(self) -> Dict[str, Any]:
        remote_state = dict(default_frontend_state()["remote"])
        remote_state.update(self.frontend_state.get("remote", {}))
        active_connections = self.remote_manager.list_active_connections()
        return {
            "form": remote_state,
            "configs": self.remote_manager.list_configs(),
            "active_connections": active_connections,
            "connected": bool(remote_state.get("server_name") and remote_state.get("server_name") in active_connections),
        }

    def connect_remote(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        remote_state = dict(default_frontend_state()["remote"])
        remote_state.update(self.frontend_state.get("remote", {}))
        for key in ("enabled", "server_name", "name", "host", "port", "username", "password", "key_path", "cwd"):
            if key in payload:
                remote_state[key] = payload[key]

        server_name = str(remote_state.get("server_name") or remote_state.get("name") or "").strip()
        host = str(remote_state.get("host", "")).strip()
        username = str(remote_state.get("username", "root")).strip() or "root"
        password = str(remote_state.get("password", ""))
        key_path = str(remote_state.get("key_path", "")).strip()
        cwd = str(remote_state.get("cwd", "")).strip()
        port = int(remote_state.get("port", 22) or 22)

        if not server_name:
            server_name = f"{username}@{host}" if host else ""
            remote_state["server_name"] = server_name
        if not server_name:
            raise ValueError("Remote server name or host is required.")

        if host:
            add_server_config(
                name=server_name,
                host=host,
                port=port,
                username=username,
                password=password,
                key_path=key_path,
            )

        result = self.remote_manager.connect_to(server_name, password)
        if result.get("status") != "connected":
            raise RuntimeError(result.get("msg", "Remote connection failed."))

        remote_state["enabled"] = bool(remote_state.get("enabled"))
        self.frontend_state["remote"] = remote_state
        self._save_frontend_state()
        payload = self.remote_payload()
        payload["message"] = f"Connected to {server_name}"
        if cwd:
            payload["remote_cwd"] = cwd
        return payload

    def build_execution_context(self, prompt: str) -> str:
        blocks: List[str] = []
        remote = self.frontend_state.get("remote", {})
        server_name = str(remote.get("server_name", "")).strip()
        remote_cwd = str(remote.get("cwd", "")).strip()
        if remote.get("enabled") and server_name:
            if server_name not in self.remote_manager.list_active_connections():
                reconnect = self.remote_manager.connect_to(server_name, str(remote.get("password", "")))
                if reconnect.get("status") != "connected":
                    raise RuntimeError(reconnect.get("msg", "Remote environment is enabled but not connected."))
            blocks.append(
                "[GENERIC CODER FRONTEND CONTEXT]\n"
                f"Execution mode: remote\n"
                f"Remote server: {server_name}\n"
                f"Remote working directory: {remote_cwd or '~'}\n"
                "Rules:\n"
                "1. You must use remote_connect/remote_exec/remote_file_read/remote_file_write/remote_list_dir to inspect, edit, run, and debug in the remote workspace.\n"
                "2. Do not download remote project files to local temp before modifying them unless the user explicitly asks for that.\n"
                f"3. When running remote commands, use cwd={remote_cwd or '~'}.\n"
            )
        else:
            active = self.workspace_manager.get_active_workspace()
            if active.get("status") == "success":
                blocks.append(
                    "[GENERIC CODER FRONTEND CONTEXT]\n"
                    "Execution mode: local workspace\n"
                    f"Active workspace: {active['path']}\n"
                    "Prefer operating in this workspace when the user asks for code changes, searches, or debugging.\n"
                )
        return "\n\n".join(blocks + [prompt])

    def current_model_label(self) -> str:
        if getattr(self.agent, "llmclient", None) is None:
            return "No LLM configured"
        return model_label_for_client(self.agent.llmclient)

    def models_payload(self) -> Dict[str, object]:
        self.agent.load_llm_sessions()
        raw_models = [
            {"index": idx, "label": model_label_for_client(client)}
            for idx, client in enumerate(getattr(self.agent, "llmclients", []) or [])
        ]
        current_index = getattr(self.agent, "llm_no", 0)
        deduped = []
        seen = set()
        current_visible = 0
        for item in raw_models:
            key = item["label"].strip().lower()
            if key in seen:
                if item["index"] == current_index:
                    for visible_idx, kept in enumerate(deduped):
                        if kept["label"].strip().lower() == key:
                            current_visible = visible_idx
                            break
                continue
            if item["index"] == current_index:
                current_visible = len(deduped)
            deduped.append(item)
            seen.add(key)
        return {"models": deduped, "current_index": current_visible}

    def set_model(self, index: int) -> Dict[str, object]:
        self.agent.load_llm_sessions()
        clients = getattr(self.agent, "llmclients", []) or []
        if getattr(self.agent, "is_running", False):
            raise RuntimeError("Cannot switch model while a task is running.")
        if not (0 <= index < len(clients)):
            raise IndexError(f"Model index out of range: {index}")
        self.agent.next_llm(index)
        return {
            "current_index": getattr(self.agent, "llm_no", 0),
            "model": self.current_model_label(),
            "models": self.models_payload()["models"],
        }

    def set_theme(self, theme: str) -> None:
        with self.lock:
            if theme in SUPPORTED_THEMES:
                self.theme = theme

    def reset_messages(self, notice: str | None = None) -> Dict[str, object]:
        with self.lock:
            self.messages = []
            self.last_reply_time = int(time.time())
            payload: Dict[str, object] = {"handled": True, "messages": list(self.messages)}
            if notice:
                payload["notice"] = notice
            return payload

    def apply_command(self, prompt: str) -> Dict[str, object] | None:
        cmd = (prompt or "").strip()
        if cmd == "/new":
            reset_conversation(self.agent, message="")
            return self.reset_messages()

        if not cmd.startswith("/continue"):
            return None

        matched = re.match(r"/continue\s+(\d+)\s*$", cmd)
        sessions = list_sessions(exclude_pid=os.getpid()) if matched else []
        target_path = None
        if matched:
            idx = int(matched.group(1)) - 1
            if 0 <= idx < len(sessions):
                target_path = sessions[idx][0]

        result = handle_frontend_command(self.agent, cmd)
        restored = extract_ui_messages(target_path) if target_path and result.startswith("✅") else None

        with self.lock:
            if restored:
                self.messages = restored + [{"role": "assistant", "content": result}]
            else:
                self.messages.append({"role": "assistant", "content": result})
            self.last_reply_time = int(time.time())
            return {"handled": True, "messages": list(self.messages), "notice": result}

    def start_task(self, prompt: str) -> str:
        task_id = uuid.uuid4().hex
        prepared_prompt = self.build_execution_context(prompt)
        with self.lock:
            self.messages.append({"role": "user", "content": prompt})
            self.pending[task_id] = {
                "preview": "Synthesizing response...",
                "final": "",
                "done": False,
                "updated_at": time.time(),
            }
        threading.Thread(target=self._drain_task, args=(task_id, prepared_prompt), daemon=True).start()
        return task_id

    def _drain_task(self, task_id: str, prompt: str) -> None:
        raw_text = ""
        try:
            display_queue = self.agent.put_task(prompt, source="user")
            while True:
                try:
                    item = display_queue.get(timeout=1)
                except queue.Empty:
                    with self.lock:
                        if task_id not in self.pending:
                            return
                    continue

                if "next" in item:
                    raw_text = item["next"]
                    with self.lock:
                        if task_id in self.pending:
                            self.pending[task_id]["preview"] = normalize_assistant_text(raw_text, streaming=True)
                            self.pending[task_id]["updated_at"] = time.time()

                if "done" in item:
                    raw_text = item["done"]
                    break

            final_text = normalize_assistant_text(raw_text, streaming=False)
            with self.lock:
                if task_id in self.pending:
                    self.pending[task_id]["preview"] = final_text
                    self.pending[task_id]["final"] = final_text
                    self.pending[task_id]["done"] = True
                    self.pending[task_id]["updated_at"] = time.time()
                self.messages.append({"role": "assistant", "content": final_text})
                self.last_reply_time = int(time.time())
        except Exception as exc:
            final_text = f"Runtime error: {exc}"
            with self.lock:
                if task_id in self.pending:
                    self.pending[task_id]["preview"] = final_text
                    self.pending[task_id]["final"] = final_text
                    self.pending[task_id]["done"] = True
                    self.pending[task_id]["updated_at"] = time.time()
                self.messages.append({"role": "assistant", "content": final_text})
                self.last_reply_time = int(time.time())

    def task_payload(self, task_id: str) -> Dict[str, object]:
        with self.lock:
            task = self.pending.get(task_id)
            if task is None:
                return {"done": True, "preview": "...", "final": "..."}
            return {
                "done": bool(task["done"]),
                "preview": str(task["preview"]),
                "final": str(task["final"]),
                "updated_at": task["updated_at"],
            }

    def list_sessions_payload(self) -> Dict[str, object]:
        sessions = list_sessions(exclude_pid=os.getpid())[:MAX_SESSIONS]
        return {
            "sessions": [
                {
                    "index": idx + 1,
                    "preview": preview,
                    "rounds": rounds,
                    "mtime": mtime,
                    "relative_time": relative_time(mtime),
                }
                for idx, (_, mtime, preview, rounds) in enumerate(sessions)
            ]
        }

    def stop(self) -> Dict[str, object]:
        self.agent.abort()
        return {"ok": True, "is_running": bool(getattr(self.agent, "is_running", False))}


STATE = GenericCoderState()


def json_response(payload: Dict[str, object], status: int = 200) -> HTTPResponse:
    response.content_type = "application/json"
    response.status = status
    return HTTPResponse(body=json.dumps(payload, ensure_ascii=False), status=status, headers={"Content-Type": "application/json; charset=utf-8"})


def create_app() -> Bottle:
    app = Bottle()

    @app.get("/")
    def index() -> HTTPResponse:
        return HTTPResponse(INDEX_HTML.read_text(encoding="utf-8"), headers={"Content-Type": "text/html; charset=utf-8"})

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/static/<filepath:path>")
    def static(filepath: str):
        return static_file(filepath, root=str(STATIC_DIR))

    @app.get("/api/bootstrap")
    def bootstrap() -> HTTPResponse:
        return json_response(STATE.bootstrap_payload())

    @app.post("/api/theme")
    def set_theme() -> HTTPResponse:
        payload = request.json or {}
        STATE.set_theme(str(payload.get("theme", DEFAULT_THEME)))
        return json_response({"theme": STATE.theme})

    @app.get("/api/models")
    def models() -> HTTPResponse:
        return json_response(STATE.models_payload())

    @app.get("/api/settings")
    def settings() -> HTTPResponse:
        return json_response({
            "llm_form": STATE.llm_form_payload(),
            "workspace": STATE.workspace_payload(),
            "remote": STATE.remote_payload(),
            "models": STATE.models_payload(),
        })

    @app.post("/api/model")
    def set_model() -> HTTPResponse:
        payload = request.json or {}
        try:
            index = int(payload.get("index"))
            return json_response(STATE.set_model(index))
        except Exception as exc:
            return json_response({"error": str(exc)}, status=400)

    @app.post("/api/llm-config")
    def set_llm_config() -> HTTPResponse:
        payload = request.json or {}
        try:
            return json_response(STATE.save_llm_form(payload))
        except Exception as exc:
            return json_response({"error": str(exc)}, status=400)

    @app.post("/api/workspace")
    def set_workspace() -> HTTPResponse:
        payload = request.json or {}
        try:
            return json_response(STATE.set_workspace(str(payload.get("path", "")).strip(), str(payload.get("name", "")).strip()))
        except Exception as exc:
            return json_response({"error": str(exc)}, status=400)

    @app.post("/api/remote/connect")
    def connect_remote() -> HTTPResponse:
        payload = request.json or {}
        try:
            return json_response(STATE.connect_remote(payload))
        except Exception as exc:
            return json_response({"error": str(exc)}, status=400)

    @app.post("/api/chat")
    def chat() -> HTTPResponse:
        payload = request.json or {}
        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            return json_response({"error": "Prompt is required."}, status=400)

        handled = STATE.apply_command(prompt)
        if handled is not None:
            return json_response(handled)

        try:
            task_id = STATE.start_task(prompt)
            return json_response({"task_id": task_id})
        except Exception as exc:
            return json_response({"error": str(exc)}, status=400)

    @app.get("/api/tasks/<task_id>")
    def task(task_id: str) -> HTTPResponse:
        return json_response(STATE.task_payload(task_id))

    @app.get("/api/sessions")
    def sessions() -> HTTPResponse:
        return json_response(STATE.list_sessions_payload())

    @app.post("/api/stop")
    def stop() -> HTTPResponse:
        return json_response(STATE.stop())

    return app


class QuietHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


APP = create_app()


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    with make_server(host, port, APP, handler_class=QuietHandler) as server:
        print(f"[Generic Coder] running at http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Generic Coder web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)
