# Generic Coder

<div align="center">
  <img src="assets/images/generic-coder-banner.svg" width="880" alt="Generic Coder banner"/>
</div>

<p align="center">
  <a href="#zh-cn">中文</a> | <a href="#en">English</a> | <a href="#es">Español</a>
</p>

<p align="center">
  Built on the GenericAgent foundation, reworked into a SOLO-style coding and maintenance cockpit.
</p>

---

<a id="zh-cn"></a>
## 中文

### 项目定位

**Generic Coder** 是在 **GenericAgent** 项目基石之上，面向真实代码维护场景重构出来的开发工作台。它保留了 GenericAgent 的 Agent Loop、记忆层、工具能力与多模型运行基础，同时参考 **Trae SOLO** 的交互体验，落成了一套接近 SOLO 风格的代码维护界面与执行流。

这不是对原项目的简单换皮，而是一次面向开发任务的聚焦化重构：把 GenericAgent 的通用自治能力，收束为更适合日常编码、修复、调试、切换模型、切换工作区、连接远程环境的 **Generic Coder**。

### 核心亮点

- **基于 GenericAgent 基石演进**：继续使用原有的 Agent runtime、记忆机制、工具链与任务执行能力。
- **参考 Trae SOLO 的代码维护体验**：围绕“看代码、改代码、验证代码、继续会话”组织界面与流程，适合持续维护项目。
- **模型自由切换**：支持在界面中切换不同模型，并通过设置面板维护模型参数。
- **多协议与多模型预设**：可在设置中选择常见模型与协议预设，自动填充可推断字段，减少手工配置成本。
- **多配色主题切换**：内置多套高对比度主题，兼顾前卫感、科技感与长时间使用的可读性。
- **简洁界面**：主界面围绕对话、状态、会话恢复和设置展开，不堆砌无关控件。
- **Web 端与桌面端并存**：既可用浏览器打开，也可通过桌面壳直接启动，适合不同使用习惯。
- **本地与远程工作环境兼容**：支持本地工作区选择，也支持接入远程环境开展文件修改与调试。

### 适合什么场景

- 持续维护现有代码仓库
- 快速修复 Bug 并进行回归验证
- 在不同模型之间切换比较效果
- 需要在简洁 UI 中完成日常代码代理工作
- 同时希望保留浏览器形态和桌面应用形态

### 当前形态

- **Web 工作台**：Bottle 驱动的 Generic Coder 前端，适合浏览器直接使用。
- **桌面工作台**：`launch.pyw` 通过 pywebview 将同一套 Web 工作台包装为桌面应用。
- **安装产物**：仓库已支持生成 macOS 安装包，以及 Windows 可执行安装器。

### 快速开始

```bash
git clone https://github.com/lsdefine/GenericAgent.git
cd GenericAgent
pip install -e ".[ui,installer,media,remote,workspace]"
cp mykey_template.py mykey.py
python launch.pyw
```

如果只想启动 Web 端，也可以使用：

```bash
python frontends/generic_coder_web.py --host 127.0.0.1 --port 8876
```

### 安装包生成

macOS：

```bash
python3 build_installer.py --target macos --clean
```

Windows 可执行安装器：

```bash
python3 build_installer.py --target windows-source-installer
```

生成结果位于 `dist/`，当前仓库可产出：

- `Generic Coder.app`
- `Generic Coder-0.2.0.dmg`
- `Generic Coder-0.2.0.pkg`
- `Generic Coder-0.2.0-setup-win64-source.exe`

### 相关文档

- 新手上手说明见 [GETTING_STARTED.md](GETTING_STARTED.md)
- 若你想看当前 Web 工作台实现，可从 [launch.pyw](launch.pyw) 与 [frontends/generic_coder_web.py](frontends/generic_coder_web.py) 开始

---

<a id="en"></a>
## English

### Positioning

**Generic Coder** is a coding-focused workstation rebuilt on top of the **GenericAgent** foundation. It keeps the original agent runtime, memory layers, tool-driven execution model, and multi-model base, then reshapes the user experience into a coding cockpit inspired by **Trae SOLO**.

The result is a SOLO-style code maintenance workflow rather than a general-purpose agent shell: inspect code, edit code, validate changes, resume sessions, switch models, switch workspaces, and move between local and remote environments inside one compact interface.

### Highlights

- **Built on GenericAgent**: keeps the existing runtime, memory architecture, and agent execution capabilities.
- **Trae SOLO-inspired maintenance flow**: optimized for ongoing repository maintenance instead of broad generic automation.
- **Free model switching**: switch models from the UI and manage model settings without editing Python files every time.
- **Preset-driven configuration**: common model and protocol presets reduce repetitive manual entry.
- **Multiple color themes**: several high-contrast themes are built in for different visual preferences.
- **Clean interface**: the UI stays focused on conversation, session recovery, model state, and settings.
- **Web and desktop together**: run it in a browser or launch the same cockpit as a desktop app.
- **Local and remote work modes**: choose a local workspace or connect to a remote environment for direct maintenance work.

