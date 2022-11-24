
import Resource from './Resource'


export default class DifferenceService extends Resource<any> {
    constructor () {
        super(
         '/difference', 
         true, 
         true, 
         true,
         true,
         true,
         true
        )
    }
}

