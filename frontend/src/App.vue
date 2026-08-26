<script setup lang="ts">
import ChatDashboard from './components/ChatDashboard.vue'
</script>

<template>
  <div class="min-h-screen bg-brain-dark text-brain-ivory">
    <nav class="mx-auto flex max-w-[1440px] items-center justify-between px-5 py-6 md:px-10">
      <div>
        <p class="text-xs uppercase tracking-[0.32em] text-brain-muted">AI Data Analyst</p>
        <h1 class="font-display text-2xl uppercase tracking-[0.18em] text-brain-gold">Brainwave BI</h1>
      </div>
      <div class="hidden items-center gap-2 rounded-full border border-brain-line bg-brain-panel px-2 py-2 md:flex">
        <a href="#" class="nav-pill active">Dashboard</a>
        <a href="#" class="nav-pill">Datasets</a>
        <a href="#" class="nav-pill">Insights</a>
      </div>
      <button class="btn-primary">Consultar dados</button>
    </nav>

    <main class="mx-auto max-w-[1440px] px-5 pb-10 md:px-10">
      <div class="mb-9 text-center">
        <p class="mb-3 text-sm uppercase tracking-[0.36em] text-brain-muted">Portfolio Analytics</p>
        <h2 class="font-display text-4xl uppercase tracking-[0.12em] text-brain-gold md:text-6xl">
          Analytics Dashboard
        </h2>
        <p class="mx-auto mt-4 max-w-2xl text-sm leading-6 text-brain-muted md:text-base">
          Pergunte em portugues, veja o SQL seguro, confira a tabela e acompanhe os insights em uma interface de BI pronta para portfolio.
        </p>
      </div>

      <ChatDashboard />
    </main>
  </div>
</template>

<style scoped>
</style>
