import _ from 'lodash'
import { NORMAL, Slot } from '../contexts/SLOTS'
import { BACKEND_HOST } from '../../config/connection'

const cyrb53 = function (str, seed = 0) {
   if (!str) return null
   let h1 = 0xdeadbeef ^ seed
   let h2 = 0x41c6ce57 ^ seed
   for (let i = 0, ch; i < str.length; i++) {
      ch = str.charCodeAt(i)
      h1 = Math.imul(h1 ^ ch, 2654435761)
      h2 = Math.imul(h2 ^ ch, 1597334677)
   }
   h1 =
      Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^
      Math.imul(h2 ^ (h2 >>> 13), 3266489909)
   h2 =
      Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^
      Math.imul(h1 ^ (h1 >>> 13), 3266489909)
   return 4294967296 * (2097151 & h2) + (h1 >>> 0)
}

export default class Resource {
   get_allowed: Boolean
   read_allowed: Boolean
   correct_allowed: Boolean
   private readonly route: string
   delete_allowed: Boolean
   upload_allowed: Boolean

   slot: Slot

   constructor(
      route: string,
      get_allowed = true,
      read_allowed = true,
      upload_allowed = true,
      correct_allowed = true,
      delete_allowed = true,
   ) {
      this.route = route
      this.get_allowed = get_allowed
      this.correct_allowed = get_allowed
      this.read_allowed = read_allowed
      this.correct_allowed = correct_allowed
      this.upload_allowed = upload_allowed
      this.delete_allowed = delete_allowed
   }

   setSlot = (slot) => (this.slot = slot)

   request = async (
      method: String,
      data = {},
      callback: Function,
      params = {},
      is_file = false,
      query: string = null,
   ) => {
      let querystring = new URLSearchParams(params).toString()
      if (this.slot === NORMAL) {
         if (query) {
            querystring = query
         } else if (typeof window !== 'undefined') {
            const add_query = window?.location.search.substring(1)
            if (querystring) querystring = add_query + '&' + querystring
            else querystring = window?.location.search.substring(1)
         }
      }

      const fetch_init: RequestInit = {
         method: method.toUpperCase(),
         headers: {
            ...(!is_file ? { 'Content-Type': 'application/json' } : {}),
            'API-Key': 'secret',
            origin: 'localhost',
            'Accept-Encoding': 'gzip',
         },
         body: (!is_file ? JSON.stringify(data) : data) as BodyInit,
      }
      if (method === 'get') {
         delete fetch_init.body
      }

      const request_query =
         BACKEND_HOST + this.route + (querystring ? '?' + querystring : '')

      try {
         const response = await fetch(request_query, fetch_init)

         if (response.status === 503) {
            _.debounce(
               () =>
                  this.request(method, data, callback, params, is_file, query),
               7000,
            )()
            return
         }

         if (!response.ok) {
            throw response.statusText
         }

         let result = null
         try {
            if (response.status == 204) result = null
            else result = await response.json()
         } catch (e) {
            console.error('Did not get a json back', e, result)
            result = null
         }

         try {
            return callback(result)
         } catch (e) {
            console.error('returning result', e, callback, result)

            return result
         }
      } catch (e) {
         console.error(e)
      }
   }

   exists = async (id, callback: Function) => {
      if (this.get_allowed) {
         return await this.request('get', undefined, callback, 'id=' + id)
      }
   }

   getOne = async (id, callback: Function, params) => {
      if (this.get_allowed) {
         return await this.request('get', id, callback, params)
      }
   }

   get = async (callback, query = {}) => {
      if (this.get_allowed) {
         return await this.request('get', undefined, callback, query)
      }
   }

   ok = async (id, url = '', data = {}, callback, params) => {
      if (this.read_allowed) {
         await this.request('post', id, callback, params)
      }
   }

   change = async (json_path, value, callback, params) => {
      if (this.upload_allowed) {
         return await this.request('put', [json_path, value], callback, params)
      }
   }

   save = async (id, data = {}, callback, params) => {
      if (this.upload_allowed) {
         return await this.request('post', [id, data], callback, params)
      }
   }

   cancel = async (id, data = {}, callback, params) => {
      if (this.upload_allowed) {
         return await this.request('delete', [id, data], callback, params)
      }
   }

   upload = async (form_data: HTMLFormElement, callback: Function) => {
      if (this.upload_allowed) {
         console.debug(
            new FormData(form_data),
            new FormData(form_data).get('file'),
         )
         return await this.request(
            'patch',
            new FormData(form_data),
            callback,
            true,
         )
      }
   }
}
