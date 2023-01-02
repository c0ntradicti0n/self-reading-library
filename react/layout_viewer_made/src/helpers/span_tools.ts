import { nest } from './array'
import _ from 'lodash'
import webpack from 'webpack'
import prefix = webpack.Template.prefix

const minDistance = 1

export function valueText(value) {
   return `${value}°C`
}

export const PRECEDENCE = {
   ASPECT: 2,
   SUBJECT: 1,
   SUBJ: 1,
   CONTRAST: 0,
}

export function sortSpans_precedence(spans) {
   const sortedSpans = spans.sort((a, b) => PRECEDENCE[b[0]] - PRECEDENCE[a[0]])
   return sortedSpans
}

export function sortSpans_position(spans) {
   const sortedSpans = spans.sort((a, b) => a[1] - b[1])
   return sortedSpans
}

export const spans2annotation = (annotation, spans) => {
   let result = annotation.map(([w]) => [w, 'O'])
   const sortedSpans = sortSpans_precedence(spans).reverse()

   sortedSpans.forEach(([_tag, begin, end, words]) => {
      _.range(Math.round(begin), Math.round(end)).forEach((index) => {
         let prefix = ''
         if (index === begin) prefix = 'B-'
         if (index === end - 1) prefix = 'L-'
         if (index === begin && index === end - 1) prefix = 'U-'
         if (index > begin && index < end - 1) prefix = 'I-'
         if (index >= result.length) {
            result[index] = ['.', 'O']
            console.warn('Spans overflow on original annotations')
         }
         if (result[index] === undefined) {
            result[index] = ['.', 'O']
            console.warn('Annotation contained undefined at', result, index)
         }
         result[index][1] = prefix + _tag
      })
   })
   return result
}

export const annotation2spans = (annotation) => {
   const value = annotation.map(([w, t], i) => [w, ...tagStrip(t), i])
   const result = nest(
      ['$..[2]', (item) => item[1] === 'B' || item[1] === 'U'],
      value,
   )
   const rawSpans = result.reduce((acc, sub) => {
      return [
         ...acc,
         ...Object.entries(sub.value).map(([group, sub]) => {
            // @ts-ignore
            return sub.value
         }),
      ]
   }, [])

   const spans = rawSpans.map((l) => {
      return [l[0][2], l[0][3], l[l.length - 1][3] + 1, l.map((a) => a[0])]
   })

   const sortedSpans = sortSpans_position(spans)

   return sortedSpans
}

export function adjustSpanValue(
   newValue: [number, number],
   activeThumb: number,
   _spanIndices: [string, number, number, string[]][],
   i: number,
   tag: string,
   annotation: [string, string][],
) {
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
   spanIndices = spanIndices.map(([tag, start, end, ws]) => [
      tag,
      start,
      end,
      annotation.slice(start, end).map(([w]) => w),
   ])

   return spanIndices //.sort((a, b) => a[1] - b[1])
}

export const addSpan = (
   spanIndices: [string, number, number, string[]][],
   annotation,
   tag = null,
) => {
   const tagOccurrences = spanIndices.reduce((acc, e) => {
      acc[e[0]] = (acc[e[0]] || 0) + 1
      return acc
   }, {})
   let incompleteTags
   if (!tag) {
      incompleteTags = [...Object.entries(tagOccurrences)].filter(
         ([, v]) => v !== 2,
      )

      if (
         Object.entries(tagOccurrences).every(([, len]) => len === 2) ||
         Object.entries(tagOccurrences).length === 0
      )
         incompleteTags = [
            ['SUBJECT', 0],
            ['CONTRAST', 0],
         ]
   } else {
      incompleteTags = [[tag, 0]]
   }

   let newSpanIndices = spanIndices
   const averageSpanLength =
      annotation.length / (spanIndices.length + incompleteTags.length)

   incompleteTags.forEach(([k, v], i) => {
      let newSpan: [number, number] = [
         annotation.length - (incompleteTags.length - i) * averageSpanLength,
         annotation.length -
            (incompleteTags.length - i - 1) * averageSpanLength,
      ]
      newSpanIndices = adjustSpanValue(
         newSpan,
         0,
         newSpanIndices,
         newSpanIndices.length,
         k,
         annotation,
      )
   })
   return [...newSpanIndices]
}

