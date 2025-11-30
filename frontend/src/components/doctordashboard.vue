<template>
  <div class="doctor-dashboard container mt-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-3">
      <div>
        <h3 class="mb-1">Doctor Dashboard</h3>
        <p class="text-muted mb-0">Manage your schedule and patients.</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary" @click="refreshAll" :disabled="loading">
          {{ loading ? '...' : 'Refresh' }}
        </button>
        <button class="btn btn-outline-primary" @click="exportCsv">Export CSV</button>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-12 col-md-4">
        <div class="card p-3 border-start border-4 border-primary shadow-sm h-100">
          <h6 class="text-primary text-uppercase small fw-bold">Today</h6>
          <h2 class="m-0 display-6">{{ todayCount }}</h2>
          <small class="text-muted">Appointments</small>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card p-3 border-start border-4 border-success shadow-sm h-100">
          <h6 class="text-success text-uppercase small fw-bold">Completed</h6>
          <h2 class="m-0 display-6">{{ completedCount }}</h2>
          <small class="text-muted">Total patients</small>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card p-3 border-start border-4 border-info shadow-sm h-100">
          <h6 class="text-info text-uppercase small fw-bold">Upcoming</h6>
          <h2 class="m-0 display-6">{{ appointments.length }}</h2>
          <small class="text-muted">Pending</small>
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
      <div class="row g-4">
        <div class="col-12 col-lg-8">
          <div class="card p-3 shadow-sm border-0 h-100">
            <h5 class="card-title mb-3">Upcoming Schedule</h5>
            <div v-if="appointments.length === 0" class="text-center py-5 text-muted">
              No upcoming appointments.
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Patient</th>
                    <th>Time</th>
                    <th>Reason</th>
                    <th class="text-end">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in appointments" :key="a.id">
                    <td class="fw-medium">{{ a.patient_name || '—' }}</td>
                    <td>
                      <div>{{ formatDate(a.start_time) }}</div>
                      <small class="text-muted">{{ formatTime(a.start_time) }}</small>
                    </td>
                    <td><div class="text-truncate" style="max-width: 150px;" :title="a.problem">{{ a.problem }}</div></td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-success me-1" @click="openTreatmentModal(a)">✓</button>
                      <button class="btn btn-sm btn-outline-danger" @click="cancelAppointment(a)">✕</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="col-12 col-lg-4">
          <div class="card p-3 shadow-sm border-0 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="m-0 fw-bold">My Availability</h6>
              <button class="btn btn-sm btn-primary py-0" @click="openAvailModal">Manage</button>
            </div>
            <ul class="list-group list-group-flush small">
              <li v-for="d in availability" :key="d.date" class="list-group-item d-flex justify-content-between align-items-center px-0">
                <span>{{ d.day.substring(0,3) }} <span class="text-muted" style="font-size:0.8em">({{ d.date.slice(5) }})</span></span>
                <span v-if="d.is_available" class="badge bg-success rounded-pill">{{ d.start_time }} - {{ d.end_time }}</span>
                <span v-else class="badge bg-light text-muted border">Off</span>
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
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Schedule</h5>
            <button type="button" class="btn-close" @click="closeAvailModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveAvailability">
              <div class="mb-3">
                <label class="form-label">Day</label>
                <select v-model="availForm.day" class="form-select">
                  <option v-for="d in next7Days" :key="d.value" :value="d.value">{{ d.label }}</option>
                </select>
              </div>
              <div class="row g-2 mb-3">
                <div class="col">
                  <label class="form-label">Start</label>
                  <input type="time" v-model="availForm.start" class="form-control">
                </div>
                <div class="col">
                  <label class="form-label">End</label>
                  <input type="time" v-model="availForm.end" class="form-control">
                </div>
              </div>
              <div class="form-check form-switch mb-3">
                <input type="checkbox" class="form-check-input" id="availCheck" v-model="availForm.is_active">
                <label class="form-check-label" for="availCheck">Available</label>
              </div>
              <button class="btn btn-success w-100">Save</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" ref="treatmentModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Complete Appointment</h5>
            <button type="button" class="btn-close" @click="closeTreatmentModal"></button>
          </div>
          <div class="modal-body">
            <p v-if="selectedAppt" class="mb-3">Patient: <strong>{{ selectedAppt.patient_name }}</strong></p>
            <form @submit.prevent="submitTreatment">
              <div class="mb-3">
                <label class="form-label">Diagnosis</label>
                <input v-model="treatmentForm.diagnosis" class="form-control" placeholder="Diagnosis" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Prescription</label>
                <textarea v-model="treatmentForm.prescription" class="form-control" rows="3" placeholder="Prescription details..." required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea v-model="treatmentForm.notes" class="form-control" rows="2" placeholder="Private notes..."></textarea>
              </div>
              <button class="btn btn-primary w-100" :disabled="processing">
                {{ processing ? 'Saving...' : 'Complete Appointment' }}
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
      availModal: null,
      treatmentModal: null,
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
        this.loadAppointments();
      } catch(e) {
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