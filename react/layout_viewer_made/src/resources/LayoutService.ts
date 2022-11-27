import Resource from './Resource'

export default class LayoutService extends Resource<any> {
   constructor() {
      super('/layout', true, true, true, true, true, false)
   }
}