export function popSpan(
   spanIndices: [string, number, number, string[]][],
   i: number,
) {
   spanIndices.splice(i, 1)
   return [...spanIndices]
}

export const tagStrip = (t) => {
   if (t.length < 2) return [t, '']
   try {
      return [t.slice(0, 1), t.slice(2)]
   } catch (e) {
      console.trace()
      throw `No 't.slice of ${t}`
   }
}

export const tagStripFlag = (t) => {
   if (t.length < 2) return ''
   try {
      return t.slice(0, 1)
   } catch (e) {
      throw e
   }
}

const check = (errors, yes_no, msg) => (yes_no ? null : errors.push(msg))

export const validateSpans = (spans, annotation, TAG_SET) => {
   let errors = []
   check(
      errors,
      spans.length / TAG_SET.length != 1,
      `Must have multiple sets of ${JSON.stringify(
         TAG_SET,
      )} or must be without any annotation`,
   )

   check(
      errors,
      spans.length % TAG_SET.length === 0,
      `Must have length proportional to ${JSON.stringify(TAG_SET)}`,
   )
   let new_annotation = spans2annotation(annotation, spans)
   new_annotation = new_annotation.map((l) => [...l, tagStrip(l[1])])
   const split_O = nest(
      [
         (span) => {
            if (!span) return false
            try {
               return span[2][0] === 'O'
            } catch (e) {
               throw e
            }
         },
         '$..[2][1]',
      ],
      new_annotation,
   ).filter((set) => !set.elements.every((span) => span[2][0] === 'O'))

   check(
      errors,
      split_O.every((group) => group.value.find((v) => v.group === 'SUBJECT')),
      'Must have annotations split with None-Tags',
   )

   check(
      errors,
      split_O.map((tag_set) => {
         check(
            errors,
            tag_set.elements
               .map((l) => l[2][0])
               .filter((t) => ['B', 'U'].includes(t)).length === TAG_SET.length,
            `${JSON.stringify(
               tag_set.elements.map((l) => l[2][0]),
            )} does have more beginnings of tags than ${TAG_SET}`,
         )

         check(
            errors,
            tag_set.elements
               .map((l) => l[2][0])
               .filter((t) => ['L', 'U'].includes(t)).length === TAG_SET.length,
            `${JSON.stringify(
               tag_set.elements.map((l) => l[2][0]),
            )} does have more last tokens than expected ${TAG_SET}`,
         )
         return tag_set.value.length === TAG_SET
      }),
      'Must have annotations split with None-Tags',
   )

   return errors
}

export const mergeSpans = (spans, annotation) => {
   let new_annotation = spans2annotation(annotation, spans)
   new_annotation = new_annotation.map((l, i) => [...l, tagStrip(l[1]), i])
   const split_O = nest(
      [
         (span) => {
            return span[2][0] === 'O'
         },

         "$..[2][?(@ == 'SUBJECT' ||  @ == 'CONTRAST' )]",
      ],
      new_annotation,
   ).filter((set) => !set.elements.every((span) => span[2][0] === 'O'))

   const newSpans = split_O
      .map((g) =>
         g.value
            .filter((a) => a.group != 'undefined')
            .map((l) => {
               return [
                  l.group,
                  Math.min(...l.value.map((i) => i[3])),
                  Math.max(...l.value.map((i) => i[3])) + 1,
                  l.value.map((e) => e[0]),
               ]
            }),
      )
      .flat()

   return newSpans
}

export const correctPrefix = (annotation) => {
   let open = {}
   annotation.forEach(([w, pt], i) => {
      let [prefix, tag] = tagStrip(pt)
      switch (prefix) {
         case 'B':
         case 'I':
            if (!open[tag]) {
               open[tag] = true
               annotation[i] = [w, 'B-' + tag]
            }
            break
         case 'O':
            open = {}
            break
      }
   })

   return annotation
}
