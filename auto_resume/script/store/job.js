import { defineStore } from 'pinia'
import { useFetch, get } from '@vueuse/core'
import { ref, computed } from 'vue'

export const useJobs = defineStore('jobs', () => {

  const jobs = ref([])

  const {
    execute,
    isFetching,
    onFetchResponse,
    onFetchError,
    data
  } = useFetch('/api/jobs', { immediate: false }).get().json()

  onFetchResponse(async (response) => {
    console.log(response, data)
    jobs.value = get(data).jobs
  })

  onFetchError((error) => {
    console.log(error)
  })


  return {
    jobs,
    isFetching,
    fetch: execute
  }
})

export const useJob = defineStore('job', () => {
  const jobs = useJobs()
  const job = ref(null)
  const id = computed(() => {
    if (!get(job)) return null

    return get(job).id
  })

  async function find(job_id) {
    const { data } = await useFetch(`/api/jobs/${job_id}`).get().json()
    job.value = get(data).job
  }

  async function summarize() {
    const { data } = await useFetch(`/api/jobs/${get(id)}/summarize`).post().json()

    job.value = get(data).job
  }

  async function resume() {
    const { data } = await useFetch(`/api/jobs/${get(id)}/resume`).post().json()

    job.value = get(data).job
  }

  return {
    id,
    job,
    find,
    summarize,
    resume,
  }
})