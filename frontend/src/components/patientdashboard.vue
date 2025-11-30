<template>
  <div class="container mt-3">
    <div class="row">
      <div class="col-md-4 mb-3">
        <div class="card p-4 shadow-sm text-center mb-3">
          <h5>Welcome Back</h5>
          <p class="text-muted">Manage your health journey.</p>
          <router-link to="/search" class="btn btn-primary w-100 mb-2">Book New Appointment</router-link>
          <router-link to="/profile" class="btn btn-outline-secondary w-100">Update Profile</router-link>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card p-3 mb-4 shadow-sm">
          <h5 class="mb-3 border-bottom pb-2">Upcoming Appointments</h5>
          <div v-if="upcoming.length === 0" class="text-muted py-3">You have no scheduled appointments.</div>
          <ul class="list-group list-group-flush">
            <li v-for="a in upcoming" :key="a.id" class="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{{ a.doctor_name }}</strong>
                <div class="text-muted small">{{ new Date(a.start_time).toLocaleString() }}</div>
                <div class="small fst-italic">{{ a.problem }}</div>
              </div>
              <div>
                <button class="btn btn-sm btn-outline-danger" @click="cancel(a)">Cancel</button>
              </div>
            </li>
          </ul>
        </div>

        <div class="card p-3 shadow-sm">
          <h5 class="mb-3 border-bottom pb-2">Past History</h5>
          <div v-if="past.length === 0" class="text-muted py-3">No past history found.</div>
          <ul class="list-group list-group-flush">
            <li v-for="a in past" :key="a.id" class="list-group-item">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <strong>{{ a.doctor_name }}</strong>
                  <span class="text-muted small ms-2">{{ new Date(a.start_time).toLocaleDateString() }}</span>
                </div>
                <span :class="statusBadge(a.status)" class="badge">{{ a.status }}</span>
              </div>
              
              <div class="mt-2 p-2 bg-light rounded small" v-if="a.treatment && a.status === 'completed'">
                <div><span class="fw-bold">Diagnosis:</span> {{ a.treatment.diagnosis }}</div>
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
        // Fetch Booked
        const res1 = await api.get("/patient/appointments?status=booked");
        this.upcoming = res1.data;
        
        // Fetch Completed
        const res2 = await api.get("/patient/appointments?status=completed");
        
        // Fetch Cancelled (optional, but good for history)
        const res3 = await api.get("/patient/appointments?status=cancelled");
        
        // Combine completed and cancelled for "History"
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