<template>
  <div>
    <h5>Patients</h5>
    <input v-model="q" @input="search" placeholder="search name or email" class="form-control mb-2"/>
    <ul class="list-group">
      <li v-for="p in patients" :key="p.id" class="list-group-item d-flex justify-content-between">
        <div>
          <strong>{{ p.name }}</strong><br/><small class="text-muted">{{ p.email }}</small>
        </div>
        <div>
          <button class="btn btn-sm btn-primary" @click="viewHistory(p.id)">History</button>
        </div>
      </li>
    </ul>
    <nav class="mt-2">
      <button class="btn btn-sm btn-outline-secondary" :disabled="page<=1" @click="prev">Prev</button>
      <span class="mx-2">Page {{ page }}</span>
      <button class="btn btn-sm btn-outline-secondary" @click="next">Next</button>
    </nav>

    <!-- history modal simple -->
    <div v-if="history" class="card p-3 mt-2">
      <h6>History (patient)</h6>
      <div v-for="h in history" :key="h.appointment.id" class="mb-2">
        <div><strong>{{ h.appointment.start_time }}</strong> — {{ h.appointment.status }}</div>
        <div>Diagnosis: {{ h.treatment.diagnosis }}</div>
        <div>Prescription: {{ h.treatment.prescription }}</div>
      </div>
      <button class="btn btn-sm btn-secondary" @click="history=null">Close</button>
    </div>
  </div>
</template>

<script>
import api from "../api/api";
export default {
  data(){ return { q:'', patients:[], page:1, per_page:12, history:null }; },
  mounted(){ this.load(); },
  methods:{
    async load(){ const res = await api.get(`/doctor/patients?page=${this.page}&per_page=${this.per_page}&q=${encodeURIComponent(this.q)}`); this.patients = res.data.patients; },
    search(){ this.page=1; this.load(); },
    prev(){ if(this.page>1){ this.page--; this.load(); } },
    next(){ this.page++; this.load(); },
    async viewHistory(id){ const r = await api.get(`/doctor/patient/${id}/history`); this.history = r.data.history; }
  }
}
</script>
