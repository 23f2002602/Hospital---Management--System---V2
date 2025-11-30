<template>
  <div class="app-root">
    <nav class="navbar navbar-expand-lg sticky-top">
      <div class="container">
        <router-link class="navbar-brand fw-bold d-flex align-items-center gap-2" to="/">
          <span style="font-size: 1.5rem;">🏥</span> SeattleGrace
        </router-link>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navMenu" aria-controls="navMenu" aria-expanded="false"
                aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navMenu">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0 ms-lg-3 gap-lg-2">
            <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>

            <template v-if="!isLoggedIn">
              <li class="nav-item"><router-link class="nav-link" to="/search">Find Doctors</router-link></li>
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

          <div class="d-flex flex-column flex-lg-row align-items-lg-center gap-3 mt-3 mt-lg-0">
            <install-pwa />
            
            <button class="btn btn-icon align-self-start align-self-lg-center" @click="toggleTheme" :title="themeTitle">
              <span v-if="isDark" style="font-size:1.2rem">☀️</span>
              <span v-else style="font-size:1.2rem">🌙</span>
            </button>

            <template v-if="isLoggedIn">
              <div class="dropdown" ref="dropdownRef">
                <button class="btn btn-outline-secondary dropdown-toggle btn-sm d-flex align-items-center gap-2" 
                        type="button" 
                        @click="toggleDropdown">
                  <span>👤</span> {{ userNameShort }}
                </button>
                <ul class="dropdown-menu dropdown-menu-end shadow" :class="{ 'show': dropdownOpen }">
                  <li><span class="dropdown-item-text small text-muted text-uppercase fw-bold" style="font-size: 0.75rem;">{{ userRole }}</span></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><router-link class="dropdown-item" to="/profile" @click="closeDropdown">My Profile</router-link></li>
                  <li><button class="dropdown-item text-danger" @click="logout">Logout</button></li>
                </ul>
              </div>
            </template>
            
            <template v-else>
               <router-link to="/login" class="btn btn-primary btn-sm px-3">Sign In</router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <main class="container py-4 py-lg-5 fade-in">
      <router-view />
    </main>

    <footer class="footer mt-auto py-4 text-center">
      <div class="container">
        <small class="text-muted">
          &copy; {{ new Date().getFullYear() }} SeattleGrace Hospital. All rights reserved.
        </small>
      </div>
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
      userRole: "",
      dropdownOpen: false
    };
  },
  computed: {
    isDark() { return this.theme === "dark"; },
    themeTitle() { return this.isDark ? "Switch to Light Mode" : "Switch to Dark Mode"; },
    userNameShort() { return this.userName || "User"; }
  },
  watch: {
    $route() { 
      this.checkAuth();
      this.dropdownOpen = false; // Close dropdown on route change
    }
  },
  mounted() {
    this.applyTheme();
    this.checkAuth();
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    toggleDropdown(event) {
      event.stopPropagation(); // Prevent closing immediately
      this.dropdownOpen = !this.dropdownOpen;
    },
    closeDropdown() {
      this.dropdownOpen = false;
    },
    handleClickOutside(event) {
      if (this.$refs.dropdownRef && !this.$refs.dropdownRef.contains(event.target)) {
        this.dropdownOpen = false;
      }
    },
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
      this.applyTheme();
    },
    applyTheme() {
      const el = document.documentElement;
      el.setAttribute("data-theme", this.theme);
      if (this.theme === "dark") {
        el.classList.add("theme-dark");
        el.classList.remove("theme-light");
      } else {
        el.classList.add("theme-light");
        el.classList.remove("theme-dark");
      }
    },
    logout() {
      setAuthToken(null);
      this.isLoggedIn = false;
      this.userName = "";
      this.userRole = "";
      this.dropdownOpen = false;
      this.$router.push("/login");
    }
  }
};
</script>

<style scoped>
.app-root { 
  min-height: 100vh; 
  display: flex; 
  flex-direction: column; 
  background-color: var(--bg-body);
}
main.container { flex: 1 0 auto; }

.btn-icon {
  background: transparent;
  border: none;
  padding: 0.25rem;
  transition: transform 0.2s;
}
.btn-icon:hover { transform: scale(1.1); }

/* Ensure dropdown works with our manual class */
.dropdown-menu.show {
  display: block;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: pageFade 0.4s ease-in-out;
}
@keyframes pageFade {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>