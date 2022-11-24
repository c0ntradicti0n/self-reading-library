import React, { useCallback, useEffect } from 'react'
import { zip } from '../helpers/array'

export const KeySelect = ({
  set,
  onSelect,
}: {
  set: string[]
  onSelect: (string) => void
}) => {
  const KEYS = set.map((key) => 'Key' + key[0])

  const KEY_TRANSLATE = zip([KEYS, set]).reduce(
    (acc, [key, tag]) => ({ ...acc, [key]: tag }),
    {}
  )

  useEffect(() => {
    document.addEventListener('keydown', key, true)
    return () => {
      document.removeEventListener('keydown', key, true)
    }
  }, [])

  const key = useCallback((event) => {
    console.log(
      event.keyCode,
      event.key,
      event.which,
      event.code,
      'a'.charCodeAt(0)
    )

    const next_key = KEY_TRANSLATE[event.code]

    if (!next_key) {
      console.log('unknown keycode', event.code, KEY_TRANSLATE)
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
            key={i + '_1'}
            style={{
              border: '1px',
              fontFamily: 'keys',
              fontSize: '2rem !important',
              verticalAlign: 'bottom',
            }}>
            {key[0]}
          </span>

          <span
            style={{
              backgroundColor: `tag-${key}`,
              display: 'inline',
              borderRadius: '7px',
            }}>
            {' '}
            {key}{' '}
          </span>
        </span>
      ))}
    </>
  )
}