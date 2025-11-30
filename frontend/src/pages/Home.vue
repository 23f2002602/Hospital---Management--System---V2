<template>
  <div class="home">
    <div class="text-center py-5 hero-section">
      <h1 class="display-3 fw-bold mb-3 text-gradient">SeattleGrace Hospital</h1>
      <p class="lead mb-5 mx-auto" style="max-width: 600px;">
        Advanced healthcare management for a better tomorrow. 
        Streamlined for patients, doctors, and administrators.
      </p>

      <div v-if="!isLoggedIn" class="d-flex justify-content-center gap-3">
        <router-link to="/login" class="btn btn-primary btn-lg px-5 shadow-lg">Login</router-link>
        <router-link to="/register" class="btn btn-outline-secondary btn-lg px-5">Register</router-link>
      </div>

      <div v-else>
        <p class="fs-5 mb-4">Welcome back, <span class="fw-bold text-primary">{{ role }}</span>.</p>
        <button @click="goToDashboard" class="btn btn-success btn-lg px-5 shadow-lg">
          Go to Dashboard &rarr;
        </button>
      </div>
    </div>

    <div class="container mt-5">
      <div class="row g-4">
        <div class="col-md-4">
          <div class="card h-100 p-4 border-0 shadow-hover text-center">
            <div class="icon-box bg-blue-soft mb-3 mx-auto">😷</div>
            <h5>For Patients</h5>
            <p class="text-muted small">
              Easy appointment booking, access to your medical history, and direct communication with specialists.
            </p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100 p-4 border-0 shadow-hover text-center">
            <div class="icon-box bg-green-soft mb-3 mx-auto">👨‍⚕️</div>
            <h5>For Doctors</h5>
            <p class="text-muted small">
              Manage your daily schedule, update patient records instantly, and track treatment plans efficiently.
            </p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100 p-4 border-0 shadow-hover text-center">
            <div class="icon-box bg-purple-soft mb-3 mx-auto">📊</div>
            <h5>For Admins</h5>
            <p class="text-muted small">
              Comprehensive oversight of hospital operations, user management, and detailed analytical reports.
            </p>
          </div>
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

<style scoped>
/* Gradient text effect */
.text-gradient {
  background: linear-gradient(90deg, var(--primary) 0%, #a855f7 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-section {
  animation: slideDown 0.6s ease-out;
}

/* Custom soft backgrounds for icons */
.icon-box {
  width: 60px; 
  height: 60px; 
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
}
.bg-blue-soft { background-color: rgba(37, 99, 235, 0.1); color: var(--primary); }
.bg-green-soft { background-color: rgba(16, 185, 129, 0.1); color: var(--success); }
.bg-purple-soft { background-color: rgba(168, 85, 247, 0.1); color: #a855f7; }

/* Hover lift effect */
.shadow-hover { transition: transform 0.3s, box-shadow 0.3s; }
.shadow-hover:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md) !important;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>