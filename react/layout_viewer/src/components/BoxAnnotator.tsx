import React, { useCallback, useContext, useEffect, useState } from 'react'
import { pairwise, zip } from '../helpers/array'
import { Button } from '@mui/material'
import Router from 'next/router'
import { Watch } from 'react-loader-spinner'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import Resource from '../resources/Resource'

import {Slot} from "../contexts/SLOTS";

const LABELS = ['NONE', 'c1', 'c2', 'c3', 'wh', 'h', 'pn', 'fn', 'fg', 'tb']

const LABEL_SWITCH = Object.fromEntries(pairwise([...LABELS, LABELS[0]]))

const KEYS = {
  KeyF: 'fn',
  KeyG: 'fg',
  KeyT: 'tb',
  Digit1: 'c1',
  Digit2: 'c2',
  Digit3: 'c3',
  Digit0: 'wh',
  KeyW: 'wh',
  KeyN: 'pn',
  KeyH: 'h',
  Space: 'NONE',
}

const KEY_TRANSLATE = {
  KeyF: 'F',
  KeyG: 'G',
  KeyT: 'T',
  Digit1: '1',
  Digit2: '2',
  Digit3: '3',
  Digit0: '0',
  KeyW: 'W',
  KeyN: 'N',
  KeyH: 'H',
  Space: 'w',
}

const TAG_TRANSLATE = {
  fn: 'footnote',
  fg: 'figure',
  tb: 'table',
  c1: 'column 1',
  c2: 'column 2',
  c3: 'column 3',
  wh: 'single column',
  pn: 'page number',
  h: 'header',
  NONE: 'out of scope',
}

const TAG_COLOR = {
  c1: 'blue',
  c2: 'green',
  c3: 'orange',
  NONE: 'violet',
  none: 'violet',
  None: 'violet',
  other: 'yellow',
  null: 'violet',
  pn: 'yellow',
  h: 'red',
  wh: 'purple',
  fg: 'brown',
  fn: 'grey',
  tb: 'beige',
}

