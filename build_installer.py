import os, sys, shutil, json, platform, subprocess, textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
DIST_DIR = PROJECT_ROOT / 'dist'
BUILD_DIR = PROJECT_ROOT / 'build'

APP_NAME = 'Generic Coder'
VERSION = '0.2.0'
BUNDLE_ID = 'com.genericcoder.app'

ICON_SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" fill="none">
  <defs>
        <linearGradient id="bg" x1="28" y1="20" x2="220" y2="236" gradientUnits="userSpaceOnUse">
            <stop offset="0%" style="stop-color:#FFF6E8"/>
            <stop offset="100%" style="stop-color:#FFD6A8"/>
    </linearGradient>
        <linearGradient id="star" x1="68" y1="40" x2="188" y2="216" gradientUnits="userSpaceOnUse">
            <stop offset="0%" style="stop-color:#FFB45A"/>
            <stop offset="55%" style="stop-color:#FF7A00"/>
            <stop offset="100%" style="stop-color:#F14D00"/>
        </linearGradient>
  </defs>
  <rect width="256" height="256" rx="48" fill="url(#bg)"/>
    <path d="M128 46L146 110L210 128L146 146L128 210L110 146L46 128L110 110L128 46Z" fill="#FF8E1A" opacity="0.32"/>
    <path d="M128 46L146 110L210 128L146 146L128 210L110 146L46 128L110 110L128 46Z" fill="url(#star)"/>
    <path d="M128 67L141 115L189 128L141 141L128 189L115 141L67 128L115 115L128 67Z" fill="#FFE5C2" fill-opacity="0.82"/>
    <circle cx="128" cy="128" r="15" fill="#23130B" fill-opacity="0.16"/>
