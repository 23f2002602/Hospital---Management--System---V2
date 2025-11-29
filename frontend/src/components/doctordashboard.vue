<template>
  <div class="doctor-dashboard">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="m-0">Doctor Dashboard</h3>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary" @click="refreshAll" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm"></span>
          Refresh
        </button>
        <button class="btn btn-outline-primary" @click="exportCsv" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm"></span>
          Export CSV
        </button>
      </div>
    </div>

    <ul class="nav nav-tabs mb-3" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{active: tab==='appointments'}" @click="tab='appointments'">Appointments</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{active: tab==='patients'}" @click="tab='patients'">Patients</button>
      </li>
      <li class="nav-item ms-auto" role="presentation">
        <small class="text-muted align-self-center">X-Cache: <strong>{{ cacheHeader || '—' }}</strong></small>
      </li>
    </ul>

    <div v-if="tab === 'appointments'">
      <div class="row gx-3 gy-3">
        <div class="col-12 col-lg-8">
          <div class="card p-3">
            <h5>Upcoming Appointments</h5>
            <div v-if="appointments.length === 0" class="py-4 text-center text-muted">
              No upcoming appointments
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Problem</th>
                    <th>Status</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in appointments" :key="a.id">
                    <td>{{ a.patient_name || '—' }}</td>
                    <td>{{ formatDate(a.start_time) }}</td>
                    <td>{{ formatTimeRange(a.start_time, a.end_time) }}</td>
                    <td class="text-truncate" style="max-width:200px">{{ a.problem || '—' }}</td>
                    <td>
                      <span :class="statusBadge(a.status)">{{ a.status }}</span>
                    </td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-secondary me-1" @click="viewAppointment(a)">
                        View
                      </button>
                      <button v-if="a.status==='booked'" class="btn btn-sm btn-success me-1" @click="completeAppointment(a)" :disabled="a.processing">
                        ✓ Complete
                      </button>
                      <button v-if="a.status==='booked'" class="btn btn-sm btn-danger" @click="cancelAppointment(a)" :disabled="a.processing">
                        ✕ Cancel
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>

        <div class="col-12 col-lg-4">
          <div class="card p-3 mb-3">
            <h6>Availability (next 7 days)</h6>
            <div v-if="availability.length === 0" class="text-muted">No availability set.</div>
            <ul class="list-group list-group-flush">
              <li v-for="d in availability" :key="d.date" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <div class="fw-semibold">{{ d.day }}</div>
                  <small class="text-muted">{{ d.date }}</small>
                </div>
                <div class="text-end">
                  <div v-if="d.is_available">
                    <small>{{ d.start_time || '—' }} — {{ d.end_time || '—' }}</small>
                  </div>
                  <div v-else>
                    <small class="text-danger">Off</small>
                  </div>
                </div>
              </li>
            </ul>
          </div>

          <div class="card p-3">
            <h6>Quick Actions</h6>
            <button class="btn btn-outline-secondary w-100 mb-2" @click="refreshAvailability">Refresh Availability</button>
            <button class="btn btn-outline-info w-100" @click="openPatientsTab">Open Patients</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'patients'">
      <doctor-patients />
    </div>

    <!-- Appointment detail modal -->
    <div class="modal fade" tabindex="-1" ref="apptModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="currentAppt">
              <p><strong>Patient:</strong> {{ currentAppt.patient_name }}</p>
              <p><strong>Date/Time:</strong> {{ formatDate(currentAppt.start_time) }} — {{ formatTimeRange(currentAppt.start_time, currentAppt.end_time) }}</p>
              <p><strong>Problem:</strong> {{ currentAppt.problem || '—' }}</p>
              <hr />
              <div v-if="currentAppt.treatment">
                <h6>Treatment</h6>
                <p><strong>Diagnosis:</strong> {{ currentAppt.treatment.diagnosis }}</p>
                <p><strong>Prescription:</strong> {{ currentAppt.treatment.prescription }}</p>
                <p><strong>Notes:</strong> {{ currentAppt.treatment.notes }}</p>
              </div>
              <div v-else>
                <p class="text-muted">No treatment recorded yet.</p>
              </div>
            </div>
            <div v-else class="text-center text-muted">No appointment selected</div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import DoctorPatients from "./DoctorPatients.vue";
