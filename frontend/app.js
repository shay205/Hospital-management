const API_URL = "http://127.0.0.1:8000/api";
const tokenKey = "careline_token";

const loginView = document.querySelector("#login-view");
const appView = document.querySelector("#app-view");
const loginForm = document.querySelector("#login-form");
const loginError = document.querySelector("#login-error");

function authHeaders() {
  return { Authorization: `Token ${localStorage.getItem(tokenKey)}`, "Content-Type": "application/json" };
}

function showApp(user) {
  loginView.classList.add("hidden");
  appView.classList.remove("hidden");
  document.querySelector("#user-name").textContent = user.first_name || user.username;
  document.querySelector("#user-role").textContent = (user.role || "staff").replaceAll("_", " ");
  loadDashboard();
}

async function loadDashboard() {
  const response = await fetch(`${API_URL}/dashboard/`, { headers: authHeaders() });
  if (response.status === 401) return signOut();
  if (!response.ok) throw new Error("Unable to load dashboard data.");
  const data = await response.json();
  const stats = [["total_patients", "Patients"], ["todays_appointments", "Today's appointments"], ["doctors", "Doctors"], ["nurses", "Nurses"], ["admissions", "Admissions"], ["available_beds", "Available beds"], ["pending_laboratory_tests", "Pending lab tests"], ["outstanding_invoices", "Outstanding invoices"]];
  document.querySelector("#stat-grid").innerHTML = stats.map(([key, label]) => `<article class="stat-card"><strong>${data[key] ?? 0}</strong><span>${label}</span></article>`).join("");
  const activities = data.recent_activities || [];
  document.querySelector("#activity-list").innerHTML = activities.length ? activities.map(item => `<div class="activity"><div><strong>${item.action} ${item.module.toLowerCase()}</strong><span>Record ${item.record_id || "-"}</span></div><time>${new Date(item.created_at).toLocaleString()}</time></div>`).join("") : "<p>No activity recorded yet.</p>";
}

async function loadPatients() {
  const query = document.querySelector("#patient-search").value.trim();
  const response = await fetch(`${API_URL}/patients/${query ? `?search=${encodeURIComponent(query)}` : ""}`, { headers: authHeaders() });
  if (!response.ok) return;
  const data = await response.json();
  const patients = data.results || data;
  document.querySelector("#patient-empty").classList.toggle("hidden", patients.length > 0);
  document.querySelector("#patient-table").innerHTML = patients.map(patient => `<tr><td><strong>${patient.patient_id}</strong></td><td>${patient.first_name} ${patient.last_name}</td><td>${patient.phone}<br>${patient.email || ""}</td><td>${new Date(patient.registration_date).toLocaleDateString()}</td><td><span class="status-badge">${patient.is_active ? "Active" : "Inactive"}</span></td><td><button class="outline-button deactivate-patient" data-id="${patient.id}" type="button">Deactivate</button></td></tr>`).join("");
  document.querySelectorAll(".deactivate-patient").forEach(button => button.addEventListener("click", () => deactivatePatient(button.dataset.id)));
}

async function deactivatePatient(id) {
  if (!window.confirm("Deactivate this patient record?")) return;
  const response = await fetch(`${API_URL}/patients/${id}/`, { method: "PATCH", headers: authHeaders(), body: JSON.stringify({ is_active: false }) });
  if (response.ok) { document.querySelector("#patient-message").textContent = "Patient record deactivated."; loadPatients(); }
}

function showView(viewName) {
  document.querySelectorAll(".view-section").forEach(section => section.classList.toggle("hidden", section.id !== viewName));
  document.querySelectorAll("[data-view]").forEach(link => link.classList.toggle("active", link.dataset.view === viewName));
  if (viewName === "patients") loadPatients();
}

function signOut() {
  fetch(`${API_URL}/auth/logout/`, { method: "POST", headers: authHeaders() }).finally(() => { localStorage.removeItem(tokenKey); appView.classList.add("hidden"); loginView.classList.remove("hidden"); });
}

loginForm.addEventListener("submit", async event => {
  event.preventDefault();
  loginError.textContent = "";
  const formData = new FormData(loginForm);
  const response = await fetch(`${API_URL}/auth/login/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.fromEntries(formData)) });
  const data = await response.json();
  if (!response.ok) { loginError.textContent = data.non_field_errors?.[0] || "Sign in failed."; return; }
  localStorage.setItem(tokenKey, data.token);
  showApp(data.user);
});

document.querySelector("#logout-button").addEventListener("click", signOut);
document.querySelector("#refresh-button").addEventListener("click", loadDashboard);
document.querySelectorAll("[data-view]").forEach(link => link.addEventListener("click", event => { event.preventDefault(); showView(link.dataset.view); }));
document.querySelector("#patient-search-button").addEventListener("click", loadPatients);
document.querySelector("#patient-search").addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); loadPatients(); } });
document.querySelector("#new-patient-button").addEventListener("click", () => document.querySelector("#patient-form").classList.remove("hidden"));
document.querySelector("#cancel-patient-button").addEventListener("click", () => document.querySelector("#patient-form").classList.add("hidden"));
document.querySelector("#patient-form").addEventListener("submit", async event => {
  event.preventDefault();
  const response = await fetch(`${API_URL}/patients/`, { method: "POST", headers: authHeaders(), body: JSON.stringify(Object.fromEntries(new FormData(event.target))) });
  const message = document.querySelector("#patient-message");
  if (!response.ok) { message.textContent = "Unable to save patient. Check the required fields."; return; }
  message.textContent = "Patient registered successfully.";
  event.target.reset();
  event.target.classList.add("hidden");
  loadPatients();
});

(async function init() {
  if (!localStorage.getItem(tokenKey)) return;
  const response = await fetch(`${API_URL}/auth/me/`, { headers: authHeaders() });
  if (response.ok) showApp(await response.json()); else localStorage.removeItem(tokenKey);
})();
