
class ServerResource <T> {
    constructor (
         fetch_allowed = true, 
         read_allowed = true, 
         upload_allowed = true,
         correct_allowed = true,
         delete_allowed = true) {
         correct = fetch_allowed
         read_allowed = read_allowed
         correct_allowed = correct_allowed
         delete_allowed = delete_allowed
         
         
    }
    
    async function request (method : String, url = '', data = {}) {
      // Default options are marked with *
        const response = await fetch(url, {
            method: method.toUpperCase(),
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
              'Content-Type': 'application/json'
            },
            redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: JSON.stringify(data)
        })
      return response.json(); // parses JSON response into native JavaScript objects
    }
    
    async function read(url = '', data = {}) {
        if (this.fetch_allowed) {
            return this.request(method="get", data = id)
        }
    }
    

    async function upload(url = '', data : T) {
        if (this.upload_allowed) {
            this.request(method="put", data = data)
        }
    }
    
    async function correct(url = '', data : T, id : String) {
        if (this.correct_allowed) {
            this.request(method="patch", data = data, id=id)
        }
    }
    async function hide(url = '', data = {}) {
        if (this.delete_allowed) {
            this.request(method="delete", data = data)
        }
    }

}
