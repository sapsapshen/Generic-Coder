const DEFAULT_LLM_FORM = {
  entry_key: 'generic_coder_native_oai_config',
  session_type: 'native_oai',
  protocol_preset: 'custom',
  api_mode: 'chat_completions',
  provider: '',
  name: '',
  apikey: '',
  apibase: '',
  model: '',
};

const DEFAULT_REMOTE_FORM = {
  enabled: false,
  server_name: '',
  name: '',
  host: '',
  port: 22,
  username: 'root',
  password: '',
  key_path: '',
  cwd: '',
};

const state = {
  messages: [],
  pendingTaskId: null,
  theme: 'solarflare',
  taskPlaceholderId: null,
  isRunning: false,
  locale: 'zh',
  models: [],
  currentModelIndex: 0,
  llmForm: { ...DEFAULT_LLM_FORM },
  workspace: { active: null, workspaces: [], recent_folders: [] },
  remote: { form: { ...DEFAULT_REMOTE_FORM }, configs: [], active_connections: [], connected: false },
};

const THEME_OPTIONS = ['solarflare', 'graphite', 'neonwave', 'daybreak', 'ember'];
const LANGUAGE_OPTIONS = ['zh', 'en', 'es'];
const SESSION_TYPE_OPTIONS = ['native_oai', 'oai', 'native_claude', 'claude'];
const PROTOCOL_PRESET_OPTIONS = ['custom', 'deepseek', 'openai_chat', 'openai_responses', 'anthropic_messages', 'openrouter', 'moonshot_oai', 'kimi_coding', 'minimax_oai', 'zhipu_anthropic'];
const MODEL_PRESET_OPTIONS = ['custom', 'deepseek_chat', 'deepseek_reasoner', 'gpt_5_4', 'gpt_4_1', 'claude_sonnet_4', 'claude_opus_4_7', 'kimi_for_coding', 'minimax_m27', 'glm_5_1', 'openrouter_claude'];

const PROTOCOL_PRESETS = {
  custom: { sessionType: 'native_oai', api_mode: 'chat_completions', provider: '', apibase: '' },
  deepseek: { sessionType: 'native_oai', api_mode: 'chat_completions', provider: 'DeepSeek', apibase: 'https://api.deepseek.com/v1' },
  openai_chat: { sessionType: 'native_oai', api_mode: 'chat_completions', provider: 'OpenAI', apibase: 'https://api.openai.com/v1' },
  openai_responses: { sessionType: 'native_oai', api_mode: 'responses', provider: 'OpenAI', apibase: 'https://api.openai.com/v1' },
  anthropic_messages: { sessionType: 'native_claude', api_mode: 'chat_completions', provider: 'Anthropic', apibase: 'https://api.anthropic.com' },
  openrouter: { sessionType: 'oai', api_mode: 'chat_completions', provider: 'OpenRouter', apibase: 'https://openrouter.ai/api/v1' },
  moonshot_oai: { sessionType: 'oai', api_mode: 'chat_completions', provider: 'Moonshot', apibase: 'https://api.moonshot.cn/v1' },
  kimi_coding: { sessionType: 'native_claude', api_mode: 'chat_completions', provider: 'Moonshot', apibase: 'https://api.kimi.com/coding' },
  minimax_oai: { sessionType: 'oai', api_mode: 'chat_completions', provider: 'MiniMax', apibase: 'https://api.minimaxi.com/v1' },
  zhipu_anthropic: { sessionType: 'native_claude', api_mode: 'chat_completions', provider: 'Zhipu', apibase: 'https://open.bigmodel.cn/api/anthropic' },
};

const MODEL_PRESETS = {
  custom: {},
  deepseek_chat: { provider: 'DeepSeek', model: 'deepseek-chat', displayName: 'deepseek-chat', protocolPreset: 'deepseek' },
  deepseek_reasoner: { provider: 'DeepSeek', model: 'deepseek-reasoner', displayName: 'deepseek-reasoner', protocolPreset: 'deepseek' },
  gpt_5_4: { provider: 'OpenAI', model: 'gpt-5.4', displayName: 'gpt-5.4', protocolPreset: 'openai_responses' },
  gpt_4_1: { provider: 'OpenAI', model: 'gpt-4.1', displayName: 'gpt-4.1', protocolPreset: 'openai_chat' },
  claude_sonnet_4: { provider: 'Anthropic', model: 'claude-sonnet-4-20250514', displayName: 'claude-sonnet-4', protocolPreset: 'anthropic_messages' },
  claude_opus_4_7: { provider: 'Anthropic', model: 'claude-opus-4-7', displayName: 'claude-opus-4-7', protocolPreset: 'anthropic_messages' },
  kimi_for_coding: { provider: 'Moonshot', model: 'kimi-for-coding', displayName: 'kimi-coding', protocolPreset: 'kimi_coding' },
  minimax_m27: { provider: 'MiniMax', model: 'MiniMax-M2.7', displayName: 'MiniMax-M2.7', protocolPreset: 'minimax_oai' },
  glm_5_1: { provider: 'Zhipu', model: 'glm-5.1', displayName: 'glm-5.1', protocolPreset: 'zhipu_anthropic' },
  openrouter_claude: { provider: 'OpenRouter', model: 'anthropic/claude-opus-4-7', displayName: 'openrouter-claude', protocolPreset: 'openrouter' },
};