### Best Fit

- Maintaining an existing codebase with an agent in the loop
- Switching between models to compare coding quality
- Working in a simplified high-signal interface
- Keeping both browser-based and desktop-based workflows available
- Extending GenericAgent into a more productized coding environment

### Runtime Shape

- **Web cockpit**: a Bottle-powered Generic Coder frontend for browser usage.
- **Desktop shell**: `launch.pyw` wraps the same cockpit through pywebview.
- **Installer support**: the repository can generate macOS installers and a Windows executable installer.

### Quick Start

```bash
git clone https://github.com/lsdefine/GenericAgent.git
cd GenericAgent
pip install -e ".[ui,installer,media,remote,workspace]"
cp mykey_template.py mykey.py
python launch.pyw
```

To run only the web cockpit:

```bash
python frontends/generic_coder_web.py --host 127.0.0.1 --port 8876
```

### Build Installers

macOS:

```bash
python3 build_installer.py --target macos --clean
```

Windows executable installer:

```bash
python3 build_installer.py --target windows-source-installer
```

Artifacts are written to `dist/`, including:

- `Generic Coder.app`
- `Generic Coder-0.2.0.dmg`
- `Generic Coder-0.2.0.pkg`
- `Generic Coder-0.2.0-setup-win64-source.exe`

### More

- Beginner setup guide: [GETTING_STARTED.md](GETTING_STARTED.md)
- Main entry points: [launch.pyw](launch.pyw) and [frontends/generic_coder_web.py](frontends/generic_coder_web.py)

---

<a id="es"></a>
## Español

### Posicionamiento

**Generic Coder** es una estación de trabajo para mantenimiento de código, reconstruida sobre la base de **GenericAgent**. Conserva el runtime del agente, la memoria por capas, la ejecución basada en herramientas y la base multimodelo del proyecto original, pero reorganiza la experiencia con una lógica inspirada en **Trae SOLO**.

El resultado es un flujo de mantenimiento de código parecido a SOLO: revisar código, modificar archivos, validar cambios, continuar sesiones, cambiar de modelo, cambiar de espacio de trabajo y operar tanto en entorno local como remoto desde una interfaz compacta.

### Ventajas principales

- **Basado en GenericAgent**: mantiene el runtime, la memoria y la capacidad de ejecución autónoma del proyecto original.
- **Flujo inspirado en Trae SOLO**: pensado para mantenimiento continuo de repositorios.
- **Cambio libre de modelos**: el usuario puede cambiar de modelo desde la interfaz.
- **Configuración con preajustes**: modelos y protocolos comunes se rellenan más rápido con presets.
- **Varios temas de color**: incluye múltiples temas de alto contraste.
- **Interfaz limpia**: la UI se centra en conversación, sesiones, estado del modelo y ajustes.
- **Web y escritorio al mismo tiempo**: puede usarse como cockpit web o como aplicación de escritorio.
- **Modo local y remoto**: permite trabajar con carpetas locales o con entornos remotos.

### Casos ideales

- Mantenimiento diario de un proyecto existente
- Comparación entre varios modelos para tareas de programación
- Uso de un agente en una interfaz más simple y directa
- Necesidad de convivir con flujo web y flujo de escritorio

### Forma actual del producto

- **Cockpit web**: frontend Generic Coder impulsado por Bottle.
- **Contenedor de escritorio**: `launch.pyw` usa pywebview para abrir la misma interfaz como app de escritorio.
- **Instaladores**: el repositorio ya puede generar instaladores para macOS y un instalador ejecutable para Windows.

### Inicio rápido

```bash
git clone https://github.com/lsdefine/GenericAgent.git
cd GenericAgent
pip install -e ".[ui,installer,media,remote,workspace]"
cp mykey_template.py mykey.py
python launch.pyw
```

Para ejecutar solo la versión web:

```bash
python frontends/generic_coder_web.py --host 127.0.0.1 --port 8876
```

### Generación de instaladores

macOS:

```bash
python3 build_installer.py --target macos --clean
```

Instalador ejecutable para Windows:

```bash
python3 build_installer.py --target windows-source-installer
```

Los archivos se generan en `dist/`, por ejemplo:

- `Generic Coder.app`
- `Generic Coder-0.2.0.dmg`
- `Generic Coder-0.2.0.pkg`
- `Generic Coder-0.2.0-setup-win64-source.exe`

### Documentación relacionada

- Guía para empezar: [GETTING_STARTED.md](GETTING_STARTED.md)
- Puntos de entrada principales: [launch.pyw](launch.pyw) y [frontends/generic_coder_web.py](frontends/generic_coder_web.py)
