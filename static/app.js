// ==========================================
// AGP PUBLISHER DASHBOARD APP (VANILLA JS)
// ==========================================

const API_BASE = ""; 
let currentUser = null;
let systemConfig = null;
let currentTheme = localStorage.getItem("theme") || "light";
let activeGroupId = null; // Grupo de e-mail selecionado no momento

// ==========================================
// INICIALIZAÇÃO E CONTROLE DE ESTADO
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  checkAuth();
  setupEventListeners();
  
  // Roteamento via Hash no carregamento inicial
  window.addEventListener("hashchange", () => {
    const pageId = window.location.hash.replace("#", "");
    if (pageId && currentUser) {
      switchPage(pageId);
    }
  });
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
      
      if (currentUser.role === "admin") {
        document.querySelectorAll(".admin-only").forEach(el => el.style.display = "block");
      } else {
        document.querySelectorAll(".admin-only").forEach(el => el.style.display = "none");
      }
      
      await fetchSystemConfig();
      
      document.getElementById("login-section").style.display = "none";
      document.getElementById("sidebar-section").style.display = "flex";
      document.getElementById("main-section").style.display = "block";
      
      // Carrega página pelo Hash da URL ou default para Dashboard
      const currentHash = window.location.hash.replace("#", "");
      const allowedPages = ["dashboard-page", "topics-page", "emails-page", "whatsapp-page", "history-page", "models-page", "admin-page"];
      const targetPage = allowedPages.includes(currentHash) ? currentHash : "dashboard-page";
      
      switchPage(targetPage);
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
      document.title = `${systemConfig.company_name} - Painel SaaS`;
      
      const mobileBrand = document.getElementById("mobile-company-name");
      if (mobileBrand) mobileBrand.innerText = systemConfig.company_name;
      
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
      
      // Aplica variáveis de cor nativas do White-Label
      document.documentElement.style.setProperty("--primary-color", systemConfig.theme_color_primary);
      document.documentElement.style.setProperty("--secondary-color", systemConfig.theme_color_secondary);
      
      // Preenche campos do painel admin
      const companyNameInput = document.getElementById("admin-company-name");
      if (companyNameInput) {
        companyNameInput.value = systemConfig.company_name;
        document.getElementById("admin-color-primary").value = systemConfig.theme_color_primary;
        document.getElementById("admin-color-secondary").value = systemConfig.theme_color_secondary;
        document.getElementById("admin-evolution-url").value = systemConfig.evolution_url || "";
        document.getElementById("admin-evolution-token").value = systemConfig.evolution_token || "";
        
        // SMTP
        document.getElementById("admin-smtp-host").value = systemConfig.smtp_host || "";
        document.getElementById("admin-smtp-port").value = systemConfig.smtp_port || "587";
        document.getElementById("admin-smtp-user").value = systemConfig.smtp_user || "";
        document.getElementById("admin-smtp-pass").value = systemConfig.smtp_pass || "";
        document.getElementById("admin-smtp-sender").value = systemConfig.smtp_sender || "";
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
  window.location.hash = "";
  showLogin();
}

// ==========================================
// ROTEAMENTO DE TELA (NAVEGAÇÃO SIDEBAR)
// ==========================================