const I18N = {
  zh: {
    newChat: '新建会话',
    sessions: '恢复会话',
    stop: '停止生成',
    settings: '设置',
    close: '关闭',
    send: '发送',
    model: '模型',
    theme: '主题',
    language: '语言',
    sessionsTitle: '可恢复会话',
    composerPlaceholder: '输入消息',
    idle: '空闲',
    running: '运行中',
    modelOffline: '未配置模型',
    pollingError: '任务轮询失败',
    stopSent: '已发送停止信号',
    requestError: '请求未成功发出',
    modelSwitchError: '模型切换失败',
    modelSwitchOk: '模型已切换',
    modelSettings: '模型设置',
    commonModel: '常见模型',
    protocolPreset: '协议预设',
    sessionType: '接入协议',
    provider: '提供商',
    displayName: '显示名',
    modelName: '模型名称',
    baseUrl: 'Base URL',
    apiKey: 'API Key',
    showSecret: '显示',
    hideSecret: '隐藏',
    saveModelSettings: '保存模型配置',
    llmSaveOk: '模型配置已保存并启用',
    llmSaveError: '模型配置保存失败',
    workspaceSettings: '本地工作区',
    workspaceName: '工作区名称',
    workspacePath: '工作目录',
    applyWorkspace: '应用工作区',
    workspaceSaveOk: '工作区已切换',
    workspaceSaveError: '工作区切换失败',
    currentWorkspace: '当前工作区',
    noWorkspace: '未设置本地工作区',
    recentWorkspaces: '最近工作区',
    use: '使用',
    remoteSettings: '远程工作环境',
    remoteMode: '启用远程工作环境',
    remoteName: '连接名称',
    host: '主机',
    port: '端口',
    username: '用户名',
    password: '密码',
    keyPath: '密钥路径',
    remoteCwd: '远程工作目录',
    connectRemote: '连接远程环境',
    remoteConnectOk: '远程环境已连接',
    remoteConnectError: '远程环境连接失败',
    currentRemote: '当前远程环境',
    noRemote: '未连接远程环境',
    savedRemotes: '已保存连接',
    connected: '已连接',
    disconnected: '未连接',
    interfaceSettings: '界面',
    noSessions: '没有可恢复的历史会话。',
    userRole: '你',
    assistantRole: 'Generic Coder',
    languageName: '中文',
    rounds: (value) => `${value} 轮`,
  },
  en: {
    newChat: 'New chat',
    sessions: 'Sessions',
    stop: 'Stop',
    settings: 'Settings',
    close: 'Close',
    send: 'Send',
    model: 'Model',
    theme: 'Theme',
    language: 'Language',
    sessionsTitle: 'Sessions',
    composerPlaceholder: 'Type a message',
    idle: 'Idle',
    running: 'Running',
    modelOffline: 'Model offline',
    pollingError: 'Task polling failed',
    stopSent: 'Stop signal sent',
    requestError: 'Request did not start',
    modelSwitchError: 'Model switch failed',
    modelSwitchOk: 'Model switched',
    modelSettings: 'Model settings',
    commonModel: 'Common model',
    protocolPreset: 'Protocol preset',
    sessionType: 'Session type',
    provider: 'Provider',
    displayName: 'Display name',
    modelName: 'Model name',
    baseUrl: 'Base URL',
    apiKey: 'API Key',
    showSecret: 'Show',
    hideSecret: 'Hide',
    saveModelSettings: 'Save model settings',
    llmSaveOk: 'Model settings saved and activated',
    llmSaveError: 'Failed to save model settings',
    workspaceSettings: 'Local workspace',
    workspaceName: 'Workspace name',
    workspacePath: 'Workspace path',
    applyWorkspace: 'Apply workspace',
    workspaceSaveOk: 'Workspace switched',
    workspaceSaveError: 'Failed to switch workspace',
    currentWorkspace: 'Current workspace',
    noWorkspace: 'No local workspace selected',
    recentWorkspaces: 'Recent workspaces',
    use: 'Use',
    remoteSettings: 'Remote environment',
    remoteMode: 'Use remote environment',
    remoteName: 'Connection name',
    host: 'Host',
    port: 'Port',
    username: 'Username',
    password: 'Password',
    keyPath: 'Key path',
    remoteCwd: 'Remote working directory',
    connectRemote: 'Connect remote environment',
    remoteConnectOk: 'Remote environment connected',
    remoteConnectError: 'Failed to connect remote environment',
    currentRemote: 'Current remote environment',
    noRemote: 'No remote environment connected',
    savedRemotes: 'Saved connections',
    connected: 'Connected',
    disconnected: 'Disconnected',
    interfaceSettings: 'Interface',
    noSessions: 'No recoverable sessions.',
    userRole: 'You',
    assistantRole: 'Generic Coder',
    languageName: 'English',
    rounds: (value) => `${value} rounds`,
  },
  es: {
    newChat: 'Nuevo chat',
    sessions: 'Sesiones',
    stop: 'Detener',
    settings: 'Ajustes',
    close: 'Cerrar',
    send: 'Enviar',
    model: 'Modelo',
    theme: 'Tema',
    language: 'Idioma',
    sessionsTitle: 'Sesiones',
    composerPlaceholder: 'Escribe un mensaje',
    idle: 'En espera',
    running: 'En curso',
    modelOffline: 'Modelo inactivo',
    pollingError: 'Falló la lectura de la tarea',
    stopSent: 'Se envió la señal de parada',
    requestError: 'La solicitud no se inició',
    modelSwitchError: 'Falló el cambio de modelo',
    modelSwitchOk: 'Modelo cambiado',
    modelSettings: 'Ajustes del modelo',
    commonModel: 'Modelo común',
    protocolPreset: 'Preajuste de protocolo',
    sessionType: 'Tipo de sesión',
    provider: 'Proveedor',
    displayName: 'Nombre visible',
    modelName: 'Nombre del modelo',
    baseUrl: 'Base URL',
    apiKey: 'API Key',
    showSecret: 'Mostrar',
    hideSecret: 'Ocultar',
    saveModelSettings: 'Guardar modelo',
    llmSaveOk: 'La configuración del modelo se guardó y activó',
    llmSaveError: 'No se pudo guardar la configuración del modelo',
    workspaceSettings: 'Espacio de trabajo local',
    workspaceName: 'Nombre del espacio',
    workspacePath: 'Ruta del espacio',
    applyWorkspace: 'Aplicar espacio',
    workspaceSaveOk: 'Espacio de trabajo cambiado',
    workspaceSaveError: 'No se pudo cambiar el espacio',
    currentWorkspace: 'Espacio actual',
    noWorkspace: 'No hay espacio local seleccionado',
    recentWorkspaces: 'Espacios recientes',
    use: 'Usar',
    remoteSettings: 'Entorno remoto',
    remoteMode: 'Usar entorno remoto',
    remoteName: 'Nombre de conexión',
    host: 'Host',
    port: 'Puerto',
    username: 'Usuario',
    password: 'Contraseña',
    keyPath: 'Ruta de clave',
    remoteCwd: 'Directorio remoto',
    connectRemote: 'Conectar entorno remoto',
    remoteConnectOk: 'Entorno remoto conectado',
    remoteConnectError: 'No se pudo conectar el entorno remoto',
    currentRemote: 'Entorno remoto actual',
    noRemote: 'No hay entorno remoto conectado',
    savedRemotes: 'Conexiones guardadas',
    connected: 'Conectado',
    disconnected: 'Desconectado',
    interfaceSettings: 'Interfaz',
    noSessions: 'No hay sesiones recuperables.',
    userRole: 'Tú',
    assistantRole: 'Generic Coder',
    languageName: 'Español',
    rounds: (value) => `${value} rondas`,
  },
};