const BoxAnnotator = ({ service,     slot
 }: {service: Resource, slot: Slot}) => {
  service.setSlot(slot)
  const [next_key, setNextKey] = useState('')
  const [finished, setFinished] = useState(false)
  const [imgOriginalSize, setImgOriginalSize] = useState(null)
  const [imgRenderSize, setImgRenderSize] = useState(null)
  const [labels, setLabels] = useState(null)

  const context = useContext<DocumentContext>(DocumentContext)

  useEffect(() => {
    document.addEventListener('keydown', key, true)
    return () => {
      document.removeEventListener('keydown', key, true)
    }
  }, [])

  useEffect(() => {
    const width = window.innerWidth
    const scaleW = width * 0.5
    const height = window.innerHeight
    const scaleH = height * 1.01

    let im = new Image()
    im.src = 'data:image/jpeg;charset=utf-8;base64,' + context.meta[slot]?.image
    im.onload = () => {
      setImgOriginalSize({ width: im.width, height: im.height })
      setImgRenderSize({ width: scaleW, height: scaleH })
    }
  }, [context.meta[slot]?.image])

  const key = useCallback((event) => {
    console.log(
      event.keyCode,
      event.key,
      event.which,
      event.code,
      'a'.charCodeAt(0)
    )

    const next_key = KEYS[event.code]

    if (!next_key) {
      console.log('unknown keycode', event.code)
    }
    if (next_key) {
      setNextKey(next_key)
      event.preventDefault()
    }
  }, [])

  let cols
    console.log("meta", context.meta[slot].bbox, labels ?? context.meta[slot].LABEL ?? context.meta[slot].labels)
  if (context?.meta[slot]?.bbox)
    cols = zip([context.meta[slot].bbox, labels ?? context.meta[slot].LABEL ?? context.meta[slot].labels])
  else
    return <pre>Not rendering {slot}, missing bbox{JSON.stringify(context, null,  2)}</pre>

  console.log({ imgOriginalSize, imgRenderSize, service })
    console.table(cols)
  return (
    <div style={{ fontSize: '1em !important', display: 'flex' }}>
        box
      {finished ? (
        <div>
          <h2>
            We have annotated the whole document!{' '}
            <Button
              onClick={(e) => {
                console.log(e)
                Router.push({
                  pathname: '/difference/',
                  query: { id: context.value[slot] },
                }).catch(console.error)
              }}>
              Return to document!
            </Button>
          </h2>
        </div>
      ) : (
        <div className="container" style={{ position: 'absolute' }}>
          {context.meta[slot]?.image ? (
            <img
              id="annotation_canvas"
              src={
                'data:image/jpeg;charset=utf-8;base64,' + context.meta[slot]?.image
              }
              alt="layout annotation"
            />
          ) : null}

          {imgOriginalSize ? (
            cols?.map((row, i) => (
              <div
                style={{
                  position: 'absolute',
                  left:
                    (
                      (row[0][0] /1000) *
                      imgRenderSize.width-
                      imgRenderSize.height * 0.03
                    ).toString() + 'px',
                  top:
                    (
                      (row[0][1] / 1000) *
                        imgRenderSize.height -
                      imgRenderSize.height * 0.003
                    ).toString() + 'px',
                  width:
                    (
                      ((row[0][2] - row[0][0]) / 1000) *
                      imgRenderSize.width *
                      1.02
                    ).toString() + 'px',
                  height:
                    (
                      ((row[0][3] - row[0][1]) /1000) *
                        imgRenderSize.height +
                      imgRenderSize.height * 0.003
                    ).toString() + 'px',
                  //border: "1px solid black",
                  zIndex: Math.ceil(
                    9000000 - (row[0][2] - row[0][0]) * (row[0][3] - row[0][1])
                  ),
                  opacity: '0.5',
                  background: TAG_COLOR[row[1]],
                }}
                onClick={() => {
                  console.log('row', i)
                  let label
                  if (next_key) {
                    label = next_key
                  } else {
                    label = LABEL_SWITCH[row[1]]
                  }
                  console.log({ label, ls: LABEL_SWITCH, service })
                  if (label)
                    service.change('[1].labels.[' + i + ']', label, (res) => {
                      console.log(res)
                      setLabels(res[1].labels)
                    }).catch(console.error)
                }}></div>
            ))
          ) : (
            <Watch ariaLabel="Waiting for image" />
          )}

          {cols ? (
            <>
              <Button
                style={{ backgroundColor: '#DEF' }}
                onClick={() => {
                  ;(async () => {
                    console.log('ok')
                    await service.ok(
                      [context.value[slot], context.meta[slot]],
                      '',
                      {},
                      async (val) => {
                        console.log(await val)
                        if (!Object.keys(val).length) {
                          setFinished(true)
                        }

                        console.log('get new')

                        await service.fetch_all((val) => context.setValueMetas(slot, val))
                      }
                    )
                  })()
                }}>
                OK
              </Button>
              <Button
                style={{ backgroundColor: '#FED' }}
                onClick={service.cancel}>
                Discard
              </Button>
            </>
          ) : null}

          <div>
            <table style={{ width: '10%' }}>
              <tr>
                <td> KEY</td>
                <td>TAG</td>
              </tr>
              {Object.entries(KEYS).map(([k, v], i) => (
                <tr onClick={() => setNextKey(KEYS[k])}>
                  <td
                    key={i + '_1'}
                    style={{
                      border: '1px',
                      fontFamily: 'keys',
                      fontSize: '4em',
                      verticalAlign: 'bottom',
                    }}>
                    {KEY_TRANSLATE[k]}
                  </td>
                  <td
                    key={i + '_2'}
                    style={{
                      verticalAlign: 'top',
                    }}>
                    <div
                      style={{
                        backgroundColor: TAG_COLOR[v] as string,
                        border: '10px solid ' + TAG_COLOR[v],
                        display: 'block',
                        borderRadius: '7px',
                      }}>
                      {' '}
                      {TAG_TRANSLATE[v]}{' '}
                    </div>
                  </td>
                </tr>
              ))}
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
export default BoxAnnotator
