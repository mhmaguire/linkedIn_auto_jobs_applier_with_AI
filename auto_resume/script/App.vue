<script setup>
import { ref } from 'vue'

const msg = ref('Hello World!')
</script>

<template>
  <div class="container mx-auto">
    <nav>
      <router-link to="/">Home</router-link>
      <router-link to="/jobs">Jobs</router-link>
      <router-link to="/resume">Resume</router-link>
      <router-link to="/cover-letter">Cover Letter</router-link>
    </nav>
    <h1>{{ msg }}</h1>
    <router-view></router-view>
  </div>
</template>

<style scoped>
h1 {
  color: #42b983;
}
</style>
