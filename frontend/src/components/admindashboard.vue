<template>
    <div class="container mt-4">
        <h2 class="mb-4">Admin Panel</h2>

        <div class="row g-4">
            <div class="col-12 col-lg-6">
                <div class="card p-4 h-100 shadow-sm border-0">
                    <h5 class="card-title mb-3">Create Doctor</h5>
                    <form @submit.prevent="createDoctor">
                        <div class="mb-3">
                            <input v-model="form.name" placeholder="Full Name" class="form-control" required/>
                        </div>
                        <div class="mb-3">
                            <input v-model="form.email" type="email" placeholder="Email Address" class="form-control" required/>
                        </div>
                        <div class="mb-3">
                            <input v-model="form.password" type="password" placeholder="Password" class="form-control" required/>
                        </div>
                        <div class="mb-3">
                            <input v-model="form.specialization" placeholder="Specialization" class="form-control"/>
                        </div>
                        <div class="mb-3">
                            <select v-model="form.department_id" class="form-select">
                                <option :value="null">-- Select Department --</option>
                                <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-success w-100">Create Doctor</button>
                    </form>
                </div>
            </div>

            <div class="col-12 col-lg-6">
                <div class="card p-4 h-100 shadow-sm border-0">
                    <h5 class="card-title mb-3">Departments</h5>
                    <form @submit.prevent="createDepartment" class="mb-4">
                        <div class="input-group mb-2">
                            <input v-model="dept.name" placeholder="Dept Name" class="form-control" required/>
                            <button class="btn btn-primary">Add</button>
                        </div>
                        <input v-model="dept.description" placeholder="Description (optional)" class="form-control form-control-sm"/>
                    </form>

                    <div class="list-group list-group-flush border rounded overflow-auto" style="max-height: 300px;">
                        <div v-for="d in departments" :key="d.id" class="list-group-item d-flex justify-content-between align-items-center">
                            <div class="text-truncate me-2">
                                <strong>{{ d.name }}</strong> 
                                <span class="text-muted d-block small text-truncate">{{ d.description }}</span>
                            </div>
                            <button class="btn btn-sm btn-outline-danger" @click="deleteDept(d.id)">Delete</button>
                        </div>
                        <div v-if="departments.length === 0" class="p-3 text-center text-muted">No departments yet.</div>
                    </div>
                </div>
            </div>
        </div>

        <hr class="my-5"/>

        <div class="card p-4 shadow-sm border-0">
            <h5 class="mb-3">Doctors List</h5>
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Specialization</th>
                            <th>Department</th>
                            <th class="text-end">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="d in doctors" :key="d.id">
                            <td class="fw-medium">{{ d.name }}</td>
                            <td>{{ d.email }}</td>
                            <td><span class="badge bg-light text-dark border">{{ d.specialization || 'N/A' }}</span></td>
                            <td>{{ getDeptName(d.department_id) }}</td>
                            <td class="text-end text-nowrap">
                                <button class="btn btn-sm btn-outline-secondary me-1" @click="openScheduleModal(d)" title="Schedule">📅</button>
                                <button class="btn btn-sm btn-outline-info me-1" @click="editDoctor(d)" title="Edit">✏️</button>
                                <button class="btn btn-sm btn-outline-danger" @click="deleteDoctor(d.id)" title="Delete">🗑️</button>
                            </td>
                        </tr>
                        <tr v-if="doctors.length === 0">
                            <td colspan="5" class="text-center text-muted py-4">No doctors found.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div v-if="editing" class="card p-4 mt-4 border-info shadow">
            <h6 class="text-primary mb-3">Edit Doctor: {{ editing.name }}</h6>
            <form @submit.prevent="saveEdit">
                <div class="row g-3">
                    <div class="col-12 col-md-6 col-lg-3">
                        <label class="form-label small">Name</label>
                        <input v-model="editing.name" class="form-control" required />
                    </div>
                    <div class="col-12 col-md-6 col-lg-3">
                        <label class="form-label small">Email</label>
                        <input v-model="editing.email" class="form-control" required />
                    </div>
                    <div class="col-12 col-md-6 col-lg-3">
                        <label class="form-label small">Specialization</label>
                        <input v-model="editing.specialization" class="form-control" />
                    </div>
                    <div class="col-12 col-md-6 col-lg-3">
                        <label class="form-label small">Department</label>
                        <select v-model="editing.department_id" class="form-select">
                            <option :value="null">-- No Department --</option>
                            <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                        </select>
                    </div>
                </div>
                <div class="mt-3 d-flex gap-2 justify-content-end">
                    <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </div>
            </form>
        </div>

        <div class="modal fade" tabindex="-1" ref="scheduleModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Manage Schedule</h5>
                        <button type="button" class="btn-close" @click="closeScheduleModal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="text-muted small">Doctor: <strong>{{ selectedDoctor?.name }}</strong></p>
                        
                        <div class="d-flex flex-wrap gap-2 mb-3">
                            <span v-for="d in doctorAvailability" :key="d.day" 
                                  :class="['badge', d.is_available ? 'bg-success' : 'bg-secondary']">
                                {{ d.day.substring(0,3) }}
                            </span>
                        </div>

                        <form @submit.prevent="saveSchedule">
                            <div class="mb-3">
                                <label class="form-label">Select Day</label>
                                <select v-model="scheduleForm.day" class="form-select">
                                    <option v-for="d in next7Days" :key="d.value" :value="d.value">
                                        {{ d.label }}
                                    </option>
                                </select>
                            </div>
                            <div class="row g-2 mb-3">
                                <div class="col">
                                    <label class="form-label">Start</label>
                                    <input type="time" v-model="scheduleForm.start" class="form-control">
                                </div>
                                <div class="col">
                                    <label class="form-label">End</label>
                                    <input type="time" v-model="scheduleForm.end" class="form-control">
                                </div>
                            </div>
                            <div class="form-check form-switch mb-3">
                                <input type="checkbox" class="form-check-input" id="availCheck" v-model="scheduleForm.is_active">
                                <label class="form-check-label" for="availCheck">Available</label>
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
        async openScheduleModal(doctor) {
            this.selectedDoctor = doctor;
            const today = new Date();
            const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            this.scheduleForm.day = dayNames[today.getDay()];
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