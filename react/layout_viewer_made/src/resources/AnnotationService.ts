import Resource from './Resource'

export default class AnnotationService extends Resource<any> {
   constructor() {
      super('/annotation', true, true, true, true, true, true)
   }
}