const THEME_LABELS = {
  zh: { solarflare: 'Solar Flare', graphite: 'Liquid Graphite', neonwave: 'Neon Wave', daybreak: 'Daybreak', ember: 'Ember Core' },
  en: { solarflare: 'Solar Flare', graphite: 'Liquid Graphite', neonwave: 'Neon Wave', daybreak: 'Daybreak', ember: 'Ember Core' },
  es: { solarflare: 'Llamarada Solar', graphite: 'Grafito Líquido', neonwave: 'Ola Neón', daybreak: 'Amanecer', ember: 'Núcleo Ember' },
};

const LANGUAGE_LABELS = {
  zh: { zh: '中文', en: 'English', es: 'Español' },
  en: { zh: 'Chinese', en: 'English', es: 'Spanish' },
  es: { zh: 'Chino', en: 'Inglés', es: 'Español' },
};

const SESSION_TYPE_LABELS = {
  zh: { native_oai: 'Native OAI', oai: 'OAI', native_claude: 'Native Claude', claude: 'Claude' },
  en: { native_oai: 'Native OAI', oai: 'OAI', native_claude: 'Native Claude', claude: 'Claude' },
  es: { native_oai: 'Native OAI', oai: 'OAI', native_claude: 'Native Claude', claude: 'Claude' },
};

const PROTOCOL_PRESET_LABELS = {
  zh: {
    custom: '手动填写',
    deepseek: 'DeepSeek OAI',
    openai_chat: 'OpenAI Chat Completions',
    openai_responses: 'OpenAI Responses',
    anthropic_messages: 'Anthropic Messages',
    openrouter: 'OpenRouter OAI',
    moonshot_oai: 'Moonshot OAI',
    kimi_coding: 'Kimi Coding',
    minimax_oai: 'MiniMax OAI',
    zhipu_anthropic: '智谱 Anthropic 兼容',
  },
  en: {
    custom: 'Manual entry',
    deepseek: 'DeepSeek OAI',
    openai_chat: 'OpenAI Chat Completions',
    openai_responses: 'OpenAI Responses',
    anthropic_messages: 'Anthropic Messages',
    openrouter: 'OpenRouter OAI',
    moonshot_oai: 'Moonshot OAI',
    kimi_coding: 'Kimi Coding',
    minimax_oai: 'MiniMax OAI',
    zhipu_anthropic: 'Zhipu Anthropic compatible',
  },
  es: {
    custom: 'Manual',
    deepseek: 'DeepSeek OAI',
    openai_chat: 'OpenAI Chat Completions',
    openai_responses: 'OpenAI Responses',
    anthropic_messages: 'Anthropic Messages',
    openrouter: 'OpenRouter OAI',
    moonshot_oai: 'Moonshot OAI',
    kimi_coding: 'Kimi Coding',
    minimax_oai: 'MiniMax OAI',
    zhipu_anthropic: 'Zhipu Anthropic compatible',
  },
};

