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

const Reports = () => import("../pages/Reports.vue");   

const NotFound = () => import("../pages/NotFound.vue");

const routes = [
  { path: "/", name: "home", component: Home },

  { path: "/login", name: "login", component: Login },
  { path: "/register", name: "register", component: Register },

  // Admin
  {
    path: "/admin",
    name: "admin-dashboard",
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ["admin"] },
  },

  // Doctor
  {
    path: "/doctor",
    name: "doctor-dashboard",
    component: DoctorDashboard,
    meta: { requiresAuth: true, roles: ["doctor"] },
  },
  {
    path: "/doctor/patients",
    name: "doctor-patients",
    component: DoctorPatients,
    meta: { requiresAuth: true, roles: ["doctor"] },
  },

  // Patient
  {
    path: "/patient",
    name: "patient-dashboard",
    component: PatientDashboard,
    meta: { requiresAuth: true, roles: ["patient"] },
  },

  // Reports (Admin + Doctor only)
  {
    path: "/reports",
    name: "reports",
    component: Reports,
    meta: { requiresAuth: true, roles: ["admin", "doctor"] },
  },

  // Wildcard
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

// small in-memory cache for decoded token to avoid repeated parsing in one navigation
let _cachedPayload = null;
let _cachedRawToken = null;

function getTokenPayload(rawToken) {
  if (!rawToken) return null;
  try {
    // return cached payload if same token
    if (_cachedRawToken === rawToken && _cachedPayload) return _cachedPayload;
    const payload = decodeJwt(rawToken);
    // basic expiry check (if token has exp)
    if (payload && payload.exp) {
      const now = Math.floor(Date.now() / 1000);
      if (payload.exp <= now) {
        // expired
        return null;
      }
    }
    _cachedRawToken = rawToken;
    _cachedPayload = payload;
    return payload;
  } catch (err) {
    // malformed token
    return null;
  }
}

// ----------------------------
// ROUTE GUARD
// ----------------------------
router.beforeEach((to, from, next) => {
  const rawToken = localStorage.getItem("token");

  // Reset cached payload if token changed outside of this router instance
  if (_cachedRawToken !== rawToken) {
    _cachedRawToken = null;
    _cachedPayload = null;
  }

  const payload = getTokenPayload(rawToken);

  // derive role (lowercased) from payload, else fallback to localStorage
  let role = null;
  if (payload && payload.role) {
    role = String(payload.role).toLowerCase();
    // sync to localStorage for other parts of app
    localStorage.setItem("role", role);
  } else {
    const lsRole = localStorage.getItem("role");
    if (lsRole) role = String(lsRole).toLowerCase();
  }

  // If route needs authentication
  if (to.meta && to.meta.requiresAuth) {
    // no valid token or payload → redirect to login
    if (!rawToken || !payload) {
      return next({
        name: "login",
        query: { next: to.fullPath },
      });
    }

    // Role check
    if (to.meta.roles && Array.isArray(to.meta.roles) && to.meta.roles.length > 0) {
      // allow any role present in meta.roles (case-insensitive)
      const allowed = to.meta.roles.map((r) => String(r).toLowerCase());
      if (!role || !allowed.includes(role)) {
        // unauthorized role — redirect to home (or you can redirect to 403 page)
        return next({ name: "home" });
      }
    }
  }

  // If public route but user is logged and going to /login, redirect to dashboard
  if (to.name === "login" && payload) {
    // redirect based on role
    if (role === "admin") return next({ name: "admin-dashboard" });
    if (role === "doctor") return next({ name: "doctor-dashboard" });
    if (role === "patient") return next({ name: "patient-dashboard" });
    return next({ name: "home" });
  }

  return next();
});

export default router;
