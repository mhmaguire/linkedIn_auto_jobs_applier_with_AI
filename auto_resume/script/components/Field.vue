<script lang="js" setup>
import { computed, defineModel, defineProps, onMounted } from 'vue'

const model = defineModel()
const props = defineProps({
    title: String,
    name: String,
    description: String,
    type: String
})

const isText = computed(() => props.type == 'string')
const isCheckbox = computed(() => props.type == 'boolean')
const isNumber = computed(() => props.type == 'integer')

onMounted(() => {
    console.log(props)
})

</script>

<template>
<div>
    <template v-if="isText">
        <label class="text-lg" :for="props.name"> {{ props.title }} </label>
        <legend class="text-sm font-light"> {{ props.description }} </legend>
        <input :id="props.name" :name="props.name" type="text" v-model="model">
    </template>

    <template v-if="isCheckbox">
        <label class="text-lg" :for="props.name"> {{ props.title }} </label>
        <legend class="text-sm font-light"> {{ props.description }} </legend>
        <input :id="props.name" :name="props.name" type="checkbox" v-model="model">
    </template>

    <template v-if="isNumber">
        <label class="text-lg" :for="props.name"> {{ props.title }} </label>
        <legend class="text-sm font-light"> {{ props.description }} </legend>
        <input :id="props.name" :name="props.name" type="number" v-model="model">
    </template>
</div>
</template>

<style lang="css" scoped> </style>