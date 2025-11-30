<template>
  <div class="row justify-content-center">
    <div class="col-12 col-sm-9 col-md-6 col-lg-4">
      <div class="card p-4 shadow-sm">
        <h4 class="mb-3 text-center">Sign in</h4>
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" v-model="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input type="password" v-model="password" class="form-control" required />
          </div>
          <button :disabled="loading" class="btn btn-primary w-100">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Login
          </button>
        </form>
        <div class="text-center mt-3">
          <router-link to="/register">Create account</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { setAuthToken, decodeJwt } from "../api/api.js";

export default {
  data() { return { email: "", password: "", loading: false }; },
  methods: {
    async submit() {
      this.loading = true;
      try {
        const res = await api.post("/auth/login", { email: this.email, password: this.password });
        const token = res.data.access_token;
        
        // 1. Set Token centrally
        setAuthToken(token);
        
        // 2. Decode role info
        const payload = decodeJwt(token);
        const role = payload?.role || res.data.role;
        
        // 3. Save basic info
        localStorage.setItem("user_name", this.email.split('@')[0]); 
        localStorage.setItem("role", role);

        // 4. Force redirection
        if (role === 'admin') this.$router.push('/admin');
        else if (role === 'doctor') this.$router.push('/doctor');
        else this.$router.push('/patient');

      } catch (err) {
        const msg = err.response?.data?.msg || "Login failed";
        alert(msg);
      } finally { 
        this.loading = false; 
      }
    }
  }
};
</script>

<style scoped>
.card { margin-top: 2rem; }
</style>