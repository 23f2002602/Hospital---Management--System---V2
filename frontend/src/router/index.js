// frontend/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import { decodeJwt } from "../api/api";

// Lazy-loaded pages/components
const Home = () => import("../pages/Home.vue");
const Login = () => import("../pages/Login.vue");
const Register = () => import("../pages/Register.vue");

const AdminDashboard = () => import("../components/AdminDashboard.vue");
const DoctorDashboard = () => import("../components/DoctorDashboard.vue");
const DoctorPatients = () => import("../components/DoctorPatients.vue");
const PatientDashboard = () => import("../components/PatientDashboard.vue");

const NotFound = () => import("../pages/NotFound.vue");

// ----------------------------
// ROUTES
// ----------------------------
const routes = [
  { path: "/", name: "home", component: Home },

  { path: "/login", name: "login", component: Login },
  { path: "/register", name: "register", component: Register },

  // Admin
  {
    path: "/admin",
    name: "admin-dashboard",
    component: AdminDashboard,
    meta: { requiresAuth: true, role: "admin" },
  },

  // Doctor
  {
    path: "/doctor",
    name: "doctor-dashboard",
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: "doctor" },
  },
  {
    path: "/doctor/patients",
    name: "doctor-patients",
    component: DoctorPatients,
    meta: { requiresAuth: true, role: "doctor" },
  },

  // Patient
  {
    path: "/patient",
    name: "patient-dashboard",
    component: PatientDashboard,
    meta: { requiresAuth: true, role: "patient" },
  },

  // Wildcard (NotFound)
  {
    path: "/:pathMatch(.*)*",
    name: "404",
    component: NotFound,
  },
];

// ----------------------------
// ROUTER
// ----------------------------
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || "/"),
  routes,
});

// ----------------------------
// ROUTE GUARD
// ----------------------------
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");

  // Decode JWT → extract role (Preferred)
  let role = null;
  if (token) {
    const payload = decodeJwt(token);
    if (payload && payload.role) {
      role = payload.role;
      localStorage.setItem("role", role); // sync
    }
  }

  // Fallback if decoding fails
  if (!role) {
    role = localStorage.getItem("role");
  }

  // If route needs authentication
  if (to.meta.requiresAuth) {
    if (!token) {
      return next({
        name: "login",
        query: { next: to.fullPath }, // redirect after login
      });
    }

    // Check role access
    if (to.meta.role && to.meta.role !== role) {
      return next({ name: "home" });
    }
  }

  return next();
});

export default router;
