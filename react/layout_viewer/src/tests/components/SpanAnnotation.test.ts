import {
  addSpan,
  adjustSpanValue,
  annotation2spans,
  mergeSpans,
  sortSpans_position,
  sortSpans_precedence,
  spans2annotation,
  tagStrip,
  validateSpans,
} from '../../helpers/span_tools'
import { nest } from '../../helpers/array'

const TAG_SET = ['SUBJECT', 'CONSTRAST']
const testAnnotation: [string, string][] = [
  ['the', 'B-SUBJECT'],
  ['lazy', 'I-SUBJECT'],
  ['yellow', 'I-SUBJECT'],
  ['socks', 'L-SUBJECT'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
  ['the', 'B-SUBJECT'],
  ['lazy', 'I-SUBJECT'],
  ['yellow', 'I-SUBJECT'],
  ['socks', 'L-SUBJECT'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
]
const testSpans = annotation2spans(testAnnotation)

const testNestAnnotation: [string, string][] = [
  ['the', 'B-CONTRAST'],
  ['lazy', 'B-SUBJECT'],
  ['yellow', 'I-SUBJECT'],
  ['socks', 'L-SUBJECT'],
  ['glued', 'I-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
  ['the', 'B-SUBJECT'],
  ['lazy', 'I-SUBJECT'],
  ['yellow', 'I-SUBJECT'],
  ['socks', 'L-SUBJECT'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
]
//const testNestSpans = annotation2spans(testNestAnnotation)

const testAnnotationNoSubj: [string, string][] = [
  ['the', 'B-SUBJECT'],
  ['lazy', 'I-SUBJECT'],
  ['yellow', 'I-SUBJECT'],
  ['socks', 'I-SUBJECT'],
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
  ['lazy', 'B-SUBJECT'],
  ['yellow', 'I-SUBJECT'],
  ['socks', 'L-SUBJECT'],
  ['glued', 'B-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
  ['the', 'B-CONTRAST'],
  ['lazy', 'B-SUBJECT'],
  ['yellow', 'I-SUBJECT'],
  ['socks', 'L-SUBJECT'],
  ['glued', 'I-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['wall', 'L-CONTRAST'],
  ['.', 'O'],
]
//const testIncludeSpans = annotation2spans(testIncludeAnnotation)

const realWorldAnnotation = [
  ['A', 'U-CONTRAST'],
  ['low', 'B-SUBJECT'],
  ['momentum', 'I-SUBJECT'],
  ['nucleon-nucleon', 'L-SUBJECT'],
  ['(NN)', 'B-CONTRAST'],
  ['potential', 'L-CONTRAST'],
  ['Vlow−k', 'U-SUBJECT'],
  ['is', 'B-CONTRAST'],
  ['derived', 'I-CONTRAST'],
  ['from', 'I-CONTRAST'],
  ['meson', 'I-CONTRAST'],
  ['exhange', 'I-CONTRAST'],
  ['potentials', 'I-CONTRAST'],
  ['by', 'I-CONTRAST'],
  ['integrating', 'I-CONTRAST'],
  ['out', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['model', 'I-CONTRAST'],
  ['dependent', 'I-CONTRAST'],
  ['high', 'I-CONTRAST'],
  ['momentum', 'I-CONTRAST'],
  ['modes', 'I-CONTRAST'],
  ['of', 'I-CONTRAST'],
  ['.', 'I-CONTRAST'],
  ['The', 'I-CONTRAST'],
  ['smooth', 'I-CONTRAST'],
  ['and', 'I-CONTRAST'],
  ['approximately', 'I-CONTRAST'],
  ['unique', 'I-CONTRAST'],
  ['Vlow−k', 'I-CONTRAST'],
  ['is', 'I-CONTRAST'],
  ['used', 'I-CONTRAST'],
  ['as', 'I-CONTRAST'],
  ['input', 'I-CONTRAST'],
  ['for', 'I-CONTRAST'],
  ['shell', 'I-CONTRAST'],
  ['model', 'I-CONTRAST'],
  ['calculations', 'I-CONTRAST'],
  ['instead', 'I-CONTRAST'],
  ['of', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['usual', 'I-CONTRAST'],
  ['Brueckner', 'I-CONTRAST'],
  ['G', 'I-CONTRAST'],
  ['matrix', 'I-CONTRAST'],
  ['.', 'I-CONTRAST'],
  ['Such', 'I-CONTRAST'],
  ['an', 'I-CONTRAST'],
  ['approach', 'I-CONTRAST'],
  ['eliminates', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['nuclear', 'I-CONTRAST'],
  ['mass', 'I-CONTRAST'],
  ['dependence', 'I-CONTRAST'],
  ['of', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['input', 'I-CONTRAST'],
  ['interaction', 'I-CONTRAST'],
  ['one', 'I-CONTRAST'],
  ['finds', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['G', 'I-CONTRAST'],
  ['matrix', 'I-CONTRAST'],
  ['approach', 'I-CONTRAST'],
  [',', 'I-CONTRAST'],
  ['allowing', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['same', 'I-CONTRAST'],
  ['input', 'I-CONTRAST'],
  ['interaction', 'I-CONTRAST'],
  ['to', 'I-CONTRAST'],
  ['be', 'I-CONTRAST'],
  ['used', 'I-CONTRAST'],
  ['in', 'I-CONTRAST'],
  ['different', 'I-CONTRAST'],
  ['nuclear', 'I-CONTRAST'],
  ['regions', 'L-CONTRAST'],
  ['.', 'O'],
  ['Shell', 'O'],
]

it('nest annotation array', () => {
  const value = testNestAnnotation.map(([w, t], i) => [w, ...tagStrip(t), i])
  const result = nest(
    ['$..[2]', (item) => item[1] === 'B' || item[1] === 'U'],
    value
  )
  console.log(result)
  expect(result).toEqual([
    {
      elements: [
        ['the', 'B', 'CONTRAST', 0],
        ['glued', 'I', 'CONTRAST', 4],
        ['on', 'I', 'CONTRAST', 5],
        ['the', 'I', 'CONTRAST', 6],
        ['wall', 'L', 'CONTRAST', 7],
        ['glued', 'B', 'CONTRAST', 13],
        ['on', 'I', 'CONTRAST', 14],
        ['the', 'I', 'CONTRAST', 15],
        ['wall', 'L', 'CONTRAST', 16],
      ],
      group: 'CONTRAST',
      value: [
        {
          elements: [
            ['the', 'B', 'CONTRAST', 0],
            ['glued', 'I', 'CONTRAST', 4],
            ['on', 'I', 'CONTRAST', 5],
            ['the', 'I', 'CONTRAST', 6],
            ['wall', 'L', 'CONTRAST', 7],
          ],
          group: '0',
          value: [
            ['the', 'B', 'CONTRAST', 0],
            ['glued', 'I', 'CONTRAST', 4],
            ['on', 'I', 'CONTRAST', 5],
            ['the', 'I', 'CONTRAST', 6],
            ['wall', 'L', 'CONTRAST', 7],
          ],
        },
        {
          elements: [
            ['glued', 'B', 'CONTRAST', 13],
            ['on', 'I', 'CONTRAST', 14],
            ['the', 'I', 'CONTRAST', 15],
            ['wall', 'L', 'CONTRAST', 16],
          ],
          group: '1',
          value: [
            ['glued', 'B', 'CONTRAST', 13],
            ['on', 'I', 'CONTRAST', 14],
            ['the', 'I', 'CONTRAST', 15],
            ['wall', 'L', 'CONTRAST', 16],
          ],
        },
      ],
    },
    {
      elements: [
        ['lazy', 'B', 'SUBJECT', 1],
        ['yellow', 'I', 'SUBJECT', 2],
        ['socks', 'L', 'SUBJECT', 3],
        ['the', 'B', 'SUBJECT', 9],
        ['lazy', 'I', 'SUBJECT', 10],
        ['yellow', 'I', 'SUBJECT', 11],
        ['socks', 'L', 'SUBJECT', 12],
      ],
      group: 'SUBJECT',
      value: [
        {
          elements: [
            ['lazy', 'B', 'SUBJECT', 1],
            ['yellow', 'I', 'SUBJECT', 2],
            ['socks', 'L', 'SUBJECT', 3],
          ],
          group: '0',
          value: [
            ['lazy', 'B', 'SUBJECT', 1],
            ['yellow', 'I', 'SUBJECT', 2],
            ['socks', 'L', 'SUBJECT', 3],
          ],
        },
        {
          elements: [
            ['the', 'B', 'SUBJECT', 9],
            ['lazy', 'I', 'SUBJECT', 10],
            ['yellow', 'I', 'SUBJECT', 11],
            ['socks', 'L', 'SUBJECT', 12],
          ],
          group: '1',
          value: [
            ['the', 'B', 'SUBJECT', 9],
            ['lazy', 'I', 'SUBJECT', 10],
            ['yellow', 'I', 'SUBJECT', 11],
            ['socks', 'L', 'SUBJECT', 12],
          ],
        },
      ],
    },
  ])
})

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
  expect(result[1]).toEqual(['CONTRAST', 6, 7, ['the', 'wall']])
})

it('adjustSpan inhere other', () => {
  const i = 1
  const result = adjustSpanValue(
    [0, 9],
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

it('nesting does not make more spans', () => {
  const result = annotation2spans(testNestAnnotation)
  console.log(result)
  expect(result).toHaveLength(4)
  expect(result).toEqual([
    ['CONTRAST', 0, 8, ['the', 'glued', 'on', 'the', 'wall']],
    ['SUBJECT', 1, 4, ['lazy', 'yellow', 'socks']],
    ['SUBJECT', 9, 13, ['the', 'lazy', 'yellow', 'socks']],
    ['CONTRAST', 13, 17, ['glued', 'on', 'the', 'wall']],
  ])
})

it('nestannotation == span2annotation(annotation2span(nestannotation))', () => {
  const result = spans2annotation(
    testNestAnnotation,
    annotation2spans(testNestAnnotation)
  )
  expect(result).toEqual(testNestAnnotation)
})

it('real world 1', () => {
  const result = spans2annotation(
    realWorldAnnotation,
    annotation2spans(realWorldAnnotation)
  )
  expect(result).toEqual(realWorldAnnotation)
})

it('real world 2', () => {
  const prevSpans = [
      ['SUBJECT', 1, 3, ['low', 'momentum', 'nucleon-nucleon']],
      ['SUBJECT', 6, 6, ['Vlow−k']],
      ['CONTRAST', 0, 1, ['A']],
      ['CONTRAST', 4, 5, ['(NN)', 'potential']],
      [
        'CONTRAST',
        7,
        63,
        [
          'is',
          'derived',
          'from',
          'meson',
          'exhange',
          'potentials',
          'by',
          'integrating',
          'out',
          'the',
          'model',
          'dependent',
          'high',
          'momentum',
          'modes',
          'of',
          '.',
          'The',
          'smooth',
          'and',
          'approximately',
          'unique',
          'Vlow−k',
          'is',
          'used',
          'as',
          'input',
          'for',
          'shell',
          'model',
          'calculations',
          'instead',
          'of',
          'the',
          'usual',
          'Brueckner',
          'G',
          'matrix',
          '.',
          'Such',
          'an',
          'approach',
          'eliminates',
          'the',
          'nuclear',
          'mass',
          'dependence',
          'of',
          'the',
          'input',
          'interaction',
          'one',
          'finds',
          'the',
          'G',
          'matrix',
          'approach',
        ],
      ],
    ],
    annotation = [
      ['A', 'U-CONTRAST'],
      ['low', 'B-SUBJECT'],
      ['momentum', 'I-SUBJECT'],
      ['nucleon-nucleon', 'L-SUBJECT'],
      ['(NN)', 'B-CONTRAST'],
      ['potential', 'L-CONTRAST'],
      ['Vlow−k', 'U-SUBJECT'],
      ['is', 'B-CONTRAST'],
      ['derived', 'I-CONTRAST'],
      ['from', 'I-CONTRAST'],
      ['meson', 'I-CONTRAST'],
      ['exhange', 'I-CONTRAST'],
      ['potentials', 'I-CONTRAST'],
      ['by', 'I-CONTRAST'],
      ['integrating', 'I-CONTRAST'],
      ['out', 'I-CONTRAST'],
      ['the', 'I-CONTRAST'],
      ['model', 'I-CONTRAST'],
      ['dependent', 'I-CONTRAST'],
      ['high', 'I-CONTRAST'],
      ['momentum', 'I-CONTRAST'],
      ['modes', 'I-CONTRAST'],
      ['of', 'I-CONTRAST'],
      ['.', 'I-CONTRAST'],
      ['The', 'I-CONTRAST'],
      ['smooth', 'I-CONTRAST'],
      ['and', 'I-CONTRAST'],
      ['approximately', 'I-CONTRAST'],
      ['unique', 'I-CONTRAST'],
      ['Vlow−k', 'I-CONTRAST'],
      ['is', 'I-CONTRAST'],
      ['used', 'I-CONTRAST'],
      ['as', 'I-CONTRAST'],
      ['input', 'I-CONTRAST'],
      ['for', 'I-CONTRAST'],
      ['shell', 'I-CONTRAST'],
      ['model', 'I-CONTRAST'],
      ['calculations', 'I-CONTRAST'],
      ['instead', 'I-CONTRAST'],
      ['of', 'I-CONTRAST'],
      ['the', 'I-CONTRAST'],
      ['usual', 'I-CONTRAST'],
      ['Brueckner', 'I-CONTRAST'],
      ['G', 'I-CONTRAST'],
      ['matrix', 'I-CONTRAST'],
      ['.', 'I-CONTRAST'],
      ['Such', 'I-CONTRAST'],
      ['an', 'I-CONTRAST'],
      ['approach', 'I-CONTRAST'],
      ['eliminates', 'I-CONTRAST'],
      ['the', 'I-CONTRAST'],
      ['nuclear', 'I-CONTRAST'],
      ['mass', 'I-CONTRAST'],
      ['dependence', 'I-CONTRAST'],
      ['of', 'I-CONTRAST'],
      ['the', 'I-CONTRAST'],
      ['input', 'I-CONTRAST'],
      ['interaction', 'I-CONTRAST'],
      ['one', 'I-CONTRAST'],
      ['finds', 'I-CONTRAST'],
      ['the', 'I-CONTRAST'],
      ['G', 'I-CONTRAST'],
      ['matrix', 'I-CONTRAST'],
      ['approach', 'L-CONTRAST'],
      [',', 'O'],
    ],
    thumb = 1,
    newValue: [number, number] = [6, 7]
  // @ts-ignore
  const res = adjustSpanValue(
    newValue,
    thumb,
    // @ts-ignore
    prevSpans,
    4,
    'SUBJECT',
    annotation
  )
  expect(res).toEqual(res)
})

it('test sort position', () => {
  const spans = [
    ['CONTRAST', 0, 0, ['A']],
    ['CONTRAST', 4, 5, ['(NN)', 'potential']],
    [
      'CONTRAST',
      7,
      76,
      [
        'is',
        'derived',
        'from',
        'meson',
        'exhange',
        'potentials',
        'by',
        'integrating',
        'out',
        'the',
        'model',
        'dependent',
        'high',
        'momentum',
        'modes',
        'of',
        '.',
        'The',
        'smooth',
        'and',
        'approximately',
        'unique',
        'Vlow−k',
        'is',
        'used',
        'as',
        'input',
        'for',
        'shell',
        'model',
        'calculations',
        'instead',
        'of',
        'the',
        'usual',
        'Brueckner',
        'G',
        'matrix',
        '.',
        'Such',
        'an',
        'approach',
        'eliminates',
        'the',
        'nuclear',
        'mass',
        'dependence',
        'of',
        'the',
        'input',
        'interaction',
        'one',
        'finds',
        'the',
        'G',
        'matrix',
        'approach',
        ',',
        'allowing',
        'the',
        'same',
        'input',
        'interaction',
        'to',
        'be',
        'used',
        'in',
        'different',
        'nuclear',
        'regions',
      ],
    ],
    ['SUBJECT', 1, 3, ['low', 'momentum', 'nucleon-nucleon']],
    ['SUBJECT', 6, 6, ['Vlow−k']],
  ]
  const position = sortSpans_position(spans)
  const precedence = sortSpans_precedence(spans)
  console.log({ position, precedence })
})

it('test validation', () => {
  const a = [
    ['the', 'B-SUBJECT'],
    ['lazy', 'I-SUBJECT'],
    ['yellow', 'I-SUBJECT'],
    ['socks', 'L-SUBJECT'],
    ['glued', 'B-CONTRAST'],
    ['on', 'I-CONTRAST'],
    ['the', 'I-CONTRAST'],
    ['wall', 'L-CONTRAST'],
    ['.', 'O'],
    ['the', 'B-SUBJECT'],
    ['lazy', 'I-SUBJECT'],
    ['yellow', 'I-SUBJECT'],
    ['socks', 'L-SUBJECT'],
    ['glued', 'B-CONTRAST'],
    ['on', 'I-CONTRAST'],
    ['the', 'I-CONTRAST'],
    ['wall', 'L-CONTRAST'],
    ['.', 'O'],
  ]

  expect(validateSpans(testSpans, a, TAG_SET)).toEqual([])
})

it('merge inhering spans with same tag', () => {
  const a = [
    ['the', 'B-CONTRAST'],
    ['lazy', 'L-CONTRAST'],
    ['yellow', 'B-SUBJECT'],
    ['socks', 'L-SUBJECT'],
    ['glued', 'B-CONTRAST'],
    ['on', 'I-CONTRAST'],
    ['the', 'I-CONTRAST'],
    ['wall', 'L-CONTRAST'],
    ['.', 'O'],
    ['the', 'B-SUBJECT'],
    ['lazy', 'I-SUBJECT'],
    ['yellow', 'I-SUBJECT'],
    ['socks', 'L-SUBJECT'],
    ['glued', 'B-CONTRAST'],
    ['on', 'I-CONTRAST'],
    ['the', 'I-CONTRAST'],
    ['wall', 'L-CONTRAST'],
    ['.', 'O'],
  ]
  const spans = annotation2spans(a)

  const result = mergeSpans(spans, a)

  const corrected = spans2annotation(a, result)
  expect(corrected).toEqual([
    ['the', 'B-CONTRAST'],
    ['lazy', 'I-CONTRAST'],
    ['yellow', 'B-SUBJECT'],
    ['socks', 'L-SUBJECT'],
    ['glued', 'I-CONTRAST'],
    ['on', 'I-CONTRAST'],
    ['the', 'I-CONTRAST'],
    ['wall', 'L-CONTRAST'],
    ['.', 'O'],
    ['the', 'B-SUBJECT'],
    ['lazy', 'I-SUBJECT'],
    ['yellow', 'I-SUBJECT'],
    ['socks', 'L-SUBJECT'],
    ['glued', 'B-CONTRAST'],
    ['on', 'I-CONTRAST'],
    ['the', 'I-CONTRAST'],
    ['wall', 'L-CONTRAST'],
    ['.', 'O'],
  ])
})

const x = [
  ['is', 'B-CONTRAST'],
  ['a', 'I-CONTRAST'],
  ['multi-paradigm', 'I-CONTRAST'],
  [',', 'I-CONTRAST'],
  ['imperative', 'I-CONTRAST'],
  ['and', 'I-CONTRAST'],
  ['functional', 'I-CONTRAST'],
  ['programming', 'I-CONTRAST'],
  ['language', 'I-CONTRAST'],
  ['based', 'I-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['object-oriented', 'I-CONTRAST'],
  ['programming', 'I-CONTRAST'],
  ['.', 'I-CONTRAST'],
  ['It', 'I-CONTRAST'],
  ['adheres', 'I-CONTRAST'],
  ['to', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['idea', 'I-CONTRAST'],
  ['that', 'I-CONTRAST'],
  ['if', 'I-CONTRAST'],
  ['a', 'I-CONTRAST'],
  ['language', 'L-CONTRAST'],
  ['behaves', 'I-CONTRAST'],
  ['a', 'I-CONTRAST'],
  ['certain', 'I-CONTRAST'],
  ['way', 'I-CONTRAST'],
  ['in', 'I-CONTRAST'],
  ['some', 'I-CONTRAST'],
  ['contexts', 'I-CONTRAST'],
  [',', 'I-CONTRAST'],
  ['it', 'I-CONTRAST'],
  ['should', 'I-CONTRAST'],
  ['ideally', 'B-CONTRAST'],
  ['work', 'I-CONTRAST'],
  ['similarly', 'I-CONTRAST'],
  ['in', 'I-CONTRAST'],
  ['all', 'I-CONTRAST'],
  ['contexts', 'I-CONTRAST'],
  ['.', 'I-CONTRAST'],
  ['However', 'I-CONTRAST'],
  [',', 'I-CONTRAST'],
  ['it', 'I-CONTRAST'],
  ['’s', 'I-CONTRAST'],
  ['not', 'I-CONTRAST'],
  ['a', 'I-CONTRAST'],
  ['pure', 'I-CONTRAST'],
  ['OOP', 'I-CONTRAST'],
  ['language', 'I-CONTRAST'],
  ['which', 'I-CONTRAST'],
  ['does', 'I-CONTRAST'],
  ['not', 'I-CONTRAST'],
  ['support', 'I-CONTRAST'],
  ['strong', 'I-CONTRAST'],
  ['encapsulation', 'I-CONTRAST'],
  [',', 'I-CONTRAST'],
  ['which', 'I-CONTRAST'],
  ['is', 'I-CONTRAST'],
  ['one', 'I-CONTRAST'],
  ['of', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['major', 'I-CONTRAST'],
  ['principles', 'I-CONTRAST'],
  ['of', 'I-CONTRAST'],
  ['OOP', 'I-CONTRAST'],
  ['.', 'I-CONTRAST'],
  ['Go', 'I-CONTRAST'],
  [',', 'I-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['the', 'I-CONTRAST'],
  ['other', 'I-CONTRAST'],
  ['hand', 'I-CONTRAST'],
  [',', 'I-CONTRAST'],
  ['is', 'I-CONTRAST'],
  ['a', 'I-CONTRAST'],
  ['procedural', 'I-CONTRAST'],
  ['programming', 'I-CONTRAST'],
  ['language', 'I-CONTRAST'],
  ['based', 'I-CONTRAST'],
  ['on', 'I-CONTRAST'],
  ['concurrent', 'I-CONTRAST'],
  ['programming', 'I-CONTRAST'],
  ['paradigm', 'I-CONTRAST'],
  ['that', 'I-CONTRAST'],
  ['bears', 'I-CONTRAST'],
  ['a', 'I-CONTRAST'],
  ['surface', 'I-CONTRAST'],
  ['similarity', 'I-CONTRAST'],
  ['to', 'I-CONTRAST'],
  ['C', 'I-CONTRAST'],
  ['.', 'I-CONTRAST'],
  ['In', 'I-CONTRAST'],
  ['fact', 'I-CONTRAST'],
  [',', 'I-CONTRAST'],
  ['Go', 'I-CONTRAST'],
  ['is', 'I-CONTRAST'],
  ['more', 'I-CONTRAST'],
  ['like', 'I-CONTRAST'],
  ['an', 'I-CONTRAST'],
  ['updated', 'I-CONTRAST'],
  ['version', 'I-CONTRAST'],
  ['of', 'L-CONTRAST'],
  ['C', 'O'],
  ['.', 'O'],
]
const y = [
  [
    'SUBJECT',
    5,
    25,
    [
      'and',
      'functional',
      'programming',
      'language',
      'based',
      'on',
      'object-oriented',
      'programming',
      '.',
      'It',
      'adheres',
      'to',
      'the',
      'idea',
      'that',
      'if',
      'a',
      'language',
      'behaves',
      'a',
      'certain',
    ],
  ],
  [
    'SUBJECT',
    69,
    104,
    [
      'the',
      'other',
      'hand',
      ',',
      'is',
      'a',
      'procedural',
      'programming',
      'language',
      'based',
      'on',
      'concurrent',
      'programming',
      'paradigm',
      'that',
      'bears',
      'a',
      'surface',
      'similarity',
      'to',
      'C',
      '.',
      'In',
      'fact',
      ',',
      'Go',
      'is',
      'more',
      'like',
      'an',
      'updated',
      'version',
      'of',
      'C',
      '.',
    ],
  ],
  [
    'CONTRAST',
    0,
    32,
    [
      'is',
      'a',
      'multi-paradigm',
      ',',
      'imperative',
      'and',
      'functional',
      'programming',
      'language',
      'based',
      'on',
      'object-oriented',
      'programming',
      '.',
      'It',
      'adheres',
      'to',
      'the',
      'idea',
      'that',
      'if',
      'a',
      'language',
      'behaves',
      'a',
      'certain',
      'way',
      'in',
      'some',
      'contexts',
      ',',
      'it',
      'should',
    ],
  ],
  [
    'CONTRAST',
    35,
    101,
    [
      'similarly',
      'in',
      'all',
      'contexts',
      '.',
      'However',
      ',',
      'it',
      '’s',
      'not',
      'a',
      'pure',
      'OOP',
      'language',
      'which',
      'does',
      'not',
      'support',
      'strong',
      'encapsulation',
      ',',
      'which',
      'is',
      'one',
      'of',
      'the',
      'major',
      'principles',
      'of',
      'OOP',
      '.',
      'Go',
      ',',
      'on',
      'the',
      'other',
      'hand',
      ',',
      'is',
      'a',
      'procedural',
      'programming',
      'language',
      'based',
      'on',
      'concurrent',
      'programming',
      'paradigm',
      'that',
      'bears',
      'a',
      'surface',
      'similarity',
      'to',
      'C',
      '.',
      'In',
      'fact',
      ',',
      'Go',
      'is',
      'more',
      'like',
      'an',
      'updated',
      'version',
      'of',
    ],
  ],
]
it('test validation real world', () => {
  const sanitized = mergeSpans(y, x)
  expect(validateSpans(x, sanitized, TAG_SET)).toEqual([])
})
