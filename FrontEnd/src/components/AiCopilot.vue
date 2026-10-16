<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'

const toast = useToast()
const ctx = useContextStore()

const isOpen = ref(false)
const isExpanded = ref(false)
const loading = ref(false)
const checkingStatus = ref(false)
const aiStatus = ref({ configured: false, provider: null, model: null })
const messageInput = ref('')
const chatContainer = ref(null)

const messages = ref([
  {
    role: 'assistant',
    content:
      'Halo! Saya **AI Copilot Manajemen Risiko** berbasis Perwal No. 1 Tahun 2026. Ada yang bisa saya bantu terkait perumusan risiko, penetapan RTP, kriteria dampak, atau pengisian formulir?',
    time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
  },
])

const quickChips = [
  'Rumus pernyataan risiko yang tepat',
  'Kriteria dampak Perwal 1/2026',
  'Contoh RTP respon risiko',
  'Panduan Media Komunikasi (Form 8)',
  'Panduan Metode Pemantauan PI (Form 9)',
]

async function checkAiStatus() {
  checkingStatus.value = true
  try {
    const { data } = await api.get('/ai/status')
    aiStatus.value = data
  } catch {
    aiStatus.value = { configured: false }
  } finally {
    checkingStatus.value = false
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

async function send(customText = null) {
  const text = (customText || messageInput.value || '').trim()
  if (!text || loading.value) return

  const now = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
  messages.value.push({ role: 'user', content: text, time: now })
  messageInput.value = ''
  scrollToBottom()

  if (!aiStatus.value.configured) {
    messages.value.push({
      role: 'assistant',
      content:
        '⚠️ **Layanan AI Belum Dikonfigurasi**\n\nAdmin perlu mengisi **API Key & Provider (Gemini / OpenAI / Anthropic)** di menu **Administrasi → Pengaturan Aplikasi** untuk mengaktifkan AI Copilot.',
      time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
    })
    scrollToBottom()
    return
  }

  loading.value = true
  try {
    // Siapkan history ringkas (max 6 pesan terakhir)
    const history = messages.value
      .slice(-6, -1)
      .map((m) => ({ role: m.role, content: m.content }))

    const currentOpd = ctx.opds?.find((o) => o.id === ctx.opdId)
    const { data } = await api.post('/ai/chat', {
      message: text,
      history,
      context: {
        opd: currentOpd?.nama || '',
        tahun: ctx.tahun || 2026,
      },
    })

    messages.value.push({
      role: 'assistant',
      content: data.reply || 'Maaf, tidak ada respon dari asisten.',
      time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
    })
  } catch (e) {
    const errDetail = e.response?.data?.detail || e.message || 'Gagal terhubung ke AI'
    messages.value.push({
      role: 'assistant',
      content: `❌ **Terjadi Kendala:**\n\n${errDetail}`,
      time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

function clearChat() {
  messages.value = [
    {
      role: 'assistant',
      content:
        'Percakapan telah dibersihkan. Silakan tanyakan hal lain seputar Manajemen Risiko.',
      time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
    },
  ]
}

function copyMessage(content) {
  navigator.clipboard.writeText(content)
  toast.add({ severity: 'info', summary: 'Disalin', detail: 'Teks disalin ke clipboard', life: 2000 })
}

// Basic markdown formatter (bold, lists, code, line breaks)
function renderMarkdown(str) {
  if (!str) return ''
  let html = str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Code blocks ```code```
    .replace(/```([\s\S]*?)```/g, '<pre class="ai-code-block"><code>$1</code></pre>')
    // Inline code `code`
    .replace(/`([^`]+)`/g, '<code class="ai-inline-code">$1</code>')
    // Bold **text**
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Italic *text*
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // Bullet lines starting with • or -
    .replace(/^[•\-]\s+(.*)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> into <ul>
    .replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>')
    .replace(/<\/ul>\s*<ul>/g, '')
    // Newlines
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>')
  return html
}

const activeOpdName = computed(() => {
  const o = ctx.opds?.find((x) => x.id === ctx.opdId)
  return o?.nama || 'Seluruh OPD'
})

onMounted(() => {
  checkAiStatus()
})

watch(isOpen, (val) => {
  if (val) {
    checkAiStatus()
    scrollToBottom()
  }
})
</script>

<template>
  <div class="ai-copilot-container">
    <!-- Floating Launcher Button -->
    <button
      v-if="!isOpen"
      type="button"
      class="ai-launcher-btn"
      title="Tanya AI Copilot Manajemen Risiko"
      @click="isOpen = true"
    >
      <div class="ai-launcher-glow"></div>
      <div class="ai-launcher-inner">
        <i class="pi pi-sparkles ai-launcher-icon" />
        <span class="ai-launcher-text">AI Copilot</span>
      </div>
      <span class="ai-pulse-ring"></span>
    </button>

    <!-- Floating Chat Window -->
    <transition name="ai-fade-slide">
      <div
        v-if="isOpen"
        :class="['ai-chat-window', { 'ai-expanded': isExpanded }]"
      >
        <!-- Header -->
        <div class="ai-header">
          <div class="ai-header-left">
            <div class="ai-avatar">
              <i class="pi pi-sparkles" />
            </div>
            <div>
              <div class="ai-title-row">
                <span class="ai-title">AI Copilot</span>
                <span class="ai-badge-perwal">Perwal 1/2026</span>
                <span
                  v-if="aiStatus.configured"
                  class="ai-badge-provider"
                  :title="`Model: ${aiStatus.model || 'Default'}`"
                >
                  {{ aiStatus.provider }}
                </span>
                <span v-else class="ai-badge-off">Belum Aktif</span>
              </div>
              <div class="ai-subtitle">
                <i class="pi pi-building text-xs mr-1" />
                {{ activeOpdName }} • {{ ctx.tahun }}
              </div>
            </div>
          </div>
          <div class="ai-header-actions">
            <button
              type="button"
              class="ai-tool-btn"
              title="Bersihkan Percakapan"
              @click="clearChat"
            >
              <i class="pi pi-trash" />
            </button>
            <button
              type="button"
              class="ai-tool-btn"
              :title="isExpanded ? 'Kecilkan' : 'Perbesar'"
              @click="isExpanded = !isExpanded"
            >
              <i :class="['pi', isExpanded ? 'pi-window-minimize' : 'pi-window-maximize']" />
            </button>
            <button
              type="button"
              class="ai-tool-btn ai-close-btn"
              title="Tutup"
              @click="isOpen = false"
            >
              <i class="pi pi-times" />
            </button>
          </div>
        </div>

        <!-- Chat Body -->
        <div ref="chatContainer" class="ai-chat-body">
          <!-- Welcome Prompt & Quick Chips -->
          <div class="ai-chips-container">
            <span class="ai-chips-label">Pertanyaan Cepat:</span>
            <div class="ai-chips-wrap">
              <button
                v-for="(chip, idx) in quickChips"
                :key="idx"
                type="button"
                class="ai-chip"
                @click="send(chip)"
              >
                {{ chip }}
              </button>
            </div>
          </div>

          <!-- Message List -->
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="['ai-msg-row', msg.role === 'user' ? 'ai-user' : 'ai-bot']"
          >
            <div v-if="msg.role === 'assistant'" class="ai-msg-avatar">
              <i class="pi pi-sparkles" />
            </div>

            <div class="ai-msg-bubble">
              <!-- eslint-disable-next-line vue/no-v-html -->
              <div class="ai-msg-content" v-html="renderMarkdown(msg.content)"></div>
              <div class="ai-msg-footer">
                <span class="ai-msg-time">{{ msg.time }}</span>
                <button
                  v-if="msg.role === 'assistant'"
                  type="button"
                  class="ai-msg-copy"
                  title="Salin Pesan"
                  @click="copyMessage(msg.content)"
                >
                  <i class="pi pi-copy" />
                </button>
              </div>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="loading" class="ai-msg-row ai-bot">
            <div class="ai-msg-avatar">
              <i class="pi pi-sparkles" />
            </div>
            <div class="ai-msg-bubble ai-typing-bubble">
              <span class="ai-dot"></span>
              <span class="ai-dot"></span>
              <span class="ai-dot"></span>
            </div>
          </div>
        </div>

        <!-- Chat Input Footer -->
        <div class="ai-chat-footer">
          <div class="ai-input-wrap">
            <Textarea
              v-model="messageInput"
              rows="1"
              autoResize
              placeholder="Tanya perumusan risiko, saran RTP, atau regulasi... (Enter untuk kirim)"
              class="ai-textarea"
              :disabled="loading"
              @keydown="handleKeydown"
            />
            <Button
              icon="pi pi-send"
              severity="primary"
              rounded
              size="small"
              class="ai-send-btn"
              :loading="loading"
              :disabled="!messageInput.trim()"
              @click="send()"
            />
          </div>
          <div class="ai-footer-note">
            Didukung AI untuk asistensi Manajemen Risiko. Tetap lakukan verifikasi mandiri sebelum penetapan.
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.ai-copilot-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1050;
  font-family: inherit;
}

/* Floating Launcher Button */
.ai-launcher-btn {
  position: relative;
  display: flex;
  align-items: center;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
  border-radius: 9999px;
  outline: none;
  transition: transform 0.25s ease;
}

.ai-launcher-btn:hover {
  transform: translateY(-3px) scale(1.03);
}

.ai-launcher-inner {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px 10px 14px;
  border-radius: 9999px;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
  color: #ffffff;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4), 0 2px 6px rgba(0, 0, 0, 0.1);
  font-weight: 600;
  font-size: 0.9rem;
  z-index: 2;
}

.ai-launcher-icon {
  font-size: 1.15rem;
  animation: ai-sparkle-spin 6s ease-in-out infinite;
}

@keyframes ai-sparkle-spin {
  0%, 100% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(15deg) scale(1.15); }
}

.ai-pulse-ring {
  position: absolute;
  inset: -4px;
  border-radius: 9999px;
  border: 2px solid rgba(99, 102, 241, 0.6);
  animation: ai-pulse 2.2s cubic-bezier(0.24, 0, 0.38, 1) infinite;
  z-index: 1;
}

@keyframes ai-pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  70% { transform: scale(1.2); opacity: 0; }
  100% { transform: scale(1.2); opacity: 0; }
}

/* Chat Window */
.ai-chat-window {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 420px;
  height: 580px;
  max-width: calc(100vw - 32px);
  max-height: calc(100vh - 48px);
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 16px 48px -8px rgba(0, 0, 0, 0.22), 0 0 1px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.ai-chat-window.ai-expanded {
  width: 700px;
  height: 720px;
}

/* Header */
.ai-header {
  padding: 12px 14px;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #1e293b 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

.ai-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.ai-title {
  font-weight: 700;
  font-size: 0.95rem;
  color: #ffffff;
}

.ai-badge-perwal {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.16);
  color: #e0e7ff;
}

.ai-badge-provider {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  background: #059669;
  color: #ffffff;
  text-transform: uppercase;
}

.ai-badge-off {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  background: #dc2626;
  color: #ffffff;
}

.ai-subtitle {
  font-size: 0.74rem;
  color: #cbd5e1;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 240px;
}

.ai-header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ai-tool-btn {
  background: transparent;
  border: none;
  color: #cbd5e1;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s;
  font-size: 0.8rem;
}

.ai-tool-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  color: #ffffff;
}

.ai-close-btn:hover {
  background: #ef4444;
}

/* Chat Body */
.ai-chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Chips */
.ai-chips-container {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px 10px;
  margin-bottom: 4px;
}

.ai-chips-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  display: block;
  margin-bottom: 6px;
}

.ai-chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ai-chip {
  font-size: 0.74rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  border-radius: 999px;
  padding: 3px 9px;
  cursor: pointer;
  transition: all 0.18s ease;
  text-align: left;
}

.ai-chip:hover {
  background: #e0e7ff;
  border-color: #a5b4fc;
  color: #4338ca;
}

/* Messages */
.ai-msg-row {
  display: flex;
  gap: 8px;
  max-width: 90%;
}

.ai-msg-row.ai-user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.ai-msg-row.ai-bot {
  margin-right: auto;
}

.ai-msg-avatar {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.ai-msg-bubble {
  border-radius: 12px;
  padding: 9px 12px;
  font-size: 0.84rem;
  line-height: 1.48;
  position: relative;
  word-break: break-word;
}

.ai-user .ai-msg-bubble {
  background: linear-gradient(135deg, #4f46e5, #4338ca);
  color: #ffffff;
  border-bottom-right-radius: 3px;
}

.ai-bot .ai-msg-bubble {
  background: #ffffff;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 3px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.ai-msg-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  margin-top: 4px;
}

.ai-msg-time {
  font-size: 0.66rem;
  opacity: 0.65;
}

.ai-msg-copy {
  background: transparent;
  border: none;
  font-size: 0.72rem;
  color: #64748b;
  cursor: pointer;
  padding: 1px 4px;
  border-radius: 4px;
}

.ai-msg-copy:hover {
  background: #f1f5f9;
  color: #1e293b;
}

/* Typing indicator */
.ai-typing-bubble {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
}

.ai-dot {
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: ai-dot-bounce 1.4s infinite ease-in-out both;
}

.ai-dot:nth-child(1) { animation-delay: -0.32s; }
.ai-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes ai-dot-bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Markdown styling inside messages */
:deep(.ai-code-block) {
  background: #0f172a;
  color: #f8fafc;
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 0.76rem;
  overflow-x: auto;
  margin: 6px 0;
}

:deep(.ai-inline-code) {
  background: #f1f5f9;
  color: #be185d;
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 0.78rem;
}

:deep(ul) {
  margin: 6px 0;
  padding-left: 18px;
}

:deep(li) {
  margin-bottom: 3px;
}

/* Chat Footer */
.ai-chat-footer {
  padding: 10px 12px;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
}

.ai-input-wrap {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.ai-textarea {
  flex: 1;
  font-size: 0.84rem;
  max-height: 90px;
  resize: none;
}

.ai-send-btn {
  flex-shrink: 0;
}

.ai-footer-note {
  font-size: 0.65rem;
  color: #94a3b8;
  text-align: center;
  margin-top: 6px;
}

/* Transitions */
.ai-fade-slide-enter-active,
.ai-fade-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.ai-fade-slide-enter-from,
.ai-fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.96);
}
</style>
