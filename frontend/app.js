const API_URL = "https://hospital-management-bkaa.onrender.com/api";
const tokenKey = "careline_token";

const loginView = document.querySelector("#login-view");
const appView = document.querySelector("#app-view");
const loginForm = document.querySelector("#login-form");
const loginError = document.querySelector("#login-error");
const toastContainer = document.querySelector("#toast-container");
const passwordToggle = document.querySelector("#toggle-password");
const passwordInput = document.querySelector("#login-password");
const sidebarToggle = document.querySelector("#sidebar-toggle");
const sidebar = document.querySelector(".sidebar");

function authHeaders() {
  return { Authorization: `Token ${localStorage.getItem(tokenKey)}`, "Content-Type": "application/json" };
}

function showToast(message, type = "success") {
  if (!toastContainer) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 2800);
}

function setLoadingState(button, isLoading, label = "") {
  if (!button) return;
  const buttonLabel = button.querySelector(".button-label") || button;
  if (isLoading) {
    button.dataset.originalLabel = buttonLabel.textContent;
    buttonLabel.textContent = label || "Please wait...";
    button.disabled = true;
    button.classList.add("loading");
  } else {
    button.disabled = false;
    button.classList.remove("loading");
    buttonLabel.textContent = button.dataset.originalLabel || label || buttonLabel.textContent;
  }
}

function setSectionLoading(element, message) {
  element.innerHTML = `<div class="loading-state"><span class="spinner" aria-hidden="true"></span>${message}</div>`;
}

function showApp(user) {
  loginView.classList.add("hidden");
  appView.classList.remove("hidden");
  document.querySelector("#user-name").textContent = user.first_name || user.username;
  document.querySelector("#user-role").textContent = (user.role || "staff").replaceAll("_", " ");
  loadDashboard();
}

async function loadDashboard() {
  const statGrid = document.querySelector("#stat-grid");
  const activityList = document.querySelector("#activity-list");
  setSectionLoading(statGrid, "Loading overview...");
  setSectionLoading(activityList, "Loading activity...");

  try {
    const response = await fetch(`${API_URL}/dashboard/`, { headers: authHeaders() });
    if (response.status === 401) return signOut();
    if (!response.ok) throw new Error("Dashboard request failed");

    const data = await response.json();
    const stats = [
      ["total_patients", "Patients", "♙"],
      ["todays_appointments", "Today's appointments", "◷"],
      ["doctors", "Doctors", "✚"],
      ["nurses", "Nurses", "♡"],
      ["admissions", "Admissions", "↗"],
      ["available_beds", "Available beds", "▣"],
      ["pending_laboratory_tests", "Pending lab tests", "⌕"],
      ["outstanding_invoices", "Outstanding invoices", "▤"],
    ];

    statGrid.innerHTML = stats
      .map(([key, label, icon]) => `<article class="stat-card"><span class="stat-icon" aria-hidden="true">${icon}</span><strong>${data[key] ?? 0}</strong><span>${label}</span></article>`)
      .join("");

    const activities = data.recent_activities || [];
    activityList.innerHTML = activities.length
      ? activities.map(item => `<div class="activity"><span class="activity-icon" aria-hidden="true">•</span><div><strong>${item.action} ${item.module.toLowerCase()}</strong><span>Record ${item.record_id || "-"}</span></div><time>${new Date(item.created_at).toLocaleString()}</time></div>`).join("")
      : "<p class='empty-inline'>No activity recorded yet.</p>";
  } catch (error) {
    statGrid.innerHTML = "<p class='empty-inline'>Overview is temporarily unavailable.</p>";
    activityList.innerHTML = "<p class='empty-inline'>Activity is temporarily unavailable.</p>";
    showToast("Unable to load dashboard data.", "error");
  }
}

async function loadPatients() {
  const query = document.querySelector("#patient-search").value.trim();
  const table = document.querySelector("#patient-table");
  const emptyState = document.querySelector("#patient-empty");
  const patientMessage = document.querySelector("#patient-message");

  patientMessage.innerHTML = '<span class="spinner" aria-hidden="true"></span> Loading patients...';

  try {
    const response = await fetch(`${API_URL}/patients/${query ? `?search=${encodeURIComponent(query)}` : ""}`, { headers: authHeaders() });
    if (!response.ok) throw new Error("Patient request failed");

    const data = await response.json();
    const patients = data.results || data;

  emptyState.classList.toggle("hidden", patients.length > 0);
  table.innerHTML = patients.length
    ? patients.map(patient => `
      <tr>
        <td><strong>${patient.patient_id}</strong></td>
        <td>${patient.first_name} ${patient.last_name}</td>
        <td>${patient.phone}<br>${patient.email || ""}</td>
        <td>${new Date(patient.registration_date).toLocaleDateString()}</td>
        <td><span class="status-badge ${patient.is_active ? "success" : "muted"}">${patient.is_active ? "Active" : "Inactive"}</span></td>
        <td><button class="outline-button deactivate-patient" data-id="${patient.id}" type="button">Deactivate</button></td>
      </tr>
    `).join("")
    : "";

    patientMessage.textContent = patients.length ? "" : "No patient records found.";
    document.querySelectorAll(".deactivate-patient").forEach(button => {
      button.addEventListener("click", () => deactivatePatient(button.dataset.id));
    });
  } catch (error) {
    table.innerHTML = "";
    emptyState.classList.remove("hidden");
    patientMessage.textContent = "Unable to load patient records.";
    showToast("Unable to load patient records.", "error");
  }
}

