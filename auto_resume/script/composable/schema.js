import { z } from 'zod'
import { ref, toValue } from 'vue';
import { useFetch } from '@vueuse/core'
import { defineStore } from 'pinia'
import { mapEntries, crush, omit, construct } from 'radash'
import { jsonSchemaToZod } from 'json-schema-to-zod'


export const useModel = (model) => {
  return defineStore(model.title, () => {
    const schema = useSchema(model)
    const validator = eval(jsonSchemaToZod(schema))
    const data = useSchemaData(schema)

    const isValid = () => {
      return validator.safeParse(toValue(data))
    }

    const getField = (name) => {
      return schema.properties[name]
    }

    return {
      schema,
      validator,
      data,
      isValid,
      getField
    }
  })
}


export const useSchema = ({ $defs, properties, type, required }) => {

  return {
    type,
    required,
    properties: mapEntries(properties, (key, value) => {

      const obj = crush(value)
      const refKey = Object.keys(obj).find(k => k.match(/\$ref/))

      if (refKey) {
        const definition = $defs[obj[refKey].split('/').at(-1)]

        if (refKey.match(/^items/)) {
          return [
            key,
            {
              ...construct(omit(obj, [refKey])),
              items: {
                ...definition
              }
            }
          ]
        }

        if (refKey.match(/^allOf/)) {
          return [
            key,
            {
              ...construct(omit(obj, [refKey])),
              ...definition
            }
          ]
        }
      }

      return [key, value]
    })
  }
}

export const useSchemaData = ({ properties }) => {
  return ref(
    mapEntries(properties, (key, value) => {
      if (value.type == 'array') {
        return [key, []]
      } else {
        return [key, {}]
      }
    })
  )
}
