import _ from 'lodash'
import * as jp from 'jsonpath-faster'

const choice = (choices) => {
   let index = Math.floor(Math.random() * choices.length)
   return choices[index]
}

const getRandomArbitrary = (min, max) => {
   return Math.round(Math.random() * (max - min) + min)
}

const pairwise = (array) => {
   const r = []
   for (let i = 0; i < array.length - 1; i++) {
      r.push([array[i], array[i + 1]])
   }
   return r
}
const zip = (rows) => rows[0].map((_, c) => rows.map((row) => row[c]))

const swap = (json) => {
   var ret = {}
   for (var key in json) {
      ret[json[key]] = key
   }
   return ret
}

export const getUniqueBy = (arr, prop) => {
   const set = new Set()
   return arr.filter((o) => !set.has(o[prop]) && set.add(o[prop]))
}

function group(seq, key) {
   let i = undefined
   return _(seq).groupBy((item) => {
      let result
      switch (typeof key) {
         case 'string':
            result = jp.query(item, key)[0]
            break
         case 'function':
            if (key(item)) i = i === undefined ? 0 : i + 1
            result = i

            break
         default:
            throw (
               "don't know grouper type! " +
               typeof key +
               ' ' +
               JSON.stringify(key)
            )
      }
      return result
   })
}

const nest = (keys, seq) => {
   /* creates nested object based on multiple nestings by a jsonpath grouper
      https://www.npmjs.com/package/jsonpath
      */

   // reduce((accumulator, currentValue, currentIndex) => { /* … */ } , initialValue)
   const key = keys[0]
   const rest = keys.slice(1)
   if (key === undefined) return seq
   let subresult = group(seq, key)
      .map((value, key) => {
         return {
            group: key.toString(),
            value: rest ? nest(rest, value) : undefined,
            elements: value,
         }
      })
      .filter((item) => item.group)
      .value()
   return subresult
}

const iter = function* (iterable) {
   for (const x in iterable) {
      yield x
   }
}

const max = (data, f) =>
   data?.reduce(function (prev, current) {
      return f(prev, current) ? prev : current
   })

export const indexSubsequence = (seq, subseq) => {
   const starts = seq
      .map((w, i) => [w, i])
      .filter(([w, i]) => subseq[0] === w)
      .map(([w, i]) => i)
   let result
   try {
      result = max(
         starts
            .map((i) =>
               seq
                  .slice(i)
                  .filter((w, j) => w === subseq[j])
                  .map((w, k) => i + k),
            )
            .reverse(),
         (s1, s2) => s1.length > s2.length,
      )
   } catch (e) {
      result = undefined
   }
   if (!result) return undefined
   return [Math.min(...result), Math.max(...result) + 1]
}

export { nest, zip, pairwise, swap, getRandomArbitrary, iter, choice }
