<template>
  <div class="doctor-patients">
    <div class="row mb-3">
      <div class="col-12 col-md-6">
        <div class="input-group">
          <input class="form-control" placeholder="Search patients by name or email" v-model="q" @keyup.enter="search(1)" />
          <button class="btn btn-outline-primary" @click="search(1)">Search</button>
        </div>
      </div>
      <div class="col-12 col-md-6 text-end">
        <small class="text-muted">Total: {{ total }}</small>
      </div>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Phone</th>
              <th>DOB</th>
              <th>Gender</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in patients" :key="p.id">
              <td>{{ p.name }}</td>
              <td>{{ p.contact_number || p.phone || '—' }}</td>
              <td>{{ formatDate(p.date_of_birth) }}</td>
              <td>{{ p.gender || '—' }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-secondary me-1" @click="viewHistory(p)">History</button>
                <router-link :to="`/patient/${p.id}/profile`" class="btn btn-sm btn-outline-info">Open</router-link>
              </td>
            </tr>
            <tr v-if="patients.length===0">
              <td colspan="5" class="text-center text-muted py-3">No patients found</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card-footer d-flex justify-content-between align-items-center">
        <div>
          <button class="btn btn-outline-secondary btn-sm me-2" :disabled="page===1" @click="search(page-1)">Prev</button>
          <button class="btn btn-outline-secondary btn-sm" :disabled="page>=totalPages" @click="search(page+1)">Next</button>
        </div>
        <div class="small text-muted">
          Page {{ page }} / {{ totalPages }}
        </div>
      </div>
    </div>

    <!-- History modal -->
    <div class="modal fade" tabindex="-1" ref="historyModal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient History - {{ selectedPatient?.name || '' }}</h5>
            <button type="button" class="btn-close" @click="closeHistory"></button>
          </div>
          <div class="modal-body">
            <div v-if="history.length===0" class="text-muted">No history found</div>
            <div v-for="h in history" :key="h.appointment.id" class="mb-3">
              <div class="card p-3">
                <div class="d-flex justify-content-between">
                  <div>
                    <div><strong>{{ formatDate(h.appointment.start_time) }} {{ formatTimeRange(h.appointment.start_time, h.appointment.end_time) }}</strong></div>
                    <div class="text-muted">Doctor ID: {{ h.appointment.doctor_id }}</div>
                  </div>
                  <div class="text-end">
                    <div :class="statusBadge(h.appointment.status)">{{ h.appointment.status }}</div>
                  </div>
                </div>
                <hr />
                <div v-if="h.treatment && h.treatment.id">
                  <p><strong>Diagnosis:</strong> {{ h.treatment.diagnosis }}</p>
                  <p><strong>Prescription:</strong> {{ h.treatment.prescription }}</p>
                  <p><strong>Notes:</strong> {{ h.treatment.notes }}</p>
                </div>
                <div v-else class="text-muted">No treatment recorded</div>
              </div>
            </div>
          </div>
          <div class="modal-footer"><button class="btn btn-secondary" @click="closeHistory">Close</button></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api/api.js";
import { Modal } from "bootstrap";

export default {
  name: "DoctorPatients",
  data() {
    return {
      q: "",
      patients: [],
      page: 1,
      per_page: 10,
      total: 0,
      history: [],
      selectedPatient: null,
      historyModalInstance: null
    };
  },
  computed: {
    totalPages() {
      return Math.max(1, Math.ceil(this.total / this.per_page));
    }
  },
  mounted() {
    this.search(1);
    this.historyModalInstance = new Modal(this.$refs.historyModal, {});
  },
  methods: {
    async search(page = 1) {
      this.page = page;
      try {
        const resp = await api.get("/doctor/patients", {
          params: { q: this.q, page: this.page, per_page: this.per_page }
        });
        const data = resp.data;
        this.patients = data.patients || [];
        this.total = data.total || 0;
      } catch (e) {
        console.error(e);
        this.patients = [];
        this.total = 0;
      }
    },
    formatDate(iso) {
      if (!iso) return "—";
      try {
        const d = new Date(iso);
        return d.toLocaleDateString();
      } catch { return iso; }
    },
    formatTimeRange(start, end) {
      if (!start) return "—";
      const s = new Date(start).toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"});
      const e = end ? new Date(end).toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"}) : "—";
      return `${s} — ${e}`;
    },
    statusBadge(status) {
      if (!status) return "badge bg-secondary";
      if (status==="booked") return "badge bg-info text-dark";
      if (status==="completed") return "badge bg-success";
      if (status==="cancelled") return "badge bg-danger";
      return "badge bg-secondary";
    },
    async viewHistory(patient) {
      this.selectedPatient = patient;
      try {
        const resp = await api.get(`/doctor/patients/${patient.id}/history`);
        this.history = resp.data.history || [];
      } catch (e) {
        console.error(e);
        this.history = [];
      }
      this.historyModalInstance.show();
    },
    closeHistory() {
      this.historyModalInstance.hide();
      this.selectedPatient = null;
      this.history = [];
    }
  }
};
</script>

<style scoped>
.doctor-patients .card { border-radius: 10px; }
</style>
