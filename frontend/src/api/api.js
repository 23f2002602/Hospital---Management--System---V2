import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000/api",
});

// Helper to set or clear the token
export function setAuthToken(token) {
  if (token) {
    // Apply to every request
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("token", token);
  } else {
    // Clear from headers and storage
    delete api.defaults.headers.common["Authorization"];
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("user_name");
  }
}

// Helper to decode JWT
export function decodeJwt(token) {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(payload)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(json);
  } catch (e) {
    return null;
  }
}

// Interceptor: If backend says "401 Unauthorized", force logout
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      setAuthToken(null);
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;