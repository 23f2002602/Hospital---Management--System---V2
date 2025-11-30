import { createRouter, createWebHistory } from "vue-router";
import { setAuthToken } from "../api/api";

// Page Imports
const Home = () => import("../pages/Home.vue");
const Login = () => import("../pages/Login.vue");
const Register = () => import("../pages/Register.vue");
const Reports = () => import("../pages/Reports.vue");
const NotFound = () => import("../pages/NotFound.vue");
const Profile = () => import("../pages/Profile.vue");
// NEW: Import the wrapper page
const DoctorsPage = () => import("../pages/DoctorsPage.vue");

// Dashboard Imports
const AdminDashboard = () => import("../components/AdminDashboard.vue");
const DoctorDashboard = () => import("../components/DoctorDashboard.vue");
const DoctorPatients = () => import("../components/DoctorPatients.vue");
const PatientDashboard = () => import("../components/PatientDashboard.vue");

const routes = [
  { 
    path: "/", 
    name: "home", 
    component: Home 
  },
  { path: "/login", name: "login", component: Login },
  { path: "/register", name: "register", component: Register },
  
  // UPDATED: Use DoctorsPage instead of SearchDoctors component directly
  { path: "/search", name: "search-doctors", component: DoctorsPage },

  { 
    path: "/profile", 
    name: "profile", 
    component: Profile,
    meta: { requiresAuth: true } 
  },

  // Role Routes
  { 
    path: "/admin", name: "admin-dashboard", component: AdminDashboard, 
    meta: { requiresAuth: true, roles: ["admin"] } 
  },
  { 
    path: "/doctor", name: "doctor-dashboard", component: DoctorDashboard, 
    meta: { requiresAuth: true, roles: ["doctor"] } 
  },
  { 
    path: "/doctor/patients", name: "doctor-patients", component: DoctorPatients, 
    meta: { requiresAuth: true, roles: ["doctor"] } 
  },
  { 
    path: "/patient", name: "patient-dashboard", component: PatientDashboard, 
    meta: { requiresAuth: true, roles: ["patient"] } 
  },
  { 
    path: "/reports", name: "reports", component: Reports, 
    meta: { requiresAuth: true, roles: ["admin", "doctor"] } 
  },
  
  { path: "/:pathMatch(.*)*", name: "404", component: NotFound },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || "/"),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if ((to.name === "login" || to.name === "register") && token) {
    if (role === "admin") return next({ name: "admin-dashboard" });
    if (role === "doctor") return next({ name: "doctor-dashboard" });
    return next({ name: "patient-dashboard" });
  }

  if (to.meta.requiresAuth) {
    if (!token) return next({ name: "login" });
    if (to.meta.roles && !to.meta.roles.includes(role)) {
      alert("Unauthorized access");
      return next({ name: "home" });
    }
  }

  next();
});

export default router;