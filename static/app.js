// ==========================================
// AGP PUBLISHER DASHBOARD APP (VANILLA JS)
// ==========================================

const API_BASE = ""; // Rotas relativas (mesmo host)
let currentUser = null;
let systemConfig = null;
let currentTheme = localStorage.getItem("theme") || "light";

// ==========================================
// INICIALIZAÇÃO E CONTROLE DE ESTADO
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  checkAuth();
  setupEventListeners();
});

function initTheme() {
  document.documentElement.setAttribute("data-theme", currentTheme);
  const btn = document.getElementById("btn-theme-toggle");
  if (btn) btn.innerText = currentTheme === "dark" ? "☀️" : "🌙";
}

function checkAuth() {
  const token = localStorage.getItem("token");
  if (token) {
    fetchUserData();
  } else {
    showLogin();
  }
}

async function fetchUserData() {
  try {
    const res = await apiFetch("/api/auth/me");
    if (res) {
      currentUser = res;
      document.getElementById("profile-username").innerText = currentUser.username;
      document.getElementById("profile-plan").innerText = currentUser.plan_type.replace("_", " ");
      
      // Se for admin, exibe a guia administrativa
      if (currentUser.role === "admin") {
        document.querySelectorAll(".admin-only").forEach(el => el.style.display = "block");
      } else {
        document.querySelectorAll(".admin-only").forEach(el => el.style.display = "none");
      }
      
      // Carrega white-label e configurações globais
      await fetchSystemConfig();
      
      // Exibe painel principal
      document.getElementById("login-section").style.display = "none";
      document.getElementById("sidebar-section").style.display = "flex";
      document.getElementById("main-section").style.display = "block";
      
      // Carrega dados da tela padrão (Dashboard)
      switchPage("dashboard-page");
    } else {
      logout();
    }
  } catch (err) {
    console.error("Erro ao obter dados do usuário:", err);
    logout();
  }
}

async function fetchSystemConfig() {
  try {
    const cfg = await apiFetch("/api/admin/config");
    if (cfg) {
      systemConfig = cfg;
      // Aplica white-label (Nome, Logo)
      document.title = `${systemConfig.company_name} - Painel SaaS`;
      
      // Atualiza imagens de logo
      const logoImgs = [
        document.getElementById("login-logo-img"),
        document.getElementById("sidebar-logo-img"),
        document.getElementById("favicon-link")
      ];
      logoImgs.forEach(img => {
        if (img) {
          if (img.tagName === "LINK") {
            img.href = systemConfig.logo_path;
          } else {
            img.src = systemConfig.logo_path;
          }
        }
      });
      
      // Aplica cores personalizadas do Admin
      document.documentElement.style.setProperty("--primary-color", systemConfig.theme_color_primary);
      document.documentElement.style.setProperty("--secondary-color", systemConfig.theme_color_secondary);
      
      // Preenche os campos do Admin se estiver na tela de config
      const companyNameInput = document.getElementById("admin-company-name");
      if (companyNameInput) {
        companyNameInput.value = systemConfig.company_name;
        document.getElementById("admin-color-primary").value = systemConfig.theme_color_primary;
        document.getElementById("admin-color-secondary").value = systemConfig.theme_color_secondary;
        document.getElementById("admin-evolution-url").value = systemConfig.evolution_url || "";
        document.getElementById("admin-evolution-token").value = systemConfig.evolution_token || "";
      }
    }
  } catch (err) {
    console.error("Erro ao carregar configurações do sistema:", err);
  }
}

function showLogin() {
  document.getElementById("login-section").style.display = "flex";
  document.getElementById("sidebar-section").style.display = "none";
  document.getElementById("main-section").style.display = "none";
  currentUser = null;
}

function logout() {
  localStorage.removeItem("token");
  showLogin();
}

// ==========================================
// ROTEAMENTO DE TELA (NAGEVAÇÃO SIDEBAR)
// ==========================================