const MODEL_PRESET_LABELS = {
  zh: {
    custom: '手动填写',
    deepseek_chat: 'DeepSeek Chat',
    deepseek_reasoner: 'DeepSeek Reasoner',
    gpt_5_4: 'GPT-5.4',
    gpt_4_1: 'GPT-4.1',
    claude_sonnet_4: 'Claude Sonnet 4',
    claude_opus_4_7: 'Claude Opus 4.7',
    kimi_for_coding: 'Kimi for Coding',
    minimax_m27: 'MiniMax M2.7',
    glm_5_1: 'GLM 5.1',
    openrouter_claude: 'OpenRouter Claude Opus',
  },
  en: {
    custom: 'Manual entry',
    deepseek_chat: 'DeepSeek Chat',
    deepseek_reasoner: 'DeepSeek Reasoner',
    gpt_5_4: 'GPT-5.4',
    gpt_4_1: 'GPT-4.1',
    claude_sonnet_4: 'Claude Sonnet 4',
    claude_opus_4_7: 'Claude Opus 4.7',
    kimi_for_coding: 'Kimi for Coding',
    minimax_m27: 'MiniMax M2.7',
    glm_5_1: 'GLM 5.1',
    openrouter_claude: 'OpenRouter Claude Opus',
  },
  es: {
    custom: 'Manual',
    deepseek_chat: 'DeepSeek Chat',
    deepseek_reasoner: 'DeepSeek Reasoner',
    gpt_5_4: 'GPT-5.4',
    gpt_4_1: 'GPT-4.1',
    claude_sonnet_4: 'Claude Sonnet 4',
    claude_opus_4_7: 'Claude Opus 4.7',
    kimi_for_coding: 'Kimi for Coding',
    minimax_m27: 'MiniMax M2.7',
    glm_5_1: 'GLM 5.1',
    openrouter_claude: 'OpenRouter Claude Opus',
  },
};

const feedEl = document.getElementById('chat-feed');
const composerEl = document.getElementById('composer-input');
const composerForm = document.getElementById('composer-form');
const sendButton = document.getElementById('send-button');
const statusLabel = document.getElementById('status-label');
const modelLabel = document.getElementById('model-label');
const statusDot = document.getElementById('status-dot');
const modelSelect = document.getElementById('model-select');
const themeSelect = document.getElementById('theme-select');
const themePill = document.getElementById('theme-pill');
const languagePill = document.getElementById('language-pill');
const languageSelect = document.getElementById('language-select');
const messageCount = document.getElementById('message-count');
const toastEl = document.getElementById('toast');
const sessionsDialog = document.getElementById('sessions-dialog');
const settingsDialog = document.getElementById('settings-dialog');
const sessionsList = document.getElementById('sessions-list');
const lastReplyTimeEl = document.getElementById('last-reply-time');

const modelPresetSelect = document.getElementById('model-preset-select');
const protocolPresetSelect = document.getElementById('protocol-preset-select');
const sessionTypeSelect = document.getElementById('session-type-select');
const providerInput = document.getElementById('provider-input');
const displayNameInput = document.getElementById('display-name-input');
const modelNameInput = document.getElementById('model-name-input');
const baseUrlInput = document.getElementById('base-url-input');
const apiKeyInput = document.getElementById('api-key-input');
const apiKeyToggle = document.getElementById('api-key-toggle');
const saveLlmButton = document.getElementById('save-llm-settings');

const workspaceStatus = document.getElementById('workspace-status');
const workspaceNameInput = document.getElementById('workspace-name-input');
const workspacePathInput = document.getElementById('workspace-path-input');
const saveWorkspaceButton = document.getElementById('save-workspace-settings');
const workspaceList = document.getElementById('workspace-list');

const remoteStatus = document.getElementById('remote-status');
const remoteEnabledInput = document.getElementById('remote-enabled-input');
const remoteNameInput = document.getElementById('remote-name-input');
const remoteHostInput = document.getElementById('remote-host-input');
const remotePortInput = document.getElementById('remote-port-input');
const remoteUsernameInput = document.getElementById('remote-username-input');
const remotePasswordInput = document.getElementById('remote-password-input');
const remoteKeyPathInput = document.getElementById('remote-key-path-input');
const remoteCwdInput = document.getElementById('remote-cwd-input');
const connectRemoteButton = document.getElementById('connect-remote-button');
const remoteConfigList = document.getElementById('remote-config-list');

function t(key) {
  return I18N[state.locale][key];
}

function preferredLocale() {
  const stored = window.localStorage.getItem('generic-coder-locale');
  if (stored && LANGUAGE_OPTIONS.includes(stored)) return stored;
  const raw = (navigator.language || 'en').toLowerCase();
  if (raw.startsWith('zh')) return 'zh';
  if (raw.startsWith('es')) return 'es';
  return 'en';
}

function syncDocumentLanguage() {
  document.documentElement.lang = state.locale === 'zh' ? 'zh-CN' : state.locale;
}

function renderThemeOptions() {
  themeSelect.innerHTML = THEME_OPTIONS.map((theme) => `<option value="${theme}">${THEME_LABELS[state.locale][theme] || theme}</option>`).join('');
  themeSelect.value = state.theme;
}

function renderLanguageOptions() {
  languageSelect.innerHTML = LANGUAGE_OPTIONS.map((locale) => `<option value="${locale}">${LANGUAGE_LABELS[state.locale][locale] || locale}</option>`).join('');
  languageSelect.value = state.locale;
}

