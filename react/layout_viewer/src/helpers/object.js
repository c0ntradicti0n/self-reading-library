export function objectMap(o, f) {
  return Object.keys(object).reduce(function (result, key) {
    result[key] = f(o[key])
    return result
  }, {})
}
