import os, sys, json, time, threading, socket, hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Callable, Generator, Dict, List, Any

_CONFIG_DIR = Path.home() / '.genericagent'
_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
_REMOTE_CONFIG_PATH = _CONFIG_DIR / 'remote_config.json'

@dataclass
class ConnectionConfig:
    name: str
    host: str
    port: int = 22
    username: str = 'root'
    auth_type: str = 'password'
    password_encrypted: str = ''
    key_path: str = ''
    jump_host: str = ''
    jump_port: int = 22
    jump_username: str = ''
    jump_password_encrypted: str = ''
    jump_key_path: str = ''
    last_connected: float = 0.0

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d.pop('password_encrypted', None)
        d.pop('jump_password_encrypted', None)
        return {k: v for k, v in d.items() if not k.endswith('_encrypted')}

def _derive_key() -> bytes:
    hostname = socket.gethostname()
    key_material = f"genericagent_remote_{hostname}_salt_v1"
    return hashlib.sha256(key_material.encode()).digest()

def _simple_encrypt(data: str) -> str:
    if not data:
        return ''
    from base64 import b64encode
    key = _derive_key()
    result = bytes(c ^ key[i % len(key)] for i, c in enumerate(data.encode()))
    return b64encode(result).decode()

def _simple_decrypt(encrypted: str) -> str:
    if not encrypted:
        return ''
    from base64 import b64decode
    key = _derive_key()
    result = bytearray(b64decode(encrypted))
    return bytes(c ^ key[i % len(key)] for i, c in enumerate(result)).decode()

