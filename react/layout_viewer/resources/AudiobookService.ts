import ServerResource from "./GeneralResource";

export default class AudiobookService extends ServerResource<any> {
  constructor() {
    super("/audiobook", true, true, true, true, true, false);
  }
}
