import _ from 'lodash'
import * as jp from 'jsonpath-faster'

function getRandomArbitrary(min, max) {
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
          "don't know grouper type! " + typeof key + ' ' + JSON.stringify(key)
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

// https://gist.github.com/Daniel-Hug/930d5d2370bc6aab88ef
export const indexSubsequence = (seq, subseq) => {
  console.log({ seq, subseq })
  const subseqLen = subseq.length - 1
  let i = -1
  let c
  let indexes = []
  if (!subseqLen) return indexes

  while ((i = seq.indexOf(subseq[0], i + 1)) >= 0) {
    c = subseq.reduce((p, el, j) => (seq[i + j] === el ? p + 1 : p), 0)

    if (c >= subseqLen) indexes.push([i, i + subseqLen + 1])
  }
  return indexes
}

export { nest, zip, pairwise, swap, getRandomArbitrary, iter }
