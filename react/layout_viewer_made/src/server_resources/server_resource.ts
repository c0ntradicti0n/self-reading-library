import { AppSettings } from '../../config/connection'

export class ServerResource<T> {
   private fetch_allowed: any
   private upload_allowed: any
   private correct_allowed: any
   private read_allowed: boolean
   private delete_allowed: boolean

   constructor(
      fetch_allowed = true,
      read_allowed = true,
      upload_allowed = true,
      correct_allowed = true,
      delete_allowed = true,
   ) {
      this.fetch_allowed = fetch_allowed
      this.read_allowed = read_allowed
      this.correct_allowed = correct_allowed
      this.delete_allowed = delete_allowed
   }

   request = async (method: String, url = '', data = {}) => {
      // Default options are marked with *
      const response = await fetch(AppSettings.BACKEND_HOST + url, {
         method: method.toUpperCase(),
         mode: 'no-cors', // no-cors, *cors, same-origin
         cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
         credentials: 'same-origin', // include, *same-origin, omit
         headers: {
            'Content-Type': 'application/json',
         },
         redirect: 'follow', // manual, *follow, error
         referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
         body: JSON.stringify(data),
      })
      return response.json() // parses JSON response into native JavaScript objects
   }

   read = async (url = '', data = {}, id) => {
      if (this.fetch_allowed) {
         return this.request('get', (data = id))
      }
   }

   // @ts-ignore
   upload = async (url = '', data: T) => {
      if (this.upload_allowed) {
         return this.request('put', url, (data = data))
      }
   }
   // @ts-ignore
   correct = async (url = '', data: T, id: String) => {
      if (this.correct_allowed) {
         return this.request('patch', url, (data = data))
      }
   }

   // @ts-ignore

   hide = async (url = '', data = {}) => {
      if (this.delete_allowed) {
         return this.request('delete', url, (data = data))
      }
   }
}
