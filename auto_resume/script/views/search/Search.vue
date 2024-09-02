<script lang="js" setup>

</script>

<template>

<div>
    <nav>
        <router-link to="/search/detail"> Detail</router-link>
        <router-link to="/search/parameters"> Params</router-link>
    </nav>
    <router-view></router-view>
</div>
</template>

<style lang="css" scoped> 
nav {
  @apply flex flex-row flex-nowrap gap-4 mb-4;

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

