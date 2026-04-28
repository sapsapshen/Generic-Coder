#!/usr/bin/env python3
"""
Generic Coder Desktop App — premium solo-mode shell.
Tkinter-based, zero extra dependencies, identical theme engine as web UI.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, sys, json, threading, tempfile, subprocess, platform
from pathlib import Path
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from frontends.themes import (
    ALL_THEMES, THEME_MAP, THEME_PRESETS,
    DEFAULT_THEME, get_theme_tk, get_theme_colors,
)

APP_NAME = "Generic Coder"
APP_VERSION = "0.2.0"


class SoloChatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — Solo Mode")
        self.root.geometry("880x640")
        self.root.minsize(500, 360)

        try:
            if platform.system() == 'Darwin':
                self.root.tk.call('tk', 'scaling', 1.5)
        except Exception:
            pass

        self.theme_name = DEFAULT_THEME
        self.colors = get_theme_tk(DEFAULT_THEME)
        self.messages = []
        self.remote_configs = []
        self._tool = None
        self._agent = None
        self._agent_lock = threading.Lock()
        self.workspace_tree_data = None
        self.workspace_path = os.getcwd()

        self._load_remote_configs()
        self._apply_base_style()
        self._build_ui()
        self._apply_full_theme()
        self._bind_keys()

        self.root.protocol('WM_DELETE_WINDOW', self._on_close)

    def _load_remote_configs(self):
        p = Path.home() / '.genericagent' / 'remote_config.json'
        if p.exists():
            self.remote_configs = json.loads(p.read_text())

    def _apply_base_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(bg=self.colors['page_bg'])

    def _build_ui(self):
        self.top_bar = tk.Frame(
            self.root, bg=self.colors['titlebar_bg'],
            highlightbackground=self.colors['titlebar_border'],
            highlightthickness=1,
        )
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        self.top_accent = tk.Label(
            self.top_bar, text="●",
            font=('Helvetica Neue', 14, 'bold'),
            bg=self.colors['titlebar_bg'],
            fg=self.colors['accent_primary'],
        )
        self.top_accent.pack(side=tk.LEFT, padx=(14, 2), pady=6)

        self.top_label = tk.Label(
            self.top_bar, text=APP_NAME,
            font=('Helvetica Neue', 13, 'bold'),
            bg=self.colors['titlebar_bg'],
            fg=self.colors['titlebar_text'],
        )
        self.top_label.pack(side=tk.LEFT, pady=6)

        self.theme_var = tk.StringVar(value=self.theme_name)
        self.theme_combo = ttk.Combobox(
            self.top_bar, textvariable=self.theme_var,
            values=[t.name for t in ALL_THEMES],
            state='readonly', width=14,
        )
        self.theme_combo.pack(side=tk.RIGHT, padx=12, pady=4)
        self.theme_combo.bind('<<ComboboxSelected>>', self._on_theme_change)

        self.toolbar = tk.Frame(
            self.root, bg=self.colors['container_bg'],
            highlightbackground=self.colors['border_subtle'],
            highlightthickness=1,
        )
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.toolbar.pack_forget()

        self.tool_ws = tk.Button(
            self.toolbar, text="📂 Workspace",
            font=('Helvetica Neue', 10),
            bg=self.colors['btn_secondary_bg'],
            fg=self.colors['btn_secondary_text'],
            activebackground=self.colors['btn_secondary_hover'],
            activeforeground=self.colors['text_primary'],
            bd=0, padx=10, pady=3, cursor='hand2',
            command=self._toggle_workspace,
        )
        self.tool_ws.pack(side=tk.LEFT, padx=4, pady=4)

        self.tool_rm = tk.Button(
            self.toolbar, text="🌐 Remote",
            font=('Helvetica Neue', 10),
            bg=self.colors['btn_secondary_bg'],
            fg=self.colors['btn_secondary_text'],
            activebackground=self.colors['btn_secondary_hover'],
            activeforeground=self.colors['text_primary'],
            bd=0, padx=10, pady=3, cursor='hand2',
            command=self._toggle_remote,
        )
        self.tool_rm.pack(side=tk.LEFT, padx=4, pady=4)

        self.tool_up = tk.Button(
            self.toolbar, text="📎 Upload",
            font=('Helvetica Neue', 10),
            bg=self.colors['btn_secondary_bg'],
            fg=self.colors['btn_secondary_text'],
            activebackground=self.colors['btn_secondary_hover'],
            activeforeground=self.colors['text_primary'],
            bd=0, padx=10, pady=3, cursor='hand2',
            command=self._upload_file,
        )
        self.tool_up.pack(side=tk.LEFT, padx=4, pady=4)

        self.tool_status = tk.Label(
            self.toolbar, text="",
            font=('Helvetica Neue', 10),
            bg=self.colors['container_bg'],
            fg=self.colors['text_tertiary'],
        )
        self.tool_status.pack(side=tk.RIGHT, padx=12, pady=4)

        self.chat_frame = tk.Frame(self.root, bg=self.colors['page_bg'])
        self.chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.chat_display = tk.Text(
            self.chat_frame,
            font=('Helvetica Neue', 12),
            wrap=tk.WORD, state=tk.DISABLED,
            bg=self.colors['page_bg'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary'],
            selectbackground=self.colors['selection_bg'],
            selectforeground=self.colors['selection_text'],
            bd=0, padx=20, pady=12,
            relief=tk.FLAT,
        )
        self.scrollbar = tk.Scrollbar(
            self.chat_frame, orient=tk.VERTICAL,
            command=self.chat_display.yview,
            bg=self.colors['scrollbar_track'],
            troughcolor=self.colors['scrollbar_track'],
            activebackground=self.colors['scrollbar_hover'],
        )
        self.chat_display.configure(yscrollcommand=self.scrollbar.set)
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.input_frame = tk.Frame(
            self.chat_frame, bg=self.colors['container_bg'],
            highlightbackground=self.colors['border_subtle'],
            highlightthickness=1,
        )
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.input_entry = tk.Text(
            self.input_frame,
            font=('Helvetica Neue', 12),
            wrap=tk.WORD,
            bg=self.colors['input_bg'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary'],
            relief=tk.FLAT, bd=0,
            padx=14, pady=10,
            height=2,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 4), pady=8)

        send_frame = tk.Frame(self.input_frame, bg=self.colors['container_bg'])
        send_frame.pack(side=tk.RIGHT, padx=(0, 10), pady=8)

        self.send_btn = tk.Button(
            send_frame, text="Send",
            font=('Helvetica Neue', 11, 'bold'),
            bg=self.colors['accent_primary'],
            fg=self.colors['btn_primary_text'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['btn_primary_text'],
            bd=0, padx=18, pady=6, cursor='hand2',
            command=self._send_message,
        )
        self.send_btn.pack(side=tk.TOP)

        self._show_welcome()

    def _bind_keys(self):
        self.input_entry.bind('<Return>', self._on_return)
        self.input_entry.bind('<Shift-Return>', self._on_shift_return)
        self.input_entry.bind('<Command-Return>', self._on_return)
        self.root.bind('<Command-Return>', lambda e: self._send_message())
        self.root.bind('<Escape>', lambda e: self._hide_tools())
        self.input_entry.focus_set()

    def _show_welcome(self):
        self._append_text(
            "\n\n"
            "        ●\n\n"
            "    Generic Coder\n\n"
            "Autonomous agent ready to work.\n"
            "Open a workspace, connect to a\n"
            "server, upload files, or just\n"
            "start typing.\n\n",
            'empty',
        )

    def _append_text(self, text, tag=None, user=False):
        self.chat_display.configure(state=tk.NORMAL)

        if user:
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, '│  ' * 4, 'user_prefix')
            self.chat_display.insert(tk.END, text.rstrip() + "\n\n", 'user_msg')
        else:
            self.chat_display.insert(tk.END, text, tag or 'assistant_msg')

        self.chat_display.see(tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def _send_message(self):
        text = self.input_entry.get('1.0', tk.END).strip()
        if not text:
            return

        self.input_entry.delete('1.0', tk.END)

        if self.chat_display.get('1.0', '2.0').strip().startswith('●'):
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.delete('1.0', tk.END)
            self.chat_display.configure(state=tk.DISABLED)

        self._append_text(text, user=True)
        self.messages.append({
            'role': 'user', 'content': text,
            'time': datetime.now().isoformat(),
        })

        self.tool_status.configure(
            text="Processing...",
            fg=self.colors['accent_primary'],
        )
        if self.toolbar.winfo_ismapped():
            self.tool_status.configure(text="Processing...")
        else:
            self.toolbar.pack(side=tk.TOP, fill=tk.X, before=self.chat_frame)
            self.tool_status.configure(text="Processing...")

        threading.Thread(target=self._process_message, args=(text,), daemon=True).start()

    def _get_agent(self):
        with self._agent_lock:
            if self._agent is not None:
                return self._agent

            sys.path.insert(0, BASE_DIR)
            from agentmain import GeneraticAgent

            agent = GeneraticAgent()
            if getattr(agent, 'llmclient', None) is not None:
                threading.Thread(target=agent.run, daemon=True).start()
            self._agent = agent
            return agent

    def _process_message(self, text):
        try:
            agent = self._get_agent()
            if agent.llmclient is None:
                reply = "No LLM configured. Set up mykey.py with your API key."
            else:
                display_queue = agent.put_task(text, source='user')
                reply = ''
                while True:
                    item = display_queue.get()
                    if 'next' in item:
                        reply = item['next']
                    if 'done' in item:
                        reply = item['done']
                        break
                try:
                    from frontends.chatapp_common import build_done_text
                    reply = build_done_text(reply)
                except Exception:
                    reply = (reply or '').strip() or '...'
        except Exception as e:
            reply = f"Agent runtime error: {e}"

        self.messages.append({
            'role': 'assistant', 'content': reply,
            'time': datetime.now().isoformat(),
        })
        self.root.after(0, lambda: self._append_response(reply))

    def _append_response(self, reply):
        self._append_text('\n' + reply + '\n\n')
        self.tool_status.configure(text="", fg=self.colors['text_tertiary'])
        if self.toolbar.winfo_ismapped():
            self.toolbar.pack_forget()

    def _on_return(self, event):
        self._send_message()
        return 'break'

    def _on_shift_return(self, event):
        self.input_entry.insert(tk.INSERT, '\n')
        return 'break'

    def _hide_tools(self):
        if self.toolbar.winfo_ismapped():
            self.toolbar.pack_forget()
        self._tool = None

    def _on_theme_change(self, event=None):
        new = self.theme_var.get()
        if new != self.theme_name and new in THEME_MAP:
            self.theme_name = new
            self.colors = get_theme_tk(new)
            self._apply_full_theme()

    def _apply_full_theme(self):
        c = self.colors

        self.root.configure(bg=c['page_bg'])

        style = ttk.Style()
        style.configure(
            'TCombobox',
            fieldbackground=c['input_bg'],
            background=c['input_bg'],
            foreground=c['text_primary'],
            arrowcolor=c['text_secondary'],
            bordercolor=c['input_border'],
            selectbackground=c['selection_bg'],
            selectforeground=c['selection_text'],
        )
        style.map(
            'TCombobox',
            fieldbackground=[
                ('readonly', c['input_bg']),
                ('active', c['input_bg']),
            ],
            foreground=[
                ('readonly', c['text_primary']),
                ('active', c['text_primary']),
            ],
        )

        self.root.option_add('*TCombobox*Listbox.background', c['input_bg'])
        self.root.option_add('*TCombobox*Listbox.foreground', c['text_primary'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', c['accent_primary'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', c['text_inverse'])

        self.top_bar.configure(
            bg=c['titlebar_bg'],
            highlightbackground=c['titlebar_border'],
        )
        self.top_accent.configure(bg=c['titlebar_bg'], fg=c['accent_primary'])
        self.top_label.configure(bg=c['titlebar_bg'], fg=c['titlebar_text'])

        self.toolbar.configure(
            bg=c['container_bg'],
            highlightbackground=c['border_subtle'],
        )
        self.tool_status.configure(bg=c['container_bg'], fg=c['text_tertiary'])

        for btn in [self.tool_ws, self.tool_rm, self.tool_up]:
            btn.configure(
                bg=c['btn_secondary_bg'],
                fg=c['btn_secondary_text'],
                activebackground=c['btn_secondary_hover'],
                activeforeground=c['text_primary'],
            )

        self.chat_frame.configure(bg=c['page_bg'])

        self.chat_display.configure(
            bg=c['page_bg'], fg=c['text_primary'],
            insertbackground=c['accent_primary'],
            selectbackground=c['selection_bg'],
            selectforeground=c['selection_text'],
        )

        self.input_frame.configure(
            bg=c['container_bg'],
            highlightbackground=c['border_subtle'],
        )
        self.input_entry.configure(
            bg=c['input_bg'], fg=c['text_primary'],
            insertbackground=c['accent_primary'],
        )

        self.send_btn.configure(
            bg=c['accent_primary'],
            fg=c['btn_primary_text'],
            activebackground=c['accent_hover'],
            activeforeground=c['btn_primary_text'],
        )

        self.chat_display.tag_configure(
            'user_prefix',
            foreground=c['text_tertiary'],
            font=('Helvetica Neue', 10),
        )
        self.chat_display.tag_configure(
            'user_msg',
            foreground=c['text_primary'],
            font=('Helvetica Neue', 12),
        )
        self.chat_display.tag_configure(
            'assistant_msg',
            foreground=c['text_primary'],
            font=('Helvetica Neue', 12),
            lmargin1=10, lmargin2=10,
            background=c['chat_agent_bg'],
        )
        self.chat_display.tag_configure(
            'empty',
            foreground=c['text_muted'],
            font=('Helvetica Neue', 14),
            justify=tk.CENTER,
        )

        self.scrollbar.configure(
            bg=c['scrollbar_thumb'],
            troughcolor=c['scrollbar_track'],
            activebackground=c['scrollbar_hover'],
        )

    def _toggle_workspace(self):
        if self._tool == 'workspace':
            self._hide_tools()
            return
        self._tool = 'workspace'
        if not self.toolbar.winfo_ismapped():
            self.toolbar.pack(side=tk.TOP, fill=tk.X, before=self.chat_frame)
        self._show_workspace_dialog()

    def _show_workspace_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Open Workspace")
        dlg.geometry("420x140")
        dlg.configure(bg=self.colors['container_bg'])
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(
            dlg, text="Folder path:",
            font=('Helvetica Neue', 11),
            bg=self.colors['container_bg'],
            fg=self.colors['text_secondary'],
        ).pack(padx=16, pady=(16, 4), anchor=tk.W)

        entry_frame = tk.Frame(dlg, bg=self.colors['container_bg'])
        entry_frame.pack(fill=tk.X, padx=16)

        path_var = tk.StringVar(value=self.workspace_path)
        entry = tk.Entry(
            entry_frame, textvariable=path_var,
            font=('Helvetica Neue', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary'],
            relief=tk.FLAT, bd=0,
            highlightbackground=self.colors['input_border'],
            highlightthickness=1,
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        browse_btn = tk.Button(
            entry_frame, text="Browse",
            font=('Helvetica Neue', 10),
            bg=self.colors['btn_secondary_bg'],
            fg=self.colors['btn_secondary_text'],
            activebackground=self.colors['btn_secondary_hover'],
            activeforeground=self.colors['text_primary'],
            bd=0, padx=10, pady=4, cursor='hand2',
            command=lambda: path_var.set(
                filedialog.askdirectory(title="Select Folder")
                or path_var.get()
            ),
        )
        browse_btn.pack(side=tk.RIGHT)

        def open_it():
            p = os.path.abspath(os.path.expanduser(path_var.get()))
            if not os.path.isdir(p):
                messagebox.showerror("Error", f"Folder not found:\n{p}")
                return
            self.workspace_path = p
            dlg.destroy()
            self._hide_tools()
            try:
                from workspace import WorkspaceManager
                wm = WorkspaceManager()
                r = wm.open_folder(p)
                self.workspace_tree_data = r.get('tree')
                self._append_text(
                    f"\n📂 Workspace opened: `{p}`\n\n"
                )
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            dlg, text="Open",
            font=('Helvetica Neue', 11, 'bold'),
            bg=self.colors['accent_primary'],
            fg=self.colors['btn_primary_text'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['btn_primary_text'],
            bd=0, padx=24, pady=6, cursor='hand2',
            command=open_it,
        ).pack(pady=12)

        entry.bind('<Return>', lambda e: open_it())
        entry.focus_set()

    def _toggle_remote(self):
        if self._tool == 'remote':
            self._hide_tools()
            return
        self._tool = 'remote'
        if not self.toolbar.winfo_ismapped():
            self.toolbar.pack(side=tk.TOP, fill=tk.X, before=self.chat_frame)
        self._show_remote_dialog()

    def _show_remote_dialog(self):
        self._load_remote_configs()
        if not self.remote_configs:
            self._add_remote_dialog()
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Remote Servers")
        dlg.geometry("460x260")
        dlg.configure(bg=self.colors['container_bg'])
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(
            dlg, text="Select a server to connect:",
            font=('Helvetica Neue', 11),
            bg=self.colors['container_bg'],
            fg=self.colors['text_secondary'],
        ).pack(padx=16, pady=(16, 8), anchor=tk.W)

        list_frame = tk.Frame(dlg, bg=self.colors['surface_bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

        for cfg in self.remote_configs:
            nm = cfg.get('name', '')
            host = cfg.get('host', '')
            port = cfg.get('port', 22)

            row = tk.Frame(list_frame, bg=self.colors['surface_bg'])
            row.pack(fill=tk.X, pady=2)

            tk.Label(
                row, text=f"  {nm}  —  {host}:{port}",
                font=('Helvetica Neue', 10),
                bg=self.colors['surface_bg'],
                fg=self.colors['text_primary'],
            ).pack(side=tk.LEFT, padx=8, pady=4)

            btn = tk.Button(
                row, text="Connect",
                font=('Helvetica Neue', 9),
                bg=self.colors['btn_secondary_bg'],
                fg=self.colors['btn_secondary_text'],
                activebackground=self.colors['btn_secondary_hover'],
                activeforeground=self.colors['text_primary'],
                bd=0, padx=10, pady=2, cursor='hand2',
                command=lambda n=nm: self._connect_remote(n, dlg),
            )
            btn.pack(side=tk.RIGHT, padx=8, pady=4)

        bot_row = tk.Frame(dlg, bg=self.colors['container_bg'])
        bot_row.pack(fill=tk.X, padx=16, pady=(0, 12))

        tk.Button(
            bot_row, text="＋ Add Server",
            font=('Helvetica Neue', 10),
            bg=self.colors['container_bg'],
            fg=self.colors['accent_primary'],
            activebackground=self.colors['hover_bg'],
            activeforeground=self.colors['accent_hover'],
            bd=0, padx=10, pady=4, cursor='hand2',
            command=lambda: [dlg.destroy(), self._add_remote_dialog()],
        ).pack(side=tk.LEFT)

        tk.Button(
            bot_row, text="Cancel",
            font=('Helvetica Neue', 10),
            bg=self.colors['container_bg'],
            fg=self.colors['text_tertiary'],
            activebackground=self.colors['hover_bg'],
            activeforeground=self.colors['text_primary'],
            bd=0, padx=10, pady=4, cursor='hand2',
            command=lambda: [dlg.destroy(), self._hide_tools()],
        ).pack(side=tk.RIGHT)

    def _connect_remote(self, name, dlg=None):
        if dlg:
            dlg.destroy()
        self._hide_tools()

        try:
            from remoteserver import RemoteServerManager, _simple_decrypt
            mgr = RemoteServerManager()
            config_path = Path.home() / '.genericagent' / 'remote_config.json'
            configs = json.loads(config_path.read_text()) if config_path.exists() else []
            pw = ''
            for cfg in configs:
                if cfg.get('name') == name and cfg.get('_pwd'):
                    pw = _simple_decrypt(cfg['_pwd'])
                    break
            result = mgr.connect_to(name, pw)
            if result.get('status') == 'connected':
                self._append_text(f"\n✅ Connected to remote: **{name}**\n\n")
            else:
                messagebox.showerror(
                    "Connection Failed",
                    result.get('msg', 'Unknown error'),
                )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _add_remote_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Add Remote Server")
        dlg.geometry("380x290")
        dlg.configure(bg=self.colors['container_bg'])
        dlg.transient(self.root)
        dlg.grab_set()

        fields = [
            ("Name:", tk.StringVar()),
            ("Host:", tk.StringVar()),
            ("Port:", tk.StringVar(value="22")),
            ("User:", tk.StringVar(value="root")),
            ("Password:", tk.StringVar()),
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(
                dlg, text=label,
                font=('Helvetica Neue', 10),
                bg=self.colors['container_bg'],
                fg=self.colors['text_secondary'],
            ).grid(row=i, column=0, sticky=tk.W, padx=14, pady=5)

            show = '' if 'Password' not in label else '*'
            tk.Entry(
                dlg, textvariable=var, show=show,
                font=('Helvetica Neue', 10),
                bg=self.colors['input_bg'],
                fg=self.colors['text_primary'],
                insertbackground=self.colors['accent_primary'],
                relief=tk.FLAT, bd=0,
                highlightbackground=self.colors['input_border'],
                highlightthickness=1,
            ).grid(row=i, column=1, sticky=tk.EW, padx=(0, 14), pady=5)

        dlg.grid_columnconfigure(1, weight=1)

        def save():
            nm = fields[0][1].get()
            host = fields[1][1].get()
            try:
                port = int(fields[2][1].get())
            except ValueError:
                port = 22
            user = fields[3][1].get()
            password = fields[4][1].get()

            if not nm or not host:
                messagebox.showwarning("Missing", "Name and Host are required.")
                return
            try:
                from remoteserver import add_server_config
                add_server_config(nm, host, port, user, password)
                self._load_remote_configs()
                dlg.destroy()
                self._hide_tools()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            dlg, text="Save",
            font=('Helvetica Neue', 11, 'bold'),
            bg=self.colors['accent_primary'],
            fg=self.colors['btn_primary_text'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['btn_primary_text'],
            bd=0, padx=24, pady=6, cursor='hand2',
            command=save,
        ).grid(row=len(fields), column=0, columnspan=2, pady=16)

    def _upload_file(self):
        if self._tool == 'upload':
            self._hide_tools()
            return
        self._tool = 'upload'
        if not self.toolbar.winfo_ismapped():
            self.toolbar.pack(side=tk.TOP, fill=tk.X, before=self.chat_frame)

        path = filedialog.askopenfilename(
            title="Upload File",
            filetypes=[
                ("All supported",
                 "*.png *.jpg *.jpeg *.gif *.webp *.svg *.bmp "
                 "*.mp4 *.mov *.avi *.webm *.mkv "
                 "*.mp3 *.wav *.ogg *.flac *.m4a "
                 "*.pdf *.docx *.xlsx *.pptx *.csv "
                 "*.zip *.tar *.gz "
                 "*.py *.js *.ts *.go *.rs *.java *.md *.txt *.json *.yaml *.xml"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.webp *.svg *.bmp"),
                ("Video", "*.mp4 *.mov *.avi *.webm *.mkv"),
                ("Audio", "*.mp3 *.wav *.ogg *.flac *.m4a"),
                ("Documents", "*.pdf *.docx *.xlsx *.pptx *.csv"),
                ("All files", "*.*"),
            ],
        )
        self._hide_tools()

        if not path:
            return

        filename = os.path.basename(path)
        size = os.path.getsize(path)
        if size < 1024:
            sz = f'{size:,}B'
        elif size < 1024 * 1024:
            sz = f'{size/1024:.1f}KB'
        else:
            sz = f'{size/1024/1024:.1f}MB'

        self._append_text(f"📎 Uploaded: **{filename}** ({sz})\n\n")

        try:
            from media_handler import get_media_handler
            mh = get_media_handler()
            info = mh.get_file_info(path)
            if info and info.get('status') == 'success':
                mt = info.get('media_type', '')
                self._append_text(f"  Detected: {mt}\n")
                img = info.get('image', {})
                if img and img.get('width'):
                    self._append_text(
                        f"  Resolution: {img['width']}×{img['height']}\n"
                    )
                self._append_text("\n")
        except Exception:
            pass

    def _on_close(self):
        try:
            if self._agent is not None and getattr(self._agent, 'is_running', False):
                self._agent.abort()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = SoloChatApp()
    app.run()


if __name__ == '__main__':
    main()
