<template>
  <div class="card p-3">
    <h5>Patients</h5>

    <div class="d-flex mb-2 gap-2">
      <input v-model="q" @input="searchDebounced" placeholder="Search name or email" class="form-control" />
      <button class="btn btn-sm btn-primary" @click="search">Search</button>
    </div>

    <ul class="list-group">
      <li v-for="p in patients" :key="p.id" class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <div><strong>{{ p.name }}</strong></div>
          <div class="text-muted">{{ p.email }} • {{ p.phone || "—" }}</div>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-primary" @click="viewHistory(p.id)">History</button>
        </div>
      </li>
      <li v-if="!patients.length" class="list-group-item text-muted">No patients found.</li>
    </ul>

    <nav class="mt-2 d-flex justify-content-between align-items-center">
      <div>Showing {{ patients.length }} of {{ total }}</div>
      <div>
        <button class="btn btn-sm btn-outline-secondary" :disabled="page<=1" @click="prev">Prev</button>
        <span class="mx-2">Page {{ page }}</span>
        <button class="btn btn-sm btn-outline-secondary" @click="next">Next</button>
      </div>
    </nav>

    <!-- history modal -->
    <div v-if="historyOpen" class="modal-backdrop">
      <div class="card p-3" style="max-width:800px;margin:40px auto;">
        <h6>Patient History</h6>
        <div v-if="historyList && historyList.length">
          <div v-for="h in historyList" :key="h.appointment.id" class="mb-3">
            <div><strong>{{ formatLocal(h.appointment.start_time) }}</strong> — {{ h.appointment.status }}</div>
            <div>Problem: {{ h.appointment.problem }}</div>
            <div v-if="h.treatment && h.treatment.diagnosis" class="mt-1">
              <strong>Diagnosis:</strong> {{ h.treatment.diagnosis }}<br/>
              <strong>Prescription:</strong> {{ h.treatment.prescription }}<br/>
              <small class="text-muted">Recorded: {{ h.treatment.created_at }}</small>
            </div>
          </div>
        </div>
        <div v-else class="text-muted">No history found.</div>
        <div class="text-end"><button class="btn btn-sm btn-secondary" @click="closeHistory">Close</button></div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api/api";
import debounce from "lodash/debounce";

export default {
  name: "DoctorPatients",
  data() {
    return {
      q: "",
      patients: [],
      total: 0,
      page: 1,
      per_page: 12,
      historyOpen: false,
      historyList: null
    };
  },
  created() {
    this.searchDebounced = debounce(this.search, 350);
    this.search();
  },
  methods: {
    async search() {
      const res = await api.get(`/doctor/patients?q=${encodeURIComponent(this.q)}&page=${this.page}&per_page=${this.per_page}`);
      this.total = res.data.total || 0;
      this.patients = res.data.patients || [];
    },
    prev() { if (this.page > 1) { this.page--; this.search(); } },
    next() { this.page++; this.search(); },
    async viewHistory(id) {
      const r = await api.get(`/doctor/patient/${id}/history`);
      this.historyList = r.data.history || [];
      this.historyOpen = true;
    },
    closeHistory() { this.historyOpen = false; this.historyList = null; },
    formatLocal(iso) { return new Date(iso).toLocaleString(); }
  }
};
</script>

<style>
.modal-backdrop { position: fixed; inset:0; background: rgba(0,0,0,0.45); display:flex; align-items:flex-start; padding-top:6vh; z-index:9999; }
</style>
