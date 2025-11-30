<template>
  <div class="text-center mt-5 pt-5">
    <h1 class="display-1 fw-bold text-muted">404</h1>
    <p class="lead">Page Not Found</p>
    <button class="btn btn-primary" @click="goBack">Go Home</button>
  </div>
</template>

<script>
export default {
  name: "NotFound",
  methods: {
    goBack() {
      const role = localStorage.getItem("role");
      const token = localStorage.getItem("token");

      if (token && role) {
        if (role === 'admin') this.$router.push('/admin');
        else if (role === 'doctor') this.$router.push('/doctor');
        else this.$router.push('/patient');
      } else {
        this.$router.push('/');
      }
    }
  }
};
</script>