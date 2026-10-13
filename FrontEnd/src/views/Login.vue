<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const captchaId = ref('')
const captchaSvg = ref('')
const captchaAnswer = ref('')
const captchaLoading = ref(false)

async function loadCaptcha() {
  captchaLoading.value = true
  captchaAnswer.value = ''
  try {
    const { data } = await api.get('/auth/captcha')
    captchaId.value = data.id
    captchaSvg.value = data.svg
  } catch {
    captchaSvg.value = ''
  } finally {
    captchaLoading.value = false
  }
}

async function submit() {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = 'Username dan password wajib diisi'
    return
  }
  if (!captchaAnswer.value) {
    error.value = 'Masukkan kode captcha'
    return
  }
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value, {
      id: captchaId.value,
      answer: captchaAnswer.value,
    })
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Gagal login, coba lagi'
    loadCaptcha() // captcha sekali pakai — muat ulang setiap gagal
  } finally {
    loading.value = false
  }
}

onMounted(loadCaptcha)
</script>

<template>
  <div class="login-wrap">
    <form class="login-card" @submit.prevent="submit">
      <div class="login-brand">
        <i class="pi pi-shield" />
        <div>
          <h1>Manajemen Risiko</h1>
          <p>Pemerintah Kota Tegal — SPIP</p>
        </div>
      </div>

      <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

      <label>Username</label>
      <InputText v-model="username" placeholder="Username" autofocus fluid />

      <label>Password</label>
      <Password
        v-model="password"
        placeholder="Password"
        :feedback="false"
        toggleMask
        fluid
        inputStyle="width:100%"
      />

      <label>Kode Captcha</label>
      <div class="captcha-row">
        <div class="captcha-img" v-html="captchaSvg" aria-hidden="true" />
        <Button
          type="button"
          icon="pi pi-refresh"
          severity="secondary"
          outlined
          :loading="captchaLoading"
          v-tooltip.bottom="'Ganti kode'"
          @click="loadCaptcha"
        />
      </div>
      <InputText
        v-model="captchaAnswer"
        placeholder="Ketik kode di atas"
        autocomplete="off"
        fluid
        @keyup.enter="submit"
      />

      <Button
        type="submit"
        :loading="loading"
        label="Masuk"
        icon="pi pi-sign-in"
        class="login-btn"
      />
    </form>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: #0b1030;
  background-image:
    radial-gradient(700px 500px at 12% 10%, rgba(99, 102, 241, .55), transparent 55%),
    radial-gradient(700px 520px at 88% 20%, rgba(236, 72, 153, .40), transparent 55%),
    radial-gradient(760px 620px at 50% 108%, rgba(34, 211, 238, .38), transparent 58%),
    linear-gradient(135deg, #0f172a, #131a44);
}
.login-card {
  position: relative;
  width: 100%;
  max-width: 390px;
  background: rgba(255, 255, 255, .97);
  border-radius: 18px;
  padding: 2rem;
  box-shadow: 0 30px 70px -20px rgba(6, 10, 40, .7), 0 0 0 1px rgba(255, 255, 255, .08);
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  overflow: hidden;
}
.login-card::before {
  content: "";
  position: absolute;
  left: 0; right: 0; top: 0;
  height: 5px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 55%, #ec4899 100%);
}
.login-brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1rem;
}
.login-brand .pi {
  font-size: 1.5rem;
  color: #fff;
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 13px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 55%, #ec4899 100%);
  box-shadow: 0 10px 22px -6px rgba(139, 92, 246, .7);
}
.login-brand h1 {
  font-size: 1.15rem;
  margin: 0;
}
.login-brand p {
  margin: 0;
  font-size: 0.8rem;
  color: #64748b;
}
.login-card label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
  margin-top: 0.35rem;
}
.captcha-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.captcha-img {
  flex: 1;
  height: 52px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
}
.captcha-img :deep(svg) {
  width: 100%;
  height: 100%;
}
.login-btn {
  margin-top: 1.25rem;
}
</style>
