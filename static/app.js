const serverGrid = document.querySelector("#server-grid");
const requestList = document.querySelector("#request-list");
const logList = document.querySelector("#log-list");
const patientList = document.querySelector("#patient-list");
const serverCount = document.querySelector("#server-count");
const avgLoad = document.querySelector("#avg-load");
const healthyCount = document.querySelector("#healthy-count");
const warningCount = document.querySelector("#warning-count");
const downCount = document.querySelector("#down-count");
const decisionCard = document.querySelector("#decision-card");
const serverForm = document.querySelector("#server-form");
const requestForm = document.querySelector("#request-form");
const tabs = document.querySelectorAll(".tab");
const requestTypeInput = document.querySelector("#request-type");
const conditionLevelInput = document.querySelector("#condition-level");
const targetModuleInput = document.querySelector("#target-module");

function loadStatusClass(rate) {
  if (rate >= 0.85) return "danger";
  if (rate >= 0.65) return "warn";
  return "good";
}

function loadStatusLabel(rate) {
  if (rate >= 0.85) return "High load";
  if (rate >= 0.65) return "Moderate load";
  return "Healthy load";
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

function renderServers(servers) {
  serverCount.textContent = `${servers.length} servers`;
  serverGrid.innerHTML = servers
    .map((server) => {
      const status = loadStatusClass(server.load_ratio);
      return `
        <article class="hospital-card">
          <h3>${server.name}</h3>
          <p>${server.server_type}</p>
          <div class="breakdown">
            <span><strong>${server.current_load}</strong> current load</span>
            <span><strong>${server.available_capacity}</strong> free units</span>
            <span><strong>${server.avg_response_ms}</strong> ms latency</span>
            <span><strong>${Math.round(server.load_ratio * 100)}%</strong> utilized</span>
          </div>
          <div class="status-pill ${status}">${server.status}</div>
        </article>
      `;
    })
    .join("");
}

function renderRequests(items) {
  if (!items.length) {
    requestList.innerHTML = `<div class="allocation-item"><p>No requests yet.</p></div>`;
    return;
  }

  requestList.innerHTML = items
    .map(
      (item) => `
        <article class="allocation-item">
          <h3>${item.request_id} · ${item.request_type}</h3>
          <p>${item.source_name} requested ${item.target_module}</p>
          <strong>Priority ${item.priority} · ${item.status}</strong>
        </article>
      `
    )
    .join("");
}

function renderLogs(items) {
  if (!items.length) {
    logList.innerHTML = `<div class="allocation-item"><p>No routing logs yet.</p></div>`;
    return;
  }

  logList.innerHTML = items
    .map(
      (item) => `
        <article class="allocation-item">
          <h3>${item.request_id} → ${item.server_id}</h3>
          <p>${item.decision}</p>
          <strong>${item.request_type} · priority ${item.priority}</strong>
        </article>
      `
    )
    .join("");
}

function renderPatients(items) {
  if (!items.length) {
    patientList.innerHTML = `<div class="allocation-item"><p>No patient-linked records yet.</p></div>`;
    return;
  }

  patientList.innerHTML = items
    .map(
      (item) => `
        <article class="allocation-item">
          <h3>${item.patient_name}</h3>
          <p>Condition: ${item.condition_level}</p>
          <strong>Assigned module: ${item.assigned_module}</strong>
        </article>
      `
    )
    .join("");
}

function renderHealth(summary) {
  avgLoad.textContent = `${Math.round(summary.average_load * 100)}%`;
  healthyCount.textContent = summary.healthy_servers;
  warningCount.textContent = summary.warning_servers;
  downCount.textContent = summary.down_servers;
}

function renderDecision(routing) {
  const breakdown = Object.entries(routing.breakdown)
    .map(([key, value]) => `<span><strong>${value}</strong> ${key.replaceAll("_", " ")}</span>`)
    .join("");

  decisionCard.classList.remove("empty");
  decisionCard.innerHTML = `
    <h3>Assigned to ${routing.server.name}</h3>
    <p>${routing.reason}</p>
    <div class="breakdown">${breakdown}</div>
  `;
}

async function refreshDashboard() {
  const [serverPayload, requestPayload, logPayload, patientPayload, healthPayload] = await Promise.all([
    fetchJson("/api/servers"),
    fetchJson("/api/requests"),
    fetchJson("/api/logs"),
    fetchJson("/api/patients"),
    fetchJson("/api/health"),
  ]);

  renderServers(serverPayload.servers);
  renderRequests(requestPayload.requests);
  renderLogs(logPayload.logs);
  renderPatients(patientPayload.patients);
  renderHealth(healthPayload.summary);
}

serverForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(serverForm);
  const payload = {
    server_id: `srv-${Date.now()}`,
    name: data.get("name"),
    server_type: data.get("server_type"),
    max_capacity: Number(data.get("max_capacity")),
    current_load: Number(data.get("current_load")),
    status: data.get("status"),
    avg_response_ms: Number(data.get("avg_response_ms")),
  };

  await fetchJson("/api/servers", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  serverForm.reset();
  await refreshDashboard();
});

requestForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(requestForm);
  const payload = {
    request_id: `req-${Date.now()}`,
    source_name: data.get("source_name"),
    request_type: data.get("request_type"),
    target_module: data.get("target_module"),
    condition_level: data.get("condition_level"),
  };

  try {
    const response = await fetchJson("/api/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    renderDecision(response.routing);
    requestForm.reset();
    await refreshDashboard();
  } catch (error) {
    decisionCard.classList.add("empty");
    decisionCard.innerHTML = `<p>${error.message}</p>`;
  }
});

tabs.forEach((button) => {
  button.addEventListener("click", () => {
    tabs.forEach((tab) => tab.classList.remove("active"));
    button.classList.add("active");

    const tab = button.dataset.tab;
    requestTypeInput.value = tab;

    if (tab === "emergency") {
      conditionLevelInput.value = "critical";
      targetModuleInput.value = "icu-monitoring";
    } else if (tab === "doctor") {
      conditionLevelInput.value = "stable";
      targetModuleInput.value = "ehr-access";
    } else {
      conditionLevelInput.value = "normal";
      targetModuleInput.value = "appointment-booking";
    }
  });
});

refreshDashboard().catch((error) => {
  decisionCard.classList.add("empty");
  decisionCard.innerHTML = `<p>${error.message}</p>`;
});
