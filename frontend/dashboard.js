const configuredApiBase = window.API_BASE_URL || "";
const isSeparateLocalFrontend =
  ["localhost", "127.0.0.1"].includes(window.location.hostname) &&
  window.location.port !== "8000";
const apiBase =
  configuredApiBase.replace(/\/$/, "") ||
  (isSeparateLocalFrontend ? "http://127.0.0.1:8000" : "");
const token = sessionStorage.getItem("keylineToken");
const keyList = document.querySelector("#key-list");
const toast = document.querySelector("#toast");
let toastTimer;

if (!token) window.location.replace("./index.html#access");

function decodeUsername() {
  if (!token) return "YOUR VAULT";
  try {
    const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(payload)).username || "YOUR VAULT";
  } catch {
    return "YOUR VAULT";
  }
}

document.querySelector("#profile-name").textContent = decodeUsername().toUpperCase();

function showToast(message, isError = false) {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.toggle("is-error", isError);
  toast.classList.add("is-visible");
  toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 4200);
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers: { Authorization: `Bearer ${token}`, ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (response.status === 401) {
    sessionStorage.removeItem("keylineToken");
    window.location.replace("./index.html#access");
    throw new Error("Your session has expired. Please log in again.");
  }
  if (!response.ok) throw new Error(data.detail || "The request could not be completed.");
  return data;
}

function renderKeys(keys) {
  keyList.replaceChildren();
  document.querySelector("#key-count").textContent = `${keys.length} ${keys.length === 1 ? "stored key" : "stored keys"}`;
  if (!keys.length) {
    const empty = document.createElement("div");
    empty.className = "empty-vault";
    empty.innerHTML = "<p>YOUR VAULT IS CLEAR.</p><span>Add the first credential your project needs.</span>";
    keyList.append(empty);
    return;
  }

  keys.forEach((key, index) => {
    const card = document.createElement("article");
    card.className = "key-card";
    const meta = [
      ["ID", `#${key.api_id}`],
      ["SERVICE", key.model],
      ["EXPIRY", key.expiry],
      ["USE", key.usability],
    ];
    const indexEl = document.createElement("p");
    indexEl.className = "card-index";
    indexEl.textContent = String(index + 1).padStart(2, "0");
    const keyEl = document.createElement("code");
    keyEl.className = "stored-key";
    keyEl.textContent = key.api_key;
    const metaEl = document.createElement("dl");
    meta.forEach(([label, value]) => {
      const group = document.createElement("div");
      const term = document.createElement("dt");
      const detail = document.createElement("dd");
      term.textContent = label;
      detail.textContent = value || "—";
      group.append(term, detail);
      metaEl.append(group);
    });
    const copyButton = document.createElement("button");
    copyButton.className = "copy-button";
    copyButton.type = "button";
    copyButton.textContent = "Copy key ↗";
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(key.api_key);
        copyButton.textContent = "Copied ✓";
        setTimeout(() => (copyButton.textContent = "Copy key ↗"), 1800);
      } catch {
        showToast("Copy is unavailable in this browser. Select the key manually.", true);
      }
    });
    card.append(indexEl, keyEl, metaEl, copyButton);
    keyList.append(card);
  });
}

async function loadKeys() {
  keyList.setAttribute("aria-busy", "true");
  try {
    const data = await request("/home");
    renderKeys(data.api_keys || []);
  } catch (error) {
    if (token) showToast(error.message, true);
  } finally {
    keyList.removeAttribute("aria-busy");
  }
}

function openDialog(id) {
  const dialog = document.querySelector(`#${id}`);
  dialog.showModal();
  dialog.querySelector("input")?.focus();
}

document.querySelectorAll("[data-dialog-open]").forEach((button) => {
  button.addEventListener("click", () => openDialog(button.dataset.dialogOpen));
});
document.querySelectorAll("[data-dialog-close]").forEach((button) => {
  button.addEventListener("click", () => button.closest("dialog").close());
});
document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
});

document.querySelector("#create-key-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button");
  button.disabled = true;
  try {
    const values = Object.fromEntries(new FormData(form));
    const data = await request("/new", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    form.reset();
    form.closest("dialog").close();
    showToast(`Key #${data.api_id} saved and encrypted.`);
    await loadKeys();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
  }
});

document.querySelector("#delete-key-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button");
  const id = new FormData(form).get("api_id");
  button.disabled = true;
  try {
    await request(`/delete/${id}`, { method: "DELETE" });
    form.reset();
    form.closest("dialog").close();
    showToast(`Key #${id} was deleted.`);
    await loadKeys();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
  }
});

document.querySelector("#refresh-button").addEventListener("click", loadKeys);
document.querySelector("#logout-button").addEventListener("click", () => {
  sessionStorage.removeItem("keylineToken");
  window.location.assign("./index.html#access");
});

if (token) loadKeys();
