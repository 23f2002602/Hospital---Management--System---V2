<template>
  <div class="container mt-3">
    <h3>Doctor Dashboard</h3>

    <!-- TAB NAV -->
    <div class="d-flex gap-2 mb-3">
      <button
        :class="['btn', activeTab === 'appointments' ? 'btn-primary' : 'btn-outline-secondary']"
        @click="activeTab = 'appointments'">
        Appointments
      </button>

      <button
        :class="['btn', activeTab === 'patients' ? 'btn-primary' : 'btn-outline-secondary']"
        @click="activeTab = 'patients'">
        Patients
      </button>

      <button
        :class="['btn', activeTab === 'availability' ? 'btn-primary' : 'btn-outline-secondary']"
        @click="activeTab = 'availability'">
        Availability
      </button>
      <button class="btn btn-sm btn-outline-secondary ms-auto" @click="loadAll">Refresh All</button>
    </div>

    <!-- APPOINTMENTS TAB -->
    <div v-if="activeTab === 'appointments'">
      <div class="row">
        <div class="col-md-12">
          <div class="card p-3 mb-3">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Upcoming Appointments</h5>
              <div>
                <button class="btn btn-sm btn-outline-primary" @click="loadAppointments">Refresh</button>
                <button class="btn btn-sm btn-outline-secondary" @click="exportCSV">Export CSV</button>
              </div>
            </div>

            <ul class="list-group mt-3">
              <li v-for="a in appts" :key="a.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <div><strong>{{ formatShort(a.start_time) }}</strong> — {{ a.patient_name || a.patient_id }}</div>
                  <div class="text-muted">{{ a.problem }}</div>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn btn-sm btn-success" @click="openCompleteModal(a)">Complete</button>
                  <button class="btn btn-sm btn-outline-secondary" @click="openTreat(a)">Add Treatment</button>
                  <button class="btn btn-sm btn-danger" @click="cancelAppt(a)">Cancel</button>
                </div>
              </li>
              <li v-if="!appts.length" class="list-group-item text-muted">No upcoming appointments.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- PATIENTS TAB -->
    <div v-if="activeTab === 'patients'">
      <doctor-patients />
    </div>

    <!-- AVAILABILITY TAB -->
    <div v-if="activeTab === 'availability'">
      <div class="row">
        <div class="col-md-7">
          <div class="card p-3 mb-3">
            <h5>Weekly Availability</h5>
            <div v-for="d in weekdays" :key="d" class="mb-2">
              <div class="d-flex gap-2 align-items-center">
                <strong style="width:100px">{{ d }}</strong>
                <input v-model="avail[d].start_time" placeholder="HH:MM" class="form-control form-control-sm" style="width:90px"/>
                <input v-model="avail[d].end_time" placeholder="HH:MM" class="form-control form-control-sm" style="width:90px"/>
                <input type="checkbox" v-model="avail[d].is_available"/> Available
                <button class="btn btn-sm btn-primary" @click="saveDay(d)">Save</button>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-5">
          <div class="card p-3">
            <h5>Overrides (vacation / special days)</h5>
            <input type="date" v-model="ov.date" class="form-control mb-2"/>
            <div>
              <label><input type="checkbox" v-model="ov.is_available"/> Available</label>
              <button class="btn btn-sm btn-primary ms-2" @click="saveOverride">Save</button>
            </div>
            <hr/>
            <ul>
              <li v-for="o in overrides" :key="o.id">{{ o.date }} — {{ o.is_available ? 'Available' : 'Not available' }}</li>
              <li v-if="!overrides.length" class="text-muted">No overrides yet.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- treatment modal simple -->
    <div v-if="treating" class="modal-backdrop">
      <div class="card p-3" style="max-width:600px;margin:40px auto;">
        <h5>Add Treatment</h5>
        <div class="mb-2">
          <textarea v-model="treatment.diagnosis" class="form-control" placeholder="Diagnosis"></textarea>
        </div>
        <div class="mb-2">
          <textarea v-model="treatment.prescription" class="form-control" placeholder="Prescription"></textarea>
        </div>
        <div class="mb-2">
          <textarea v-model="treatment.notes" class="form-control" placeholder="Notes"></textarea>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-success" @click="submitTreatment">Save</button>
          <button class="btn btn-secondary" @click="closeTreat">Cancel</button>
        </div>
      </div>
    </div>

    <!-- complete modal -->
    <div v-if="completing" class="modal-backdrop">
      <div class="card p-3" style="max-width:600px;margin:40px auto;">
        <h5>Complete Appointment</h5>
        <div class="mb-2">
          <textarea v-model="completePayload.diagnosis" class="form-control" placeholder="Diagnosis"></textarea>
        </div>
        <div class="mb-2">
          <textarea v-model="completePayload.prescription" class="form-control" placeholder="Prescription"></textarea>
        </div>
        <div class="mb-2">
          <textarea v-model="completePayload.notes" class="form-control" placeholder="Notes"></textarea>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-success" @click="completeAppointment">Complete</button>
          <button class="btn btn-secondary" @click="completing=false">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import api from "../api/api";
