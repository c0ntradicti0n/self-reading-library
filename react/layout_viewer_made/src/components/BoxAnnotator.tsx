import React, { useCallback, useContext, useEffect, useState } from 'react'
import { pairwise, zip } from '../helpers/array'
import { Button } from 'antd'
import Router from 'next/router'
import { Watch } from 'react-loader-spinner'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import Resource from '../resources/Resource'
import { Slot } from '../contexts/SLOTS'
import dynamic from 'next/dynamic'

const RectangleSelection = dynamic(() => import('react-rectangle-selection'), {
   ssr: false,
})
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

const BoxAnnotator = ({ service, slot }: { service: Resource; slot: Slot }) => {
   service.setSlot(slot)
   const [next_key, setNextKey] = useState('W')
   const [finished, setFinished] = useState(false)
   const [imgOriginalSize, setImgOriginalSize] = useState(null)
   const [imgRenderSize, setImgRenderSize] = useState(null)
   const [labels, setLabels] = useState(null)
   const [rectangleSelection, setRectangleSelection] = useState(null)
   const context = useContext<DocumentContext>(DocumentContext)

   useEffect(() => {
      document.addEventListener('keydown', key, true)
      return () => {
         document.removeEventListener('keydown', key, true)
      }
   }, [])

   useEffect(() => {
      let im = new Image()
      im.src =
         'data:image/jpeg;charset=utf-8;base64,' + context.meta[slot]?.image

      im.onload = () => {
         const width = window.innerWidth
         const scaleH = window.innerHeight / 1000
         const scaleW = (scaleH * im.naturalWidth) / im.naturalHeight

         console.debug('loading image')
         setLabels(context.meta[slot]?.labels)
         setImgOriginalSize({ width: im.width, height: im.height })
         setImgRenderSize({ width: scaleW, height: scaleH, window })
         console.debug(
            'setting coordinates',
            im.naturalHeight,
            im.naturalWidth,
            im,
            scaleW,
            window,
            width,
         )
      }
   }, [context.meta[slot]?.image])

   const key = useCallback((event) => {
      console.debug(
         event.keyCode,
         event.key,
         event.which,
         event.code,
         'a'.charCodeAt(0),
      )

      const next_key = KEYS[event.code]

      if (!next_key) {
         console.debug('unknown keycode', event.code)
      }
      if (next_key) {
         setNextKey(next_key)
         console.debug({
            dep: context.meta[slot]?.image,
            next_key,
            finished,
            imgOriginalSize,
            imgRenderSize,
            labels,
            rectangleSelection,
            context,
         })
         event.preventDefault()
      }
   }, [])

   let cols

   if (context?.meta[slot]?.bbox)
      cols = zip([
         context.meta[slot].bbox,
         labels ?? context.meta[slot].LABEL ?? context.meta[slot].labels,
      ])
   else
      return (
         <pre>
            Not rendering {slot}, missing bbox{JSON.stringify(context, null, 2)}
         </pre>
      )

   console.debug('imageRenderSize', imgRenderSize)
   if (!imgRenderSize) return 'Not ready'
   const renderRectTagsCoords = cols?.map((row, i) => [
      row[1],
      {
         left: row[0][0] * imgRenderSize.width,
         top: row[0][1] * imgRenderSize.height,
         width: (row[0][2] - row[0][0]) * imgRenderSize.width,
         height: (row[0][3] - row[0][1]) * imgRenderSize.height,
      },
   ])

   return window ? (
      <div
         style={{
            border: '2px solid black',
            fontSize: '1em !important',
            position: 'absolute',
            top: '0px',
            left: '0px',
            zIndex: 100000,
         }}
      >
         <RectangleSelection
            onSelect={(e, coords) => {
               const [x1, x2] = [
                  Math.min(coords.origin[0], coords.target[0]),
                  Math.max(coords.origin[0], coords.target[0]),
               ]
               const [y1, y2] = [
                  Math.min(coords.origin[1], coords.target[1]),
                  Math.max(coords.origin[1], coords.target[1]),
               ]

               if (!next_key) {
                  alert(
                     'Please set Label by pressing key before selecting with the box',
                  )
                  return
               }

               const jsonPathsToChange = renderRectTagsCoords
                  .map(([rowLabel, row], i) => [rowLabel, row, i])
                  .filter(([rowLabel, row, i]) => {
                     if (
                        row.left > x1 &&
                        row.left + row.width < x2 &&
                        row.top > y1 &&
                        row.top + row.height < y2
                     )
                        return true
                     else return false
                  })
                  .map(([rowLabel, row, i]) => '[1].labels.[' + i + ']')

               setRectangleSelection([jsonPathsToChange, next_key])
            }}
            onMouseUp={(event) => {
               if (rectangleSelection)
                  service
                     .change(
                        rectangleSelection[0],
                        rectangleSelection[1],
                        (res) => {
                           console.debug(
                              'changed multiple labels',
                              res[1].labels,
                           )
                           setLabels(res[1].labels)
                        },
                     )
                     .catch(console.error)
               setRectangleSelection(null)
            }}
            style={{
               backgroundColor: 'rgba(0,0,255,0.4)',
               borderColor: 'blue',
            }}
         >
            {finished ? (
               <div>
                  <h2>
                     We have annotated the whole document!{' '}
                     <Button
                        onClick={(e) => {
                           console.debug(e)
                           Router.push({
                              pathname: '/difference/',
                              query: { id: context.value[slot] },
                           }).catch(console.error)
                        }}
                     >
                        Return to document!
                     </Button>
                  </h2>
               </div>
            ) : (
               <div
                  className="container"
                  style={{
                     position: 'absolute',
                     width: imgRenderSize.width + 'px',
                  }}
               >
                  {context.meta[slot]?.image ? (
                     <img
                        id="annotation_canvas"
                        src={
                           'data:image/jpeg;charset=utf-8;base64,' +
                           context.meta[slot]?.image
                        }
                        alt="layout annotation"
                        draggable="false"
                        style={{
                           left: '0px',
                           top: '0px',
                           border: '2px solid black',
                           height: '190vh',
                        }}
                     />
                  ) : null}
                  {imgOriginalSize ? (
                     renderRectTagsCoords?.map(([rowLabel, row], i) => {
                        console.debug('bbox', row)
                        return (
                           <div
                              key={'row' + i.toString()}
                              style={{
                                 position: 'absolute',
                                 left: row.left.toString() + 'px',
                                 top: row.top.toString() + 'px',
                                 width: row.width.toString() + 'px',
                                 height: row.height.toString() + 'px',
                                 zIndex: 900000000,
                                 opacity: '0.5',
                                 background: TAG_COLOR[rowLabel],
                              }}
                              onClick={() => {
                                 let label
                                 if (next_key) {
                                    label = next_key
                                 } else {
                                    label = LABEL_SWITCH[rowLabel]
                                 }
                                 console.debug({
                                    label,
                                    ls: LABEL_SWITCH,
                                    service,
                                 })
                                 if (label)
                                    service
                                       .change(
                                          '[1].labels.[' + i + ']',
                                          label,
                                          (res) => {
                                             console.debug(
                                                'changed single label',
                                                res,
                                             )
                                             setLabels(res[1].labels)
                                          },
                                       )
                                       .catch(console.error)
                              }}
                           ></div>
                        )
                     })
                  ) : (
                     <Watch ariaLabel="Waiting for image" />
                  )}

                  <div>
                     <div
                        style={{
                           backgroundColor: TAG_COLOR[next_key],
                        }}
                     >
                        <span
                           style={{
                              filter: 'invert(100%)',
                              fontWeight: 'bolder',
                              color: TAG_COLOR[next_key],
                           }}
                        >
                           {TAG_TRANSLATE[next_key]}
                        </span>
                     </div>
                     <table style={{ width: '10%' }}>
                        <tbody>
                           <tr>
                              <td> KEY</td>
                              <td>TAG</td>
                           </tr>
                           {Object.entries(KEYS).map(([k, v], i) => (
                              <tr
                                 key={'k1' + i}
                                 onClick={() => setNextKey(KEYS[k])}
                              >
                                 <td
                                    key={i + '_1'}
                                    style={{
                                       border: '1px',
                                       fontFamily: 'keys',
                                       fontSize: '2em',
                                       verticalAlign: 'bottom',
                                    }}
                                 >
                                    {KEY_TRANSLATE[k]}
                                 </td>
                                 <td
                                    key={i + '_2'}
                                    style={{
                                       verticalAlign: 'top',
                                    }}
                                 >
                                    <div
                                       style={{
                                          backgroundColor: TAG_COLOR[
                                             v
                                          ] as string,
                                          border: '4px solid ' + TAG_COLOR[v],
                                          display: 'block',
                                          borderRadius: '7px',
                                       }}
                                    >
                                       {' '}
                                       {TAG_TRANSLATE[v]}{' '}
                                    </div>
                                 </td>
                              </tr>
                           ))}
                        </tbody>
                     </table>
                  </div>
               </div>
            )}
         </RectangleSelection>
         {cols ? (
            <>
               <Button
                  style={{ backgroundColor: '#DEF' }}
                  onClick={() => {
                     ;(async () => {
                        console.debug('ok')
                        await service.ok(
                           [context.value[slot], context.meta[slot]],
                           '',
                           {},
                           async (val) => {
                              console.debug(await val)
                              if (!Object.keys(val).length) {
                                 setFinished(true)
                              }

                              console.debug('get new')

                              await service.fetch_all((val) =>
                                 context.setValueMetas(slot, val),
                              )
                           },
                        )
                     })()
                  }}
               >
                  Good
               </Button>
               <Button
                  style={{ backgroundColor: '#FED' }}
                  onClick={service.cancel}
               >
                  Can't solve
               </Button>
            </>
         ) : null}
      </div>
   ) : null
}
export default BoxAnnotator
