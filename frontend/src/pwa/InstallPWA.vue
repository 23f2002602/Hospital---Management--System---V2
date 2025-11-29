<template>
  <div>
    <button v-if="show" class="btn btn-outline-success me-2" @click="install">
      Install App
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return { show: false };
  },
  mounted() {
    window.addEventListener("beforeinstallprompt", () => { this.show = true; });
    window.addEventListener("appinstalled", () => { this.show = false; });
  },
  methods: {
    async install() {
      const prompt = window.deferredPrompt;
      if (!prompt) return;
      prompt.prompt();
      const choice = await prompt.userChoice;
      if (choice.outcome === "accepted") {
        this.show = false;
      }
      window.deferredPrompt = null;
    }
  }
};
</script>

<style scoped>
button { min-width: 120px; }
</style>
