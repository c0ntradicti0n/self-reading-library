import {AppSettings} from "../config/connection";

export default class ServerResource <T> {
    fetch_allowed: Boolean
    read_allowed: Boolean
    correct_allowed: Boolean
    private route: string;
    delete_allowed: Boolean
    upload_allowed: Boolean

    constructor (
         route : string,
         fetch_allowed = true,
         read_allowed = true,
         upload_allowed = true,
         correct_allowed = true,
         delete_allowed = true) {
        this.route = route;
        this.fetch_allowed = fetch_allowed
        this.correct_allowed = fetch_allowed
        this.read_allowed = read_allowed
        this.correct_allowed = correct_allowed
        this.upload_allowed = upload_allowed
        this.delete_allowed = delete_allowed
    }




    async request (method : String, data = {}, callback: Function) {
      // Default options are marked with *
        console.log("URL", AppSettings.SAUSSAGEPOINT + this.route, callback)

        var fetch_init = {
            method: method.toUpperCase(),
            mode: 'cors', // no-cors, *cors, same-origin
            //cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                'Content-Type': 'application/json'
                // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            //redirect: 'follow', // manual, *follow, error
            //referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: JSON.stringify(data)
        }
        if (method === "get")  {
            delete fetch_init.body
        }
        const response = await fetch(
            AppSettings.SAUSSAGEPOINT + this.route, fetch_init )
            .then(response => {
                if (!response.ok) {
                    throw new Error(response.statusText)
                }
                return callback(response.json())
            })

        return 1
    }

    async fetch_one(url = '', data) {
        if (this.fetch_allowed) {
            return this.request("get", data)
        }
    }

    async fetch_all(callback) {
        console.log("FETCH ALL", this.fetch_allowed, callback)
        if (this.fetch_allowed) {
            return this.request("get", undefined, callback)
        }
    }

    /*

    async read(id , url = '', data = {}) {
            if (this.read_allowed) {
            this.request(method="post", data = id)
        }
    }
    async upload(url = '', data : T) {
        if (this.upload_allowed) {
            this.request(method="put", data = data)
        }
    }

    async correct(url = '', data : T, id : String) {
        if (this.correct_allowed) {
            this.request(method="patch", data = data, id=id)
        }
    }
    async hide(url = '', data = {}) {
        if (this.delete_allowed) {
            this.request(method="delete", data = data)
        }
    }*/

}
