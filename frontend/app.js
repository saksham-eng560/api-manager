const configuredApiBase = window.API_BASE_URL || "";
const isSeparateLocalFrontend =
  ["localhost", "127.0.0.1"].includes(window.location.hostname) &&
  window.location.port !== "8000";
const apiBase =
  configuredApiBase.replace(/\/$/, "") ||
  (isSeparateLocalFrontend ? "http://127.0.0.1:8000" : "");
const authMessage = document.querySelector("#auth-message");

document.querySelector("#year").textContent = new Date().getFullYear();

function setMessage(message, isError = false) {
  authMessage.textContent = message;
  authMessage.classList.toggle("is-error", isError);
}

function setLoading(form, isLoading) {
  const button = form.querySelector("button[type='submit']");
  button.disabled = isLoading;
  button.classList.toggle("is-loading", isLoading);
}

async function request(path, options) {
  const response = await fetch(`${apiBase}${path}`, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Something went wrong. Please try again.");
  return data;
}

function showTab(name) {
  document.querySelectorAll("[data-auth-tab]").forEach((tab) => {
    const active = tab.dataset.authTab === name;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  document.querySelectorAll("[data-auth-panel]").forEach((panel) => {
    const active = panel.dataset.authPanel === name;
    panel.classList.toggle("is-active", active);
    panel.hidden = !active;
  });
  setMessage("");
}

document.querySelectorAll("[data-auth-tab]").forEach((tab) => {
  tab.addEventListener("click", () => showTab(tab.dataset.authTab));
});

document.querySelector("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const values = new FormData(form);
  setLoading(form, true);
  setMessage("Opening your vault…");
  try {
    const data = await request("/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: values.get("username"), password: values.get("password") }),
    });
    sessionStorage.setItem("keylineToken", data.access_token);
    window.location.assign("./dashboard.html");
  } catch (error) {
    setMessage(error.message, true);
    setLoading(form, false);
  }
});

document.querySelector("#signup-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const values = Object.fromEntries(new FormData(form));
  setLoading(form, true);
  setMessage("Creating your vault…");
  try {
    await request("/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    const login = await request("/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: values.username, password: values.password }),
    });
    sessionStorage.setItem("keylineToken", login.access_token);
    window.location.assign("./dashboard.html");
  } catch (error) {
    setMessage(error.message, true);
    setLoading(form, false);
  }
});

const observer = new IntersectionObserver(
  (entries) => entries.forEach((entry) => entry.isIntersecting && entry.target.classList.add("is-visible")),
  { threshold: 0.14 }
);
document.querySelectorAll(".reveal-section").forEach((section) => observer.observe(section));
