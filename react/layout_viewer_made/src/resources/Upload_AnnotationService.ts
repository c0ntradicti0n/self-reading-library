import Resource from './Resource'

export default class Upload_AnnotationService extends Resource<any> {
   constructor() {
      super('/upload_annotation', true, true, true, true, true, true)
   }
}
