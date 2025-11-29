<template>
  <div class="row justify-content-center">
    <div class="col-12 col-sm-9 col-md-6 col-lg-4">
      <div class="card p-4 shadow-sm">
        <h4 class="mb-3 text-center">Sign in</h4>
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" v-model="email" class="form-control" @blur="validateEmail" required />
            <div class="form-text text-danger" v-if="errors.email">{{ errors.email }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input type="password" v-model="password" class="form-control" required minlength="6" />
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
import api from "../api/api.js"; // adapt path to your api wrapper

export default {
  data() {
    return {
      email: "",
      password: "",
      loading: false,
      errors: {}
    };
  },
  methods: {
    validateEmail() {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      this.errors.email = re.test(this.email) ? null : "Invalid email";
    },
    async submit() {
      this.validateEmail();
      if (this.errors.email) return;
      this.loading = true;
      try {
        const res = await api.post("/auth/login", { email: this.email, password: this.password });
        const token = res.data.access_token || res.data.token;
        localStorage.setItem("token", token);
        // optional: parse token to get name
        try {
          const payload = JSON.parse(atob(token.split(".")[1]));
          localStorage.setItem("user_name", payload.name || payload.email || "User");
        } catch {}
        // set auth header in your api helper
        api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        this.$router.push("/");
      } catch (err) {
        const msg = err.response?.data?.msg || "Login failed";
        alert(msg);
      } finally { this.loading = false; }
    }
  }
};
</script>

<style scoped>
.card { margin-top: 2rem; }
</style>
