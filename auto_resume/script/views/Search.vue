<script lang="js" setup>
  import { useFetch } from '@vueuse/core'
  import { onMounted, ref } from 'vue';

  import { Parameters } from '../../model/config.py'
  import Field from '@/components/Field.vue'
  import FieldList from '@/components/FieldList.vue'
  import {PlusIcon, XMarkIcon} from '@heroicons/vue/24/solid'

  const params = Parameters()


  const submitParams = () => {
    const { success, data, ...rest } = params.isValid()

    if (success) {
      return useFetch('/api/search/parameters').put(params.data).json()
    } else {
      print(success, rest)
      return {success, ...rest}
    }
  }

  onMounted(async () => {
    const { data } = await useFetch('/api/search/parameters').get().json()
    console.log(params.validator)
    params.data = data.value.parameters
  })

  const getField = (fieldName) => {
    const {type, items, ...field} = params.schema.properties[fieldName]

    if (type == 'array') {
      return {
        ...field,
        type,
        itemType: items.type
      }
    }

    return {type, ...field, name: fieldName}
  }

</script>

<template>

<form v-if="params.schema.properties" @keyup.enter="submitParams()" @submit.prevent="submitParams()">
  <div class="grid grid-flow-row grid-cols-4 ">
    <Field v-bind="{...getField('email')}" v-model="params.data.email" />
    <Field v-bind="{...getField('workTypes')}" v-model="params.data.workTypes" />
    <Field v-bind="{...getField('experienceLevel')}" v-model="params.data.experienceLevel" />
    <Field v-bind="{...getField('jobTypes')}" v-model="params.data.jobTypes" />
    <Field v-bind="{...getField('date')}" v-model="params.data.date" />
    <Field v-bind="{...getField('distance')}" v-model="params.data.distance" />
    <Field v-bind="{...getField('positions')}" v-model="params.data.positions" />
    <Field v-bind="{...getField('locations')}" v-model="params.data.locations" />
    <Field v-bind="{...getField('companyBlacklist')}" v-model="params.data.companyBlacklist" />
    <Field v-bind="{...getField('titleBlacklist')}" v-model="params.data.titleBlacklist" />

  </div>

  <button type="submit"> Update </button>
</form>

</template>


<style>

.field--checkbox {
  @apply flex flex-row flex-nowrap gap-2 items-center;
}

.field--radio .radio--option {
  @apply flex flex-row flex-nowrap items-center;
}
</style>