<script setup>
</script>

<template>
  <div class="container mx-auto">
    <nav>
      <router-link to="/">Master Resume</router-link>
      <router-link to="/jobs">Jobs</router-link>
      <router-link to="/search/parameters">Search Params</router-link>
      <!-- <router-link to="/resume">Resume</router-link>
      <router-link to="/cover-letter">Cover Letter</router-link> -->
    </nav>
    <router-view></router-view>
  </div>
</template>

<style scoped>
nav {
  @apply flex flex-row flex-nowrap gap-4 mt-4 mb-6 py-4;

  a {

    @apply mx-4 my-2 p-2;

    &:hover, &.router-link-active:hover {
      @apply no-underline border-b-2 border-cyan-400;
    }

    &.router-link-active {
      @apply border-b-2 border-cyan-500;
    }
  }


}
</style>