function renderModelOptions() {
  if (!state.models.length) {
    modelSelect.innerHTML = `<option value="">${t('modelOffline')}</option>`;
    modelSelect.disabled = true;
    return;
  }
  modelSelect.disabled = false;
  modelSelect.innerHTML = state.models.map((item) => `<option value="${item.index}">${escapeHtml(item.label)}</option>`).join('');
  modelSelect.value = String(state.currentModelIndex);
}

function renderSessionTypeOptions() {
  sessionTypeSelect.innerHTML = SESSION_TYPE_OPTIONS.map((value) => `<option value="${value}">${SESSION_TYPE_LABELS[state.locale][value] || value}</option>`).join('');
  sessionTypeSelect.value = state.llmForm.session_type || 'native_oai';
}

function inferProtocolPreset(form) {
  const currentApiMode = String(form.api_mode || 'chat_completions').toLowerCase();
  const currentSessionType = String(form.session_type || 'native_oai').toLowerCase();
  const currentBaseUrl = String(form.apibase || '').trim().toLowerCase();
  for (const key of PROTOCOL_PRESET_OPTIONS) {
    if (key === 'custom') continue;
    const preset = PROTOCOL_PRESETS[key];
    if (!preset) continue;
    if (preset.sessionType !== currentSessionType) continue;
    if ((preset.api_mode || 'chat_completions') !== currentApiMode) continue;
    if ((preset.apibase || '').trim().toLowerCase() !== currentBaseUrl) continue;
    return key;
  }
  return 'custom';
}

function inferModelPreset(form) {
  const currentModel = String(form.model || '').trim().toLowerCase();
  for (const key of MODEL_PRESET_OPTIONS) {
    if (key === 'custom') continue;
    if ((MODEL_PRESETS[key]?.model || '').trim().toLowerCase() === currentModel) {
      return key;
    }
  }
  return 'custom';
}

function renderProtocolPresetOptions() {
  protocolPresetSelect.innerHTML = PROTOCOL_PRESET_OPTIONS.map((value) => `<option value="${value}">${PROTOCOL_PRESET_LABELS[state.locale][value] || value}</option>`).join('');
  protocolPresetSelect.value = state.llmForm.protocol_preset || 'custom';
}

function renderModelPresetOptions() {
  modelPresetSelect.innerHTML = MODEL_PRESET_OPTIONS.map((value) => `<option value="${value}">${MODEL_PRESET_LABELS[state.locale][value] || value}</option>`).join('');
  modelPresetSelect.value = state.llmForm.model_preset || 'custom';
}

function renderApiKeyToggle() {
  const isVisible = apiKeyInput.type === 'text';
  apiKeyToggle.textContent = isVisible ? t('hideSecret') : t('showSecret');
  apiKeyToggle.setAttribute('aria-pressed', isVisible ? 'true' : 'false');
  apiKeyToggle.setAttribute('aria-label', isVisible ? t('hideSecret') : t('showSecret'));
}

function syncPresetSelectionsFromFields() {
  state.llmForm.protocol_preset = inferProtocolPreset({
    session_type: sessionTypeSelect.value,
    api_mode: state.llmForm.api_mode || 'chat_completions',
    apibase: baseUrlInput.value.trim(),
  });
  state.llmForm.model_preset = inferModelPreset({ model: modelNameInput.value.trim() });
  renderProtocolPresetOptions();
  renderModelPresetOptions();
}

function applyProtocolPreset(presetKey) {
  const preset = PROTOCOL_PRESETS[presetKey] || PROTOCOL_PRESETS.custom;
  state.llmForm.protocol_preset = presetKey;
  state.llmForm.api_mode = preset.api_mode || 'chat_completions';
  if (presetKey === 'custom') {
    renderProtocolPresetOptions();
    return;
  }
  sessionTypeSelect.value = preset.sessionType;
  if (preset.provider) providerInput.value = preset.provider;
  if (preset.apibase) baseUrlInput.value = preset.apibase;
  renderProtocolPresetOptions();
}

function applyModelPreset(presetKey) {
  const preset = MODEL_PRESETS[presetKey] || MODEL_PRESETS.custom;
  state.llmForm.model_preset = presetKey;
  if (presetKey === 'custom') {
    renderModelPresetOptions();
    return;
  }
  if (preset.protocolPreset) {
    applyProtocolPreset(preset.protocolPreset);
  }
  if (preset.provider) providerInput.value = preset.provider;
  if (preset.model) modelNameInput.value = preset.model;
  if (preset.displayName) displayNameInput.value = preset.displayName;
  renderModelPresetOptions();
}

function mergeRemoteState(remote) {
  const incoming = remote || {};
  return {
    form: { ...DEFAULT_REMOTE_FORM, ...(incoming.form || {}) },
    configs: incoming.configs || [],
    active_connections: incoming.active_connections || [],
    connected: Boolean(incoming.connected),
  };
}

function hydrateSettings(data) {
  state.llmForm = { ...DEFAULT_LLM_FORM, ...(data.llm_form || {}) };
  state.llmForm.protocol_preset = state.llmForm.protocol_preset || inferProtocolPreset(state.llmForm);
  state.llmForm.model_preset = inferModelPreset(state.llmForm);
  state.workspace = {
    active: data.workspace?.active || null,
    workspaces: data.workspace?.workspaces || [],
    recent_folders: data.workspace?.recent_folders || [],
  };
  state.remote = mergeRemoteState(data.remote);
  if (data.models?.models) {
    state.models = data.models.models;
  }
  if (Number.isInteger(data.models?.current_index)) {
    state.currentModelIndex = data.models.current_index;
  }
  renderSettingsState();
}

