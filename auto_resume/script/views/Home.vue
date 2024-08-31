<script setup>

import { z } from 'zod'
import { MasterResume } from '../../model/resume.py'
import { computed, ref, toValue } from 'vue';
import { defineStore } from 'pinia'

const useResume = defineStore('masterResume', () => {

    const schema = ref(MasterResume)
    const required = computed(() => {
        return toValue(schema)['required']
    })
    const defs = computed(() => {
        return toValue(schema)['$defs']
    })

    const resolveDef = (def) => {
        const {$ref, type} = def

        if ($ref) {
            return toValue(defs)[$ref.split('/').at(-1)]
        }

        if (type == 'string') {
            return String
        }
    }

    const resolveProperty = (p) => {
        if(p['allOf']) {
            console.log('reference')
            return {
                ...p,
                ...resolveDef(p['allOf'][0])
            }
        } else if (p['type'] == 'array') {
            console.log('array')
            return {
                type: 'array',
                items: resolveDef(p['items'])
            }
        } else if (p['type'] == 'string') {
            return p
        }
    }

    const properties = computed(() => {
        let _properties = toValue(schema)['properties']

        const obj = Object.fromEntries(
            Object.entries(_properties).map(([name, value]) => {
                return [
                    name,
                    resolveProperty(value)
                ]
            })
        )

        return obj
    })



    return {
        properties,
        required
    }
})

const resumeStore = useResume() 

const Resume = z.object(
    // Object.fromEntries()
)

const prettySchema = computed(() => {
    return JSON.stringify(MasterResume, null, 2)
})

const properties = computed(() => {
    return MasterResume.properties
})

</script>

<template>
    <div>
        {{ resumeStore.required }}
        <!-- {{ resumeStore.properties }} -->

        <form v-if="resumeStore.properties">
            <fieldset v-for="{title, description, type, ...property}, key of resumeStore.properties">
                <legend class="text-xl">{{ title }}</legend>
                <label class="text-lg">{{ description }}</label>

                <div v-for="(prop, name) of property.properties">
                    <label :for="name"> {{ prop.title }} </label>
                    <legend> {{ prop.description }} </legend>
                    <input :name="name" type="text">
                </div>
            </fieldset>
        </form>
        
        <pre> {{ prettySchema }} </pre>
    </div>
</template>

<style scoped>
</style>