async function deactivatePatient(id) {
  if (!window.confirm("Deactivate this patient record?")) return;

  const response = await fetch(`${API_URL}/patients/${id}/`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify({ is_active: false }),
  });

  if (!response.ok) {
    showToast("Unable to deactivate patient record.", "error");
    return;
  }

  const message = document.querySelector("#patient-message");
  message.textContent = "Patient record deactivated.";
  showToast("Patient record deactivated.", "success");
  loadPatients();
}

function showView(viewName) {
  document.querySelectorAll(".view-section").forEach(section => section.classList.toggle("hidden", section.id !== viewName));
  document.querySelectorAll("[data-view]").forEach(link => {
    const isActive = link.dataset.view === viewName;
    link.classList.toggle("active", isActive);
  });

  if (viewName === "patients") loadPatients();
  sidebar.classList.remove("open");
  sidebarToggle?.setAttribute("aria-expanded", "false");
}

function signOut() {
  fetch(`${API_URL}/auth/logout/`, { method: "POST", headers: authHeaders() }).finally(() => {
    localStorage.removeItem(tokenKey);
    appView.classList.add("hidden");
    loginView.classList.remove("hidden");
    loginError.textContent = "";
  });
}

loginForm.addEventListener("submit", async event => {
  event.preventDefault();
  loginError.textContent = "";

  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData);
  const loginButton = document.querySelector("#login-button");

  setLoadingState(loginButton, true, "Signing in...");

  try {
    const response = await fetch(`${API_URL}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) {
      const message = data.non_field_errors?.[0] || data.detail || "Sign in failed.";
      loginError.textContent = message;
      showToast(message, "error");
      return;
    }

    localStorage.setItem(tokenKey, data.token);
    showApp(data.user);
    showToast("Signed in successfully.", "success");
  } catch (error) {
    loginError.textContent = "Unable to sign in right now. Please try again.";
    showToast("Unable to sign in right now.", "error");
  } finally {
    setLoadingState(loginButton, false, "Sign in");
  }
});

if (passwordToggle && passwordInput) {
  passwordToggle.addEventListener("click", () => {
    const isHidden = passwordInput.type === "password";
    passwordInput.type = isHidden ? "text" : "password";
    passwordToggle.textContent = isHidden ? "Hide" : "Show";
    passwordToggle.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
  });
}

sidebarToggle?.addEventListener("click", () => {
  const isOpen = sidebar.classList.toggle("open");
  sidebarToggle.setAttribute("aria-expanded", String(isOpen));
  sidebarToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
});

document.querySelector("#logout-button").addEventListener("click", signOut);
document.querySelector("#refresh-button").addEventListener("click", loadDashboard);
document.querySelectorAll("[data-view]").forEach(link => {
  link.addEventListener("click", event => {
    const viewName = link.dataset.view;
    if (!viewName) return;
    event.preventDefault();
    showView(viewName);
  });
});
document.querySelector("#patient-search-button").addEventListener("click", loadPatients);
document.querySelector("#patient-search").addEventListener("keydown", event => {
  if (event.key === "Enter") {
    event.preventDefault();
    loadPatients();
  }
});
document.querySelector("#new-patient-button").addEventListener("click", () => {
  const form = document.querySelector("#patient-form");
  form.classList.remove("hidden");
  form.scrollIntoView({ behavior: "smooth", block: "start" });
});
document.querySelector("#cancel-patient-button").addEventListener("click", () => {
  const form = document.querySelector("#patient-form");
  form.classList.add("hidden");
  form.reset();
});
document.querySelector("#patient-form").addEventListener("submit", async event => {
  event.preventDefault();

  const form = event.target;
  const submitButton = form.querySelector("[type='submit']");
  const message = document.querySelector("#patient-message");
  setLoadingState(submitButton, true, "Saving patient...");

  try {
    const response = await fetch(`${API_URL}/patients/`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(Object.fromEntries(new FormData(form))),
    });

    if (!response.ok) {
      const errors = await response.json().catch(() => ({}));
      const firstError = Array.isArray(errors.non_field_errors) ? errors.non_field_errors[0] : "Unable to save patient. Check the required fields.";
      message.textContent = firstError;
      showToast(firstError, "error");
      return;
    }

    message.textContent = "Patient registered successfully.";
    showToast("Patient registered successfully.", "success");
    form.reset();
    form.classList.add("hidden");
    loadPatients();
  } catch (error) {
    message.textContent = "Unable to save patient right now.";
    showToast("Unable to save patient right now.", "error");
  } finally {
    setLoadingState(submitButton, false, "Save patient");
  }
});

(async function init() {
  if (!localStorage.getItem(tokenKey)) return;
  const response = await fetch(`${API_URL}/auth/me/`, { headers: authHeaders() });
  if (response.ok) showApp(await response.json()); else localStorage.removeItem(tokenKey);
})();
