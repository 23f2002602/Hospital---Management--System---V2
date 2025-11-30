<template>
  <div class="card shadow-sm border-0 h-100">
    <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0">
      <h5 class="mb-3 fw-bold text-primary">Find a Specialist</h5>
      
      <div class="input-group mb-3 shadow-sm">
        <span class="input-group-text bg-white border-end-0">
          🔍
        </span>
        <input 
          v-model="q" 
          @keyup.enter="search" 
          placeholder="Search by name, specialization, or email..." 
          class="form-control border-start-0 ps-0"
        />
        <button class="btn btn-primary px-4" @click="search" :disabled="loading">
          {{ loading ? '...' : 'Search' }}
        </button>
      </div>
    </div>

    <div class="card-body px-0 pt-2">
      <div v-if="loading" class="text-center py-5 text-muted">
        <div class="spinner-border text-primary mb-2" role="status"></div>
        <div>Searching doctors...</div>
      </div>

      <div v-else-if="doctors.length === 0" class="text-center py-5 text-muted">
        <div style="font-size: 2rem;">👨‍⚕️</div>
        <p class="mt-2">No doctors found matching your criteria.</p>
      </div>

      <div v-else class="list-group list-group-flush">
        <div 
          v-for="d in doctors" 
          :key="d.id" 
          class="list-group-item d-flex justify-content-between align-items-center px-4 py-3 border-bottom-0 doctor-item"
        >
          <div class="d-flex align-items-center gap-3">
            <div 
              class="avatar rounded-circle bg-primary text-white d-flex align-items-center justify-content-center shadow-sm"
              style="width: 48px; height: 48px; font-weight: 600; font-size: 1.1rem; flex-shrink: 0;"
            >
              {{ getInitials(d.name) }}
            </div>
            
            <div style="min-width: 0;">
              <h6 class="mb-0 text-truncate fw-bold text-dark">{{ d.name }}</h6>
              <div class="text-primary small mb-1">{{ d.specialization || 'General Practitioner' }}</div>
              <small class="text-muted d-block text-truncate">📧 {{ d.email }}</small>
            </div>
          </div>
          
          <button 
            class="btn btn-sm btn-outline-primary ms-2 px-3 rounded-pill" 
            @click="$emit('book', d)"
          >
            Book
          </button>
        </div>
      </div>
    </div>

    <div class="card-footer bg-transparent border-0 d-flex justify-content-between align-items-center px-4 pb-4">
      <button 
        class="btn btn-sm btn-light text-muted" 
        :disabled="page <= 1 || loading" 
        @click="prev"
      >
        &larr; Prev
      </button>
      <span class="small text-muted">Page {{ page }}</span>
      <button 
        class="btn btn-sm btn-light text-muted" 
        :disabled="doctors.length < per_page || loading" 
        @click="next"
      >
        Next &rarr;
      </button>
    </div>
  </div>
</template>

<script>
import api from "../api/api";

export default {
  name: "SearchDoctors",
  emits: ["book"],
  data() {
    return { 
      q: '', 
      doctors: [], 
      page: 1, 
      per_page: 10,
      loading: false
    };
  },
  mounted() { 
    this.search(); 
  },
  methods: {
    async search() {
      this.loading = true;
      try {
        const res = await api.get(`/patient/doctors?q=${encodeURIComponent(this.q)}&page=${this.page}&per_page=${this.per_page}`);
        this.doctors = res.data.doctors || [];
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
    prev() { if(this.page > 1) { this.page--; this.search(); } },
    next() { this.page++; this.search(); },
    getInitials(name) {
      if (!name) return "Dr";
      return name
        .replace(/^Dr\.?\s*/i, "") // Remove "Dr." prefix
        .split(" ")
        .map(n => n[0])
        .slice(0, 2)
        .join("")
        .toUpperCase();
    }
  }
}
</script>

<style scoped>
.doctor-item {
  transition: background-color 0.2s;
  cursor: default;
}
.doctor-item:hover {
  background-color: var(--bg-surface-alt);
}
.avatar {
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
}
.form-control:focus {
  box-shadow: none;
  border-color: var(--border-color);
}
.input-group-text {
  color: var(--text-muted);
}
.input-group:focus-within {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
  border-radius: 0.375rem;
}
</style>