import api from "../api/api.js"; // adjust path if your api is elsewhere
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
      exporting: false,
      cacheHeader: null,
      currentAppt: null,
      apptModalInstance: null
    };
  },
  mounted() {
    this.loadAll();
    // init bootstrap modal instance
    this.apptModalInstance = new Modal(this.$refs.apptModal, {});
  },
  methods: {
    async loadAll() {
      this.loading = true;
      await Promise.all([this.loadAppointments(), this.loadAvailability()]);
      this.loading = false;
    },
    async loadAppointments() {
      try {
        const res = await api.get("/admin/doctors"); // sanity check or other endpoint
        // But we need doctor's own appts -> endpoint: /api/doctor/appointments
        const resp = await api.get("/doctor/appointments?upcoming=true");
        if (resp.headers) this.cacheHeader = resp.headers["x-cache"];
        this.appointments = resp.data || [];
      } catch (e) {
        console.error(e);
        this.appointments = [];
      }
    },
    async loadAvailability() {
      try {
        const resp = await api.get("/doctor/availability/next");
        if (resp.headers) this.cacheHeader = resp.headers["x-cache"] || this.cacheHeader;
        this.availability = resp.data || [];
      } catch (e) {
        console.error(e);
        this.availability = [];
      }
    },
    formatDate(iso) {
      if (!iso) return "—";
      const d = new Date(iso);
      return d.toLocaleDateString();
    },
    formatTimeRange(start, end) {
      if (!start) return "—";
      const s = new Date(start).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
      const e = end ? new Date(end).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"}) : "—";
      return `${s} — ${e}`;
    },
    statusBadge(status) {
      if (!status) return "badge bg-secondary";
      if (status === "booked") return "badge bg-info text-dark";
      if (status === "completed") return "badge bg-success";
      if (status === "cancelled") return "badge bg-danger";
      return "badge bg-secondary";
    },
    viewAppointment(appt) {
      this.currentAppt = appt;
      // open modal
      this.apptModalInstance.show();
    },
    closeModal() {
      this.apptModalInstance.hide();
      this.currentAppt = null;
    },
    async completeAppointment(appt) {
      if (!confirm("Mark appointment as completed? This will allow entering treatment on backend.")) return;
      appt.processing = true;
      try {
        const resp = await api.post(`/doctor/appointments/${appt.id}/treatment`, {
          diagnosis: "", // you can send minimal; ideally doctor UI should present a form
          prescription: "see notes",
          notes: "Recorded via app"
        });
        alert(resp.data?.msg || "Completed");
        await this.loadAppointments();
        // bump availability will be server-side; refresh availability too
        await this.loadAvailability();
      } catch (e) {
        console.error(e);
        alert(e.response?.data?.msg || "Failed");
      } finally {
        appt.processing = false;
      }
    },
    async cancelAppointment(appt) {
      if (!confirm("Cancel this appointment?")) return;
      appt.processing = true;
      try {
        const resp = await api.post(`/doctor/appointments/${appt.id}/cancel`);
        alert(resp.data?.msg || "Cancelled");
        await this.loadAppointments();
        await this.loadAvailability();
      } catch (e) {
        console.error(e);
        alert(e.response?.data?.msg || "Failed");
      } finally {
        appt.processing = false;
      }
    },
    async exportCsv() {
      this.exporting = true;
      try {
        // downloads file directly from backend
        const resp = await api.get("/doctor/appointments/export", { responseType: "blob" });
        const blob = new Blob([resp.data], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `appointments_doctor.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
      } catch (e) {
        console.error(e);
        alert("Export failed");
      } finally {
        this.exporting = false;
      }
    },
    refreshAll() {
      this.loadAll();
    },
    refreshAvailability() {
      this.loadAvailability();
    },
    openPatientsTab() {
      this.tab = "patients";
    }
  }
};
</script>

<style scoped>
.doctor-dashboard .card { border-radius: 12px; }
.table td, .table th { vertical-align: middle; }
</style>
