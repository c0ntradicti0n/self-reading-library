import Resource from './Resource'

export default class AudiobookService extends Resource<any> {
  constructor() {
    super('/audiobook', true, true, true, true, true, false)
  }
}