</svg>'''


def ensure_pyinstaller():
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        commands = [
            [sys.executable, '-m', 'pip', 'install', 'pyinstaller>=6.0'],
            [sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages', 'pyinstaller>=6.0'],
        ]
        last_error = None
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True)
                return
            except subprocess.CalledProcessError as exc:
                last_error = exc
        raise last_error


def ensure_tkinter():
    try:
        import tkinter  # noqa: F401
        return True
    except Exception as exc:
        print(f"❌ Tkinter is unavailable in this Python runtime: {exc}")
        print("   Standalone desktop builds require a Python distribution with Tk support.")
        return False


def clean_build():
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
    spec_files = list(PROJECT_ROOT.glob('*.spec'))
    for f in spec_files:
        f.unlink()


def _build_icon():
    icon_dir = BUILD_DIR / 'icons'
    icon_dir.mkdir(parents=True, exist_ok=True)
    icon_svg_path = icon_dir / 'app_icon.svg'
    with open(icon_svg_path, 'w') as f:
        f.write(ICON_SVG)
    return icon_dir, icon_svg_path


def _make_icns(icon_dir, icon_svg_path):
    iconset = icon_dir / 'app_icon.iconset'
    iconset.mkdir(exist_ok=True)
    sizes = [16, 32, 64, 128, 256, 512]
    for s in sizes:
        out_path = iconset / f'icon_{s}x{s}.png'
        subprocess.run([
            'sips', '-s', 'format', 'png', '-z', str(s), str(s),
            str(icon_svg_path), '--out', str(out_path)
        ], capture_output=True)
        out_2x = iconset / f'icon_{s}x{s}@2x.png'
        subprocess.run([
            'sips', '-s', 'format', 'png', '-z', str(s*2), str(s*2),
            str(icon_svg_path), '--out', str(out_2x)
        ], capture_output=True)
    icns_path = icon_dir / 'app_icon.icns'
    subprocess.run(['iconutil', '-c', 'icns', str(iconset), '-o', str(icns_path)], capture_output=True)
    return icns_path


def _make_ico(icon_dir, icon_svg_path):
    try:
        subprocess.run([
            'convert', str(icon_svg_path),
            '-resize', '256x256', str(icon_dir / 'app_icon.ico')
        ], capture_output=True, check=True)
        return str(icon_dir / 'app_icon.ico')
    except Exception:
        print("⚠️  Could not generate .ico, using default icon")
        return ''


def _patch_plist(app_bundle):
    plist_path = app_bundle / 'Contents' / 'Info.plist'
    if plist_path.exists():
        import plistlib
        with open(plist_path, 'rb') as f:
            plist = plistlib.load(f)
        plist['CFBundleShortVersionString'] = VERSION
        plist['CFBundleVersion'] = VERSION
        plist['NSHighResolutionCapable'] = True
        with open(plist_path, 'wb') as f:
            plistlib.dump(plist, f)


def _create_dmg(app_bundle):
    dmg_path = DIST_DIR / f'{APP_NAME}-{VERSION}.dmg'
    subprocess.run(['hdiutil', 'create', '-volname', APP_NAME,
                   '-srcfolder', str(app_bundle), '-ov', '-format', 'UDZO',
                   str(dmg_path)], capture_output=True)
    if dmg_path.exists():
        print(f"✅ DMG created: {dmg_path}")
    return dmg_path.exists()


def _create_macos_pkg(app_bundle):
    pkg_path = DIST_DIR / f'{APP_NAME}-{VERSION}.pkg'
    result = subprocess.run([
        'productbuild', '--component', str(app_bundle), '/Applications', str(pkg_path)
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠️  Could not create .pkg installer")
        if result.stderr:
            print(result.stderr.strip())
        return False
    if pkg_path.exists():
        print(f"✅ PKG created: {pkg_path}")
        return True
    return False


def _find_dist_app_dir():
    app_dir = DIST_DIR / APP_NAME
    return app_dir if app_dir.exists() else None


def _find_windows_executable():
    app_dir = _find_dist_app_dir()
    if not app_dir:
        return None, None
    exe_path = app_dir / f'{APP_NAME}.exe'
    if exe_path.exists():
        return app_dir, exe_path
    return app_dir, None


def _create_windows_installer_script(app_dir, suffix='win64'):
    script_path = DIST_DIR / f'{APP_NAME}-{VERSION}-{suffix}.iss'
    source_dir = str(app_dir).replace('\\', '\\\\')
    setup_icon = str((BUILD_DIR / 'icons' / 'app_icon.ico')).replace('\\', '\\\\')
    output_base = f'{APP_NAME}-{VERSION}-setup-{suffix}'
    icon_block = f'SetupIconFile={setup_icon}\n' if setup_icon and Path(setup_icon).exists() else ''
    content = textwrap.dedent(f'''
        #define MyAppName "{APP_NAME}"
        #define MyAppVersion "{VERSION}"
        #define MyAppPublisher "Generic Coder"
        #define MyAppExeName "{APP_NAME}.exe"

        [Setup]
        AppId={{{{{BUNDLE_ID}}}}}
        AppName={{#MyAppName}}
        AppVersion={{#MyAppVersion}}
        AppPublisher={{#MyAppPublisher}}
        DefaultDirName={{autopf}}\\{{#MyAppName}}
        DefaultGroupName={{#MyAppName}}
        DisableProgramGroupPage=yes
        OutputDir={str(DIST_DIR).replace('\\', '\\\\')}
        OutputBaseFilename={output_base}
        Compression=lzma
        SolidCompression=yes
        WizardStyle=modern
        ArchitecturesInstallIn64BitMode=x64compatible
        PrivilegesRequired=admin
        UninstallDisplayIcon={{app}}\\{{#MyAppExeName}}
        {icon_block.rstrip()}

        [Languages]
        Name: "english"; MessagesFile: "compiler:Default.isl"

        [Tasks]
        Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

        [Files]
        Source: "{source_dir}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

        [Icons]
        Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
        Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

        [Run]
        Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "Launch {{#MyAppName}}"; Flags: nowait postinstall skipifsilent
    ''').strip() + '\n'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Inno Setup script created: {script_path}")
    return script_path


def _find_inno_setup_compiler():
    candidates = [
        shutil.which('iscc'),
        shutil.which('ISCC.exe'),
        r'C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe',
        r'C:\\Program Files\\Inno Setup 6\\ISCC.exe',
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def _find_makensis_compiler():
    return shutil.which('makensis')


def _prepare_windows_source_payload():
    payload_dir = BUILD_DIR / 'windows-source-payload'
    if payload_dir.exists():
        shutil.rmtree(payload_dir)
    shutil.copytree(
        PROJECT_ROOT,
        payload_dir,
        ignore=shutil.ignore_patterns(
            '.git', 'build', 'dist', '.venv', '__pycache__', '.pytest_cache', 'temp',
            '*.pyc', '.DS_Store'
        ),
    )
    return payload_dir


def _create_windows_nsis_script(source_root: Path, output_name='Generic Coder-0.2.0-setup-win64.exe', output_dir: Path | None = None):
    script_path = BUILD_DIR / 'windows-source-installer.nsi'
    icon_dir, icon_svg = _build_icon()
    icon_path = _make_ico(icon_dir, icon_svg)
    icon_block = ''
    if icon_path and Path(icon_path).exists():
        icon_block = f'Icon "{Path(icon_path).as_posix()}"\n'
    actual_output_dir = output_dir or DIST_DIR
    script = textwrap.dedent(f'''
        Unicode True
        Name "{APP_NAME}"
        OutFile "{(actual_output_dir / output_name).as_posix()}"
        RequestExecutionLevel user
        ShowInstDetails show
        SetCompressor /SOLID lzma
        {icon_block.rstrip()}

        Page instfiles

        Section "Install"
          InitPluginsDir
          SetOutPath "$PLUGINSDIR\\payload"
          File /r "{source_root.as_posix()}/*"
          DetailPrint "Running Generic Coder Windows bootstrap installer..."
          ExecWait '"$SYSDIR\\cmd.exe" /c ""$PLUGINSDIR\\payload\\assets\\install-windows-app.bat" --embedded"' $0
          IntCmp $0 0 done failed failed
          failed:
            MessageBox MB_ICONSTOP|MB_OK "Generic Coder setup failed with exit code $0."
            Abort
          done:
        SectionEnd
    ''').strip() + '\n'
    script_path.parent.mkdir(parents=True, exist_ok=True)
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    return script_path


def _docker_available():
    try:
        result = subprocess.run(
            ['docker', 'info', '--format', '{{.ServerVersion}}'],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except Exception:
        return False


def _compile_nsis_installer(script_path: Path):
    compiler = _find_makensis_compiler()
    if compiler:
        return subprocess.run([compiler, str(script_path)], cwd=str(PROJECT_ROOT)).returncode == 0
    if not _docker_available():
        print('⚠️  NSIS compiler not available and Docker is not running.')
        return False
    docker_script = f'/workspace/{script_path.relative_to(PROJECT_ROOT).as_posix()}'
    result = subprocess.run([
        'docker', 'run', '--rm',
        '-v', f'{PROJECT_ROOT}:/workspace',
        '-w', '/workspace',
        'ubuntu:24.04',
        'sh', '-lc',
        f'apt-get update >/dev/null && DEBIAN_FRONTEND=noninteractive apt-get install -y nsis >/dev/null && makensis "{docker_script}"'
    ], cwd=str(PROJECT_ROOT))
    return result.returncode == 0


def build_windows_source_installer():
    print('🪟 Building Windows source installer (setup.exe via NSIS)...')
    payload_dir = _prepare_windows_source_payload()
    output_name = f'{APP_NAME}-{VERSION}-setup-win64-source.exe'
    compiler = _find_makensis_compiler()
    if compiler:
        script_path = _create_windows_nsis_script(payload_dir, output_name=output_name)
    elif _docker_available():
        docker_payload_dir = Path('/workspace') / payload_dir.relative_to(PROJECT_ROOT)
        docker_output_dir = Path('/workspace') / DIST_DIR.relative_to(PROJECT_ROOT)
        script_path = _create_windows_nsis_script(
            docker_payload_dir,
            output_name=output_name,
            output_dir=docker_output_dir,
        )
    else:
        print('❌ Neither makensis nor Docker is available for building the Windows installer.')
        return False
    if not _compile_nsis_installer(script_path):
        print('❌ Windows source installer build failed')
        return False
    installer_path = DIST_DIR / output_name
    if installer_path.exists():
        print(f'✅ Windows source installer created: {installer_path}')
        return True
    print('❌ Windows source installer not found')
    return False


def _compile_windows_installer(script_path):
    compiler = _find_inno_setup_compiler()
    if not compiler:
        print('⚠️  Inno Setup compiler not found. Generated .iss script for building on Windows later.')
        return False
    result = subprocess.run([compiler, str(script_path)], cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print('⚠️  Inno Setup compilation failed')
        return False
    setup_path = DIST_DIR / f'{APP_NAME}-{VERSION}-setup-win64.exe'
    if setup_path.exists():
        print(f'✅ Windows installer created: {setup_path}')
        return True
    matches = sorted(DIST_DIR.glob(f'{APP_NAME}-{VERSION}-setup-*.exe'))
    if matches:
        print(f'✅ Windows installer created: {matches[-1]}')
        return True
    return False


def _create_zip_archive(app_dir, suffix='win64'):
    import zipfile
    zip_path = DIST_DIR / f'{APP_NAME}-{VERSION}-{suffix}.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if app_dir.exists():
            for root, dirs, files in os.walk(app_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    zf.write(fp, os.path.relpath(fp, str(app_dir)))
    print(f"✅ ZIP archive created: {zip_path}")
    return zip_path.exists()


def _create_tarball(binary_path):
    import tarfile
    desktop_entry = f"""[Desktop Entry]
Name={APP_NAME}
Comment=Self-evolving autonomous agent
Exec={APP_NAME}
Icon={APP_NAME}
Type=Application
Categories=Development;Utility;
"""
    desktop_file = BUILD_DIR / f'{APP_NAME}.desktop'
    with open(desktop_file, 'w') as f:
        f.write(desktop_entry)
    tar_path = DIST_DIR / f'{APP_NAME}-{VERSION}-linux-x64.tar.gz'
    with tarfile.open(tar_path, 'w:gz') as tf:
        tf.add(str(binary_path), f'{APP_NAME}/{APP_NAME}')
        tf.add(str(desktop_file), f'{APP_NAME}/{APP_NAME}.desktop')
    print(f"✅ Tarball created: {tar_path}")
    return tar_path.exists()


# ── Bottle + pywebview app builds ────────────────────────────────────────

_WEBAPP_SCRIPT = PROJECT_ROOT / 'launch.pyw'

_WEBAPP_IMPORTS = [
    'webview', 'bottle', 'PIL', 'watchfiles', 'paramiko',
    'PyPDF2', 'pdfplumber', 'docx', 'openpyxl', 'pptx',
    'simple_websocket_server', 'bs4', 'requests',
]


def build_macos_app():
    print("🍎 Building macOS app bundle (Generic Coder web app)...")
    icon_dir, icon_svg = _build_icon()
    icns_path = _make_icns(icon_dir, icon_svg)

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', APP_NAME,
        '--windowed',
        '--icon', str(icns_path),
        '--add-data', f'{PROJECT_ROOT / "frontends"}:frontends',
        '--add-data', f'{PROJECT_ROOT / "assets"}:assets',
        '--add-data', f'{PROJECT_ROOT / "memory"}:memory',
        '--osx-bundle-identifier', BUNDLE_ID,
        '--noconfirm', '--clean',
    ]
    for hi in _WEBAPP_IMPORTS:
        cmd.extend(['--hidden-import', hi])
    cmd.append(str(_WEBAPP_SCRIPT))

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("❌ macOS build failed")
        return False

    app_bundle = DIST_DIR / f'{APP_NAME}.app'
    if app_bundle.exists():
        _patch_plist(app_bundle)
        print(f"✅ macOS app built: {app_bundle}")
        _create_macos_pkg(app_bundle)
        _create_dmg(app_bundle)
        return True

    print("❌ App bundle not found")
    return False


def build_windows_exe():
    print("🪟 Building Windows executable (Generic Coder web app)...")
    icon_dir, icon_svg = _build_icon()
    icon_path = _make_ico(icon_dir, icon_svg)

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', APP_NAME,
        '--windowed',
        '--add-data', f'{PROJECT_ROOT / "frontends"};frontends',
        '--add-data', f'{PROJECT_ROOT / "assets"};assets',
        '--add-data', f'{PROJECT_ROOT / "memory"};memory',
        '--noconfirm', '--clean',
    ]
    if icon_path:
        cmd.extend(['--icon', icon_path])
    for hi in _WEBAPP_IMPORTS:
        cmd.extend(['--hidden-import', hi])
    cmd.append(str(_WEBAPP_SCRIPT))

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("❌ Windows build failed")
        return False

    app_dir, exe_path = _find_windows_executable()
    if app_dir and exe_path and exe_path.exists():
        print(f"✅ Windows exe built: {exe_path}")
        _create_zip_archive(app_dir)
        script_path = _create_windows_installer_script(app_dir)
        _compile_windows_installer(script_path)
        return True

    print("❌ Executable not found")
    return False


def build_linux_appimage():
    print("🐧 Building Linux AppImage (Generic Coder web app)...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', APP_NAME,
        '--onefile',
        '--add-data', f'{PROJECT_ROOT / "frontends"}:frontends',
        '--add-data', f'{PROJECT_ROOT / "assets"}:assets',
        '--add-data', f'{PROJECT_ROOT / "memory"}:memory',
        '--noconfirm', '--clean',
    ]
    for hi in _WEBAPP_IMPORTS:
        cmd.extend(['--hidden-import', hi])
    cmd.append(str(_WEBAPP_SCRIPT))

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("❌ Linux build failed")
        return False

    binary = DIST_DIR / APP_NAME
    if binary.exists():
        print(f"✅ Linux binary built: {binary}")
        _create_tarball(binary)
        return True

    print("❌ Binary not found")
    return False


# ── Standalone Tkinter desktop-app builds ─────────────────────────────────

_STANDALONE_SCRIPT = PROJECT_ROOT / 'frontends' / 'standalone_app.py'

_STANDALONE_IMPORTS = [
    'PIL', 'watchfiles', 'paramiko',
    'PyPDF2', 'pdfplumber', 'docx', 'openpyxl', 'pptx',
    'requests',
]


def build_macos_standalone():
    print("🍎 Building macOS standalone app (Desktop)...")
    if not ensure_tkinter():
        return False
    icon_dir, icon_svg = _build_icon()
    icns_path = _make_icns(icon_dir, icon_svg)

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', APP_NAME,
        '--windowed',
        '--icon', str(icns_path),
        '--add-data', f'{PROJECT_ROOT / "frontends" / "themes.py"}:.',
        '--add-data', f'{PROJECT_ROOT / "assets"}:assets',
        '--add-data', f'{PROJECT_ROOT / "memory"}:memory',
        '--osx-bundle-identifier', BUNDLE_ID,
        '--noconfirm', '--clean',
    ]
    for hi in _STANDALONE_IMPORTS:
        cmd.extend(['--hidden-import', hi])
    cmd.append(str(_STANDALONE_SCRIPT))

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("❌ macOS standalone build failed")
        return False

    app_bundle = DIST_DIR / f'{APP_NAME}.app'
    if app_bundle.exists():
        _patch_plist(app_bundle)
        print(f"✅ macOS standalone app built: {app_bundle}")
        _create_macos_pkg(app_bundle)
        _create_dmg(app_bundle)
        return True

    print("❌ App bundle not found")
    return False


def build_windows_standalone():
    print("🪟 Building Windows standalone executable (Desktop)...")
    if not ensure_tkinter():
        return False
    icon_dir, icon_svg = _build_icon()
    icon_path = _make_ico(icon_dir, icon_svg)

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', APP_NAME,
        '--windowed',
        '--add-data', f'{PROJECT_ROOT / "frontends" / "themes.py"};.',
        '--add-data', f'{PROJECT_ROOT / "assets"};assets',
        '--add-data', f'{PROJECT_ROOT / "memory"};memory',
        '--noconfirm', '--clean',
    ]
    if icon_path:
        cmd.extend(['--icon', icon_path])
    for hi in _STANDALONE_IMPORTS:
        cmd.extend(['--hidden-import', hi])
    cmd.append(str(_STANDALONE_SCRIPT))

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("❌ Windows standalone build failed")
        return False

    app_dir, exe_path = _find_windows_executable()
    if app_dir and exe_path and exe_path.exists():
        print(f"✅ Windows standalone exe built: {exe_path}")
        _create_zip_archive(app_dir, suffix='win64-desktop')
        script_path = _create_windows_installer_script(app_dir, suffix='win64-desktop')
        _compile_windows_installer(script_path)
        return True

    print("❌ Executable not found")
    return False


def build_linux_standalone():
    print("🐧 Building Linux standalone binary (Desktop)...")
    if not ensure_tkinter():
        return False
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', APP_NAME,
        '--onefile',
        '--add-data', f'{PROJECT_ROOT / "frontends" / "themes.py"}:.',
        '--add-data', f'{PROJECT_ROOT / "assets"}:assets',
        '--add-data', f'{PROJECT_ROOT / "memory"}:memory',
        '--noconfirm', '--clean',
    ]
    for hi in _STANDALONE_IMPORTS:
        cmd.extend(['--hidden-import', hi])
    cmd.append(str(_STANDALONE_SCRIPT))

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("❌ Linux standalone build failed")
        return False

    binary = DIST_DIR / APP_NAME
    if binary.exists():
        print(f"✅ Linux standalone binary built: {binary}")
        _create_tarball(binary)
        return True

    print("❌ Binary not found")
    return False


# ── Unified build entry points ────────────────────────────────────────────

def build_all(standalone=False):
    current_os = platform.system()
    label = "Desktop" if standalone else "Web"
    print(f"🔨 Building {APP_NAME} v{VERSION} ({label}) for {current_os}")
    print("=" * 50)

    ensure_pyinstaller()
    clean_build()

    success = False

    if standalone:
        if current_os == 'Darwin':
            success = build_macos_standalone()
        elif current_os == 'Windows':
            success = build_windows_standalone()
        elif current_os == 'Linux':
            success = build_linux_standalone()
    else:
        if current_os == 'Darwin':
            success = build_macos_app()
        elif current_os == 'Windows':
            success = build_windows_exe()
        elif current_os == 'Linux':
            success = build_linux_appimage()

    if not success and current_os not in ('Darwin', 'Windows', 'Linux'):
        print(f"❌ Unsupported OS: {current_os}")
        return

    if success:
        print(f"\n🎉 Build complete! Output in: {DIST_DIR}")
    else:
        print(f"\n❌ Build failed. Check logs above.")


# ── Quick launchers ───────────────────────────────────────────────────────

def build_quick_launcher():
    launcher_script = PROJECT_ROOT / 'Generic Coder.command'
    content = f'''#!/bin/bash
# Generic Coder Quick Launcher
cd "$(dirname "$0")"
echo "✦ Starting Generic Coder..."
python3 "{PROJECT_ROOT}/launch.pyw"
'''
    with open(launcher_script, 'w') as f:
        f.write(content)
    os.chmod(launcher_script, 0o755)
    print(f"✅ Launcher script created: {launcher_script}")


def build_standalone_launcher():
    launcher_script = PROJECT_ROOT / 'Generic Coder Desktop.command'
    content = f'''#!/bin/bash
# Generic Coder Desktop Launcher (legacy Tkinter shell)
cd "$(dirname "$0")"
echo "✦ Starting Generic Coder Desktop..."
python3 "{PROJECT_ROOT}/frontends/standalone_app.py"
'''
    with open(launcher_script, 'w') as f:
        f.write(content)
    os.chmod(launcher_script, 0o755)
    print(f"✅ Desktop launcher created: {launcher_script}")


# ── CLI ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Build Generic Coder installer')
    parser.add_argument(
        '--target',
        choices=[
            'macos', 'windows', 'linux', 'all', 'launcher',
            'standalone-macos', 'standalone-windows',
            'standalone-linux', 'standalone', 'standalone-launcher',
            'windows-source-installer',
        ],
        default='all',
           help='Build target: platform builds package the Generic Coder web app; '
               'standalone-* builds the legacy Tkinter desktop app',
    )
    parser.add_argument('--clean', action='store_true', help='Clean before build')
    args = parser.parse_args()

    if args.target not in {'launcher', 'standalone-launcher', 'windows-source-installer'}:
        ensure_pyinstaller()

    if args.clean:
        clean_build()

    if args.target == 'launcher':
        build_quick_launcher()
    elif args.target == 'standalone-launcher':
        build_standalone_launcher()
    elif args.target == 'standalone':
        build_all(standalone=True)
    elif args.target == 'standalone-macos':
        build_macos_standalone()
    elif args.target == 'standalone-windows':
        build_windows_standalone()
    elif args.target == 'standalone-linux':
        build_linux_standalone()
    elif args.target == 'all':
        build_all()
    elif args.target == 'macos':
        build_macos_app()
    elif args.target == 'windows':
        build_windows_exe()
    elif args.target == 'windows-source-installer':
        build_windows_source_installer()
    elif args.target == 'linux':
        build_linux_appimage()
