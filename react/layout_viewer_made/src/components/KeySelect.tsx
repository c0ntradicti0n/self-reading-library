import React, { useCallback, useEffect } from 'react'
import { zip } from '../helpers/array'

export const KeySelect = ({
   set,
   onSelect,
   row,
   hints,
}: {
   set: string[]
   onSelect: (string) => void
   row: boolean
   hints: { [key: string]: { ariaDescription: string; ariaMultiline: string } }
}) => {
   const KEYS = set.map((key) => 'Key' + key[0])

   const KEY_TRANSLATE = zip([KEYS, set]).reduce(
      (acc, [key, tag]) => ({ ...acc, [key]: tag }),
      {},
   )

   useEffect(() => {
      document.addEventListener('keydown', key, true)
      return () => {
         document.removeEventListener('keydown', key, true)
      }
   }, [])

   const key = useCallback((event) => {
      console.debug(
         event.keyCode,
         event.key,
         event.which,
         event.code,
         'a'.charCodeAt(0),
      )

      const next_key = KEY_TRANSLATE[event.code]

      if (!next_key) {
         console.debug('unknown keycode', event.code, KEY_TRANSLATE)
      }
      if (next_key) {
         onSelect(next_key)
         event.preventDefault()
      }
   }, [])
   return (
      <>
         {set.map((key, i) => (
            <span key={i}>
               <span
                  {...hints[key]}
                  key={i + '_1'}
                  style={{
                     border: '1px',
                     fontFamily: 'keys',
                     fontSize: 'xxx-large',
                  }}
               >
                  {key[0]}
               </span>

               <span
                  style={{
                     backgroundColor: `tag-${key}`,
                     display: 'inline',
                     borderRadius: '7px',
                  }}
               >
                  {' '}
                  {key.slice(1)}{' '}
               </span>
               {!row && <br />}
            </span>
         ))}
      </>
   )
}
