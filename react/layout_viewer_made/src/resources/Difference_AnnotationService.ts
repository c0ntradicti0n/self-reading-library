import Resource from './Resource'

export default class Difference_AnnotationService extends Resource {
  constructor() {
    super('/difference_annotation', true, true, true, true, true, false)
  }
}