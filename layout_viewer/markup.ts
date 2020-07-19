

class Markup {
    
    async function request (method : String, url = '', data = {}) {
      // Default options are marked with *
        const response = await fetch(url, {
            method: method'.toUpperCase(),
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
              'Content-Type': 'application/json'
              // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: JSON.stringify(data)
        })
      return response.json(); // parses JSON response into native JavaScript objects
    }
    
    async function fetch(url = '', data = {}) {
        if (this.upload_allowed) {
            this.request(method="get", data = id)
        }
    }
    
    async function read(id , url = '', data = {}) {
            if (this.upload_allowed) {
            this.request(method="post", data = id)
        }
    }
    async function upload(url = '', data :  Markup) {
        if (this.upload_allowed) {
            this.request(method="put", data = data)
        }
    }
    
    async function correct(url = '', data = {}) {
    async function hide(url = '', data = {}) {

}

