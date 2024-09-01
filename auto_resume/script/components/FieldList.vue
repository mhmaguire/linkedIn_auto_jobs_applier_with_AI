<script setup lang="js">

import Field from '@/components/Field.vue'
import { PlusIcon, XMarkIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
    title: String,
    name: String,
    description: String,
    type: String,
    itemType: String,
})
const model = defineModel()

</script>

<template>

    <div>
        <div v-for="item, i in model" class="flex flex-row flex-nowrap items-center">
            <button class="border-0" @click.prevent="model.splice(i, 1)"> <XMarkIcon class="w-6 h-6" /> </button>
            <Field v-bind="{type: props.itemType}" v-model="model[i]" />
        </div>
    </div>

    <button class="border-0" @click.prevent="model.push(undefined)"> 
        <PlusIcon class="w-6 h-6" />
    </button>

</template>

<style lang="css" scoped>

</style>