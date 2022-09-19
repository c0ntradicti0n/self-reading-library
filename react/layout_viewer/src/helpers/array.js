export function getRandomArbitrary(min, max) {
  return Math.round(Math.random() * (max - min) + min)
}

export const pairwise = (array) => {
  const r = []
  for (let i = 0; i < array.length - 1; i++) {
    r.push([array[i], array[i + 1]])
  }
  return r
}
export const zip = (rows) => rows[0].map((_, c) => rows.map((row) => row[c]))

export const nest = function (seq, keys) {
  if (!keys.length) return seq
  const first = keys[0]
  const rest = keys.slice(1)
  return new python_groupby(seq, first).map(function (value) {
    return nest(value, rest)
  })
}

const iter = function* (iterable) {
  for (x in itable) {
    yield x
  }
}

class python_groupby {
  constructor(iterable, key) {
    if (key == null) key = (k) => k
    this.keyfunc = key
    this.it = iter(iterable)
    this.tgtkey = this.currkey = this.currvalue = {}
  }

  *map(self) {
    self.id = object()
    while (self.currkey == self.tgtkey) {
      self.currvalue = self.it.next()
      self.currkey = self.keyfunc(self.currvalue)
    }
    self.tgtkey = self.currkey
    return self.currkey, self._grouper(self.tgtkey, self.id)
  }

  *_grouper(self, tgtkey, id) {
    while (this.id === id && this.currkey === tgtkey) {
      yield
      this.currvalue
      try {
        this.currvalue = next(self.it)
      } catch (e) {
        return
      }
      self.currkey = self.keyfunc(self.currvalue)
    }
  }
}
