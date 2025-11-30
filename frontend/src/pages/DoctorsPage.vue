<template>
  <div class="container mt-4">
    <h3 class="mb-3">Find a Doctor</h3>
    <div class="row">
      <div class="col-md-8">
        <search-doctors @book="openBooking" />
      </div>
      
      <div class="col-md-4">
        <div v-if="selectedDoctor" class="sticky-top" style="top: 20px; z-index: 10;">
          <book-appointment 
            :doctor="selectedDoctor" 
            @close="selectedDoctor = null" 
            @booked="onBooked"
          />
        </div>
        <div v-else class="card p-4 bg-light text-muted text-center border-0 shadow-sm">
          <p class="m-0">Select a doctor from the list to book an appointment.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SearchDoctors from "../components/SearchDoctors.vue";
import BookAppointment from "../components/BookAppointment.vue";

export default {
  name: "DoctorsPage",
  components: { SearchDoctors, BookAppointment },
  data() {
    return {
      selectedDoctor: null
    };
  },
  methods: {
    openBooking(doctor) {
      this.selectedDoctor = doctor;
      // On mobile, scroll up so the user sees the form
      if (window.innerWidth < 768) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    },
    onBooked() {
      this.selectedDoctor = null;
      alert("Appointment booked successfully!");
    }
  }
};
</script>