import Resource from './Resource'

export default class AntService extends Resource<any> {
   constructor() {
      super('/ant', true, true, true, true, true, false)
   }
}
