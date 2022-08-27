import ServerResource from './GeneralResource'

export default class Difference_AnnotationService extends ServerResource<any> {
  constructor() {
    super('/difference_annotation', true, true, true, true, true, false)
  }
}
