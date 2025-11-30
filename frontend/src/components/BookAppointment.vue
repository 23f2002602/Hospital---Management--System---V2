<template>
  <div v-if="doctor" class="card p-4 shadow-sm border-0">
    <h5 class="mb-3">Book with {{ doctor.name }}</h5>
    
    <div v-if="userRole !== 'patient'" class="alert alert-warning small">
      <strong>Note:</strong> You are logged in as <strong>{{ userRole }}</strong>. 
      Only <strong>Patients</strong> can book appointments.
    </div>

    <form @submit.prevent="book">
      <div class="mb-3">
        <label class="form-label">Date</label>
        <input type="date" v-model="date" class="form-control" required />
      </div>
      
      <div class="row mb-3">
        <div class="col">
          <label class="form-label">Start Time</label>
          <input type="time" v-model="start_time" class="form-control" required />
        </div>
        <div class="col">
          <label class="form-label">End Time</label>
          <input type="time" v-model="end_time" class="form-control" required />
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">Problem / Reason</label>
        <textarea v-model="problem" class="form-control" rows="3" placeholder="Describe your symptoms..."></textarea>
      </div>

      <div v-if="msg" :class="['alert', isError ? 'alert-danger' : 'alert-success']">
        {{ msg }}
        <div v-if="errorDetail" class="small mt-1 text-break opacity-75">
          Error: {{ errorDetail }}
        </div>
      </div>

      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary w-100" :disabled="loading || userRole !== 'patient'">
          <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
          {{ loading ? 'Booking...' : 'Confirm Booking' }}
        </button>
        <button type="button" class="btn btn-outline-secondary" @click="$emit('close')">
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import api from "../api/api";

export default {
  name: "BookAppointment",
  props: ["doctor"],
  emits: ["close", "booked"],
  data() {
    return {
      date: "",
      start_time: "09:00",
      end_time: "09:30",
      problem: "",
      msg: "",
      errorDetail: "",
      isError: false,
      loading: false,
      userRole: localStorage.getItem("role") || "guest"
    };
  },
  methods: {
    async book() {
      this.msg = "";
      this.errorDetail = "";
      this.isError = false;

      if (!this.date) {
        this.msg = "Please select a date.";
        this.isError = true;
        return;
      }

      this.loading = true;
      
      const start = `${this.date}T${this.start_time}:00`;
      const end = `${this.date}T${this.end_time}:00`;

      try {
        const res = await api.post("/patient/appointments/book", {
          doctor_id: this.doctor.id,
          start_time: start,
          end_time: end,
          problem: this.problem
        });

        this.isError = false;
        this.msg = "Appointment booked successfully!";
        
        setTimeout(() => {
          this.$emit("booked", res.data);
        }, 1000);

      } catch (e) {
        this.isError = true;
        this.msg = e.response?.data?.msg || "Booking failed.";
        // Capture backend error detail if available
        this.errorDetail = e.response?.data?.error || ""; 
        console.error("Booking Error:", e);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>