<template>
    <div class="container mt-4">
        <h2>Admin Panel</h2>

        <div class="row">
            <div class="col-md-6">
                <h5>Create Doctor</h5>
                <form @submit.prevent="createDoctor">
                    <input v-model="form.name" placeholder="Name" class="form-control mb-20"/>
                    <input v-model="form.email" type="email" placeholder="Email" class="form-control mb-20"/>
                    <input v-model="form.password" type="password" placeholder="Password" class="form-control mb-20"/>
                    <input v-model="form.specialization" placeholder="Specialization" class="form-control mb-20"/>
                    <select v-model="form.department_id" class="form-control mb-20">
                        <option :value="null">-- No Departments</option>
                        <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                    </select>
                    <button type="submit" class="btn btn-success">Create Doctor</button>
                </form>
            </div>

            <div class="col-md-6">
                <h5>Departments</h5>
                <form @submit.prevent="createDepartment">
                    <input v-model="dep.name" placeholder="Dep name" class="form-control mb-2"/>
                    <input v-model="dep.description" placeholder="Description" class="form-control mb-2"/>
                    <button class="btn btn-primary">Add Dept</button>
                </form>

                <ul class="list-group mt-2">
                    <li v-for="d in departments" :key="d.id" class="list-group-item d-flex justify-content-between align-items-center">
                        {{  d.name }}
                        <button class="btn btn-sm btn-danger" @click="deleteDept(d.id)">Delete</button>
                    </li>
                </ul>
            </div>
        </div>

        <hr/>
        <div class="card p-3 mt-3">
            <h5 class="mb-3">Doctors</h5>
            <table class="table responsive-table mb-0">
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
                        <td>{{  d.specialization }}</td>
                        <td>{{  getDeptName(d.department_id) }}</td>
                        <td>
                            <button class="btn btn-sm btn-info" @click="editDoctor(d)">Edit</button>
                            <button class="btn btn-sm btn-danger" @click="deleteDoctor(d.id)">Delete</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        

        <div v-if="editing" class="card p-3">
            <h6>Edit Doctor</h6>
            <input v-model="editing.name" class="form-control mb-2" />
            <input v-model="editing.email" class="form-control mb-2"/>
            <input v-model="editing.specialization" class="form-control mb-2"/>
            <select v-model="editing.department_id" class="form-control mb-2">
                <option :value="null">-- No Departments</option>
                <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
            <button class="btn btn-success" @click="saveEdit">Save</button>
            <button class="btn btn-secondary" @click="cancelEdit">Cancel</button>
        </div>
    </div>
</template>

<script>
import { normalizeModuleId } from "vite/module-runner";
import api from "../api/api";
export default {
    data(){return {
        form: { email: '', password: '',
                name: '', specialization: '', department_id: null },
        dept: {name: '', description: ''},
        doctors: [], departments: [],
        editing: null
    }},
    mounted(){this.fetchAll();},
    methods:{
        async fetchAll(){
            const [docs, deps] = await Promise.all([api.get('/admin/doctors'), api.get('/admin/departments')]);
            this.doctors = docs.data;
            this.departments = deps.data;
        },
        getDeptName(id){
        const d = this.departments.find(x=>x.id === id); return d ? d.name: '';
        },
        async createDoctor(){
            await api.post("/admin/create_doctor", this.form);
            this.form = {eamil: '', password: '', name: '', specialization: '', department_id: null};
            this.fetchAll();
        },
        editDoctor(d){
            this.editing = Object.assign({}, d);
        },
        cancelEdit(){this.editing = null;},
        async saveEdit(){
            await api.put('/admin/doctors/${this.editing.id}', this.editing);
            this.editing = null;
            this.fetchAll();
        },
        async deleteDoctor(id){
            if(!confirm("Delete doctor?")) return;
            await api.delete('/admin/doctos/${id}');
            this.fetchAll();
        },
        async createDepartment(){
            await api.post('/admin/departments', this.dep);
            this.dept = {name: '', description:''};
            this.fetchAll();
        },
        async deleteDept(id){
            if(!confirm("Delete department?")) return;
            await api.delete('/admin/departments/${id}');
            this.fetchAll();
        }
    }   
}
</script>