<template>
    <div class="container mt-4">
        <h2>Admin Panel</h2>

        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card p-3 h-100">
                    <h5>Create Doctor</h5>
                    <form @submit.prevent="createDoctor">
                        <input v-model="form.name" placeholder="Name" class="form-control mb-2" required/>
                        <input v-model="form.email" type="email" placeholder="Email" class="form-control mb-2" required/>
                        <input v-model="form.password" type="password" placeholder="Password" class="form-control mb-2" required/>
                        <input v-model="form.specialization" placeholder="Specialization" class="form-control mb-2"/>
                        <select v-model="form.department_id" class="form-control mb-2">
                            <option :value="null">-- Select Department --</option>
                            <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                        </select>
                        <button type="submit" class="btn btn-success w-100">Create Doctor</button>
                    </form>
                </div>
            </div>

            <div class="col-md-6 mb-4">
                <div class="card p-3 h-100">
                    <h5>Departments</h5>
                    <form @submit.prevent="createDepartment">
                        <input v-model="dept.name" placeholder="Dept Name" class="form-control mb-2" required/>
                        <input v-model="dept.description" placeholder="Description" class="form-control mb-2"/>
                        <button class="btn btn-primary w-100">Add Department</button>
                    </form>

                    <ul class="list-group mt-3">
                        <li v-for="d in departments" :key="d.id" class="list-group-item d-flex justify-content-between align-items-center">
                            <span><strong>{{ d.name }}</strong> <small class="text-muted">({{ d.description }})</small></span>
                            <button class="btn btn-sm btn-danger" @click="deleteDept(d.id)">Delete</button>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <hr/>

        <div class="card p-3 mt-3">
            <h5 class="mb-3">Doctors List</h5>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Specialization</th>
                            <th>Department</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="d in doctors" :key="d.id">
                            <td>{{ d.name }}</td>
                            <td>{{ d.email }}</td>
                            <td>{{ d.specialization }}</td>
                            <td>{{ getDeptName(d.department_id) }}</td>
                            <td>
                                <button class="btn btn-sm btn-secondary me-2" @click="openScheduleModal(d)">Schedule</button>
                                <button class="btn btn-sm btn-info me-2" @click="editDoctor(d)">Edit</button>
                                <button class="btn btn-sm btn-danger" @click="deleteDoctor(d.id)">Delete</button>
                            </td>
                        </tr>
                        <tr v-if="doctors.length === 0">
                            <td colspan="5" class="text-center text-muted">No doctors found.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div v-if="editing" class="card p-3 mt-3 border-info">
            <h6>Edit Doctor: {{ editing.name }}</h6>
            <form @submit.prevent="saveEdit">
                <div class="row g-2">
                    <div class="col-md-3">
                        <input v-model="editing.name" class="form-control" placeholder="Name" required />
                    </div>
                    <div class="col-md-3">
                        <input v-model="editing.email" class="form-control" placeholder="Email" required />
                    </div>
                    <div class="col-md-3">
                        <input v-model="editing.specialization" class="form-control" placeholder="Specialization" />
                    </div>
                    <div class="col-md-3">
                        <select v-model="editing.department_id" class="form-control">
                            <option :value="null">-- No Department --</option>
                            <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                        </select>
                    </div>
                </div>
                <div class="mt-2 d-flex gap-2 justify-content-end">
                    <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
                    <button type="submit" class="btn btn-success">Save Changes</button>
                </div>
            </form>
        </div>

        <div class="modal fade" tabindex="-1" ref="scheduleModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Manage Schedule: {{ selectedDoctor?.name }}</h5>
                        <button type="button" class="btn-close" @click="closeScheduleModal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info py-2 small mb-3">
                            Currently set for: 
                            <span v-for="d in doctorAvailability" :key="d.day" class="badge bg-light text-dark border me-1">
                                {{ d.day }}: {{ d.is_available ? `${d.start_time}-${d.end_time}` : 'Off' }}
                            </span>
                        </div>

                        <form @submit.prevent="saveSchedule">
                            <div class="mb-3">
                                <label class="form-label">Day (Next 7 Days)</label>
                                <select v-model="scheduleForm.day" class="form-control">
                                    <option v-for="d in next7Days" :key="d.value" :value="d.value">
                                        {{ d.label }}
                                    </option>
                                </select>
                            </div>
                            <div class="row mb-3">
                                <div class="col">
                                    <label class="form-label">Start Time</label>
                                    <input type="time" v-model="scheduleForm.start" class="form-control">
                                </div>
                                <div class="col">
                                    <label class="form-label">End Time</label>
                                    <input type="time" v-model="scheduleForm.end" class="form-control">
                                </div>
                            </div>
                            <div class="form-check mb-3">
                                <input type="checkbox" class="form-check-input" id="availCheck" v-model="scheduleForm.is_active">
                                <label class="form-check-label" for="availCheck">Available on this day</label>
                            </div>
                            <button class="btn btn-primary w-100">Update Schedule</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import api from "../api/api";