function switchPage(pageId) {
  window.location.hash = pageId;
  
  document.querySelectorAll(".page-section").forEach(sec => sec.classList.remove("active"));
  
  const targetPage = document.getElementById(pageId);
  if (targetPage) {
    targetPage.classList.add("active");
  }
  
  document.querySelectorAll(".sidebar-menu .menu-item").forEach(item => {
    if (item.getAttribute("data-target") === pageId) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  // Carrega dados específicos da tela ativa
  if (pageId === "dashboard-page") {
    loadDashboardData();
  } else if (pageId === "topics-page") {
    loadTopicsData();
  } else if (pageId === "emails-page") {
    loadEmailsPageData();
  } else if (pageId === "whatsapp-page") {
    loadWhatsappQRCode();
  } else if (pageId === "history-page") {
    loadHistoryData();
  } else if (pageId === "models-page") {
    loadModelsData();
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

    const activeCount = topics ? topics.filter(t => t.is_active === 1).length : 0;
    document.getElementById("stat-active-topics").innerText = activeCount;

    let totalTokens = 0;
    if (tokens) {
      const now = new Date();
      const currentMonthLogs = tokens.filter(log => {
        const logDate = new Date(log.timestamp);
        return logDate.getMonth() === now.getMonth() && logDate.getFullYear() === now.getFullYear();
      });
      totalTokens = currentMonthLogs.reduce((acc, log) => acc + log.total_tokens, 0);
    }
    document.getElementById("stat-tokens-used").innerText = totalTokens.toLocaleString();
    document.getElementById("stat-tokens-limit").innerText = currentUser ? currentUser.max_tokens_monthly_limit.toLocaleString() : "100.000";

    const successPubs = history ? history.filter(h => h.status === "success").length : 0;
    document.getElementById("stat-pub-sent").innerText = successPubs;

    const trialAlert = document.getElementById("trial-alert");
    if (currentUser && currentUser.plan_type === "free_trial") {
      trialAlert.style.display = "inline-block";
      trialAlert.innerText = "Free Trial";
    } else {
      if (trialAlert) trialAlert.style.display = "none";
    }

    // Renderiza Logs de Consumo
    const tbody = document.getElementById("token-logs-table-body");
    tbody.innerHTML = "";
    if (tokens && tokens.length > 0) {
      tokens.slice(-10).reverse().forEach(log => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${escapeHtml(log.topic_id ? `Tópico #${log.topic_id}` : "N/A")}</td>
          <td><span class="status-badge" style="background-color: var(--secondary-color); color: white;">${escapeHtml(log.model_used || "N/A")}</span></td>
          <td>${log.prompt_tokens.toLocaleString()}</td>
          <td>${log.completion_tokens.toLocaleString()}</td>
          <td><strong>${log.total_tokens.toLocaleString()}</strong></td>
          <td>${new Date(log.timestamp).toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Nenhum consumo recente.</td></tr>`;
    }
  } catch (err) {
    console.error("Erro ao carregar Dashboard:", err);
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
        const intervalText = {
          "daily": "Diário",
          "weekly": "Semanal",
          "biweekly": "Quinzenal",
          "monthly": "Mensal"
        }[t.schedule_interval] || t.schedule_interval;
        
        tr.innerHTML = `
          <td><strong>${escapeHtml(t.topic_name)}</strong>${t.is_public ? ' <span class="status-badge status-success" style="font-size:0.7rem; padding: 1px 4px;">Público</span>' : ''}</td>
          <td><span class="status-badge" style="background-color:var(--border-color); color:var(--text-color);">${escapeHtml(t.whatsapp_target || "Apenas E-mail")}</span></td>
          <td>${escapeHtml(intervalText)} (${t.schedule_type === 'random' ? 'Janela' : escapeHtml(t.fixed_time)})</td>
          <td><span style="font-size: 0.85rem; color: var(--text-muted);">Cole: ${t.collector_model_id ? 'Config' : 'Nativo'} | Red: ${t.writer_model_id ? 'Config' : 'Nativo'}</span></td>
          <td><span class="status-badge ${t.is_active ? 'status-success' : 'status-warning'}">${t.is_active ? 'Ativo' : 'Inativo'}</span></td>
          <td>
            <div style="display:flex; gap: 0.5rem;">
              <button class="btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; width: auto;" onclick="editTopic(${t.id})">✏️</button>
              <button class="btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; width: auto; background-color: var(--success);" onclick="triggerTopicRun(${t.id})">🚀</button>
              <button class="btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; width: auto; background-color: var(--error);" onclick="deleteTopic(${t.id})">🗑️</button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Nenhum tópico registrado ainda.</td></tr>`;
    }
  } catch (err) {
    console.error(err);
  }
}

// ==========================================
// MÓDULO: GESTÃO DE E-MAILS (CRUD)
// ==========================================

async function loadEmailsPageData() {
  activeGroupId = null;
  document.getElementById("contacts-card").style.display = "none";
  await loadEmailGroups();
}

async function loadEmailGroups() {
  try {
    const groups = await apiFetch("/api/email-groups");
    const tbody = document.getElementById("email-groups-table-body");
    tbody.innerHTML = "";
    
    if (groups && groups.length > 0) {
      groups.forEach(g => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.onclick = (e) => {
          if (e.target.tagName !== "BUTTON" && e.target.parentElement.tagName !== "BUTTON") {
            selectEmailGroup(g.id, g.name);
          }
        };
        tr.innerHTML = `
          <td><strong>${escapeHtml(g.name)}</strong><br><small style="color:var(--text-muted);">${escapeHtml(g.description || "")}</small></td>
          <td style="width: 80px;">
            <button class="btn-primary" style="padding: 0.3rem 0.6rem; background-color: var(--error); width: auto;" onclick="deleteEmailGroup(${g.id})">🗑️</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="2" style="text-align: center; color: var(--text-muted);">Nenhum grupo de e-mail criado.</td></tr>`;
    }
  } catch (err) {
    console.error(err);
  }
}

async function selectEmailGroup(groupId, groupName) {
  activeGroupId = groupId;
  document.getElementById("active-group-title").innerText = `Membros: ${groupName}`;
  document.getElementById("contacts-card").style.display = "block";
  await loadEmailContacts();
}

async function loadEmailContacts() {
  if (!activeGroupId) return;
  try {
    const groups = await apiFetch("/api/email-groups");
    const group = groups.find(g => g.id === activeGroupId);
    const tbody = document.getElementById("email-contacts-table-body");
    tbody.innerHTML = "";
    
    if (group && group.contacts && group.contacts.length > 0) {
      group.contacts.forEach(c => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${escapeHtml(c.name)}</td>
          <td>${escapeHtml(c.email)}</td>
          <td>
            <button class="btn-primary" style="padding: 0.3rem 0.6rem; background-color: var(--error); width: auto;" onclick="deleteEmailContact(${c.id})">🗑️</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">Nenhum contato cadastrado neste grupo.</td></tr>`;
    }
  } catch (err) {
    console.error(err);
  }
}

async function deleteEmailGroup(groupId) {
  if (!confirm("Tem certeza que deseja excluir este grupo e todos os seus contatos?")) return;
  try {
    await apiFetch(`/api/email-groups/${groupId}`, { method: "DELETE" });
    showToast("Grupo de e-mail deletado.");
    loadEmailsPageData();
  } catch (err) {
    alert(err.message);
  }
}

async function deleteEmailContact(contactId) {
  if (!confirm("Tem certeza que deseja remover este contato?")) return;
  try {
    await apiFetch(`/api/email-contacts/${contactId}`, { method: "DELETE" });
    showToast("Contato removido.");
    loadEmailContacts();
  } catch (err) {
    alert(err.message);
  }
}

// ==========================================
// MÓDULO: GESTÃO DE MODELOS DE IA (ADMIN)
// ==========================================

async function loadModelsData() {
  try {
    const configs = await apiFetch("/api/admin/model-configs");
    const tbody = document.getElementById("models-table-body");
    tbody.innerHTML = "";

    if (configs && configs.length > 0) {
      configs.forEach(c => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><span class="status-badge" style="background-color: var(--secondary-color); color: white; text-transform: uppercase;">${escapeHtml(c.provider)}</span></td>
          <td><strong>${escapeHtml(c.model_name)}</strong></td>
          <td>${escapeHtml(c.base_url || "Padrão")}</td>
          <td><span class="status-badge ${c.is_active ? 'status-success' : 'status-warning'}">${c.is_active ? 'Ativo' : 'Inativo'}</span></td>
          <td>
            <div style="display:flex; gap: 0.5rem;">
              <button class="btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; width: auto;" onclick="editModelConfig(${c.id})">✏️</button>
              <button class="btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; width: auto; background-color: var(--error);" onclick="deleteModelConfig(${c.id})">🗑️</button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Nenhum modelo customizado cadastrado.</td></tr>`;
    }
  } catch (err) {
    console.error(err);
  }
}

async function deleteModelConfig(configId) {
  if (!confirm("Deseja realmente remover esta configuração de modelo?")) return;
  try {
    await apiFetch(`/api/admin/model-configs/${configId}`, { method: "DELETE" });
    showToast("Modelo de IA deletado.");
    loadModelsData();
  } catch (err) {
    alert(err.message);
  }
}

// ==========================================
// MÓDULO: CONEXÃO WHATSAPP E QR CODE
// ==========================================

async function loadWhatsappQRCode() {
  const qrImage = document.getElementById("qrcode-image");
  const statusBadge = document.getElementById("wa-status-badge");
  
  qrImage.src = "";
  qrImage.alt = "Buscando status...";
  
  try {
    const res = await apiFetch("/api/whatsapp/connect");
    if (res.connected) {
      qrImage.src = "https://placehold.co/200x200/10b981/ffffff?text=WhatsApp+Conectado";
      statusBadge.className = "status-badge status-success";
      statusBadge.innerText = "Conectado";
    } else if (res.qrcode) {
      qrImage.src = res.qrcode;
      statusBadge.className = "status-badge status-warning";
      statusBadge.innerText = "Aguardando Leitura";
    } else {
      qrImage.src = "https://placehold.co/200x200/ef4444/ffffff?text=Sem+Serviço";
      statusBadge.className = "status-badge status-danger";
      statusBadge.innerText = "Sem Comunicação";
    }
  } catch (err) {
    qrImage.alt = "Falha ao carregar QR Code.";
    statusBadge.className = "status-badge status-danger";
    statusBadge.innerText = "Erro";
  }
}

// ==========================================
// MÓDULO: HISTÓRICO & PREVIEWS
// ==========================================

async function loadHistoryData() {
  try {
    const history = await apiFetch("/api/history");
    const tbody = document.getElementById("history-table-body");
    tbody.innerHTML = "";

    if (history && history.length > 0) {
      history.reverse().forEach(h => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${escapeHtml(h.topic_name || `Tópico #${h.topic_id}`)}</strong></td>
          <td>${new Date(h.sent_at).toLocaleString()}</td>
          <td><span class="status-badge ${h.status === 'success' ? 'status-success' : 'status-danger'}">${h.status.toUpperCase()}</span></td>
          <td>
            ${h.status === 'success' 
              ? `<button class="btn-primary" style="padding: 0.3rem 0.8rem; font-size: 0.8rem; width: auto;" onclick="previewReport(${h.id})">🔍 Ver Conteúdo</button>` 
              : `<span style="color:var(--error); font-size: 0.85rem;">${escapeHtml(h.error_message)}</span>`}
          </td>
          <td>
            ${h.status === 'success' 
              ? `<a href="/api/history/${h.id}/pdf" class="btn-primary" style="padding: 0.3rem 0.8rem; font-size: 0.8rem; width: auto; background-color: var(--secondary-color); text-decoration: none; display: inline-flex;" target="_blank">📥 Baixar PDF</a>` 
              : '-'}
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Nenhum histórico registrado.</td></tr>`;
    }
  } catch (err) {
    console.error(err);
  }
}

async function previewReport(historyId) {
  try {
    const h = await apiFetch(`/api/history/${historyId}`);
    if (h && h.generated_markdown) {
      document.getElementById("preview-modal-body").innerHTML = marked.parse(h.generated_markdown);
      openModal("preview-modal");
    } else {
      alert("Nenhum conteúdo markdown disponível para este relatório.");
    }
  } catch (err) {
    alert("Falha ao obter preview: " + err.message);
  }
}

async function triggerTopicRun(topicId) {
  if (!confirm("Deseja disparar este tópico manualmente agora?")) return;
  showToast("Disparando pipeline...");
  try {
    await apiFetch(`/api/topics/${topicId}/run`, { method: "POST" });
    showToast("Executado com sucesso!");
    loadDashboardData();
  } catch (err) {
    alert("Falha no disparo: " + err.message);
  }
}

async function deleteTopic(topicId) {
  if (!confirm("Deseja excluir este tópico?")) return;
  try {
    await apiFetch(`/api/topics/${topicId}`, { method: "DELETE" });
    showToast("Tópico removido.");
    loadTopicsData();
  } catch (err) {
    alert(err.message);
  }
}

// ==========================================
// PAINEL ADMIN (GESTÃO DE CONFIG E USUÁRIOS)
// ==========================================

async function loadAdminData() {
  await fetchSystemConfig();
  await loadAdminUsers();
}

async function loadAdminUsers() {
  try {
    const users = await apiFetch("/api/admin/users");
    const tbody = document.getElementById("admin-users-table-body");
    tbody.innerHTML = "";
    
    if (users && users.length > 0) {
      users.forEach(u => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${escapeHtml(u.username)}</strong></td>
          <td><span class="status-badge" style="background-color: var(--border-color); color: var(--text-color);">${escapeHtml(u.role)}</span></td>
          <td><span class="status-badge" style="background-color: var(--secondary-color); color: white;">${escapeHtml(u.plan_type.toUpperCase())}</span></td>
          <td>Tópicos: ${u.max_topics_limit} | Tokens: ${u.max_tokens_monthly_limit.toLocaleString()}</td>
          <td>${u.trial_ends_at ? new Date(u.trial_ends_at).toLocaleDateString() : '-'}</td>
          <td>
            <div style="display:flex; gap: 0.5rem;">
              <button class="btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; width: auto;" onclick="editUser(${u.id})">✏️</button>
              <button class="btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; width: auto; background-color: var(--error);" onclick="deleteUser(${u.id})">🗑️</button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error(err);
  }
}

async function deleteUser(userId) {
  if (!confirm("Deseja realmente remover este usuário e todos os seus tópicos?")) return;
  try {
    await apiFetch(`/api/admin/users/${userId}`, { method: "DELETE" });
    showToast("Usuário removido.");
    loadAdminUsers();
  } catch (err) {
    alert(err.message);
  }
}

// ==========================================
// FORMULÁRIOS DE CRIAÇÃO / EDIÇÃO (EDIT HANDLERS)
// ==========================================

async function editTopic(id) {
  try {
    const topics = await apiFetch("/api/topics");
    const t = topics.find(topic => topic.id === id);
    if (!t) return;
    
    document.getElementById("topic-modal-title").innerText = "Editar Tópico";
    document.getElementById("topic-id-hidden").value = t.id;
    document.getElementById("topic-name").value = t.topic_name;
    document.getElementById("topic-query").value = t.search_query;
    document.getElementById("topic-target").value = t.whatsapp_target || "";
    document.getElementById("topic-model").value = t.preferred_model;
    document.getElementById("topic-period").value = t.time_period;
    document.getElementById("topic-is-public").value = t.is_public;
    
    document.getElementById("topic-date-start").value = t.date_range_start || "";
    document.getElementById("topic-date-end").value = t.date_range_end || "";
    
    document.getElementById("topic-custom-key").value = t.custom_gemini_key || "";
    document.getElementById("topic-schedule-type").value = t.schedule_type;
    document.getElementById("topic-fixed-time").value = t.fixed_time || "08:00";
    document.getElementById("topic-range-start").value = t.random_range_start || "08:00";
    document.getElementById("topic-range-end").value = t.random_range_end || "10:00";
    
    document.getElementById("topic-schedule-interval").value = t.schedule_interval || "daily";
    document.getElementById("topic-schedule-days").value = t.schedule_days || "";
    
    // Atualiza exibições baseadas no modo de agendamento
    if (t.schedule_type === "fixed") {
      document.getElementById("schedule-fixed-fields").style.display = "block";
      document.getElementById("schedule-random-fields").style.display = "none";
    } else {
      document.getElementById("schedule-fixed-fields").style.display = "none";
      document.getElementById("schedule-random-fields").style.display = "grid";
    }

    // Preenche chaves de IA por etapa e checklists de e-mail
    await populateTopicFormRelations(t);
    
    openModal("topic-modal");
  } catch (err) {
    alert("Falha ao abrir edição: " + err.message);
  }
}

async function populateTopicFormRelations(topic = null) {
  try {
    // 1. Popula dropdowns de modelos de IA cadastrados
    const models = await apiFetch("/api/admin/model-configs");
    const collectorSelect = document.getElementById("topic-collector-model");
    const writerSelect = document.getElementById("topic-writer-model");
    const auditorSelect = document.getElementById("topic-auditor-model");
    
    [collectorSelect, writerSelect, auditorSelect].forEach(select => {
      select.innerHTML = '<option value="">Nativo (Gemini)</option>';
      models.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m.id;
        opt.innerText = `${m.provider.toUpperCase()} - ${m.model_name}`;
        select.appendChild(opt);
      });
    });
    
    if (topic) {
      collectorSelect.value = topic.collector_model_id || "";
      writerSelect.value = topic.writer_model_id || "";
      auditorSelect.value = topic.auditor_model_id || "";
    }

    // 2. Popula checklist de Grupos de E-mail
    const emailGroups = await apiFetch("/api/email-groups");
    const listContainer = document.getElementById("topic-email-groups-list");
    listContainer.innerHTML = "";
    
    if (emailGroups && emailGroups.length > 0) {
      emailGroups.forEach(g => {
        const div = document.createElement("div");
        div.style.display = "flex";
        div.style.alignItems = "center";
        div.style.gap = "0.5rem";
        
        const isChecked = topic && topic.email_groups && topic.email_groups.some(eg => eg.id === g.id);
        
        div.innerHTML = `
          <input type="checkbox" id="chk-group-${g.id}" class="email-group-checkbox" value="${g.id}" ${isChecked ? 'checked' : ''}>
          <label for="chk-group-${g.id}" style="text-transform:none; font-weight:normal; font-size:0.9rem; margin-bottom:0; cursor:pointer;">
            ${escapeHtml(g.name)} (${g.contacts.length} e-mails)
          </label>
        `;
        listContainer.appendChild(div);
      });
    } else {
      listContainer.innerHTML = '<span style="color:var(--text-muted); font-size:0.85rem;">Nenhum grupo de e-mail cadastrado.</span>';
    }
  } catch (err) {
    console.error(err);
  }
}

async function editUser(id) {
  try {
    const users = await apiFetch("/api/admin/users");
    const u = users.find(user => user.id === id);
    if (!u) return;
    
    document.getElementById("user-modal-title").innerText = "Editar Usuário";
    document.getElementById("user-id-hidden").value = u.id;
    document.getElementById("user-username").value = u.username;
    document.getElementById("user-password").value = ""; // Não preenche por segurança
    document.getElementById("user-role").value = u.role;
    document.getElementById("user-plan").value = u.plan_type;
    document.getElementById("user-max-topics").value = u.max_topics_limit;
    document.getElementById("user-max-tokens").value = u.max_tokens_monthly_limit;
    
    openModal("user-modal");
  } catch (err) {
    console.error(err);
  }
}

async function editModelConfig(id) {
  try {
    const configs = await apiFetch("/api/admin/model-configs");
    const c = configs.find(cfg => cfg.id === id);
    if (!c) return;
    
    document.getElementById("model-config-modal-title").innerText = "Editar Modelo de IA";
    document.getElementById("model-config-id-hidden").value = c.id;
    document.getElementById("model-config-provider").value = c.provider;
    document.getElementById("model-config-name").value = c.model_name;
    document.getElementById("model-config-key").value = ""; // Ocultado por segurança
    document.getElementById("model-config-base-url").value = c.base_url || "";
    
    openModal("model-config-modal");
  } catch (err) {
    console.error(err);
  }
}

// ==========================================
// CONFIGURAÇÃO DOS EVENT LISTENERS DA PÁGINA
// ==========================================

function setupEventListeners() {
  // Mobile sidebar toggle handler
  const toggleBtn = document.getElementById("sidebar-toggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      document.getElementById("sidebar-section").classList.toggle("show");
    });
  }

  // Alterna páginas a partir da sidebar
  document.querySelectorAll(".sidebar-menu .menu-item").forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const pageId = item.getAttribute("data-target");
      if (pageId) {
        switchPage(pageId);
        document.getElementById("sidebar-section").classList.remove("show"); // fecha menu no mobile
      }
    });
  });

  // Login Submit
  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const loginBtn = document.getElementById("login-submit-btn");
    loginBtn.disabled = true;
    
    const credentials = {
      username: document.getElementById("login-username").value,
      password: document.getElementById("login-password").value
    };

    try {
      const res = await apiFetch("/api/auth/token", {
        method: "POST",
        body: JSON.stringify(credentials)
      });
      if (res && res.access_token) {
        localStorage.setItem("token", res.access_token);
        await fetchUserData();
        showToast("Logado com sucesso!");
      }
    } catch (err) {
      alert("Falha de autenticação: " + err.message);
    } finally {
      loginBtn.disabled = false;
    }
  });

  // Theme Toggle Button
  document.getElementById("btn-theme-toggle").addEventListener("click", () => {
    currentTheme = currentTheme === "light" ? "dark" : "light";
    localStorage.setItem("theme", currentTheme);
    initTheme();
  });

  // Logout Button
  document.getElementById("btn-logout").addEventListener("click", (e) => {
    e.preventDefault();
    logout();
  });

  // Add Topic Button Click
  document.getElementById("btn-add-topic").addEventListener("click", async () => {
    document.getElementById("topic-modal-title").innerText = "Novo Tópico de Pesquisa";
    document.getElementById("topic-id-hidden").value = "";
    document.getElementById("topic-form").reset();
    document.getElementById("topic-date-start").value = "";
    document.getElementById("topic-date-end").value = "";
    
    await populateTopicFormRelations();
    
    openModal("topic-modal");
  });

  // Add Email Group Button Click
  document.getElementById("btn-add-email-group").addEventListener("click", () => {
    document.getElementById("email-group-modal-title").innerText = "Novo Grupo de E-mail";
    document.getElementById("email-group-id-hidden").value = "";
    document.getElementById("email-group-form").reset();
    openModal("email-group-modal");
  });

  // Add Contact Button Click
  document.getElementById("btn-add-email-contact").addEventListener("click", () => {
    if (!activeGroupId) return;
    document.getElementById("email-contact-form").reset();
    openModal("email-contact-modal");
  });

  // Add Model Config Button Click
  document.getElementById("btn-add-model-config").addEventListener("click", () => {
    document.getElementById("model-config-modal-title").innerText = "Cadastrar Modelo de IA";
    document.getElementById("model-config-id-hidden").value = "";
    document.getElementById("model-config-form").reset();
    openModal("model-config-modal");
  });

  // Switch to Register (Free Trial link)
  document.getElementById("switch-to-register").addEventListener("click", (e) => {
    e.preventDefault();
    alert("Para novos planos SaaS, favor contatar o suporte comercial da empresa.");
  });

  // Refresh QR Code Button
  document.getElementById("btn-refresh-qrcode").addEventListener("click", () => {
    loadWhatsappQRCode();
  });

  // Toggle do Tipo de Agendamento no Modal
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
    
    // Coleta IDs dos grupos de e-mail marcados
    const emailGroupIds = [];
    document.querySelectorAll(".email-group-checkbox:checked").forEach(cb => {
      emailGroupIds.push(parseInt(cb.value));
    });
    
    const topicData = {
      topic_name: document.getElementById("topic-name").value,
      search_query: document.getElementById("topic-query").value,
      whatsapp_target: document.getElementById("topic-target").value || "N/A",
      preferred_model: document.getElementById("topic-model").value,
      time_period: document.getElementById("topic-period").value,
      is_public: parseInt(document.getElementById("topic-is-public").value),
      date_range_start: document.getElementById("topic-date-start").value || null,
      date_range_end: document.getElementById("topic-date-end").value || null,
      collector_model_id: parseInt(document.getElementById("topic-collector-model").value) || null,
      writer_model_id: parseInt(document.getElementById("topic-writer-model").value) || null,
      auditor_model_id: parseInt(document.getElementById("topic-auditor-model").value) || null,
      custom_gemini_key: document.getElementById("topic-custom-key").value || null,
      schedule_type: document.getElementById("topic-schedule-type").value,
      schedule_interval: document.getElementById("topic-schedule-interval").value,
      schedule_days: document.getElementById("topic-schedule-days").value || null,
      fixed_time: document.getElementById("topic-fixed-time").value,
      random_range_start: document.getElementById("topic-range-start").value,
      random_range_end: document.getElementById("topic-range-end").value,
      email_group_ids: emailGroupIds
    };

    try {
      if (id) {
        await apiFetch(`/api/topics/${id}`, {
          method: "PUT",
          body: JSON.stringify(topicData)
        });
        showToast("Tópico atualizado.");
      } else {
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

  // Submissão de IA Model Config (Criar/Editar)
  document.getElementById("model-config-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("model-config-id-hidden").value;
    
    const configData = {
      provider: document.getElementById("model-config-provider").value,
      model_name: document.getElementById("model-config-name").value,
      api_key: document.getElementById("model-config-key").value,
      base_url: document.getElementById("model-config-base-url").value || null
    };

    try {
      if (id) {
        await apiFetch(`/api/admin/model-configs/${id}`, {
          method: "PUT",
          body: JSON.stringify(configData)
        });
        showToast("Configuração de modelo atualizada.");
      } else {
        await apiFetch("/api/admin/model-configs", {
          method: "POST",
          body: JSON.stringify(configData)
        });
        showToast("Configuração de modelo criada.");
      }
      closeModal("model-config-modal");
      loadModelsData();
    } catch (err) {
      alert("Falha ao salvar provedor de IA: " + err.message);
    }
  });

  // Submissão de Grupo de E-mail (Criar/Editar)
  document.getElementById("email-group-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("email-group-id-hidden").value;
    
    const groupData = {
      name: document.getElementById("email-group-name").value,
      description: document.getElementById("email-group-desc").value || null
    };

    try {
      if (id) {
        await apiFetch(`/api/email-groups/${id}`, {
          method: "PUT",
          body: JSON.stringify(groupData)
        });
        showToast("Grupo atualizado.");
      } else {
        await apiFetch("/api/email-groups", {
          method: "POST",
          body: JSON.stringify(groupData)
        });
        showToast("Grupo de e-mail criado.");
      }
      closeModal("email-group-modal");
      loadEmailGroups();
    } catch (err) {
      alert("Falha ao salvar grupo: " + err.message);
    }
  });

  // Submissão de Novo Contato no Grupo Ativo
  document.getElementById("email-contact-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!activeGroupId) return;
    
    const contactData = {
      name: document.getElementById("email-contact-name").value,
      email: document.getElementById("email-contact-email").value
    };

    try {
      await apiFetch(`/api/email-groups/${activeGroupId}/contacts`, {
        method: "POST",
        body: JSON.stringify(contactData)
      });
      showToast("Contato adicionado.");
      closeModal("email-contact-modal");
      loadEmailContacts();
    } catch (err) {
      alert("Falha ao salvar contato: " + err.message);
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
        showToast("Usuário atualizado.");
      } else {
        await apiFetch("/api/auth/register", {
          method: "POST",
          body: JSON.stringify(userData)
        });
        showToast("Usuário criado.");
      }
      closeModal("user-modal");
      loadAdminUsers();
    } catch (err) {
      alert("Falha ao salvar usuário: " + err.message);
    }
  });

  // Admin Config Form Submit (White-Label & SMTP)
  document.getElementById("admin-config-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const configData = {
      company_name: document.getElementById("admin-company-name").value,
      theme_color_primary: document.getElementById("admin-color-primary").value,
      theme_color_secondary: document.getElementById("admin-color-secondary").value,
      evolution_url: document.getElementById("admin-evolution-url").value,
      evolution_token: document.getElementById("admin-evolution-token").value,
      
      // SMTP
      smtp_host: document.getElementById("admin-smtp-host").value,
      smtp_port: document.getElementById("admin-smtp-port").value,
      smtp_user: document.getElementById("admin-smtp-user").value,
      smtp_pass: document.getElementById("admin-smtp-pass").value,
      smtp_sender: document.getElementById("admin-smtp-sender").value
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
        showToast("Logo atualizada.");
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

  // Add User Button Click (Admin Page)
  document.getElementById("btn-add-user").addEventListener("click", () => {
    document.getElementById("user-modal-title").innerText = "Novo Usuário";
    document.getElementById("user-id-hidden").value = "";
    document.getElementById("user-form").reset();
    openModal("user-modal");
  });
}

// ==========================================
// UTILITÁRIOS DA API E UI MODAIS
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

function openModal(modalId) {
  document.getElementById(modalId).style.display = "flex";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}

function showToast(message) {
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

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
