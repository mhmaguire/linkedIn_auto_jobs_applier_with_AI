<script lang="js" setup>
import { useWs } from '@/store/socket';
import { useFetch } from '@vueuse/core'

const search = async () => {
    const { data } = await useFetch('/api/tasks/search').post().json()
    console.log(data)
}

const ws = useWs()
</script>

<template>
    <div>
        <button @click="search()"> 
            Search
        </button>

        {{ ws.connected }}

        <div>
            <p v-for="m in ws.messages">
                {{ m }}
            </p>
        </div>
    </div>

</template>