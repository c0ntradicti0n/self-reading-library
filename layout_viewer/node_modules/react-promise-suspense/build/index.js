"use strict";
var __values = (this && this.__values) || function (o) {
    var m = typeof Symbol === "function" && o[Symbol.iterator], i = 0;
    if (m) return m.call(o);
    return {
        next: function () {
            if (o && i >= o.length) o = void 0;
            return { value: o && o[i++], done: !o };
        }
    };
};
var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
var __spread = (this && this.__spread) || function () {
    for (var ar = [], i = 0; i < arguments.length; i++) ar = ar.concat(__read(arguments[i]));
    return ar;
};
var deepEqual = require('fast-deep-equal');
var promiseCaches = [];
var usePromise = function (promise, inputs, lifespan) {
    if (lifespan === void 0) { lifespan = 0; }
    var e_1, _a;
    try {
        for (var promiseCaches_1 = __values(promiseCaches), promiseCaches_1_1 = promiseCaches_1.next(); !promiseCaches_1_1.done; promiseCaches_1_1 = promiseCaches_1.next()) {
            var promiseCache_1 = promiseCaches_1_1.value;
            if (deepEqual(inputs, promiseCache_1.inputs)) {
                if (Object.prototype.hasOwnProperty.call(promiseCache_1, 'error')) {
                    throw promiseCache_1.error;
                }
                if (Object.prototype.hasOwnProperty.call(promiseCache_1, 'response')) {
                    return promiseCache_1.response;
                }
                throw promiseCache_1.promise;
            }
        }
    }
    catch (e_1_1) { e_1 = { error: e_1_1 }; }
    finally {
        try {
            if (promiseCaches_1_1 && !promiseCaches_1_1.done && (_a = promiseCaches_1.return)) _a.call(promiseCaches_1);
        }
        finally { if (e_1) throw e_1.error; }
    }
    var promiseCache = {
        promise: promise.apply(void 0, __spread(inputs)).then(function (response) {
            promiseCache.response = response;
        })
            .catch(function (e) {
            promiseCache.error = e;
        })
            .then(function () {
            if (lifespan > 0) {
                setTimeout(function () {
                    var index = promiseCaches.indexOf(promiseCache);
                    if (index !== -1) {
                        promiseCaches.splice(index, 1);
                    }
                }, lifespan);
            }
        }),
        inputs: inputs,
    };
    promiseCaches.push(promiseCache);
    throw promiseCache.promise;
};
module.exports = usePromise;
