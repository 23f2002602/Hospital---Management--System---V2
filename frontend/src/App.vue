<template>
  <div :class="['app-root', theme]">
    <nav class="navbar navbar-expand-lg sticky-top" :class="navClass">
      <div class="container-fluid">
        <a class="navbar-brand" href="/">HMS V2</a>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navMenu" aria-controls="navMenu" aria-expanded="false"
                aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navMenu">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/search">Doctors</router-link></li>
            <li v-if="!loggedIn" class="nav-item"><router-link class="nav-link" to="/login">Login</router-link></li>
          </ul>

          <div class="d-flex align-items-center gap-2">
            <install-pwa />
            <button class="btn btn-outline-secondary" @click="toggleTheme" :title="themeTitle">
              <span v-if="isDark">🌙</span><span v-else>☀️</span>
            </button>

            <div v-if="loggedIn" class="dropdown">
              <button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                {{ userNameShort }}
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><router-link class="dropdown-item" to="/profile">Profile</router-link></li>
                <li><a class="dropdown-item" @click="logout">Logout</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="container py-4">
      <router-view />
    </main>

    <footer class="footer mt-auto py-3 bg-light text-muted">
      <div class="container text-center small">© HMS V2</div>
    </footer>
  </div>
</template>

<script>
import InstallPWA from "./pwa/InstallPWA.vue";

export default {
  name: "App",
  components: { InstallPWA },
  data() {
    return {
      theme: localStorage.getItem("theme") || "light",
    };
  },
  computed: {
    isDark() { return this.theme === "dark"; },
    themeTitle() { return this.isDark ? "Switch to light" : "Switch to dark"; },
    loggedIn() { return !!localStorage.getItem("token"); },
    userNameShort() {
      const name = localStorage.getItem("user_name") || "";
      return name ? name.split(" ")[0] : "User";
    },
    navClass() { return this.isDark ? "navbar-dark bg-dark" : "navbar-light bg-white"; }
  },
  methods: {
    toggleTheme() {
      this.theme = this.isDark ? "light" : "dark";
      localStorage.setItem("theme", this.theme);
    },
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("user_name");
      this.$router.push("/login");
      // reload to clear any cached ui state
      window.location.reload();
    }
  },
  mounted() {
    // Apply theme class to body for global styling
    document.documentElement.setAttribute("data-theme", this.theme);
  },
  watch: {
    theme(newVal) {
      document.documentElement.setAttribute("data-theme", newVal);
    }
  }
};
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
main.container { flex: 1 0 auto; }
.footer { margin-top: auto; }
</style>
