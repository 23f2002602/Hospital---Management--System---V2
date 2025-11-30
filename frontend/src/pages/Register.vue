<template>
  <div class="container" style="max-width:640px;margin-top:2.5rem;">
    <div class="card p-4">
      <h4 class="mb-3">Create account</h4>

      <div class="row g-2">
        <div class="col-md-6">
          <input v-model="name" class="form-control" placeholder="Full name"/>
        </div>
        <div class="col-md-6">
          <input v-model="email" class="form-control" placeholder="Email"/>
        </div>
      </div>

      <div class="row g-2 mt-2">
        <div class="col-md-6">
          <input v-model="password" type="password" class="form-control" placeholder="Password"/>
        </div>
        <div class="col-md-6">
          <input v-model="phone" class="form-control" placeholder="Phone"/>
        </div>
      </div>

      <div class="row g-2 mt-2">
        <div class="col-md-4">
          <input type="date" v-model="dob" class="form-control" />
        </div>
        <div class="col-md-4">
          <select v-model="gender" class="form-control">
            <option value="">Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="col-md-4">
          <button class="btn btn-primary w-100" @click="submit" :disabled="loading">
            {{ loading ? "Creating..." : "Create account" }}
          </button>
        </div>
      </div>

      <div v-if="err" class="alert alert-danger mt-2">{{ err }}</div>
      <div class="mt-2">
        <small>Already have an account?</small> <router-link to="/login">Sign in</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import api, { setAuthToken, decodeJwt } from "../api/api";

export default {
  name: "RegisterPage",
  data() {
    return { name: "", email: "", password: "", phone: "", dob: "", gender: "", loading: false, err: "" };
  },
  methods: {
    async submit() {
      this.err = "";
      if (!this.name || !this.email || !this.password) { this.err = "Name, email, and password required"; return; }
      this.loading = true;
      try {
        const payload = {
          name: this.name,
          email: this.email,
          password: this.password,
          phone: this.phone || null,
          dob: this.dob || null,
          gender: this.gender || null
        };
        await api.post("/auth/register", payload);
        
        // Auto-login
        const loginRes = await api.post("/auth/login", { email: this.email, password: this.password });
        const token = loginRes.data.access_token;
        setAuthToken(token);
        
        // --- FIX: Save actual Name ---
        localStorage.setItem("user_name", loginRes.data.name);
        
        const payloadDec = decodeJwt(token);
        const role = payloadDec?.role || loginRes.data.role || "patient";
        localStorage.setItem("role", role);
        
        this.$router.push("/patient");
      } catch (e) {
        this.err = e.response?.data?.msg || e.message || "Registration failed";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>