<script setup>
import { toValue, onMounted } from 'vue';
import { useFetch } from '@vueuse/core'
import {  } from 'vue';

import { PlusIcon, XMarkIcon } from '@heroicons/vue/24/solid'

import { MasterResume } from '../../model/resume.py'

import Field from '@/components/Field.vue'

const resume = MasterResume()


onMounted(async () => {
  const {data} = await useFetch('/api/resumes/master').get().json()

  console.log(resume, data)

  resume.data = toValue(data).master_resume
})

const submitResume = () => {
  const { success, data } = resume.validator.safeParse(toValue(resume.data))
  console.log('SUBMIT', resume.isValid())

  resume.update()
}

</script>

<template>


<form v-if="resume.schema.properties" 
  @keyup.enter="submitResume()"
  @submit.prevent="submitResume()">

  <div class="flex flex-col space-y-12">
    <fieldset class="grid grid-cols-3 lg:grid-cols-4 grid-flow-row auto-rows-min pb-12 border-b-2 border-b-gray-500"
      v-for="{ title, description, type, ...property }, key of resume.schema.properties">

      <div class="lg:col-span-1"> 
        <legend class="text-2xl">{{ title }}</legend>
        <span class="text-md">{{ description }}</span>
      </div>

      <template v-if="type == 'object'">
        <div class="lg:col-span-3 grid grid-cols-subgrid">
        <Field 
          class=""
          v-bind="{ ...prop }" :name="name" v-for="(prop, name) of property.properties"
          v-model="resume.data[key][name]" />
        </div>
      </template>
      
      <template v-if="type == 'array'">
        <div class="col-span-3">
          <template v-for="item, i in resume.data[key]">
            <button class="border-0" @click.prevent="resume.data[key].splice(i, 1)"> <XMarkIcon class="w-6 h-6" /> </button>
            <div class="grid grid-flow-row auto-rows-min grid-cols-3">
              <Field v-bind="{ ...prop }" :name="name" v-for="(prop, name) of property.items.properties"
                v-model="item[name]" />
            </div>
          </template>
          <button class="border-0" @click.prevent="resume.data[key].push({})"> 
            <PlusIcon class="w-6 h-6" />
          </button>
        </div>
      </template>
    </fieldset>
  </div>

  <button type="submit"> Update </button>
</form>

</template>

<!-- <template>
  <div>
    <pre> {{ data }} </pre>
    <form v-if="masterResumeSchema.properties">
      <fieldset v-for="{ title, description, type, ...property }, key of masterResumeSchema.properties">
        <legend class="text-xl">{{ title }}</legend>
        <span class="text-lg">{{ description }}</span>

        <template v-if="type == 'object'">
          <div v-for="(prop, name) of property.properties">
            <label :for="name"> {{ prop.title }} </label>
            <legend> {{ prop.description }} </legend>
            <input :id="name" :name="name" type="text" v-model="data[key][name]">
          </div>
        </template>


        <template v-if="type == 'array'">
          <div> 
            <button @click.prevent="data[key].push({})"> Add Item </button>

            <div v-for="item, i in data[key]">
              <button @click.prevent="data[key].splice(i)"> Remove Item </button>

              <div v-for="(prop, name) of property.items.properties">
                <label :for="name"> {{ prop.title }} </label>
                <legend> {{ prop.description }} </legend>
                <input :id="name" :name="name" type="text" v-model="item[name]">
              </div>

            </div>
          </div>
        </template>
      </fieldset>
    </form>
  </div>
</template> -->

<style scoped></style>
