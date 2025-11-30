<template>
  <div class="doctor-dashboard">
    <div class="row mb-4">
      <div class="col-md-8">
        <h3 class="mb-1">Doctor Dashboard</h3>
        <p class="text-muted">Welcome back, manage your schedule and patients.</p>
      </div>
      <div class="col-md-4 text-md-end">
        <button class="btn btn-outline-secondary me-2" @click="refreshAll" :disabled="loading">Refresh</button>
        <button class="btn btn-outline-primary" @click="exportCsv">Export CSV</button>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card p-3 border-primary h-100">
          <h6 class="text-primary">Appointments Today</h6>
          <h2 class="m-0">{{ todayCount }}</h2>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card p-3 border-success h-100">
          <h6 class="text-success">Total Completed</h6>
          <h2 class="m-0">{{ completedCount }}</h2>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card p-3 border-info h-100">
          <h6 class="text-info">Upcoming</h6>
          <h2 class="m-0">{{ appointments.length }}</h2>
        </div>
      </div>
    </div>

    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <button class="nav-link" :class="{active: tab==='appointments'}" @click="tab='appointments'">Appointments</button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{active: tab==='patients'}" @click="tab='patients'">Patients</button>
      </li>
    </ul>

    <div v-if="tab === 'appointments'">
      <div class="row gx-3 gy-3">
        <div class="col-lg-8">
          <div class="card p-3 shadow-sm">
            <h5>Upcoming Schedule</h5>
            <div v-if="appointments.length === 0" class="text-center py-5 text-muted">
              No upcoming appointments found.
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Time</th>
                    <th>Reason</th>
                    <th class="text-end">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in appointments" :key="a.id">
                    <td>{{ a.patient_name || '—' }}</td>
                    <td>
                      <div>{{ formatDate(a.start_time) }}</div>
                      <small class="text-muted">{{ formatTime(a.start_time) }}</small>
                    </td>
                    <td>{{ a.problem }}</td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-success me-1" @click="openTreatmentModal(a)">Complete</button>
                      <button class="btn btn-sm btn-outline-danger" @click="cancelAppointment(a)">Cancel</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card p-3 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="m-0 fw-bold">My Availability</h6>
              <button class="btn btn-sm btn-primary" @click="openAvailModal">Manage</button>
            </div>
            <ul class="list-group list-group-flush small">
              <li v-for="d in availability" :key="d.date" class="list-group-item d-flex justify-content-between">
                <span>{{ d.day }} <span class="text-muted">({{ d.date.slice(5) }})</span></span>
                <span v-if="d.is_available" class="badge bg-success">{{ d.start_time }} - {{ d.end_time }}</span>
                <span v-else class="badge bg-secondary">Off</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'patients'">
      <doctor-patients />
    </div>

    <div class="modal fade" tabindex="-1" ref="availModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Weekly Schedule</h5>
            <button type="button" class="btn-close" @click="closeAvailModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveAvailability">
              <div class="mb-3">
                <label class="form-label">Day (Next 7 Days)</label>
                <select v-model="availForm.day" class="form-control">
                  <option v-for="d in next7Days" :key="d.value" :value="d.value">{{ d.label }}</option>
                </select>
              </div>
              <div class="row mb-3">
                <div class="col">
                  <label class="form-label">Start Time</label>
                  <input type="time" v-model="availForm.start" class="form-control">
                </div>
                <div class="col">
                  <label class="form-label">End Time</label>
                  <input type="time" v-model="availForm.end" class="form-control">
                </div>
              </div>
              <div class="form-check mb-3">
                <input type="checkbox" class="form-check-input" id="availCheck" v-model="availForm.is_active">
                <label class="form-check-label" for="availCheck">Available on this day</label>
              </div>
              <button class="btn btn-success w-100">Save Schedule</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" ref="treatmentModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Complete Appointment</h5>
            <button type="button" class="btn-close" @click="closeTreatmentModal"></button>
          </div>
          <div class="modal-body">
            <p v-if="selectedAppt"><strong>Patient:</strong> {{ selectedAppt.patient_name }}</p>
            <form @submit.prevent="submitTreatment">
              <div class="mb-3">
                <label class="form-label">Diagnosis</label>
                <input v-model="treatmentForm.diagnosis" class="form-control" placeholder="e.g. Migraine" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Prescription</label>
                <textarea v-model="treatmentForm.prescription" class="form-control" rows="3" placeholder="e.g. Paracetamol 500mg" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Notes (Optional)</label>
                <textarea v-model="treatmentForm.notes" class="form-control" rows="2"></textarea>
              </div>
              <button class="btn btn-primary w-100" :disabled="processing">
                {{ processing ? 'Saving...' : 'Save & Complete' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import DoctorPatients from "./DoctorPatients.vue";
import api from "../api/api.js";
import { Modal } from "bootstrap";

export default {
  name: "DoctorDashboard",
  components: { DoctorPatients },
  data() {
    return {
      tab: "appointments",
      appointments: [],
      availability: [],
      loading: false,
      processing: false,
      
      // Modals
      availModal: null,
      treatmentModal: null,
      
      // Forms
      availForm: { day: 'Monday', start: '09:00', end: '17:00', is_active: true },
      treatmentForm: { diagnosis: "", prescription: "", notes: "" },
      selectedAppt: null
    };
  },
  computed: {
    todayCount() {
      const today = new Date().toISOString().slice(0, 10);
      return this.appointments.filter(a => a.date && a.date.startsWith(today)).length;
    },
    completedCount() { return 0; }, 
    
    next7Days() {
      const days = [];
      const today = new Date();
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      for (let i = 0; i < 7; i++) {
        const d = new Date(today);
        d.setDate(today.getDate() + i);
        const dayName = dayNames[d.getDay()];
        const dateStr = d.toLocaleDateString(undefined, { month: 'numeric', day: 'numeric' });
        days.push({ value: dayName, label: `${dayName} (${dateStr})` });
      }
      return days;
    }
  },
  mounted() {
    this.loadAll();
    this.availModal = new Modal(this.$refs.availModal);
    this.treatmentModal = new Modal(this.$refs.treatmentModal);
  },
  methods: {
    async loadAll() {
      this.loading = true;
      await Promise.all([this.loadAppointments(), this.loadAvailability()]);
      this.loading = false;
    },
    async loadAppointments() {
      try {
        const resp = await api.get("/doctor/appointments?upcoming=true");
        this.appointments = resp.data || [];
      } catch (e) { this.appointments = []; }
    },
    async loadAvailability() {
      try {
        const resp = await api.get("/doctor/availability/next");
        this.availability = resp.data || [];
      } catch (e) { this.availability = []; }
    },
    formatDate(iso) { return iso ? new Date(iso).toLocaleDateString() : ''; },
    formatTime(iso) { return iso ? new Date(iso).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) : ''; },
    
    // --- AVAILABILITY LOGIC ---
    openAvailModal() { 
      const today = new Date();
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      this.availForm.day = dayNames[today.getDay()];
      this.availModal.show(); 
    },
    closeAvailModal() { this.availModal.hide(); },
    async saveAvailability() {
      try {
        await api.post("/doctor/availability/week", {
          entries: [{ 
            day_of_week: this.availForm.day, 
            start_time: this.availForm.start, 
            end_time: this.availForm.end, 
            is_available: this.availForm.is_active 
          }]
        });
        alert("Saved!");
        this.closeAvailModal();
        this.loadAvailability();
      } catch(e) { alert("Failed to save schedule"); }
    },

    // --- TREATMENT LOGIC ---
    openTreatmentModal(appt) {
      this.selectedAppt = appt;
      this.treatmentForm = { diagnosis: "", prescription: "", notes: "" };
      this.treatmentModal.show();
    },
    closeTreatmentModal() {
      this.treatmentModal.hide();
      this.selectedAppt = null;
    },
    async submitTreatment() {
      if (!this.selectedAppt) return;
      this.processing = true;
      try {
        await api.post(`/doctor/appointments/${this.selectedAppt.id}/treatment`, this.treatmentForm);
        alert("Appointment Completed!");
        this.closeTreatmentModal();
        this.loadAppointments(); // Refresh list
      } catch(e) {
        // Show actual backend error
        const errorMsg = e.response?.data?.msg || e.response?.data?.error || "Failed to complete appointment";
        alert(`Error: ${errorMsg}`);
      } finally {
        this.processing = false;
      }
    },

    async cancelAppointment(a) {
      if(!confirm("Are you sure you want to cancel this appointment?")) return;
      try {
        await api.post(`/doctor/appointments/${a.id}/cancel`);
        this.loadAppointments();
      } catch(e) { alert("Failed to cancel"); }
    },
    exportCsv() {
      window.open(`${api.defaults.baseURL}/doctor/appointments/export?token=${localStorage.getItem('token')}`);
    },
    refreshAll() { this.loadAll(); }
  }
};
</script>