import { Modal } from "bootstrap";

export default {
    name: "AdminDashboard",
    data() {
        return {
            form: { email: '', password: '', name: '', specialization: '', department_id: null },
            dept: { name: '', description: '' },
            doctors: [],
            departments: [],
            editing: null,
            
            // Schedule Data
            selectedDoctor: null,
            scheduleModalInstance: null,
            doctorAvailability: [],
            scheduleForm: { day: 'Monday', start: '09:00', end: '17:00', is_active: true }
        };
    },
    computed: {
        next7Days() {
            const days = [];
            const today = new Date();
            const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            for (let i = 0; i < 7; i++) {
                const d = new Date(today);
                d.setDate(today.getDate() + i);
                const dayName = dayNames[d.getDay()];
                const dateStr = d.toLocaleDateString(undefined, { month: 'numeric', day: 'numeric' });
                days.push({ value: dayName, label: `${dayName} (${dateStr})` });
            }
            return days;
        }
    },
    mounted() {
        this.fetchAll();
        this.scheduleModalInstance = new Modal(this.$refs.scheduleModal);
    },
    methods: {
        async fetchAll() {
            try {
                const [docs, deps] = await Promise.all([
                    api.get('/admin/doctors'),
                    api.get('/admin/departments')
                ]);
                this.doctors = docs.data;
                this.departments = deps.data;
            } catch (e) {
                console.error("Failed to fetch data", e);
            }
        },
        getDeptName(id) {
            const d = this.departments.find(x => x.id === id);
            return d ? d.name : '—';
        },
        async createDoctor() {
            try {
                await api.post("/admin/create_doctor", this.form);
                alert("Doctor created!");
                this.form = { email: '', password: '', name: '', specialization: '', department_id: null };
                this.fetchAll();
            } catch (e) {
                alert(e.response?.data?.msg || "Failed to create doctor");
            }
        },
        // ... [Edit/Delete/Dept methods unchanged] ...
        editDoctor(d) {
            this.editing = JSON.parse(JSON.stringify(d)); 
        },
        cancelEdit() {
            this.editing = null;
        },
        async saveEdit() {
            try {
                await api.put(`/admin/doctors/${this.editing.id}`, this.editing);
                this.editing = null;
                this.fetchAll();
            } catch (e) {
                alert(e.response?.data?.msg || "Update failed");
            }
        },
        async deleteDoctor(id) {
            if (!confirm("Are you sure you want to delete this doctor?")) return;
            try {
                await api.delete(`/admin/doctors/${id}`);
                this.fetchAll();
            } catch (e) {
                alert(e.response?.data?.msg || "Failed to delete");
            }
        },
        async createDepartment() {
            try {
                await api.post('/admin/departments', this.dept);
                this.dept = { name: '', description: '' };
                this.fetchAll();
            } catch (e) {
                alert(e.response?.data?.msg || "Failed to add department");
            }
        },
        async deleteDept(id) {
            if (!confirm("Delete department?")) return;
            try {
                await api.delete(`/admin/departments/${id}`);
                this.fetchAll();
            } catch (e) {
                alert("Failed to delete");
            }
        },

        // --- NEW: Schedule Methods ---
        async openScheduleModal(doctor) {
            this.selectedDoctor = doctor;
            // Set default day to today
            const today = new Date();
            const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            this.scheduleForm.day = dayNames[today.getDay()];
            
            // Fetch current availability
            try {
                const res = await api.get(`/admin/doctors/${doctor.id}/availability/next`);
                this.doctorAvailability = res.data;
            } catch(e) {
                console.error(e);
                this.doctorAvailability = [];
            }
            
            this.scheduleModalInstance.show();
        },
        closeScheduleModal() {
            this.scheduleModalInstance.hide();
            this.selectedDoctor = null;
        },
        async saveSchedule() {
            if(!this.selectedDoctor) return;
            try {
                await api.post(`/admin/doctors/${this.selectedDoctor.id}/availability/week`, {
                    entries: [{ 
                        day_of_week: this.scheduleForm.day, 
                        start_time: this.scheduleForm.start, 
                        end_time: this.scheduleForm.end, 
                        is_available: this.scheduleForm.is_active 
                    }]
                });
                alert("Schedule updated!");
                this.closeScheduleModal();
            } catch(e) {
                alert(e.response?.data?.msg || "Failed to update schedule");
            }
        }
    }
};
</script>