import DoctorPatients from "./DoctorPatients.vue";

export default {
  components: { DoctorPatients },
  data(){
    return {
      activeTab: "appointments",
      appts: [],
      weekdays: ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
      avail: {},
      overrides: [],
      ov: { date: "", is_available: false },
      treating: false,
      treatment: {},
      treating_appt: null,
      completing: false,
      completePayload: { diagnosis:"", prescription:"", notes:"" }
    };
  },
  mounted(){
    this.initAvailObj();
    this.loadAll();
  },
  methods:{
    initAvailObj(){
      this.weekdays.forEach(d => { this.$set(this.avail, d, { start_time:"", end_time:"", is_available:false }); });
    },
    async loadAll(){
      await Promise.all([this.loadAppointments(), this.loadAvailability()]);
    },
    async loadAppointments(){
      try{
        const res = await api.get("/doctor/appointments?upcoming=true");
        this.appts = res.data;
      }catch(e){
        console.error(e);
      }
    },
    formatShort(iso){
      return new Date(iso).toLocaleString();
    },
    openTreat(a){
      this.treating = true;
      this.treatment = { diagnosis:"", prescription:"", notes:"" };
      this.trating_appt = a;
      this.treating_appt = a;
    },
    closeTreat(){ this.treating = false; this.treating_appt = null; },
    async submitTreatment(){
      if(!this.treating_appt) return;
      await api.post(`/doctor/appointments/${this.treating_appt.id}/complete`, this.treatment);
      this.closeTreat();
      this.loadAppointments();
    },
    openCompleteModal(a){
      this.completing = true;
      this.completePayload = { diagnosis:"", prescription:"", notes:"" };
      this.completing_appt = a;
      this.completing_id = a.id;
    },
    async completeAppointment(){
      if(!this.completing_id) return;
      await api.post(`/doctor/appointments/${this.completing_id}/complete`, this.completePayload);
      this.completing = false;
      this.completing_id = null;
      this.loadAppointments();
    },
    async cancelAppt(a){
      if(!confirm("Cancel appointment?")) return;
      await api.post(`/doctor/appointments/${a.id}/cancel`);
      this.loadAppointments();
    },
    async loadAvailability(){
      const res = await api.get("/doctor/availability");
      const weekly = res.data.weekly || [];
      this.overrides = res.data.overrides || [];
      // reset
      this.initAvailObj();
      weekly.forEach(w => {
        this.$set(this.avail, w.day_of_week, { start_time: w.start_time ? w.start_time.slice(0,5) : "", end_time: w.end_time ? w.end_time.slice(0,5) : "", is_available: w.is_available });
      });
    },
    async saveDay(day){
      const payload = { day_of_week: day, start_time: this.avail[day].start_time, end_time: this.avail[day].end_time, is_available: this.avail[day].is_available };
      await api.post("/doctor/availability", payload);
      alert("Saved");
      this.loadAvailability();
    },
    async saveOverride(){
      if(!this.ov.date){ alert("pick a date"); return; }
      await api.post("/doctor/override", { date: this.ov.date, is_available: this.ov.is_available });
      this.ov = { date:"", is_available:false };
      this.loadAvailability();
    },
    async exportCSV(){
      const resp = await api.get("/doctor/appointments/export", { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([resp.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "appointments.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    }
  }
};
</script>

<style>
.modal-backdrop { position: fixed; inset:0; background: rgba(0,0,0,0.4); display:flex; align-items:flex-start; padding-top:6vh; z-index:9999; }
.card { background: var(--surface); }
</style>
