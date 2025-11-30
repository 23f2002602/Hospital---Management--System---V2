<template>
  <div :class="['app-root', theme]">
    <nav class="navbar navbar-expand-lg sticky-top" :class="navClass">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="/">SeattleGrace</a>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navMenu" aria-controls="navMenu" aria-expanded="false"
                aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navMenu">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>

            <template v-if="!isLoggedIn">
              <li class="nav-item"><router-link class="nav-link" to="/search">Find Doctors</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/login">Login</router-link></li>
            </template>

            <template v-if="userRole === 'patient'">
              <li class="nav-item"><router-link class="nav-link" to="/patient">Dashboard</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/search">Doctors</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/profile">Profile</router-link></li>
            </template>

            <template v-if="userRole === 'doctor'">
              <li class="nav-item"><router-link class="nav-link" to="/doctor">Dashboard</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/doctor/patients">My Patients</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/reports">Reports</router-link></li>
            </template>

            <template v-if="userRole === 'admin'">
              <li class="nav-item"><router-link class="nav-link" to="/admin">Dashboard</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/reports">Reports</router-link></li>
            </template>
          </ul>

          <div class="d-flex align-items-center gap-2">
            <install-pwa />
            <button class="btn btn-sm btn-outline-secondary" @click="toggleTheme" :title="themeTitle">
              <span v-if="isDark">🌙</span><span v-else>☀️</span>
            </button>

            <template v-if="isLoggedIn">
              <span class="navbar-text me-2 d-none d-lg-block">
                Hi, <strong>{{ userNameShort }}</strong> <span class="badge bg-secondary rounded-pill">{{ userRole }}</span>
              </span>
              <button class="btn btn-sm btn-danger" @click="logout">Logout</button>
            </template>
            
            <template v-else>
               <router-link to="/login" class="btn btn-primary btn-sm">Sign In</router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <main class="container py-4">
      <router-view />
    </main>

    <footer class="footer mt-auto py-3 bg-light text-muted">
      <div class="container text-center small">© SeattleGrace Hospital</div>
    </footer>
  </div>
</template>

<script>
import InstallPWA from "./pwa/InstallPWA.vue";
import { setAuthToken } from "./api/api";

export default {
  name: "App",
  components: { InstallPWA },
  data() {
    return {
      theme: localStorage.getItem("hms:theme") || "light",
      isLoggedIn: false,
      userName: "User",
      userRole: ""
    };
  },
  computed: {
    isDark() { return this.theme === "dark"; },
    themeTitle() { return this.isDark ? "Switch to light" : "Switch to dark"; },
    navClass() { return this.isDark ? "navbar-dark bg-dark" : "navbar-light bg-white"; },
    // UPDATE: Now returns full name (or fallback)
    userNameShort() { return this.userName ? this.userName : "User"; }
  },
  watch: {
    $route() { this.checkAuth(); }
  },
  mounted() {
    document.documentElement.setAttribute("data-theme", this.theme);
    this.checkAuth();
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem("token");
      this.isLoggedIn = !!token;
      if (this.isLoggedIn) {
        this.userName = localStorage.getItem("user_name") || "User";
        this.userRole = localStorage.getItem("role") || "";
      } else {
        this.userName = "";
        this.userRole = "";
      }
    },
    toggleTheme() {
      this.theme = this.isDark ? "light" : "dark";
      localStorage.setItem("hms:theme", this.theme);
      document.documentElement.setAttribute("data-theme", this.theme);
    },
    logout() {
      setAuthToken(null);
      this.isLoggedIn = false;
      this.userName = "";
      this.userRole = "";
      this.$router.push("/login");
    }
  }
};
</script>

<style scoped>
.app-root { min-height: 100vh; display: flex; flex-direction: column; }
main.container { flex: 1 0 auto; }
</style>