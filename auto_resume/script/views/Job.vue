<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useJob } from '@/store/job'
import VueMarkdown from 'vue-markdown-render'
import { ArrowTopRightOnSquareIcon as ExternalIcon } from '@heroicons/vue/24/solid'

const route = useRoute()
const job = useJob()

watch(() => route.params.id,
    async () => await job.find(route.params.id),
    { immediate: true }
)

async function summarize() {
    await job.summarize()
}

async function resume() {
    await job.resume()
}

</script>

<template>
<div class="page">
    <h1 class="page--header"> Job </h1>
    
    <div v-if="job.job" class="page--body">
        
        <header class="subheader">
            <nav class="ctx-nav">
                <button @click='summarize()'> Summarize </button>
                <button @click='resume()'> Resume </button>
            </nav>
        </header>


        <div class="job">
            <div class="job--header">
                <a :href="job.job.link" class="job--title link"> 
                    <ExternalIcon class="link--icon"/>
                    <span class="link--text"> {{ job.job.title }} </span>
                </a>

                <a :href="job.job.company.link" class="job--company link"> 
                    <ExternalIcon class="link--icon"/>
                    <span class="link--text"> {{ job.job.company.name }} </span>
                </a>
            </div>

            <div class="job--resumes card">
                <div class="card--header"> <h3> Resumes </h3> </div>

                <div class="card--body"> 
                    <template v-if="job.job.resumes">
                        <ul>
                            <li v-for="resume in job.job.resumes">
                                <router-link :to="`/resumes/${resume.id}`">
                                    Resume created on {{ resume.created_at }}
                                </router-link>
                            </li>
                        </ul>
                    </template>

                    <template v-else>
                        <p> No resumes available. </p>
                    </template>
                </div>
            </div>

            <div class="job--summary card">
                <div class="card--header"><h3> Summary </h3></div>
                
                <div class="card--body">
                    <VueMarkdown :source="job.job.summary" v-if="job.job.summary" class="text" />
                </div>
            </div>

            <div class="job--commpany company card">
                <div class="card--header"> <h3> Company Description </h3> </div>

                <div class="card--body text"> 
                    <p class="text">
                        <template v-if="job.job.company.description">
                            {{ job.job.company.description }}
                        </template>

                        <template v-else>
                            No Description
                        </template>
                    </p>
                </div>
            </div>

            <div class="job--description card">
                <div class="card--header"> <h3> Description </h3> </div>
                <div class="card--body">
                    <p class="text">
                        {{ job.job.description }}
                    </p>
                </div>
            </div>
        </div>

    </div>

</div>

</template>

<style scoped>

    .subheader {
        @apply my-4;

        & .ctx-nav {
            @apply flex flex-row flex-nowrap gap-4 items-baseline;
        }
    }

    .job {
        @apply pt-4 pb-8 flex flex-col flex-nowrap gap-8;
        
        & .job {

            &--header {
                @apply flex flex-row flex-nowrap gap-8 items-baseline;
            }

            &--company {}

            &--resumes {}

            &--description {}

            &--summary {}

        }
    }
</style>
