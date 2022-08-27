import {
  addSpan,
  adjustSpanValue,
  annotation2spans,
  spans2annotation,
} from '../../helpers/span_tools'

const testAnnotation: [string, string][] = [
  ['the', 'B-SUBJ'],
  ['lazy', 'I-SUBJ'],
  ['yellow', 'I-SUBJ'],
  ['socks', 'L-SUBJ'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
  ['the', 'B-SUBJ'],
  ['lazy', 'I-SUBJ'],
  ['yellow', 'I-SUBJ'],
  ['socks', 'L-SUBJ'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
]
const testSpans = annotation2spans(testAnnotation)

const testAnnotationNoSubj: [string, string][] = [
  ['the', 'B-SUBJ'],
  ['lazy', 'I-SUBJ'],
  ['yellow', 'I-SUBJ'],
  ['socks', 'I-SUBJ'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
  ['lazy', 'O'],
  ['yellow', 'O'],
  ['socks', 'O'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', ''],
]
const testSpansNoSubj = annotation2spans(testAnnotationNoSubj)

const testIncludeAnnotation: [string, string][] = [
  ['the', 'O'],
  ['lazy', 'B-SUBJ'],
  ['yellow', 'I-SUBJ'],
  ['socks', 'L-SUBJ'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
  ['the', 'B-CONTRAST'],
  ['lazy', 'B-SUBJ'],
  ['yellow', 'I-SUBJ'],
  ['socks', 'L-SUBJ'],
  ['glued', 'I-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
]
const testIncludeSpans = annotation2spans(testIncludeAnnotation)
console.log(testSpans)

it('adjustSpan simple', () => {
  const i = 2
  const result = adjustSpanValue(
    [7, 10],
    1,
    testSpans,
    i,
    'SUBJECT',
    testAnnotation
  )
  console.log(result)
  expect(result[i]).toEqual(['SUBJECT', 7, 10, ['wall', '.', 'the']])
})

it('adjustSpan also second', () => {
  const i = 0
  const result = adjustSpanValue(
    [0, 5],
    1,
    testSpans,
    i,
    'SUBJECT',
    testAnnotation
  )
  console.log(result)
  expect(result[i]).toEqual([
    'SUBJECT',
    0,
    5,
    ['the', 'lazy', 'yellow', 'socks', 'glued'],
  ])
  expect(result[1]).toEqual(['CONTRAST', 5, 8, ['on', 'the', 'wall']])
})

it('adjustSpan include', () => {
  const i = 1
  const result = adjustSpanValue(
    [0, 8],
    0,
    testSpans,
    i,
    'SUBJECT',
    testAnnotation
  )
  console.log(result)

  expect(result[0]).toEqual(['SUBJECT', 1, 5, ['on', 'the', 'wall']])
  expect(result[i]).toEqual(['CONTRAST', 0, 8, ['on', 'the', 'wall']])
})

it('annotation == span2annotation(annotation2span(annotation))', () => {
  const result = spans2annotation(
    testAnnotation,
    annotation2spans(testAnnotation)
  )
  expect(result).toEqual(testAnnotation)
})

it('addSpan both', () => {
  const result = addSpan(testSpans, testAnnotation)
  expect(result).toHaveLength(6)
})

it('addSpan both when zero', () => {
  const result = addSpan([], testAnnotation)
  expect(result).toHaveLength(2)
  const result2 = addSpan(result, testAnnotation)
  expect(result2).toHaveLength(4)
})

it('addSpan no Subj', () => {
  const result = addSpan(testSpansNoSubj, testAnnotationNoSubj)
  expect(result).toHaveLength(4)
})
