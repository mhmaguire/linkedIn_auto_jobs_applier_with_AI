<script lang="js" setup>
import { computed, defineModel, defineProps, reactive, toValue } from 'vue'
import FieldList from '@/components/FieldList.vue'

const model = defineModel()
const props = defineProps({
    title: String,
    name: String,
    description: String,
    type: String,
    itemType: String,
    enum: Array,
    required: Array,
    properties: {
        type: Object,
        optional: true
    }
})

const isText = computed(() => props.type == 'string' && !props.enum)
const isRadio = computed(() => props.enum)
const isCheckbox = computed(() => props.type == 'boolean')
const isNumber = computed(() => props.type == 'integer' && !props.enum)
const isComplex = computed(() => props.type == 'object')
const isArray = computed(() => props.type == 'array')


const fieldClass = reactive({
    'field--array': toValue(isArray),
    'field--object': toValue(isComplex),
    'field--number': toValue(isNumber),
    'field--checkbox': toValue(isCheckbox),
    'field--radio': toValue(isRadio),
    'field--text': toValue(isText),
})

</script>

<template>
<div class="field" :class="fieldClass">
    <template v-if="isText">
        <label class="text-lg" :for="name"> {{ title }} </label>
        <legend class="text-sm font-light"> {{ description }} </legend>
        <input :id="name" :name="name" type="text" v-model="model">
    </template>

    <template v-if="isCheckbox">
        <input :id="name" :name="name" type="checkbox" v-model="model">
        <label class="text-lg" :for="name"> {{ title }} </label>
        <legend class="text-sm font-light"> {{ description }} </legend>
    </template>

    <template v-if="isNumber">
        <label class="text-lg" :for="name"> {{ title }} </label>
        <legend class="text-sm font-light"> {{ description }} </legend>
        <input :id="name" :name="name" type="number" v-model="model">
    </template>

    <template v-if="isRadio">
        <label class="text-lg" :for="name"> {{ title }} </label>
        <legend class="text-sm font-light"> {{ description }} </legend>
        <div class="flex flex-row gap-2">
            <div v-for="option in enum" class="radio--option space-x-2">
                <label :for="`${name}_${option}`"> {{option}} </label>
                <input :value="option" :id="`${name}_${option}`" :name="name" type="radio" v-model="model">
            </div>
        </div>
    </template>

    <template v-if="isComplex">
        <label class="text-lg" :for="name"> {{ title }} </label>
        <legend class="text-sm font-light"> {{ description }} </legend>
        <Field v-for="prop, key of properties" v-bind="{...prop, name: key}" v-model="model[key]"/>
    </template>

    <template v-if="isArray">
        <label class="text-lg" :for="name"> {{ title }} </label>
        <legend class="text-sm font-light"> {{ description }} </legend>
        <FieldList v-bind="{...props}" />
    </template>
</div>
</template>

<style lang="css" scoped> </style>