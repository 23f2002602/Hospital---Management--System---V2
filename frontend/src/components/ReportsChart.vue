<template>
  <div>
    <canvas ref="chart"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

export default {
  name: "ReportsChart",
  props: {
    labels: { type: Array, default: () => [] },
    series: { type: Array, default: () => [] }, // datasets array
    type: { type: String, default: "line" },
    options: { type: Object, default: () => ({ responsive: true, maintainAspectRatio: false }) }
  },
  mounted() {
    this.renderChart();
  },
  watch: {
    labels: "renderChart",
    series: "renderChart"
  },
  methods: {
    renderChart() {
      if (this._chart) {
        this._chart.destroy();
      }
      const ctx = this.$refs.chart.getContext("2d");
      this._chart = new Chart(ctx, {
        type: this.type,
        data: { labels: this.labels, datasets: this.series },
        options: this.options
      });
    }
  },
  beforeUnmount() {
    if (this._chart) this._chart.destroy();
  }
};
</script>

<style scoped>
canvas { width: 100%; height: 320px; display: block; }
</style>
