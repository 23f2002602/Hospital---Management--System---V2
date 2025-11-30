<template>
  <div class="container mt-4">
    <h2 class="mb-4">Hospital Reports</h2>
    
    <div class="card p-4 mb-4 shadow-sm">
      <div class="row g-3 align-items-end">
        <div class="col-md-4">
          <label class="form-label fw-bold">Select Month</label>
          <input type="month" v-model="month" class="form-control" />
        </div>
        <div class="col-md-4">
          <button class="btn btn-primary w-100" @click="fetchData" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Generate Report
          </button>
        </div>
        <div class="col-md-4 d-flex gap-2">
           <button class="btn btn-outline-danger w-100" @click="downloadFile('pdf')" :disabled="!hasData || downloading">
             <span v-if="downloading" class="spinner-border spinner-border-sm me-1"></span>
             Download PDF
           </button>
           <button class="btn btn-outline-success w-100" @click="downloadFile('csv')" :disabled="!hasData || downloading">
             <span v-if="downloading" class="spinner-border spinner-border-sm me-1"></span>
             Download CSV
           </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Crunching the numbers...</p>
    </div>

    <div v-else-if="hasData">
      <div class="row mb-4">
        <div class="col-md-8">
          <div class="card p-3 shadow-sm h-100">
            <h5 class="card-title">Appointments by Date</h5>
            <div class="chart-container">
              <reports-chart :labels="dateLabels" :series="dateData" type="line" />
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card p-3 shadow-sm h-100">
            <h5 class="card-title">By Specialization</h5>
            <div class="chart-container">
              <reports-chart :labels="specLabels" :series="specData" type="doughnut" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center text-muted py-5">
      <div class="mb-2" style="font-size: 3rem;">📊</div>
      <p>Select a month and click <strong>Generate Report</strong> to view data.</p>
    </div>
  </div>
</template>

<script>
import api from "../api/api";
import ReportsChart from "../components/ReportsChart.vue";

export default {
  name: "ReportsPage",
  components: { ReportsChart },
  data() {
    return {
      month: new Date().toISOString().slice(0, 7), // Defaults to current YYYY-MM
      loading: false,
      downloading: false,
      reportData: null
    };
  },
  computed: {
    hasData() {
      return this.reportData && this.reportData.by_date.length > 0;
    },
    dateLabels() {
      return this.reportData ? this.reportData.by_date.map(x => x.date) : [];
    },
    dateData() {
      return [{
        label: "Appointments",
        data: this.reportData ? this.reportData.by_date.map(x => x.count) : [],
        borderColor: "#0d6efd",
        backgroundColor: "rgba(13, 110, 253, 0.2)",
        fill: true,
        tension: 0.3
      }];
    },
    specLabels() {
      return this.reportData ? this.reportData.by_specialization.map(x => x.specialization) : [];
    },
    specData() {
      return [{
        label: "Count",
        data: this.reportData ? this.reportData.by_specialization.map(x => x.count) : [],
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]
      }];
    }
  },
  methods: {
    async fetchData() {
      if (!this.month) {
        alert("Please select a month first.");
        return;
      }
      this.loading = true;
      this.reportData = null;
      try {
        const res = await api.get(`/reports/monthly/json?month=${this.month}`);
        this.reportData = res.data;
        if (this.reportData.by_date.length === 0) {
          alert("No data found for the selected month.");
        }
      } catch (e) {
        console.error(e);
        const msg = e.response?.data?.msg || "Failed to load report data.";
        alert(msg);
      } finally {
        this.loading = false;
      }
    },
    async downloadFile(type) {
      this.downloading = true;
      try {
        // We use Axios to fetch the blob so headers are sent automatically
        const response = await api.get(`/reports/monthly/${type}?month=${this.month}`, {
          responseType: 'blob' // Critical: tells Axios to expect binary data
        });

        // Create a hidden link to download the blob
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        const ext = type === 'csv' ? 'csv' : 'pdf';
        link.setAttribute('download', `report_${this.month}.${ext}`);
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (e) {
        console.error("Download failed", e);
        alert("Failed to download file. Please try again.");
      } finally {
        this.downloading = false;
      }
    }
  }
};
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>