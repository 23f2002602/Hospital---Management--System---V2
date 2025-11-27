<template>
  <div>
    <nav class="navbar navbar-expand-lg" :class="['py-2', 'px-3']" style="border-bottom:1px solid var(--border);">
      <div class="container-fluid">
        <a class="navbar-brand" href="#" style="color:var(--text); font-weight:600">Hospital Management System</a>
      

        <button class="navbar-toggle" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navMenu">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <!-- Add navigation items here -->
          </ul>

          <div class="d-flex align-items-center gap-2">
            <div class="theme-toggle" @click="toggle-Theme" :title="theme === 'dark' ? 'Switch to light':'Switch to dark'" >
              <svg v-if="theme === 'dark'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-sun" viewBox="0 0 16 16">
                <path d="M8 4.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z"/>
                <path d="M8 0a.5.5 0 0 1 .5.5V2a.5.5 0 0 1-1 0V.5A.5.5 0 0 1 8 0zM8 14a.5.5 0 0 1 .5.5v1.5a.5.5 0 0 1-1 0V14.5A.5.5 0 0 1 8 14zM14 8a.5.5 0 0 1 .5.5H16a.5.5 0 0 1 0 1h-1.5A.5.5 0 0 1 14 8zM0 8a.5.5 0 0 1 .5.5H2a.5.5 0 0 1 0-1H.5A.5.5 0 0 1 0 8zM12.657 3.343a.5.5 0 0 1 .707 0l1.061 1.06a.5.5 0 0 1-.707.707L12.657 4.05a.5.5 0 0 1 0-.707zM2.636 13.364a.5.5 0 0 1 .707 0l1.06-1.06a.5.5 0 1 1-.707-.707l-1.06 1.06a.5.5 0 0 1 0 .707zM13.364 13.364a.5.5 0 0 1 0-.707l1.06-1.06a.5.5 0 1 1 .707.707l-1.06 1.06a.5.5 0 0 1-.707 0zM3.343 3.343a.5.5 0 0 1 .707.707L3-1.06A.5.5 0 1 1 1.586 2.636l1.757.707z"/>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-moon" viewBox="0 0 16 16">
                  <path d="M6 0a6 6 0 0 0 0 12 6 6 0 1 1 0-12z"/>
              </svg>
              <small class="text-muted" :style="{color:'var(--muted)'}">{{ theme === 'dark' ? 'Dark' : 'Light' }}</small>
            </div>

            <button class="btn btn-outline-secondary btn-sm" @click="logout">Logout</button>
          </div>
        </div>
      </div>
    </nav>

    <main class="container">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import {getTheme, setTheme} from "./main";

export default{
  data() {return { theme: getTheme() }; },
  methods: {
    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark';
      setTheme(this.theme);
    },
    logout(){
      localStorage.removeItem("token");
      this.$router.push("/login");
    }
  }
};
</script>

<style>
/* small safety: navbar uses tokens */
.navbar { background: var(--surface); color: var(--text); }
.navbar .navbar-brand { color: var(--text) !important; }
</style>