function renderWorkspaceChoices() {
  const entries = [];
  const seen = new Set();
  if (state.workspace.active?.path) {
    entries.push({ path: state.workspace.active.path, name: state.workspace.active.name || '', label: `${t('currentWorkspace')}: ${state.workspace.active.path}` });
    seen.add(state.workspace.active.path);
  }
  (state.workspace.workspaces || []).forEach((item) => {
    if (!item.path || seen.has(item.path)) return;
    entries.push({ path: item.path, name: item.name || '', label: item.path });
    seen.add(item.path);
  });
  (state.workspace.recent_folders || []).forEach((path) => {
    if (!path || seen.has(path)) return;
    entries.push({ path, name: '', label: path });
    seen.add(path);
  });
  if (!entries.length) {
    workspaceList.innerHTML = `<div class="settings-empty">${t('noWorkspace')}</div>`;
    return;
  }
  workspaceList.innerHTML = entries.map((item) => `<button type="button" class="settings-chip-button" data-workspace-path="${escapeHtml(item.path)}" data-workspace-name="${escapeHtml(item.name)}">${escapeHtml(item.label)}</button>`).join('');
}

function renderRemoteChoices() {
  const configs = state.remote.configs || [];
  if (!configs.length) {
    remoteConfigList.innerHTML = `<div class="settings-empty">${t('noRemote')}</div>`;
    return;
  }
  remoteConfigList.innerHTML = configs.map((item) => {
    const connected = (state.remote.active_connections || []).includes(item.name);
    const label = `${item.name} · ${item.username}@${item.host}:${item.port} · ${connected ? t('connected') : t('disconnected')}`;
    return `<button type="button" class="settings-chip-button" data-remote-name="${escapeHtml(item.name || '')}" data-remote-host="${escapeHtml(item.host || '')}" data-remote-port="${escapeHtml(String(item.port || 22))}" data-remote-username="${escapeHtml(item.username || 'root')}">${escapeHtml(label)}</button>`;
  }).join('');
}

function renderSettingsState() {
  renderThemeOptions();
  renderLanguageOptions();
  renderModelOptions();
  renderSessionTypeOptions();
  renderProtocolPresetOptions();
  renderModelPresetOptions();

  providerInput.value = state.llmForm.provider || '';
  displayNameInput.value = state.llmForm.name || '';
  modelNameInput.value = state.llmForm.model || '';
  baseUrlInput.value = state.llmForm.apibase || '';
  apiKeyInput.value = state.llmForm.apikey || '';
  renderApiKeyToggle();

  workspaceNameInput.value = state.workspace.active?.name || '';
  workspacePathInput.value = state.workspace.active?.path || '';
  workspaceStatus.textContent = state.workspace.active?.path ? `${t('currentWorkspace')}: ${state.workspace.active.path}` : t('noWorkspace');
  renderWorkspaceChoices();

  const remoteForm = state.remote.form || DEFAULT_REMOTE_FORM;
  remoteEnabledInput.checked = Boolean(remoteForm.enabled);
  remoteNameInput.value = remoteForm.server_name || remoteForm.name || '';
  remoteHostInput.value = remoteForm.host || '';
  remotePortInput.value = String(remoteForm.port || 22);
  remoteUsernameInput.value = remoteForm.username || 'root';
  remotePasswordInput.value = remoteForm.password || '';
  remoteKeyPathInput.value = remoteForm.key_path || '';
  remoteCwdInput.value = remoteForm.cwd || '';
  remoteStatus.textContent = state.remote.connected && (remoteForm.server_name || remoteForm.name)
    ? `${t('currentRemote')}: ${remoteForm.server_name || remoteForm.name} · ${remoteForm.cwd || '~'}`
    : t('noRemote');
  renderRemoteChoices();
}

