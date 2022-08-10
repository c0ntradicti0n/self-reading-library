import { AppSettings } from "../config/connection";
import { getRandomArbitrary } from "../../layout_viewer/src/util/array";

const cyrb53 = function (str, seed = 0) {
  let h1 = 0xdeadbeef ^ seed,
    h2 = 0x41c6ce57 ^ seed;
  for (let i = 0, ch; i < str.length; i++) {
    ch = str.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 =
    Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^
    Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 =
    Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^
    Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return 4294967296 * (2097151 & h2) + (h1 >>> 0);
};

export default class ServerResource<T> {
  fetch_allowed: Boolean;
  read_allowed: Boolean;
  correct_allowed: Boolean;
  private route: string;
  delete_allowed: Boolean;
  upload_allowed: Boolean;

  id: string = "";

  constructor(
    route: string,
    fetch_allowed = true,
    read_allowed = true,
    upload_allowed = true,
    correct_allowed = true,
    delete_allowed = true,
    add_id = false
  ) {
    this.route = route;
    this.fetch_allowed = fetch_allowed;
    this.correct_allowed = fetch_allowed;
    this.read_allowed = read_allowed;
    this.correct_allowed = correct_allowed;
    this.upload_allowed = upload_allowed;
    this.delete_allowed = delete_allowed;

    if (add_id) {
      let id;

      if (typeof window !== "undefined") {
        if (!localStorage.getItem(route)) {
          id = getRandomArbitrary(100000, 999999).toString();
          localStorage.setItem(route, id);
        } else {
          id = localStorage.getItem(route);
        }
        console.log(
          localStorage,
          route,
          localStorage.getItem(route),
          new window.URLSearchParams(window.location.search).get("id")
        );

        // @ts-ignore
        this.id =
          "/" +
          id +
          "_" +
          cyrb53(new window.URLSearchParams(window.location.search).get("id"));
      }
    }
  }

  request = async (
    method: String,
    data = {},
    callback: Function,
    is_file = false
  ) => {
    // Default options are marked with *
    console.log("URL", AppSettings.BACKEND_HOST + this.route + this.id);

    let querystring = "";
    if (typeof window !== "undefined") {
      querystring = window?.location.search.substring(1);
      console.log(querystring);
    }

    var fetch_init = {
      method: method.toUpperCase(),
      headers: {
        ...(!is_file ? { "Content-Type": "application/json" } : {}),
        "API-Key": "secret",
        origin: "localhost",
        "Accept-Encoding": "gzip",
      },
      body: !is_file ? JSON.stringify(data) : data,
    };
    if (method === "get") {
      delete fetch_init.body;
    }

    console.log(fetch_init);

    try {
      const response = await fetch(
        // @ts-ignore
        AppSettings.BACKEND_HOST +
          this.route +
          this.id +
          (querystring ? "?" + querystring : ""),
        fetch_init
      );

      if (!response.ok) {
        throw response.statusText;
      }

      let result = null;
      try {
        result = await response.json();
        console.log({ result });
      } catch (e) {
        console.log("Did not get a json back", e, result);
        result = null;
      }

      try {
        return callback(result);
      } catch (e) {
        console.log("No callback given?", e, callback);
        console.trace();
      }
    } catch (e) {
      console.error(e);
    }
  };

  exists = async (id, callback: Function) => {
    console.log("Fetch all resources");
    if (this.fetch_allowed) {
      return this.request("get", undefined, callback);
    }
  };

  fetch_one = async (id, callback: Function) => {
    if (this.fetch_allowed) {
      return this.request("post", id, callback);
    }
  };

  fetch_all = async (callback) => {
    console.log("Fetch all resources");
    if (this.fetch_allowed) {
      return this.request("get", undefined, callback);
    }
  };

  // @ts-ignore
  ok = async (id, url = "", data = {}, callback) => {
    if (this.read_allowed) {
      await this.request("post", id, callback);
    }
  };
  // @ts-ignore
  change = async (json_path, value, callback) => {
    if (this.upload_allowed) {
      await this.request("put", [json_path, value], callback);
    }
  };

  // @ts-ignore
  save = async (id, data = {}, callback) => {
    console.log("save", id, data);
    if (this.upload_allowed) {
      await this.request("put", [id, data], callback);
    }
  };

  // @ts-ignore
  upload = async (form_data, callback) => {
    console.log("UPLOADING", form_data, this.upload_allowed);
    if (this.upload_allowed) {
      console.log(new FormData(form_data), new FormData(form_data).get("file"));
      await this.request("patch", new FormData(form_data), callback, true);
    }
  };
}
