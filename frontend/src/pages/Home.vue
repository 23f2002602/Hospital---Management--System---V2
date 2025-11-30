<template>
  <div class="home text-center py-5">
    <h1 class="display-4 mb-4 fw-bold">Welcome to SeattleGrace</h1>
    <p class="lead mb-5">
      A modern Hospital Management System for Patients, Doctors, and Administrators.
    </p>

    <div v-if="!isLoggedIn" class="d-flex justify-content-center gap-3">
      <router-link to="/login" class="btn btn-primary btn-lg px-4">Login</router-link>
      <router-link to="/register" class="btn btn-outline-secondary btn-lg px-4">Register</router-link>
    </div>

    <div v-else>
      <p class="fs-5">You are logged in as <strong>{{ role }}</strong>.</p>
      <button @click="goToDashboard" class="btn btn-success btn-lg px-5">Go to Dashboard</button>
    </div>

    <div class="row mt-5 g-4">
      <div class="col-md-4">
        <div class="card p-4 h-100 shadow-sm border-0 bg-light">
          <h5>For Patients</h5>
          <p class="text-muted">Book appointments, view history, and manage your profile.</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card p-4 h-100 shadow-sm border-0 bg-light">
          <h5>For Doctors</h5>
          <p class="text-muted">Manage schedules, view patient history, and prescribe treatments.</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card p-4 h-100 shadow-sm border-0 bg-light">
          <h5>For Admins</h5>
          <p class="text-muted">Manage users, departments, and generate system reports.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomePage",
  data() {
    return {
      isLoggedIn: !!localStorage.getItem("token"),
      role: localStorage.getItem("role")
    }
  },
  methods: {
    goToDashboard() {
      if (this.role === 'admin') this.$router.push('/admin');
      else if (this.role === 'doctor') this.$router.push('/doctor');
      else this.$router.push('/patient');
    }
  }
};
</script>