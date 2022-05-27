import {AppSettings} from "../config/connection";
import {getRandomArbitrary} from "../../layout_viewer/src/util/array";

export default class ServerResource<T> {
    fetch_allowed: Boolean
    read_allowed: Boolean
    correct_allowed: Boolean
    private route: string;
    delete_allowed: Boolean
    upload_allowed: Boolean

    id: string = ""

    constructor(
        route: string,
        fetch_allowed = true,
        read_allowed = true,
        upload_allowed = true,
        correct_allowed = true,
        delete_allowed = true,
        add_id = false) {
        this.route = route;
        this.fetch_allowed = fetch_allowed
        this.correct_allowed = fetch_allowed
        this.read_allowed = read_allowed
        this.correct_allowed = correct_allowed
        this.upload_allowed = upload_allowed
        this.delete_allowed = delete_allowed

        if (add_id) {
            let id

            if (typeof window !== "undefined") {

                if (!localStorage.getItem(route)) {
                    id = getRandomArbitrary(100000, 999999).toString()
                    localStorage.setItem(route, id)
                } else {
                    id = localStorage.getItem(route)
                }
                console.log(localStorage, route, localStorage.getItem(route))


                this.id = "/" + id
            }
        }
    }

    request = async (method: String, data = {}, callback: Function, is_file = false) => {
        // Default options are marked with *
        console.log("URL", AppSettings.SAUSSAGEPOINT + this.route + this.id, callback)

        var fetch_init = {
            method: method.toUpperCase(),
            mode: 'cors', // no-cors, *cors, same-origin
            //cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                ...(!is_file ? {'Content-Type': 'application/json'} : {}),
                'API-Key': 'secret',
                //'Cache-Control': 'no-cache'
            },

            //redirect: 'follow', // manual, *follow, error
            //referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: !is_file ? JSON.stringify(data) : data
        }
        if (method === "get") {
            delete fetch_init.body
        }

        console.log(fetch_init)

        try {
            const response = await fetch(
                // @ts-ignore
                AppSettings.SAUSSAGEPOINT + this.route + this.id, fetch_init)


            if (!response.ok) {
                throw response.statusText
            }

            let result = null
            try {
                result = await response.json()
                console.log({result})

            } catch (e) {
                console.log("Did not get a json back")
                result = null
            }

            try {
                return callback(result)
            } catch (e) {
                console.log("no callback given")
            }
        } catch (e) {
            console.error(e)
        }

    }

    fetch_one = async (id, callback: Function) => {
        if (this.fetch_allowed) {
            return this.request("post", id, callback)
        }
    }

    fetch_all = async (callback) => {
        console.log("FETCH ALL", this.fetch_allowed, callback)
        if (this.fetch_allowed) {
            console.log("fetching")
            return this.request("get", undefined, callback)
        }
    }


    // @ts-ignore
    ok = async (id, url = '', data = {}, callback) => {
        if (this.read_allowed) {
            this.request("post", id, callback)
        }
    }
    // @ts-ignore
    change = async (json_path, value, callback) => {
        if (this.upload_allowed) {
            this.request("put", [json_path, value], callback)
        }
    }

    // @ts-ignore
    upload = async (form_data, callback) => {
        console.log("UPLOADING", form_data, this.upload_allowed)
        if (this.upload_allowed) {
            console.log(new FormData(form_data), new FormData(form_data).get("file"))
            await this.request("patch", new FormData(form_data), callback, true)
        }
    }
    /*
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
