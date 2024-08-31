<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useJobs } from '../store/job';

const jobStore = useJobs()
const { isFetching, jobs } = storeToRefs(jobStore)

onMounted(() => {
    jobStore.fetch()
})

</script>

<template>
<div class="page">
    <h1 class="page--header"> Job List </h1>

    <div class="page--body">
        <template v-if="isFetching">
            fetching ...
        </template>

        <template v-else>
            <ul>
                <li v-for="job in jobs">
                    <router-link :to="`/jobs/${job.job.id}`">
                        {{job.job.title}} - {{ job.score }}
                    </router-link>
                </li>
            </ul>
        </template>
    </div>
</div>
</template>

<style scoped>
</style>
