<template>
  <div class="container" style="max-width:480px;margin-top:3rem;">
    <div class="card p-4">
      <h4 class="mb-3">Login</h4>

      <div class="mb-2">
        <input v-model="email" type="email" class="form-control" placeholder="Email" />
      </div>
      <div class="mb-2">
        <input v-model="password" type="password" class="form-control" placeholder="Password" />
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-primary" @click="submit" :disabled="loading">
          {{ loading ? "Signing in..." : "Sign in" }}
        </button>
        <router-link to="/register" class="btn btn-outline-secondary">Register</router-link>
      </div>

      <div v-if="err" class="alert alert-danger mt-2">{{ err }}</div>
    </div>
  </div>
</template>

<script>
import api, { setAuthToken, decodeJwt } from "../api/api";

export default {
  name: "LoginPage",
  data() {
    return { email: "", password: "", loading: false, err: "" };
  },
  methods: {
    async submit() {
      this.err = "";
      if (!this.email || !this.password) { this.err = "Email and password required"; return; }
      this.loading = true;
      try {
        const res = await api.post("/auth/login", { email: this.email, password: this.password });
        const token = res.data.access_token;
        if (!token) throw new Error("No token returned");
        // set token for axios
        setAuthToken(token);
        // decode to get role (best-effort)
        const payload = decodeJwt(token);
        const role = payload?.role || res.data.role || localStorage.getItem("role") || "";
        if (role) localStorage.setItem("role", role);
        // redirect based on role
        if (role === "admin") this.$router.push("/admin");
        else if (role === "doctor") this.$router.push("/doctor");
        else this.$router.push("/patient");
      } catch (e) {
        this.err = e.response?.data?.msg || e.message || "Login failed";
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    // if already logged in, go to appropriate route
    const token = localStorage.getItem("token");
    if (token) {
      const payload = decodeJwt(token);
      const role = payload?.role || localStorage.getItem("role");
      if (role === "admin") this.$router.replace("/admin");
      else if (role === "doctor") this.$router.replace("/doctor");
      else if (role === "patient") this.$router.replace("/patient");
    }
  }
};
</script>
