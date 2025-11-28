<template>
  <div v-if="doctor" class="card p-3">
    <h5>Book with {{ doctor.name }}</h5>
    <div>
      <label>Date</label>
      <input type="date" v-model="date" class="form-control mb-2"/>
      <label>Start time</label>
      <input type="time" v-model="start_time" class="form-control mb-2"/>
      <label>End time</label>
      <input type="time" v-model="end_time" class="form-control mb-2"/>
      <label>Problem</label>
      <textarea v-model="problem" class="form-control mb-2"></textarea>
      <div class="d-flex gap-2">
        <button class="btn btn-primary" @click="book">Book</button>
        <button class="btn btn-secondary" @click="$emit('close')">Close</button>
      </div>
    </div>
    <div v-if="msg" class="alert alert-info mt-2">{{ msg }}</div>
  </div>
</template>

<script>
import api from "../api/api";
export default {
  props: ["doctor"],
  data(){ return { date:'', start_time:'09:00', end_time:'09:30', problem:'', msg:'' } },
  methods:{
    async book(){
      if(!this.date){ this.msg="Pick date"; return; }
      const start = `${this.date}T${this.start_time}:00`;
      const end = `${this.date}T${this.end_time}:00`;
      try{
        const res = await api.post("/patient/appointments/book", { doctor_id: this.doctor.id, start_time: start, end_time: end, problem: this.problem });
        this.msg = res.data.msg;
        this.$emit("booked", res.data);
      }catch(e){
        this.msg = e.response && e.response.data && e.response.data.msg ? e.response.data.msg : "Booking failed";
      }
    }
  }
}
</script>