def load_remote_config() -> List[dict]:
    if _REMOTE_CONFIG_PATH.exists():
        try:
            with open(_REMOTE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_remote_config(configs: List[dict]):
    with open(_REMOTE_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(configs, f, indent=2, ensure_ascii=False)

def add_server_config(name: str, host: str, port: int = 22, username: str = 'root',
                      password: str = '', key_path: str = '',
                      jump_host: str = '', jump_port: int = 22,
                      jump_username: str = '', jump_password: str = '') -> bool:
    configs = load_remote_config()
    for c in configs:
        if c.get('name') == name:
            c['host'] = host
            c['port'] = port
            c['username'] = username
            if password:
                c['_pwd'] = _simple_encrypt(password)
            c['key_path'] = key_path
            c['jump_host'] = jump_host
            c['jump_port'] = jump_port
            c['jump_username'] = jump_username
            if jump_password:
                c['_jpwd'] = _simple_encrypt(jump_password)
            save_remote_config(configs)
            return True
    entry = {
        'name': name, 'host': host, 'port': port,
        'username': username, 'key_path': key_path,
        'jump_host': jump_host, 'jump_port': jump_port,
        'jump_username': jump_username,
    }
    if password:
        entry['_pwd'] = _simple_encrypt(password)
    if jump_password:
        entry['_jpwd'] = _simple_encrypt(jump_password)
    configs.append(entry)
    save_remote_config(configs)
    return True

def remove_server_config(name: str) -> bool:
    configs = load_remote_config()
    new_configs = [c for c in configs if c.get('name') != name]
    if len(new_configs) != len(configs):
        save_remote_config(new_configs)
        return True
    return False

try:
    import paramiko
    from paramiko import SSHClient, AutoAddPolicy, RSAKey, Ed25519Key
    _PARAMIKO_AVAILABLE = True
except ImportError:
    _PARAMIKO_AVAILABLE = False

if not _PARAMIKO_AVAILABLE:
    import subprocess as _sp
    import tempfile as _tmp

class RemoteServerConnection:
    def __init__(self):
        self._client = None
        self._sftp = None
        self._config = None
        self._connected = False
        self._lock = threading.Lock()

    def connect(self, host: str, port: int = 22, username: str = 'root',
                password: str = '', key_path: str = '',
                jump_host: str = '', jump_port: int = 22,
                jump_username: str = '', jump_password: str = '') -> dict:
        with self._lock:
            if self._connected:
                self.disconnect()
            self._config = {
                'host': host, 'port': port, 'username': username,
                'key_path': key_path, 'jump_host': jump_host,
                'jump_port': jump_port, 'jump_username': jump_username,
            }
            if not _PARAMIKO_AVAILABLE:
                test_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                           '-o', 'ConnectTimeout=5', '-o', 'BatchMode=yes']
                if port != 22:
                    test_cmd += ['-p', str(port)]
                if key_path:
                    test_cmd += ['-i', key_path]
                test_cmd += [f'{username}@{host}', 'echo', 'OK']
                try:
                    result = _sp.run(test_cmd, capture_output=True, text=True, timeout=10,
                                    env={**os.environ, 'SSHPASS': password} if password else None)
                    if result.returncode == 0 and 'OK' in result.stdout:
                        self._connected = True
                        return {'status': 'connected', 'host': host, 'method': 'openssh_cli'}
                    return {'status': 'error', 'msg': f'SSH connection failed: {result.stderr.strip()}'}
                except Exception as e:
                    return {'status': 'error', 'msg': str(e)}

            try:
                self._client = SSHClient()
                self._client.set_missing_host_key_policy(AutoAddPolicy())

                connect_kwargs = {
                    'hostname': host, 'port': port,
                    'username': username, 'timeout': 10,
                    'allow_agent': True, 'look_for_keys': True,
                }

                jump_channel = None
                if jump_host:
                    jump_client = SSHClient()
                    jump_client.set_missing_host_key_policy(AutoAddPolicy())
                    jump_kwargs = {
                        'hostname': jump_host, 'port': jump_port,
                        'username': jump_username, 'timeout': 10,
                    }
                    if jump_password:
                        jump_kwargs['password'] = jump_password
                    jump_client.connect(**jump_kwargs)
                    jump_transport = jump_client.get_transport()
                    dest_addr = (host, port)
                    jump_channel = jump_transport.open_channel(
                        'direct-tcpip', dest_addr, ('', 0))
                    connect_kwargs['sock'] = jump_channel
                    connect_kwargs['hostname'] = host
                    connect_kwargs['port'] = port

                if password:
                    connect_kwargs['password'] = password
                elif key_path:
                    if key_path.endswith('.pem'):
                        try:
                            connect_kwargs['key_filename'] = key_path
                        except Exception:
                            with open(key_path, 'r') as f:
                                key_data = f.read()
                            from io import StringIO
                            connect_kwargs['pkey'] = RSAKey.from_private_key(StringIO(key_data))
                    else:
                        connect_kwargs['key_filename'] = key_path

                self._client.connect(**connect_kwargs)
                self._sftp = self._client.open_sftp()
                self._connected = True
                add_server_config(
                    name=f'{username}@{host}', host=host, port=port,
                    username=username, password=password,
                    key_path=key_path, jump_host=jump_host,
                    jump_port=jump_port, jump_username=jump_username,
                    jump_password=jump_password)
                return {'status': 'connected', 'host': host, 'method': 'paramiko'}
            except Exception as e:
                self._client = None
                self._sftp = None
                return {'status': 'error', 'msg': str(e)}

    def disconnect(self):
        with self._lock:
            try:
                if self._sftp:
                    self._sftp.close()
            except Exception:
                pass
            try:
                if self._client:
                    self._client.close()
            except Exception:
                pass
            self._client = None
            self._sftp = None
            self._connected = False

    def is_connected(self) -> bool:
        if not self._connected:
            return False
        if _PARAMIKO_AVAILABLE and self._client:
            try:
                t = self._client.get_transport()
                if t and t.is_active():
                    return True
            except Exception:
                pass
            self._connected = False
            return False
        return self._connected

    def exec_command(self, command: str, timeout: int = 60, cwd: str = '') -> Generator[str, None, dict]:
        if not self.is_connected():
            yield '[Error] Not connected to any server\n'
            return {'status': 'error', 'msg': 'Not connected'}

        full_cmd = command
        if cwd:
            full_cmd = f'cd "{cwd}" && {command}'

        if not _PARAMIKO_AVAILABLE:
            host = self._config['host']
            username = self._config['username']
            port = self._config['port']
            key_path = self._config.get('key_path', '')

            ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                      '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=30']
            if port != 22:
                ssh_cmd += ['-p', str(port)]
            if key_path:
                ssh_cmd += ['-i', key_path]
            ssh_cmd += [f'{username}@{host}', full_cmd]

            yield f'[Remote] Executing: {command}\n'
            try:
                proc = _sp.Popen(ssh_cmd, stdout=_sp.PIPE, stderr=_sp.STDOUT,
                                text=True, bufsize=1)
                output_lines = []
                for line in proc.stdout:
                    output_lines.append(line)
                    yield line
                proc.wait(timeout=timeout)
                exit_code = proc.returncode
                result = {
                    'status': 'success' if exit_code == 0 else 'error',
                    'stdout': ''.join(output_lines),
                    'exit_code': exit_code
                }
                yield f'\n[Remote] Exit Code: {exit_code}\n'
                return result
            except _sp.TimeoutExpired:
                proc.kill()
                return {'status': 'error', 'msg': 'Command timed out'}
            except Exception as e:
                return {'status': 'error', 'msg': str(e)}

        yield f'[Remote] Executing: {command}\n'
        try:
            transport = self._client.get_transport()
            channel = transport.open_session()
            channel.settimeout(timeout)
            if cwd:
                channel.exec_command(full_cmd)
            else:
                channel.exec_command(command)

            output_lines = []
            stdout = channel.makefile('r', -1)
            stderr = channel.makefile_stderr('r', -1)

            for line in iter(stdout.readline, ''):
                output_lines.append(line)
                yield line

            stderr_output = stderr.read()
            if stderr_output:
                output_lines.append(stderr_output)
                yield stderr_output

            exit_code = channel.recv_exit_status()
            result = {
                'status': 'success' if exit_code == 0 else 'error',
                'stdout': ''.join(output_lines),
                'exit_code': exit_code
            }
            yield f'\n[Remote] Exit Code: {exit_code}\n'
            return result
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def remote_read(self, path: str) -> dict:
        if not self.is_connected():
            return {'status': 'error', 'msg': 'Not connected'}

        if not _PARAMIKO_AVAILABLE:
            host = self._config['host']
            username = self._config['username']
            port = self._config['port']
            key_path = self._config.get('key_path', '')
            ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10']
            if port != 22:
                ssh_cmd += ['-p', str(port)]
            if key_path:
                ssh_cmd += ['-i', key_path]
            ssh_cmd += [f'{username}@{host}', 'cat', f'"{path}"']
            try:
                result = _sp.run(ssh_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return {'status': 'error', 'msg': result.stderr.strip() or 'File not found'}
                return {'status': 'success', 'content': result.stdout}
            except Exception as e:
                return {'status': 'error', 'msg': str(e)}

        try:
            with self._sftp.open(path, 'r') as f:
                content = f.read().decode('utf-8', errors='replace')
            return {'status': 'success', 'content': content}
        except UnicodeDecodeError:
            try:
                with self._sftp.open(path, 'rb') as f:
                    content = f.read()
                return {'status': 'success', 'binary': True,
                       'size': len(content), 'preview': str(content[:200])}
            except Exception as e:
                return {'status': 'error', 'msg': str(e)}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def remote_write(self, path: str, content: str) -> dict:
        if not self.is_connected():
            return {'status': 'error', 'msg': 'Not connected'}

        if not _PARAMIKO_AVAILABLE:
            host = self._config['host']
            username = self._config['username']
            port = self._config['port']
            key_path = self._config.get('key_path', '')
            escaped = content.replace("'", "'\\''")
            ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10']
            if port != 22:
                ssh_cmd += ['-p', str(port)]
            if key_path:
                ssh_cmd += ['-i', key_path]
            ssh_cmd += [f'{username}@{host}', 'bash', '-c',
                       f"cat > '{path}' << 'GAEOF'\n{content}\nGAEOF"]
            try:
                result = _sp.run(ssh_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return {'status': 'error', 'msg': result.stderr.strip()}
                return {'status': 'success', 'path': path}
            except Exception as e:
                return {'status': 'error', 'msg': str(e)}

        try:
            dir_path = os.path.dirname(path)
            if dir_path:
                try:
                    self._sftp.stat(dir_path)
                except FileNotFoundError:
                    self.exec_command_sync(f'mkdir -p "{dir_path}"')

            with self._sftp.open(path, 'w') as f:
                f.write(content)
            return {'status': 'success', 'path': path}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def remote_list_dir(self, path: str = '.') -> dict:
        if not self.is_connected():
            return {'status': 'error', 'msg': 'Not connected'}

        if not _PARAMIKO_AVAILABLE:
            host = self._config['host']
            username = self._config['username']
            port = self._config['port']
            key_path = self._config.get('key_path', '')
            ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10']
            if port != 22:
                ssh_cmd += ['-p', str(port)]
            if key_path:
                ssh_cmd += ['-i', key_path]
            ssh_cmd += [f'{username}@{host}', 'ls', '-la', '--time-style=+%s', f'"{path}"']
            try:
                result = _sp.run(ssh_cmd, capture_output=True, text=True, timeout=15)
                items = []
                for line in result.stdout.strip().split('\n')[1:]:
                    parts = line.split()
                    if len(parts) >= 7:
                        is_dir = parts[0].startswith('d')
                        items.append({
                            'name': ' '.join(parts[6:]),
                            'type': 'directory' if is_dir else 'file',
                            'size': int(parts[4]) if parts[4].isdigit() else 0,
                            'modified': float(parts[5]) if parts[5].isdigit() else 0,
                        })
                return {'status': 'success', 'items': items, 'path': path}
            except Exception as e:
                return {'status': 'error', 'msg': str(e)}

        try:
            attrs = self._sftp.listdir_attr(path)
            items = []
            for attr in attrs:
                items.append({
                    'name': attr.filename,
                    'type': 'directory' if attr.st_mode & 0o40000 else 'file',
                    'size': attr.st_size,
                    'modified': attr.st_mtime,
                })
            return {'status': 'success', 'items': items, 'path': path}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def remote_delete(self, path: str) -> dict:
        if not self.is_connected():
            return {'status': 'error', 'msg': 'Not connected'}

        if not _PARAMIKO_AVAILABLE:
            return self.exec_command_sync(f'rm -rf "{path}"')

        try:
            try:
                self._sftp.stat(path)
            except FileNotFoundError:
                return {'status': 'error', 'msg': f'Path not found: {path}'}

            s = self._sftp.stat(path)
            if s.st_mode & 0o40000:
                self._rmtree_sftp(path)
            else:
                self._sftp.remove(path)
            return {'status': 'success', 'path': path}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def remote_stat(self, path: str) -> dict:
        if not self.is_connected():
            return {'status': 'error', 'msg': 'Not connected'}

        if not _PARAMIKO_AVAILABLE:
            host = self._config['host']
            username = self._config['username']
            port = self._config['port']
            key_path = self._config.get('key_path', '')
            ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10']
            if port != 22:
                ssh_cmd += ['-p', str(port)]
            if key_path:
                ssh_cmd += ['-i', key_path]
            ssh_cmd += [f'{username}@{host}', 'stat', '--format=%F|%s|%Y|%a', f'"{path}"']
            try:
                result = _sp.run(ssh_cmd, capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    return {'status': 'error', 'msg': 'File not found'}
                parts = result.stdout.strip().split('|')
                return {
                    'status': 'success',
                    'type': 'directory' if 'directory' in parts[0] else 'file',
                    'size': int(parts[1]) if len(parts) > 1 else 0,
                    'modified': float(parts[2]) if len(parts) > 2 else 0,
                    'permissions': parts[3] if len(parts) > 3 else ''
                }
            except Exception as e:
                return {'status': 'error', 'msg': str(e)}

        try:
            s = self._sftp.stat(path)
            return {
                'status': 'success',
                'type': 'directory' if s.st_mode & 0o40000 else 'file',
                'size': s.st_size,
                'modified': s.st_mtime,
                'permissions': oct(s.st_mode)[-3:]
            }
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def upload_file(self, local_path: str, remote_path: str,
                    progress_callback: Optional[Callable] = None) -> dict:
        if not self.is_connected():
            return {'status': 'error', 'msg': 'Not connected'}

        if not os.path.exists(local_path):
            return {'status': 'error', 'msg': f'Local file not found: {local_path}'}

        if not _PARAMIKO_AVAILABLE:
            host = self._config['host']
            username = self._config['username']
            port = self._config['port']
            key_path = self._config.get('key_path', '')
            scp_cmd = ['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=30']
            if port != 22:
                scp_cmd += ['-P', str(port)]
            if key_path:
                scp_cmd += ['-i', key_path]
            scp_cmd += [local_path, f'{username}@{host}:{remote_path}']
            try:
                result = _sp.run(scp_cmd, capture_output=True, text=True, timeout=120)
                if result.returncode != 0:
                    return {'status': 'error', 'msg': result.stderr.strip()}
                return {'status': 'success', 'local': local_path, 'remote': remote_path}
            except Exception as e:
                return {'status': 'error', 'msg': str(e)}

        try:
            dir_path = os.path.dirname(remote_path)
            if dir_path:
                try:
                    self._sftp.stat(dir_path)
                except FileNotFoundError:
                    self.exec_command_sync(f'mkdir -p "{dir_path}"')

            total_size = os.path.getsize(local_path)
            transferred = [0]

            def _progress(transferred_bytes, total_bytes):
                transferred[0] = transferred_bytes
                if progress_callback:
                    progress_callback(transferred_bytes, total_bytes)

            self._sftp.put(local_path, remote_path, callback=_progress)
            return {'status': 'success', 'local': local_path, 'remote': remote_path,
                   'size': total_size}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def download_file(self, remote_path: str, local_path: str,
                      progress_callback: Optional[Callable] = None) -> dict:
        if not self.is_connected():
            return {'status': 'error', 'msg': 'Not connected'}

        local_dir = os.path.dirname(local_path)
        if local_dir:
            os.makedirs(local_dir, exist_ok=True)

        if not _PARAMIKO_AVAILABLE:
            host = self._config['host']
            username = self._config['username']
            port = self._config['port']
            key_path = self._config.get('key_path', '')
            scp_cmd = ['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=30']
            if port != 22:
                scp_cmd += ['-P', str(port)]
            if key_path:
                scp_cmd += ['-i', key_path]
            scp_cmd += [f'{username}@{host}:{remote_path}', local_path]
            try:
                result = _sp.run(scp_cmd, capture_output=True, text=True, timeout=120)
                if result.returncode != 0:
                    return {'status': 'error', 'msg': result.stderr.strip()}
                return {'status': 'success', 'remote': remote_path, 'local': local_path}
            except Exception as e:
                return {'status': 'error', 'msg': str(e)}

        try:
            self._sftp.get(remote_path, local_path, callback=progress_callback)
            return {'status': 'success', 'remote': remote_path, 'local': local_path}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def exec_command_sync(self, command: str, timeout: int = 60, cwd: str = '') -> dict:
        gen = self.exec_command(command, timeout=timeout, cwd=cwd)
        result = None
        for _ in gen:
            pass
        return result or {'status': 'error', 'msg': 'Unknown error'}

    def _rmtree_sftp(self, path: str):
        for item in self._sftp.listdir_attr(path):
            item_path = f'{path}/{item.filename}'
            if item.st_mode & 0o40000:
                self._rmtree_sftp(item_path)
            else:
                self._sftp.remove(item_path)
        self._sftp.rmdir(path)


class RemoteServerManager:
    def __init__(self):
        self.connections: Dict[str, RemoteServerConnection] = {}
        self._lock = threading.Lock()

    def list_configs(self) -> list:
        configs = load_remote_config()
        return [{'name': c.get('name'), 'host': c.get('host'),
                 'port': c.get('port'), 'username': c.get('username')}
                for c in configs]

    def connect_to(self, name: str, password: str = '') -> dict:
        configs = load_remote_config()
        config = None
        for c in configs:
            if c.get('name') == name:
                config = c
                break
        if not config:
            return {'status': 'error', 'msg': f'Server config "{name}" not found'}

        pwd = password
        if not pwd and config.get('_pwd'):
            try:
                pwd = _simple_decrypt(config['_pwd'])
            except Exception:
                pass

        jump_pwd = ''
        if config.get('_jpwd'):
            try:
                jump_pwd = _simple_decrypt(config['_jpwd'])
            except Exception:
                pass

        conn = RemoteServerConnection()
        result = conn.connect(
            host=config['host'], port=config.get('port', 22),
            username=config.get('username', 'root'), password=pwd,
            key_path=config.get('key_path', ''),
            jump_host=config.get('jump_host', ''),
            jump_port=config.get('jump_port', 22),
            jump_username=config.get('jump_username', ''),
            jump_password=jump_pwd)

        if result.get('status') == 'connected':
            self.connections[name] = conn
        return result

    def disconnect_from(self, name: str):
        conn = self.connections.pop(name, None)
        if conn:
            conn.disconnect()

    def get_connection(self, name: str) -> Optional[RemoteServerConnection]:
        return self.connections.get(name)

    def is_connected_to(self, name: str) -> bool:
        conn = self.connections.get(name)
        return conn is not None and conn.is_connected()

    def list_active_connections(self) -> list:
        return [name for name, conn in self.connections.items() if conn.is_connected()]

    def disconnect_all(self):
        for name in list(self.connections.keys()):
            self.disconnect_from(name)
