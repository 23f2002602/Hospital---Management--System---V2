<template>
  <div class="container mt-4">
    <h2 class="mb-4">My Dashboard</h2>
    <div class="row g-4">
      <div class="col-12 col-lg-4 order-lg-last">
        <div class="card p-4 shadow-sm border-0 text-center h-100">
          <div class="mb-3 text-primary" style="font-size: 3rem;">🏥</div>
          <h5 class="card-title">Welcome Back</h5>
          <p class="text-muted">Manage your health journey.</p>
          <div class="d-grid gap-2 mt-4">
            <router-link to="/search" class="btn btn-primary">Book New Appointment</router-link>
            <router-link to="/profile" class="btn btn-outline-secondary">Update Profile</router-link>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-8">
        <div class="card p-4 mb-4 shadow-sm border-0">
          <h5 class="mb-3 border-bottom pb-2 d-flex justify-content-between align-items-center">
            Upcoming Appointments
            <span class="badge bg-primary rounded-pill">{{ upcoming.length }}</span>
          </h5>
          
          <div v-if="upcoming.length === 0" class="text-muted py-4 text-center bg-light rounded">
            You have no scheduled appointments.
          </div>
          
          <ul v-else class="list-group list-group-flush">
            <li v-for="a in upcoming" :key="a.id" class="list-group-item px-0 py-3">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="mb-1 text-primary">{{ a.doctor_name }}</h6>
                  <div class="text-muted small">
                    📅 {{ new Date(a.start_time).toLocaleDateString() }} 
                    ⏰ {{ new Date(a.start_time).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) }}
                  </div>
                  <div class="small fst-italic mt-1 opacity-75">"{{ a.problem }}"</div>
                </div>
                <button class="btn btn-sm btn-outline-danger" @click="cancel(a)">Cancel</button>
              </div>
            </li>
          </ul>
        </div>

        <div class="card p-4 shadow-sm border-0">
          <h5 class="mb-3 border-bottom pb-2">History</h5>
          <div v-if="past.length === 0" class="text-muted py-4 text-center bg-light rounded">
            No past history found.
          </div>
          <ul v-else class="list-group list-group-flush">
            <li v-for="a in past" :key="a.id" class="list-group-item px-0 py-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                  <strong class="fw-bold">{{ a.doctor_name }}</strong>
                  <span class="text-muted small ms-2">{{ new Date(a.start_time).toLocaleDateString() }}</span>
                </div>
                <span :class="statusBadge(a.status)" class="badge">{{ a.status }}</span>
              </div>
              
              <div class="p-3 bg-light rounded small" v-if="a.treatment && a.status === 'completed'">
                <div class="mb-1"><span class="fw-bold">Diagnosis:</span> {{ a.treatment.diagnosis }}</div>
                <div><span class="fw-bold">Prescription:</span> {{ a.treatment.prescription }}</div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api/api";

export default {
  name: "PatientDashboard",
  data(){ return { upcoming:[], past:[] } },
  mounted(){ this.loadAppointments(); },
  methods:{
    async loadAppointments(){
      try {
        const res1 = await api.get("/patient/appointments?status=booked");
        this.upcoming = res1.data;
        
        const res2 = await api.get("/patient/appointments?status=completed");
        const res3 = await api.get("/patient/appointments?status=cancelled");
        
        this.past = [...res2.data, ...res3.data].sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
      } catch(e) { console.error(e); }
    },
    async cancel(a){
      if(!confirm("Cancel appointment?")) return;
      try {
        await api.post(`/patient/appointments/${a.id}/cancel`);
        this.loadAppointments();
      } catch(e) { alert(e.response?.data?.msg || "Failed to cancel"); }
    },
    statusBadge(status) {
      if (status === 'completed') return 'bg-success';
      if (status === 'cancelled') return 'bg-danger';
      return 'bg-secondary';
    }
  }
}
</script>