function applyLocale(locale, persist = true) {
  if (!LANGUAGE_OPTIONS.includes(locale)) return;
  state.locale = locale;
  if (persist) {
    window.localStorage.setItem('generic-coder-locale', locale);
  }
  syncDocumentLanguage();
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {
    node.setAttribute('placeholder', t(node.dataset.i18nPlaceholder));
  });
  renderSettingsState();
  setTheme(state.theme, false);
  renderMessages();
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderContent(text, streaming = false) {
  const escaped = escapeHtml(text || '...');
  const withCode = escaped.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  const withInline = withCode.replace(/`([^`]+)`/g, '<code>$1</code>');
  return `<div class="message-card__body${streaming ? ' is-streaming' : ''}">${withInline.replace(/\n/g, '<br />')}</div>`;
}

function roleLabel(role) {
  return role === 'user' ? t('userRole') : t('assistantRole');
}

function renderMessages() {
  feedEl.innerHTML = state.messages.map((message) => {
    const roleClass = message.role === 'user' ? 'message-card--user' : 'message-card--assistant';
    const streaming = Boolean(message.streaming);
    return `
      <article class="message-card ${roleClass}">
        <div class="message-card__meta">
          <span>${roleLabel(message.role)}</span>
        </div>
        ${renderContent(message.content, streaming)}
      </article>
    `;
  }).join('');

  messageCount.textContent = String(state.messages.length);
  feedEl.scrollTop = feedEl.scrollHeight;
  const lastAssistant = [...state.messages].reverse().find((item) => item.role === 'assistant' && !item.streaming);
  lastReplyTimeEl.textContent = String(lastAssistant ? Date.now() : 0);
}

function setRunning(isRunning) {
  state.isRunning = isRunning;
  statusLabel.textContent = isRunning ? t('running') : t('idle');
  statusDot.classList.toggle('is-live', isRunning);
  sendButton.disabled = isRunning;
  document.getElementById('stop-button').disabled = !isRunning;
  document.getElementById('new-chat-button').disabled = isRunning;
}

function showToast(message) {
  toastEl.textContent = message;
  toastEl.hidden = false;
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => {
    toastEl.hidden = true;
  }, 3200);
}

function setTheme(theme, persist = true) {
  state.theme = theme;
  document.body.dataset.theme = theme;
  themePill.textContent = THEME_LABELS[state.locale][theme] || theme;
  languagePill.textContent = I18N[state.locale].languageName;
  if (persist) {
    window.localStorage.setItem('generic-coder-theme', theme);
  }
}

async function loadBootstrap() {
  const res = await fetch('/api/bootstrap');
  const data = await res.json();
  state.messages = data.messages || [];
  modelLabel.textContent = data.model || t('modelOffline');
  state.currentModelIndex = Number.isInteger(data.model_index) ? data.model_index : 0;
  if (data.llm_form || data.workspace || data.remote) {
    hydrateSettings(data);
  }
  const storedTheme = window.localStorage.getItem('generic-coder-theme');
  const resolvedTheme = THEME_OPTIONS.includes(storedTheme) ? storedTheme : (data.theme || 'solarflare');
  setTheme(resolvedTheme, false);
  setRunning(Boolean(data.is_running));
  renderMessages();
  await loadModels();
  if (resolvedTheme !== data.theme) {
    await fetch('/api/theme', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ theme: resolvedTheme }),
    });
  }
}

async function loadModels() {
  const res = await fetch('/api/models');
  const data = await res.json();
  state.models = data.models || [];
  state.currentModelIndex = Number.isInteger(data.current_index) ? data.current_index : state.currentModelIndex;
  renderModelOptions();
}

async function loadSettings() {
  const res = await fetch('/api/settings');
  const data = await res.json();
  hydrateSettings(data);
}

async function updateTheme(event) {
  const theme = event.target.value;
  await fetch('/api/theme', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme }),
  });
  setTheme(theme);
  renderSettingsState();
}

async function updateModel(event) {
  const index = Number(event.target.value);
  const res = await fetch('/api/model', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ index }),
  });
  const data = await res.json();
  if (!res.ok) {
    showToast(data.error || t('modelSwitchError'));
    await loadModels();
    return;
  }
  state.currentModelIndex = data.current_index;
  modelLabel.textContent = data.model || t('modelOffline');
  renderModelOptions();
  showToast(`${t('modelSwitchOk')}: ${data.model}`);
}

function updateLanguage(event) {
  applyLocale(event.target.value);
}

async function saveLlmConfig() {
  const protocolPreset = protocolPresetSelect.value || 'custom';
  const preset = PROTOCOL_PRESETS[protocolPreset] || PROTOCOL_PRESETS.custom;
  const payload = {
    session_type: sessionTypeSelect.value,
    protocol_preset: protocolPreset,
    api_mode: preset.api_mode || 'chat_completions',
    provider: providerInput.value.trim(),
    name: displayNameInput.value.trim(),
    model: modelNameInput.value.trim(),
    apibase: baseUrlInput.value.trim(),
    apikey: apiKeyInput.value.trim(),
  };
  const res = await fetch('/api/llm-config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    showToast(data.error || t('llmSaveError'));
    return;
  }
  modelLabel.textContent = data.model || t('modelOffline');
  await loadSettings();
  showToast(t('llmSaveOk'));
}

async function saveWorkspace() {
  const payload = {
    name: workspaceNameInput.value.trim(),
    path: workspacePathInput.value.trim(),
  };
  const res = await fetch('/api/workspace', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    showToast(data.error || t('workspaceSaveError'));
    return;
  }
  state.workspace = {
    active: data.active || null,
    workspaces: data.workspaces || [],
    recent_folders: data.recent_folders || [],
  };
  renderSettingsState();
  showToast(t('workspaceSaveOk'));
}

async function connectRemote() {
  const payload = {
    enabled: remoteEnabledInput.checked,
    server_name: remoteNameInput.value.trim(),
    host: remoteHostInput.value.trim(),
    port: Number(remotePortInput.value || 22),
    username: remoteUsernameInput.value.trim() || 'root',
    password: remotePasswordInput.value,
    key_path: remoteKeyPathInput.value.trim(),
    cwd: remoteCwdInput.value.trim(),
  };
  const res = await fetch('/api/remote/connect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    showToast(data.error || t('remoteConnectError'));
    return;
  }
  state.remote = mergeRemoteState(data);
  renderSettingsState();
  showToast(data.message || t('remoteConnectOk'));
}

function addStreamingPlaceholder() {
  const placeholder = { role: 'assistant', content: '...', streaming: true };
  state.messages.push(placeholder);
  state.taskPlaceholderId = state.messages.length - 1;
  renderMessages();
}

async function pollTask(taskId) {
  try {
    while (true) {
      const res = await fetch(`/api/tasks/${taskId}`);
      const data = await res.json();
      if (typeof state.taskPlaceholderId === 'number') {
        state.messages[state.taskPlaceholderId] = {
          role: 'assistant',
          content: data.preview || '...',
          streaming: !data.done,
        };
        renderMessages();
      }
      if (data.done) {
        if (typeof state.taskPlaceholderId === 'number') {
          state.messages[state.taskPlaceholderId] = {
            role: 'assistant',
            content: data.final || data.preview || '...',
            streaming: false,
          };
        }
        state.pendingTaskId = null;
        state.taskPlaceholderId = null;
        setRunning(false);
        renderMessages();
        return;
      }
      await new Promise((resolve) => window.setTimeout(resolve, 700));
    }
  } catch (error) {
    setRunning(false);
    showToast(`${t('pollingError')}: ${error.message}`);
  }
}

async function sendPrompt(prompt) {
  const trimmed = prompt.trim();
  if (!trimmed || state.isRunning) return;

  state.messages.push({ role: 'user', content: trimmed, streaming: false });
  renderMessages();
  composerEl.value = '';
  setRunning(true);

  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: trimmed }),
  });
  const data = await res.json();

  if (data.handled) {
    state.messages = data.messages || state.messages;
    setRunning(false);
    renderMessages();
    if (data.notice) showToast(data.notice);
    return;
  }

  if (!data.task_id) {
    setRunning(false);
    showToast(data.error || t('requestError'));
    return;
  }

  state.pendingTaskId = data.task_id;
  addStreamingPlaceholder();
  pollTask(data.task_id);
}

async function loadSessions() {
  const res = await fetch('/api/sessions');
  const data = await res.json();
  const items = data.sessions || [];
  if (!items.length) {
    sessionsList.innerHTML = `<div class="session-item"><div class="session-item__preview">${t('noSessions')}</div></div>`;
    return;
  }

  sessionsList.innerHTML = items.map((item) => `
    <article class="session-item">
      <div>
        <div class="session-item__meta">
          <span class="session-chip">#${item.index}</span>
          <span class="session-chip">${t('rounds')(item.rounds)}</span>
          <span class="session-chip">${escapeHtml(item.relative_time)}</span>
        </div>
        <div class="session-item__preview">${escapeHtml(item.preview || '无法预览')}</div>
      </div>
      <button class="session-item__action" data-session-index="${item.index}">${t('sessions')}</button>
    </article>
  `).join('');
}

async function stopTask() {
  await fetch('/api/stop', { method: 'POST' });
  showToast(t('stopSent'));
}

composerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  await sendPrompt(composerEl.value);
});

composerEl.addEventListener('keydown', async (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    await sendPrompt(composerEl.value);
  }
});

themeSelect.addEventListener('change', updateTheme);
languageSelect.addEventListener('change', updateLanguage);
modelSelect.addEventListener('change', updateModel);
protocolPresetSelect.addEventListener('change', (event) => applyProtocolPreset(event.target.value));
modelPresetSelect.addEventListener('change', (event) => applyModelPreset(event.target.value));
sessionTypeSelect.addEventListener('change', syncPresetSelectionsFromFields);
providerInput.addEventListener('input', syncPresetSelectionsFromFields);
modelNameInput.addEventListener('input', syncPresetSelectionsFromFields);
baseUrlInput.addEventListener('input', syncPresetSelectionsFromFields);
apiKeyToggle.addEventListener('click', () => {
  apiKeyInput.type = apiKeyInput.type === 'password' ? 'text' : 'password';
  renderApiKeyToggle();
});
saveLlmButton.addEventListener('click', saveLlmConfig);
saveWorkspaceButton.addEventListener('click', saveWorkspace);
connectRemoteButton.addEventListener('click', connectRemote);

document.getElementById('new-chat-button').addEventListener('click', async () => sendPrompt('/new'));
document.getElementById('session-button').addEventListener('click', async () => {
  await loadSessions();
  sessionsDialog.showModal();
});
document.getElementById('stop-button').addEventListener('click', stopTask);
document.getElementById('settings-button').addEventListener('click', async () => {
  await loadSettings();
  settingsDialog.showModal();
});
document.getElementById('close-sessions').addEventListener('click', () => sessionsDialog.close());
document.getElementById('close-settings').addEventListener('click', () => settingsDialog.close());

workspaceList.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-workspace-path]');
  if (!button) return;
  workspacePathInput.value = button.dataset.workspacePath || '';
  workspaceNameInput.value = button.dataset.workspaceName || '';
  await saveWorkspace();
});

remoteConfigList.addEventListener('click', (event) => {
  const button = event.target.closest('[data-remote-name]');
  if (!button) return;
  remoteNameInput.value = button.dataset.remoteName || '';
  remoteHostInput.value = button.dataset.remoteHost || '';
  remotePortInput.value = button.dataset.remotePort || '22';
  remoteUsernameInput.value = button.dataset.remoteUsername || 'root';
});

sessionsList.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-session-index]');
  if (!button) return;
  sessionsDialog.close();
  await sendPrompt(`/continue ${button.dataset.sessionIndex}`);
});

window.addEventListener('click', (event) => {
  if (event.target === sessionsDialog) {
    sessionsDialog.close();
  }
  if (event.target === settingsDialog) {
    settingsDialog.close();
  }
});

applyLocale(preferredLocale(), false);
loadBootstrap().catch((error) => {
  showToast(`启动失败: ${error.message}`);
});
