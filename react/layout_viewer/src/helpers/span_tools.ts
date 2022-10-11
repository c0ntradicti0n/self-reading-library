import assert from 'assert'

const intersectingRanges = require('intersecting-ranges')

const minDistance = 1

export function valueText(value) {
  return `${value}°C`
}

export const spans2annotation = (annotation, spans) => {
  return annotation.map(([word, tag], index) => {
    let [_tag, begin, end] = spans.find(
      ([, begin, end]) => index >= begin && index < end
    ) ?? [null, null, null, null]
    if (_tag == null) return [word, 'O']
    let prefix = ''
    if (index === begin) prefix = 'B-'
    if (index === end - 1) prefix = 'L-'
    if (index === begin && index === end - 1) prefix = 'U-'
    if (index > begin && index < end - 1) prefix = 'I-'
    return [word, prefix + _tag]
  })
}

export const annotation2spans = (annotation) => {
  let groups: [string, number, number, string[]][] = annotation.reduce(
    (acc, [w, t], i) => {
      if (acc.length === 0) return [[tagStrip(t), 0, i + 1, [w]]]
      let last = acc[acc.length - 1]
      if (last[0] === tagStrip(t))
        acc[acc.length - 1] = [tagStrip(t), last[1], i + 1, [...last[3], w]]
      else acc.push([tagStrip(t), i, i + 1, [w]])
      return acc
    },
    []
  )
  groups = groups.filter(([t]) => t.length > 2)
  return groups
}

export function adjustSpanValue(
  newValue: [number, number],
  activeThumb: number,
  _spanIndices: [string, number, number, string[]][],
  i: number,
  tag: string,
  annotation: [string, string][]
) {
  console.log(newValue, activeThumb, _spanIndices, i, tag, annotation)
  let spanIndices = [..._spanIndices]
  if (!Array.isArray(newValue)) {
    return
  }
  let value: [number, number]

  if (newValue[1] - newValue[0] < minDistance) {
    if (activeThumb === 0) {
      const clamped = Math.min(newValue[0], annotation.length - minDistance)
      value = [clamped, clamped + minDistance]
    } else {
      const clamped = Math.max(newValue[1], minDistance)
      value = [clamped - minDistance, clamped]
    }
  } else {
    value = newValue
  }

  spanIndices[i] = [
    tag,
    ...value,
    annotation.slice(value[0], value[1]).map(([w]) => w),
  ]

  if (spanIndices.length === 1) return spanIndices

  const ranges = spanIndices.map(([tag, start, end], index) => [
    start,
    end,
    { tag, index },
  ])
  const intersections_forwards = intersectingRanges(ranges, { withData: true })
  const intersections_backward = intersectingRanges(ranges.reverse(), {
    withData: true,
  })

  intersections_forwards.forEach(([i_start, i_end, data]) => {
    if (data && data.index > i) {
      const [tag, start, end, words] = spanIndices[data.index]
      spanIndices[data.index] = [
        data.tag,
        Math.max(start, i_end),
        Math.max(i_start, end),
        words,
      ]
    }
  })

  intersections_backward.forEach(([i_start, i_end, data]) => {
    if (data && data.index < i) {
      const [tag, start, end, words] = spanIndices[data.index]
      spanIndices[data.index] = [
        data.tag,
        Math.min(start, i_end),
        Math.min(i_start, end),
        words,
      ]
    }
  })

  const changedRanges = spanIndices.map(([tag, start, end], index) => [
    start,
    end,
    { tag, index },
  ])
  const checkIntersectingRanges = intersectingRanges(changedRanges, {
    withData: true,
  }).filter(([start, end]) => start - end !== 0)
  assert.ok(
    checkIntersectingRanges.length === 0,
    'Had intersections after applying intersection remedying \n' +
      'on changing ' +
      i +
      '\n' +
      JSON.stringify(checkIntersectingRanges) +
      '\n' +
      JSON.stringify(spanIndices)
  )

  console.log('changed to ', spanIndices)

  spanIndices = spanIndices.map(([tag, start, end, ws]) => [
    tag,
    start,
    end,
    annotation.slice(start, end).map(([w]) => w),
  ])
  return spanIndices
}

export const addSpan = (
  spanIndices: [string, number, number, string[]][],
  annotation
) => {
  const tagOccurrences = spanIndices.reduce((acc, e) => {
    acc[e[0]] = (acc[e[0]] || 0) + 1
    return acc
  }, {})

  let incompleteTags = [...Object.entries(tagOccurrences)].filter(
    ([, v]) => v !== 2
  )

  if (
    Object.entries(tagOccurrences).every(([, len]) => len === 2) ||
    Object.entries(tagOccurrences).length === 0
  )
    incompleteTags = [
      ['SUBJECT', 0],
      ['CONTRAST', 0],
    ]

  let newSpanIndices = spanIndices
  const averageSpanLength =
    annotation.length / (spanIndices.length + incompleteTags.length)

  incompleteTags.forEach(([k, v], i) => {
    let newSpan: [number, number] = [
      annotation.length - (incompleteTags.length - i) * averageSpanLength,
      annotation.length - (incompleteTags.length - i - 1) * averageSpanLength,
    ]
    newSpanIndices = adjustSpanValue(
      newSpan,
      0,
      newSpanIndices,
      newSpanIndices.length,
      k,
      annotation
    )
  })
  return [...newSpanIndices]
}

export function popSpan(
  spanIndices: [string, number, number, string[]][],
  i: number,
  setSpanIndices: (
    value:
      | ((
          prevState: [string, number, number, string[]][]
        ) => [string, number, number, string[]][])
      | [string, number, number, string[]][]
  ) => void
) {
  spanIndices.splice(i, 1)
  setSpanIndices([...spanIndices])
}

export const tagStrip = (t) => {
  if (t.length < 2) return ''
  return t.slice(2)
}
