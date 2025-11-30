import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import api, { setAuthToken, decodeJwt } from "./api/api";

// BOOTSTRAP
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

import "./styles.css";

export function getTheme() {
  try {
    const saved = localStorage.getItem("hms:theme");
    if (saved === "dark" || saved === "light") return saved;
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    return prefersDark ? "dark" : "light";
  } catch (e) {
    return "light";
  }
}

export function setTheme(name) {
  document.documentElement.classList.remove("theme-light", "theme-dark");
  document.documentElement.classList.add(name === "dark" ? "theme-dark" : "theme-light");
  try { localStorage.setItem("hms:theme", name); } catch (e) {}
}

const initial = getTheme();
setTheme(initial);

const token = localStorage.getItem("token");
if (token) {
  setAuthToken(token);
  try {
    const payload = decodeJwt(token);
    const role = payload?.role;
    if (role) localStorage.setItem("role", role);
  } catch (e) {
    console.warn("Failed to decode token", e);
  }
}

const app = createApp(App);
app.use(router);
app.mount("#app");

try {
  const mq = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
  mq.addEventListener?.("change", (e) => {
    try {
      const saved = localStorage.getItem("hms:theme");
      if (!saved) {
        setTheme(e.matches ? "dark" : "light");
      }
    } catch (_) {}
  });
} catch (_) {}