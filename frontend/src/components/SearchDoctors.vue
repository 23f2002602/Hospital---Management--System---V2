<template>
  <div class="card p-3">
    <h5>Find Doctors</h5>
    <div class="d-flex gap-2 mb-2">
      <input v-model="q" @keyup.enter="search" placeholder="Search by name or specialization" class="form-control"/>
      <button class="btn btn-primary" @click="search">Search</button>
    </div>

    <ul class="list-group">
      <li v-for="d in doctors" :key="d.id" class="list-group-item d-flex justify-content-between">
        <div>
          <strong>{{ d.name }}</strong> <small class="text-muted">({{ d.specialization }})</small><br/>
          <small class="text-muted">{{ d.email }}</small>
        </div>
        <div>
          <button class="btn btn-sm btn-outline-primary" @click="$emit('book', d)">Book</button>
        </div>
      </li>
    </ul>

    <nav class="mt-2">
      <button class="btn btn-sm btn-outline-secondary" :disabled="page<=1" @click="prev">Prev</button>
      <span class="mx-2">Page {{ page }}</span>
      <button class="btn btn-sm btn-outline-secondary" @click="next">Next</button>
    </nav>
  </div>
</template>

<script>
import api from "../api/api";
export default {
  emits: ["book"],
  data(){ return { q:'', doctors:[], page:1, per_page:10 }},
  mounted(){ this.search(); },
  methods:{
    async search(){
      const res = await api.get(`/patient/doctors?q=${encodeURIComponent(this.q)}&page=${this.page}&per_page=${this.per_page}`);
      this.doctors = res.data.doctors;
    },
    prev(){ if(this.page>1){ this.page--; this.search(); } },
    next(){ this.page++; this.search(); }
  }
}
</script>
