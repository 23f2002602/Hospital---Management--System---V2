import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import "./style.css"; 

const app = createApp(App)
app.use(router)
app.mount('#app')

export function setTheme(name){
    document.documentElement.classList.remove("theme-light", "theme-dark");
    document.documentElement.classList.add(name == "dark" ? "theme-dark" : "theme-light");
    try {localStorage.setItem("hms:theme", name);} catch(e){}
}
export function getTheme(){
    try{
        const saved = localStorage.getItem("hms:theme");
        if (saved) return saved;
        const prefersDark = window.matchMedia && window.matchMedia('prefers-color-scheme: dark').matches;
        return prefersDark ? "dark" : "light";
    } catch(e){
        return "light";
    }
}