import Resource from './Resource'

export default class LibraryService extends Resource<any> {
   constructor() {
      super('/library', true, true, true, true, true, false)
   }
}