function switchPage(pageId) {
  // Desativa todas as telas
  document.querySelectorAll(".page-section").forEach(sec => sec.classList.remove("active"));
  
  // Ativa a tela escolhida
  const targetPage = document.getElementById(pageId);
  if (targetPage) {
    targetPage.classList.add("active");
  }
  
  // Atualiza menu active
  document.querySelectorAll(".sidebar-menu .menu-item").forEach(item => {
    if (item.getAttribute("data-target") === pageId) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  // Carrega dados específicos da tela
  if (pageId === "dashboard-page") {
    loadDashboardData();
  } else if (pageId === "topics-page") {
    loadTopicsData();
  } else if (pageId === "whatsapp-page") {
    loadWhatsappQRCode();
  } else if (pageId === "history-page") {
    loadHistoryData();
  } else if (pageId === "admin-page") {
    loadAdminData();
  }
}

// ==========================================
// CARREGAMENTO E RENDERIZAÇÃO DE DADOS
// ==========================================

async function loadDashboardData() {
  try {
    const topics = await apiFetch("/api/topics");
    const tokens = await apiFetch("/api/tokens/usage");
    const history = await apiFetch("/api/history");

    // Tópicos ativos
    const activeCount = topics ? topics.filter(t => t.is_active === 1).length : 0;
    document.getElementById("stat-active-topics").innerText = activeCount;

    // Tokens consumidos
    let totalTokens = 0;
    if (tokens) {
      // Filtrar tokens do mês atual
      const now = new Date();
      const currentMonthLogs = tokens.filter(log => {
        const logDate = new Date(log.timestamp);
        return logDate.getMonth() === now.getMonth() && logDate.getFullYear() === now.getFullYear();
      });
      totalTokens = currentMonthLogs.reduce((acc, log) => acc + log.total_tokens, 0);
    }
    document.getElementById("stat-tokens-used").innerText = totalTokens.toLocaleString();
    document.getElementById("stat-tokens-limit").innerText = currentUser ? currentUser.max_tokens_monthly_limit.toLocaleString() : "100.000";

    // Publicações enviadas (Sucesso)
    const successPubs = history ? history.filter(h => h.status === "success").length : 0;
    document.getElementById("stat-pub-sent").innerText = successPubs;

    // Alerta de Free Trial
    const trialAlert = document.getElementById("trial-alert");
    if (currentUser && currentUser.plan_type === "free_trial") {
      trialAlert.style.display = "inline-block";
      trialAlert.innerText = "Free Trial";
    } else {
      if (trialAlert) trialAlert.style.display = "none";
    }

    // Tabela de Logs Recentes
    const tbody = document.getElementById("token-logs-table-body");
    tbody.innerHTML = "";
    if (tokens && tokens.length > 0) {
      tokens.slice(-5).reverse().forEach(log => {
        const tr = document.createElement("tr");
        const topicName = topics.find(t => t.id === log.topic_id)?.topic_name || "Daily AI Group";
        tr.innerHTML = `
          <td><strong>${topicName}</strong></td>
          <td><span class="status-badge status-warning">${log.model_used || "pro"}</span></td>
          <td>${log.prompt_tokens.toLocaleString()}</td>
          <td>${log.completion_tokens.toLocaleString()}</td>
          <td><strong>${log.total_tokens.toLocaleString()}</strong></td>
          <td>${new Date(log.timestamp).toLocaleString("pt-BR")}</td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Nenhum consumo registrado.</td></tr>`;
    }

  } catch (err) {
    console.error("Erro ao carregar dados do dashboard:", err);
  }
}

async function loadTopicsData() {
  try {
    const topics = await apiFetch("/api/topics");
    const tbody = document.getElementById("topics-table-body");
    tbody.innerHTML = "";

    if (topics && topics.length > 0) {
      topics.forEach(t => {
        const tr = document.createElement("tr");
        
        let schedText = "";
        if (t.schedule_type === "fixed") {
          schedText = `⏰ Diário às ${t.fixed_time}`;
        } else {
          schedText = `🎲 Janela ${t.random_range_start} - ${t.random_range_end} (Aleatório)`;
        }

        tr.innerHTML = `
          <td><strong>${t.topic_name}</strong><br><small style="color: var(--text-muted);">${t.search_query.substring(0, 40)}...</small></td>
          <td><code>${t.whatsapp_target}</code></td>
          <td>${schedText}</td>
          <td><span class="status-badge status-warning">${t.preferred_model}</span></td>
          <td>
            <label class="switch">
              <input type="checkbox" ${t.is_active === 1 ? 'checked' : ''} onchange="toggleTopicActive(${t.id}, this.checked)">
              <span class="slider"></span>
            </label>
          </td>
          <td>
            <div class="action-buttons">
              <button class="btn-icon" onclick="triggerTopicRun(${t.id})" title="Enviar Agora / Testar">🚀</button>
              <button class="btn-icon" onclick="openEditTopicModal(${JSON.stringify(t).replace(/"/g, '&quot;')})" title="Editar">✏️</button>
              <button class="btn-icon" onclick="deleteTopic(${t.id})" title="Excluir" style="color: var(--error);">🗑️</button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Nenhum tópico criado. Clique em '+ Novo Tópico' para começar.</td></tr>`;
    }
  } catch (err) {
    console.error("Erro ao carregar tópicos:", err);
  }
}

async function toggleTopicActive(topicId, isActive) {
  try {
    await apiFetch(`/api/topics/${topicId}`, {
      method: "PUT",
      body: JSON.stringify({ is_active: isActive ? 1 : 0 })
    });
    showToast("Status do tópico atualizado.");
  } catch (err) {
    console.error("Erro ao alterar status do tópico:", err);
  }
}

async function triggerTopicRun(topicId) {
  try {
    showToast("Executando pipeline em segundo plano...");
    await apiFetch(`/api/topics/${topicId}/run`, { method: "POST" });
  } catch (err) {
    console.error("Erro ao forçar execução:", err);
  }
}

async function deleteTopic(topicId) {
  if (!confirm("Tem certeza que deseja excluir este tópico de pesquisa?")) return;
  try {
    await apiFetch(`/api/topics/${topicId}`, { method: "DELETE" });
    showToast("Tópico deletado com sucesso.");
    loadTopicsData();
  } catch (err) {
    console.error("Erro ao deletar tópico:", err);
  }
}

async function loadWhatsappQRCode() {
  const qrImage = document.getElementById("qrcode-image");
  const statusBadge = document.getElementById("wa-status-badge");
  
  qrImage.src = "";
  statusBadge.innerText = "Carregando status...";
  statusBadge.className = "status-badge status-warning";

  try {
    const data = await apiFetch("/api/whatsapp/connect");
    if (data) {
      if (data.status === "connected") {
        qrImage.src = "https://placehold.co/200x200/10b981/ffffff?text=CONECTADO";
        statusBadge.innerText = "WhatsApp Conectado";
        statusBadge.className = "status-badge status-success";
      } else {
        qrImage.src = data.qrcode;
        statusBadge.innerText = "Aguardando Leitura";
        statusBadge.className = "status-badge status-warning";
      }
    }
  } catch (err) {
    console.error("Erro ao obter QR code:", err);
    statusBadge.innerText = "Erro ao Conectar";
    statusBadge.className = "status-badge status-error";
  }
}

async function loadHistoryData() {
  try {
    const history = await apiFetch("/api/history");
    const tbody = document.getElementById("history-table-body");
    tbody.innerHTML = "";

    if (history && history.length > 0) {
      history.reverse().forEach(h => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${h.topic_name || "Daily AI Group"}</strong></td>
          <td>${new Date(h.sent_at).toLocaleString("pt-BR")}</td>
          <td><span class="status-badge ${h.status === 'success' ? 'status-success' : 'status-error'}">${h.status}</span></td>
          <td><small style="color: var(--text-muted);">${h.error_message || "Enviado com sucesso"}</small></td>
          <td>
            ${h.status === 'success' ? `<a href="/${h.pdf_path}" target="_blank" class="btn-icon" style="text-decoration: none; width: auto; display: inline-flex; gap: 0.25rem; font-size: 0.8rem; padding: 0.35rem 0.75rem;">📥 Baixar PDF</a>` : '-'}
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Nenhum relatório enviado no histórico.</td></tr>`;
    }
  } catch (err) {
    console.error("Erro ao buscar histórico:", err);
  }
}

async function loadAdminData() {
  await fetchSystemConfig();
  loadAdminUsers();
}

async function loadAdminUsers() {
  try {
    const users = await apiFetch("/api/admin/users");
    const tbody = document.getElementById("admin-users-table-body");
    tbody.innerHTML = "";

    if (users && users.length > 0) {
      users.forEach(u => {
        const tr = document.createElement("tr");
        const expDate = u.trial_ends_at ? new Date(u.trial_ends_at).toLocaleDateString("pt-BR") : "N/A";
        
        tr.innerHTML = `
          <td><strong>${u.username}</strong></td>
          <td><span class="status-badge status-warning">${u.role}</span></td>
          <td><span class="status-badge status-success">${u.plan_type}</span></td>
          <td>Tópicos: ${u.max_topics_limit} | Tokens: ${u.max_tokens_monthly_limit.toLocaleString()}</td>
          <td>${expDate}</td>
          <td>
            <div class="action-buttons">
              <button class="btn-icon" onclick="openEditUserModal(${JSON.stringify(u).replace(/"/g, '&quot;')})" title="Editar">✏️</button>
              <button class="btn-icon" onclick="deleteUser(${u.id})" title="Excluir" style="color: var(--error);">🗑️</button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("Erro ao listar usuários:", err);
  }
}

async function deleteUser(userId) {
  if (!confirm("Tem certeza que deseja deletar este usuário?")) return;
  try {
    await apiFetch(`/api/admin/users/${userId}`, { method: "DELETE" });
    showToast("Usuário deletado.");
    loadAdminUsers();
  } catch (err) {
    console.error("Erro ao deletar usuário:", err);
  }
}

// ==========================================
// MODAIS E SUBMISSÕES DE FORMULÁRIO
// ==========================================

function openModal(modalId) {
  document.getElementById(modalId).classList.add("active");
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove("active");
}

function openEditTopicModal(topic) {
  document.getElementById("topic-modal-title").innerText = "Editar Tópico de Pesquisa";
  document.getElementById("topic-id-hidden").value = topic.id;
  document.getElementById("topic-name").value = topic.topic_name;
  document.getElementById("topic-query").value = topic.search_query;
  document.getElementById("topic-target").value = topic.whatsapp_target;
  document.getElementById("topic-model").value = topic.preferred_model;
  document.getElementById("topic-custom-key").value = topic.custom_gemini_key || "";
  
  const typeSelect = document.getElementById("topic-schedule-type");
  typeSelect.value = topic.schedule_type;
  
  if (topic.schedule_type === "fixed") {
    document.getElementById("schedule-fixed-fields").style.display = "block";
    document.getElementById("schedule-random-fields").style.display = "none";
    document.getElementById("topic-fixed-time").value = topic.fixed_time || "08:00";
  } else {
    document.getElementById("schedule-fixed-fields").style.display = "none";
    document.getElementById("schedule-random-fields").style.display = "grid";
    document.getElementById("topic-range-start").value = topic.random_range_start || "08:00";
    document.getElementById("topic-range-end").value = topic.random_range_end || "10:00";
  }
  
  openModal("topic-modal");
}

function openEditUserModal(user) {
  document.getElementById("user-modal-title").innerText = "Editar Usuário";
  document.getElementById("user-id-hidden").value = user.id;
  document.getElementById("user-username").value = user.username;
  document.getElementById("user-password").value = ""; // Senha em branco para manter a atual
  document.getElementById("user-role").value = user.role;
  document.getElementById("user-plan").value = user.plan_type;
  document.getElementById("user-max-topics").value = user.max_topics_limit;
  document.getElementById("user-max-tokens").value = user.max_tokens_monthly_limit;
  
  openModal("user-modal");
}

// ==========================================
// EVENT LISTENERS E ASSINATURAS
// ==========================================

function setupEventListeners() {
  // Theme toggle
  document.getElementById("btn-theme-toggle").addEventListener("click", () => {
    currentTheme = currentTheme === "dark" ? "light" : "dark";
    localStorage.setItem("theme", currentTheme);
    initTheme();
  });

  // Sidebar links
  document.querySelectorAll(".sidebar-menu .menu-item").forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const target = item.getAttribute("data-target");
      if (target) switchPage(target);
    });
  });

  // Logout
  document.getElementById("btn-logout").addEventListener("click", (e) => {
    e.preventDefault();
    logout();
  });

  // Alternar registro e login
  let isRegistering = false;
  document.getElementById("switch-to-register").addEventListener("click", (e) => {
    e.preventDefault();
    isRegistering = !isRegistering;
    if (isRegistering) {
      document.getElementById("login-title").innerText = "Registre seu Free Trial";
      document.getElementById("login-subtitle").innerText = "Ganhe 7 dias e 100.000 tokens grátis.";
      document.getElementById("login-submit-btn").innerText = "Registrar-se";
      document.getElementById("login-footer-text").innerHTML = 'Já tem conta? <a href="#" id="switch-to-register">Faça Login</a>';
    } else {
      document.getElementById("login-title").innerText = "Acesse sua Conta";
      document.getElementById("login-subtitle").innerText = "Entre com seus dados para gerenciar suas publicações.";
      document.getElementById("login-submit-btn").innerText = "Entrar";
      document.getElementById("login-footer-text").innerHTML = 'Não tem conta? <a href="#" id="switch-to-register">Registre-se no Free Trial</a>';
    }
    // Re-bind click
    setupEventListeners();
  });

  // Login/Register Submit
  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const user = document.getElementById("login-username").value;
    const pass = document.getElementById("login-password").value;
    
    if (isRegistering) {
      // Registro de conta trial
      try {
        const res = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: user, password: pass })
        });
        if (!res.ok) {
          const err = await res.json();
          alert("Falha ao registrar: " + (err.detail || "Usuário já existe"));
          return;
        }
        showToast("Registro concluído! Faça login agora.");
        isRegistering = false;
        document.getElementById("switch-to-register").click();
      } catch (err) {
        alert("Erro na conexão.");
      }
    } else {
      // Login tradicional
      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: user, password: pass })
        });
        if (!res.ok) {
          alert("Login inválido.");
          return;
        }
        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        fetchUserData();
      } catch (err) {
        alert("Erro na conexão.");
      }
    }
  });

  // WhatsApp Connect QR Code refresh
  document.getElementById("btn-refresh-qrcode").addEventListener("click", () => {
    loadWhatsappQRCode();
  });

  // Modais de criação
  document.getElementById("btn-add-topic").addEventListener("click", () => {
    document.getElementById("topic-modal-title").innerText = "Novo Tópico de Pesquisa";
    document.getElementById("topic-id-hidden").value = "";
    document.getElementById("topic-form").reset();
    document.getElementById("schedule-fixed-fields").style.display = "block";
    document.getElementById("schedule-random-fields").style.display = "none";
    openModal("topic-modal");
  });

  document.getElementById("btn-add-user").addEventListener("click", () => {
    document.getElementById("user-modal-title").innerText = "Novo Usuário";
    document.getElementById("user-id-hidden").value = "";
    document.getElementById("user-form").reset();
    openModal("user-modal");
  });

  // Toggle do Tipo de Agendamento no Formulário
  document.getElementById("topic-schedule-type").addEventListener("change", (e) => {
    if (e.target.value === "fixed") {
      document.getElementById("schedule-fixed-fields").style.display = "block";
      document.getElementById("schedule-random-fields").style.display = "none";
    } else {
      document.getElementById("schedule-fixed-fields").style.display = "none";
      document.getElementById("schedule-random-fields").style.display = "grid";
    }
  });

  // Submissão do Tópico (Criar/Editar)
  document.getElementById("topic-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("topic-id-hidden").value;
    
    const topicData = {
      topic_name: document.getElementById("topic-name").value,
      search_query: document.getElementById("topic-query").value,
      whatsapp_target: document.getElementById("topic-target").value,
      preferred_model: document.getElementById("topic-model").value,
      custom_gemini_key: document.getElementById("topic-custom-key").value || null,
      schedule_type: document.getElementById("topic-schedule-type").value,
      fixed_time: document.getElementById("topic-fixed-time").value,
      random_range_start: document.getElementById("topic-range-start").value,
      random_range_end: document.getElementById("topic-range-end").value
    };

    try {
      if (id) {
        // Edit
        await apiFetch(`/api/topics/${id}`, {
          method: "PUT",
          body: JSON.stringify(topicData)
        });
        showToast("Tópico atualizado.");
      } else {
        // Create
        await apiFetch("/api/topics", {
          method: "POST",
          body: JSON.stringify(topicData)
        });
        showToast("Tópico criado.");
      }
      closeModal("topic-modal");
      loadTopicsData();
    } catch (err) {
      alert("Falha ao salvar tópico: " + err.message);
    }
  });

  // Submissão do Usuário (Criar/Editar)
  document.getElementById("user-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("user-id-hidden").value;
    
    const userData = {
      username: document.getElementById("user-username").value,
      password: document.getElementById("user-password").value || null,
      role: document.getElementById("user-role").value,
      plan_type: document.getElementById("user-plan").value,
      max_topics_limit: parseInt(document.getElementById("user-max-topics").value),
      max_tokens_monthly_limit: parseInt(document.getElementById("user-max-tokens").value)
    };

    try {
      if (id) {
        await apiFetch(`/api/admin/users/${id}`, {
          method: "PUT",
          body: JSON.stringify(userData)
        });
        showToast("Usuário atualizado com sucesso.");
      } else {
        await apiFetch("/api/auth/register", {
          method: "POST",
          body: JSON.stringify(userData)
        });
        showToast("Usuário criado com sucesso.");
      }
      closeModal("user-modal");
      loadAdminUsers();
    } catch (err) {
      alert("Falha ao salvar usuário: " + err.message);
    }
  });

  // Admin Config Form Submit
  document.getElementById("admin-config-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const configData = {
      company_name: document.getElementById("admin-company-name").value,
      theme_color_primary: document.getElementById("admin-color-primary").value,
      theme_color_secondary: document.getElementById("admin-color-secondary").value,
      evolution_url: document.getElementById("admin-evolution-url").value,
      evolution_token: document.getElementById("admin-evolution-token").value
    };

    try {
      await apiFetch("/api/admin/config", {
        method: "PUT",
        body: JSON.stringify(configData)
      });
      showToast("Configurações salvas.");
      await fetchSystemConfig();
    } catch (err) {
      alert("Falha ao salvar configurações: " + err.message);
    }
  });

  // Logo file upload handler
  document.getElementById("admin-logo").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const res = await fetch("/api/admin/logo", {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + localStorage.getItem("token")
        },
        body: formData
      });
      if (res.ok) {
        showToast("Logo atualizada com sucesso.");
        await fetchSystemConfig();
      } else {
        alert("Falha ao enviar logo.");
      }
    } catch (err) {
      console.error(err);
    }
  });

  // Seletores de cores pré-definidos (White-label)
  document.querySelectorAll(".palette-item").forEach(item => {
    item.addEventListener("click", () => {
      document.querySelectorAll(".palette-item").forEach(p => p.classList.remove("active"));
      item.classList.add("active");
      
      const pColor = item.getAttribute("data-primary");
      const sColor = item.getAttribute("data-secondary");
      
      document.getElementById("admin-color-primary").value = pColor;
      document.getElementById("admin-color-secondary").value = sColor;
    });
  });
}

// ==========================================
// UTILITÁRIOS DA API E UI
// ==========================================

async function apiFetch(url, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...options.headers
  };
  
  if (token) {
    headers["Authorization"] = "Bearer " + token;
  }
  
  const res = await fetch(url, { ...options, headers });
  
  if (res.status === 401) {
    logout();
    throw new Error("Sessão expirada.");
  }
  
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro na chamada da API.");
  }
  
  return res.status !== 204 ? await res.json() : null;
}

function showToast(message) {
  // Cria um pequeno elemento flutuante temporário
  const toast = document.createElement("div");
  toast.innerText = message;
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.right = "20px";
  toast.style.backgroundColor = "var(--primary-color)";
  toast.style.color = "#fff";
  toast.style.padding = "10px 20px";
  toast.style.borderRadius = "8px";
  toast.style.boxShadow = "0 4px 6px rgba(0,0,0,0.15)";
  toast.style.zIndex = "9999";
  toast.style.fontWeight = "600";
  toast.style.fontFamily = "inherit";
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 3000);
}
