
import Resource from './Resource'


export default class ConfigService extends Resource<any> {
    constructor () {
        super(
         '/config', 
         true, 
         true, 
         true,
         true,
         true,
         false
        )
    }
}

