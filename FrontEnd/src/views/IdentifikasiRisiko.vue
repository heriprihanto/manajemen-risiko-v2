<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import Form3 from '@/views/Form3.vue'

const route = useRoute()
const router = useRouter()

// Tab aktif disinkronkan dengan query parameter ?tab=3a | 3b | 3c
const validTabs = ['3a', '3b', '3c']
const initialTab = validTabs.includes(route.query.tab) ? route.query.tab : '3a'
const currentTab = ref(initialTab)

watch(
  () => route.query.tab,
  (newTab) => {
    if (newTab && validTabs.includes(newTab) && newTab !== currentTab.value) {
      currentTab.value = newTab
    }
  },
)

function onTabChange(val) {
  currentTab.value = val
  router.replace({ query: { ...route.query, tab: val } })
}
</script>

<template>
  <div class="identifikasi-container">
    <div class="page-header no-print">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-flag"></i>
        </div>
        <div>
          <h1 class="page-title">Identifikasi Risiko</h1>
          <p class="page-desc">
            Identifikasi risiko strategis Pemda, risiko strategis OPD, dan risiko operasional OPD
          </p>
        </div>
      </div>
    </div>

    <!-- Tabs Container -->
    <div class="tabs-card">
      <Tabs :value="currentTab" @update:value="onTabChange">
        <TabList class="custom-tab-list">
          <Tab value="3a" class="custom-tab">
            <i class="pi pi-building tab-icon"></i>
            <span>Strategis Pemda</span>
          </Tab>
          <Tab value="3b" class="custom-tab">
            <i class="pi pi-sitemap tab-icon"></i>
            <span>Strategis OPD</span>
          </Tab>
          <Tab value="3c" class="custom-tab">
            <i class="pi pi-cog tab-icon"></i>
            <span>Operasional OPD</span>
          </Tab>
        </TabList>

        <TabPanels class="custom-tab-panels">
          <TabPanel value="3a">
            <div class="tab-content-wrap">
              <Form3 jenis="strategis_pemda" />
            </div>
          </TabPanel>
          <TabPanel value="3b">
            <div class="tab-content-wrap">
              <Form3 jenis="strategis_opd" />
            </div>
          </TabPanel>
          <TabPanel value="3c">
            <div class="tab-content-wrap">
              <Form3 jenis="operasional_opd" />
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>
  </div>
</template>

<style scoped>
.identifikasi-container {
  padding: 1.25rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

.page-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.2rem 0;
  letter-spacing: -0.02em;
}

.page-desc {
  color: #64748b;
  font-size: 0.85rem;
  margin: 0;
}

.tabs-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.custom-tab-list {
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  padding: 0.25rem 0.5rem 0;
}

.custom-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.85rem 1.25rem;
  transition: all 0.2s;
  color: #64748b;
}

.custom-tab:hover {
  color: #4f46e5;
}

.tab-icon {
  font-size: 1rem;
}

.custom-tab-panels {
  padding: 1.25rem;
  background: #ffffff;
}

.tab-content-wrap {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
