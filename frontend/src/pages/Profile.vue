<template>
  <div class="container mt-4">
    <div class="card p-4 shadow-sm" style="max-width: 600px; margin: 0 auto;">
      <h3 class="mb-4">My Profile</h3>
      
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else>
        <div v-if="role === 'patient'">
          <form @submit.prevent="updateProfile">
            <div class="mb-3">
              <label class="form-label">Full Name</label>
              <input v-model="form.name" class="form-control" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="form.email" type="email" class="form-control" required />
            </div>

            <hr class="my-4" />
            
            <div class="mb-3">
              <label class="form-label">Phone Number</label>
              <input v-model="form.phone" class="form-control" />
            </div>
            <div class="row">
              <div class="col-6 mb-3">
                <label class="form-label">Gender</label>
                <select v-model="form.gender" class="form-control">
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="col-6 mb-3">
                <label class="form-label">Date of Birth</label>
                <input type="date" v-model="form.dob" class="form-control" />
              </div>
            </div>
            <button class="btn btn-primary w-100">Save Changes</button>
          </form>
        </div>

        <div v-else>
           <div class="mb-3">
             <label class="small text-muted">Name</label>
             <div class="fs-5">{{ user.name }}</div>
           </div>
           <div class="mb-3">
             <label class="small text-muted">Email</label>
             <div class="fs-5">{{ user.email }}</div>
           </div>
           <div class="alert alert-info mt-3">
             Profile editing is currently only available for patients.
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api/api";

export default {
  name: "ProfilePage",
  data() {
    return {
      user: {},
      form: { name: "", email: "", phone: "", gender: "", dob: "" },
      loading: true,
      role: localStorage.getItem("role")
    };
  },
  mounted() {
    this.fetchProfile();
  },
  methods: {
    async fetchProfile() {
      this.loading = true;
      try {
        if (this.role === 'patient') {
          const res = await api.get("/patient/profile");
          this.user = res.data;
          this.form = { 
            name: res.data.name,
            email: res.data.email,
            phone: res.data.phone || "", 
            gender: res.data.gender || "", 
            dob: res.data.dob || "" 
          };
        } else {
          this.user = { 
            name: localStorage.getItem("user_name"), 
            email: "—" // Backend needs update to send email for doctors/admins
          };
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
    async updateProfile() {
      try {
        await api.put("/patient/profile", this.form);
        alert("Profile updated successfully!");
        
        // Update local storage name if it changed
        if(this.form.name) {
          localStorage.setItem("user_name", this.form.name);
        }
        this.fetchProfile();
      } catch (e) {
        alert(e.response?.data?.msg || "Failed to update profile.");
      }
    }
  }
};
</script>