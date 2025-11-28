<template>
  <div class="container mt-3">
    <div class="row">
      <div class="col-md-5">
        <search-doctors @book="openBooking" ref="search"/>
        <div v-if="bookingDoctor" class="mt-2">
          <book-appointment :doctor="bookingDoctor" @close="bookingDoctor=null" @booked="onBooked"/>
        </div>
      </div>

      <div class="col-md-7">
        <div class="card p-3 mb-3">
          <h5>Upcoming Appointments</h5>
          <ul class="list-group">
            <li v-for="a in upcoming" :key="a.id" class="list-group-item d-flex justify-content-between">
              <div>
                <strong>{{ a.doctor_name }}</strong><br/>
                <small class="text-muted">{{ new Date(a.start_time).toLocaleString() }}</small>
                <div>{{ a.problem }}</div>
              </div>
              <div class="d-flex gap-2">
                <button class="btn btn-sm btn-outline-secondary" @click="reschedule(a)">Reschedule</button>
                <button class="btn btn-sm btn-danger" @click="cancel(a)">Cancel</button>
              </div>
            </li>
          </ul>
        </div>

        <div class="card p-3">
          <h5>Past Appointments</h5>
          <ul class="list-group">
            <li v-for="a in past" :key="a.id" class="list-group-item">
              <div><strong>{{ a.doctor_name }}</strong> — {{ a.start_time }}</div>
              <div>Diagnosis: {{ a.treatment.diagnosis }}</div>
              <div>Prescription: {{ a.treatment.prescription }}</div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api/api";
import SearchDoctors from "./SearchDoctors.vue";
import BookAppointment from "./BookAppointment.vue";
export default {
  components: { SearchDoctors, BookAppointment },
  data(){ return { bookingDoctor:null, upcoming:[], past:[] } },
  mounted(){ this.loadAppointments(); },
  methods:{
    openBooking(d){ this.bookingDoctor = d; },
    async onBooked(){ this.bookingDoctor = null; this.loadAppointments(); this.$refs.search.search(); },
    async loadAppointments(){
      const res1 = await api.get("/patient/appointments?status=booked");
      this.upcoming = res1.data;
      const res2 = await api.get("/patient/appointments?status=completed");
      this.past = res2.data;
    },
    async cancel(a){
      if(!confirm("Cancel appointment?")) return;
      await api.post(`/patient/appointments/${a.id}/cancel`);
      this.loadAppointments();
    },
    reschedule(a){
      const newDate = prompt("Enter new start datetime (YYYY-MM-DDTHH:MM:SS)"); // simple prompt for demo
      if(!newDate) return;
      const newEnd = prompt("Enter new end datetime (YYYY-MM-DDTHH:MM:SS)");
      api.post(`/patient/appointments/${a.id}/reschedule`, { start_time: newDate, end_time: newEnd }).then(()=> this.loadAppointments()).catch(e=> alert(e.response?.data?.msg || "Failed"));
    }
  }
}
</script>
