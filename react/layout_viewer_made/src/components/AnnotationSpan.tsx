import React, {
   forwardRef,
   useCallback,
   useContext,
   useEffect,
   useImperativeHandle,
   useRef,
   useState,
} from 'react'
import { Button, Card, Modal, Row, Space } from 'antd'
import { Slider } from '@mui/material'
import { ThreeCircles, ThreeDots } from 'react-loader-spinner'
import { DocumentContext } from '../contexts/DocumentContext.tsx'

import {
   addSpan,
   adjustSpanValue,
   annotation2spans,
   correctPrefix,
   mergeSpans,
   popSpan,
   sortSpans_position,
   sortSpans_precedence,
   spans2annotation,
   validateSpans,
   valueText,
} from '../helpers/span_tools'
import {CheckOutlined, MinusCircleOutlined, PlusCircleOutlined} from '@ant-design/icons'
import { CAPTCHA, NORMAL, Slot } from '../contexts/SLOTS'
import Resource from '../resources/Resource'
import SelectText from './SelectText'
import { indexSubsequence } from '../helpers/array'
import { ClickBoundary } from './ClickBoundary'
import { KeySelect } from './KeySelect'
import Meta from 'antd/lib/card/Meta'

const hints = {
   SUBJECT: {
      'aria-description': 'Subject',
      'aria-multiline': `A 'subject' is a concept to be opposed to another.
      So if it is a difference-set, there should be at least two, but it's also possible
      to select more than two. And they can be embedded in their explanations`,
   },
   CONTRAST: {
      'aria-description': 'Contrast',
      'aria-multiline': `This is the explaining phrase to the 'subject'. It needs
          some explanation, why it is textually opposed to the other word and not just
          a conjunction. There should be as many such phrases as 'subjects'`,
   },
}
export function AnnotationModal({ text, onClose, service }) {
   const ref = useRef(null) // ref => { current: null }
console.log(ref?.current)
   return (
      <ClickBoundary>
         <div data-backdrop="false">
            <Modal
               open={true}
               onCancel={onClose}
               footer={[
                  <Button
                     key="back"
                     onClick={() => {
                        ref?.current?.onCloseDiscard()
                     }}
                  >
                     Unclear
                  </Button>,
                  <Button
                     key="submit"
                     type="primary"
                     onClick={() => {
                        ref?.current?.onCloseSave()
                     }}
                  >
                     Submit
                  </Button>,
                  <Button onClick={() => onClose()}>Back</Button>,
                  <span style={{ display: 'inline-block', width: '7%' }} />,
               ]}
            >
               <AnnotationSpan
                  ref={ref}
                  text={text}
                  service={service}
                  slot={NORMAL}
               />
            </Modal>
         </div>
      </ClickBoundary>
   )
}

export function AnnotationTable(props: {
   annotation: string[][]
   spans: [string, number, number, string[]][]
}) {
   console.debug('AnnotationTable', props)
   const sortedSpans = sortSpans_precedence(props.spans)
   return (
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
         {props.annotation.map(([word, tag], index) => {
            let span_no =
               sortedSpans.find(
                  ([, begin, end]) => index >= begin && index < end,
               )?.[0] ?? 'O'
            return (
               <span key={index} className={'tag span_' + span_no}>
                  {word}{' '}
               </span>
            )
         })}
      </div>
   )
}

const AnnotationSpan = forwardRef<
   {},
   {
      text: string
      onClose?: () => void
      service: Resource
      slot: Slot
      TAG_SET?: string[]
   }
>(
   (
      {
         text = null,
         onClose = () => console.debug('close span_annotation'),
         service,
         slot,
         TAG_SET = ['SUBJECT', 'CONTRAST'],
      },
      inputRef,
   ) => {
      const [annotation, setAnnotation] = useState(null)
      const [errors, setErrors] = useState(null)
      const [success, setSuccess] = useState(false)
      const [kind, setKind] = useState(TAG_SET[0])

      const context = useContext<DocumentContext>(DocumentContext)
      let value = context.value[slot]
      let meta = context.meta[slot]

      console.debug('AnnotationSpan', slot, value, meta, context)

      const initializeFromAnnotation = (annotation) => {
         const sanitized = correctPrefix(annotation)
         setAnnotation(sanitized)
         setSpanIndices([...annotation2spans(sanitized)])
      }

      const [spanIndices, setSpanIndices] = useState<
         [string, number, number, string[]][]
      >([])
      useEffect(() => {
         ;(async () => {
            if (text)
               await service.getOne(null, initializeFromAnnotation, {
                  doc_id: value,
                  text: text,
                  pdf_path: value,
               })
         })()
      }, [])

      useEffect(() => {
         if (!text && !meta?.annotation) {
            service.get(
               (val) => {
                  context.setValueMetas(slot, val)
               },
               { doc_id: value, text: text, pdf_path: value },
            )
            return
         }
         if (meta?.annotation) {
            console.debug(meta, meta?.annotation)
            initializeFromAnnotation(meta?.annotation)
         }
      }, [meta?.annotation])

      useImperativeHandle(inputRef, () => ({
         inputRef: inputRef,
         onCloseSave: onCloseSave,
         onCloseDiscard: onCloseDiscard,
         success:success
      }))

      const onCloseSave = () => {
         console.debug('save', annotation, spanIndices)
         const updatedAnnotation = spans2annotation(annotation, spanIndices)
         const newSpans = mergeSpans(spanIndices, updatedAnnotation)
         const newAnnotation = spans2annotation(annotation, newSpans)

         const _errors = validateSpans(newSpans, newAnnotation, TAG_SET)
         setErrors(_errors)
         if (_errors.length > 0) {
                        setSuccess(false)

            return false
         }
         ;(async () => {
            await service.save(value, newAnnotation, (r) =>
               console.debug('saved', r),
            )
            setSuccess(true)
            setErrors([])

         })()
         onClose()
         return true
      }

      const onCloseDiscard = () => {
         service.cancel(value, {}, () => console.debug('dicarded'))
         onClose()
                     setSuccess(true)

         return true
      }

      return (
         <ClickBoundary>
            {!annotation ? (
               <>
                  <ThreeCircles />
               </>
            ) : (
               <div style={{ fontSize: '0.71rem' }}>
                  <div
                     aria-description={'Select spans for annotations'}
                     aria-multiline={`Here you can mark the difference set, that explain you, 
      how to tell apart thing A from B. You can use those 'Sliders' or also select 
      text with the mouse.`}
                  >
                     <SelectText
                        onSelect={(text) => {
                           if (!kind) {
                              alert(`First set the tag to be set ${kind}`)
                              return
                           }
                           const words = annotation.map(([w, t]) => w)
                           const selectedWords = text
                              .split('\n')
                              .map((s) => s.split(' '))
                              .flat()
                              .map((s) => s.trim())
                              .filter((s) => s)
                           const subIndexes = indexSubsequence(
                              words,
                              selectedWords,
                           )
                           if (!subIndexes) {
                              alert(`Subsequence not found ${kind}`)
                              return
                           }
                           const newSpanIndices = sortSpans_position([
                              ...spanIndices,
                              [kind, ...subIndexes, words.slice(...subIndexes)],
                           ])
                           if (!newSpanIndices) {
                              console.debug(
                                 'Selection could not be found in annotation',
                                 selectedWords,
                                 words,
                              )
                           }
                           console.debug(
                              'new Span:',
                              newSpanIndices,
                              subIndexes[0],
                              words.slice(...subIndexes),
                           )

                           setSpanIndices(newSpanIndices)
                        }}
                     >
                        <AnnotationTable
                           annotation={annotation}
                           spans={spanIndices}
                        />
                     </SelectText>
                     {sortSpans_position(spanIndices).map(
                        ([tag, i1, i2, ws], i) => (
                           <div
                              key={
                                 i.toString() +
                                 'tag' +
                                 i1.toString() +
                                 '-' +
                                 i2.toString()
                              }
                           >
                              <div
                                 style={{
                                    width: '100%',
                                    display: 'inline-block',
                                 }}
                              >
                                 <Button
                                    icon={<MinusCircleOutlined />}
                                    onClick={() =>
                                       setSpanIndices(
                                          popSpan(
                                             sortSpans_position(spanIndices),
                                             i,
                                          ),
                                       )
                                    }
                                 />
                                 <b>
                                    <span
                                       style={{
                                          display: 'inline-block',
                                          width: '5vw',
                                       }}
                                    >
                                       {tag}
                                    </span>
                                 </b>
                                 <span
                                    style={{
                                       wordWrap: 'break-word',
                                       whiteSpace: 'normal',
                                       width: '50vw',
                                       marginLeft: '1%',
                                    }}
                                 >
                                    {ws.map((w, iii) => (
                                       <span
                                          key={iii}
                                          className={'tag span_' + tag}
                                       >
                                          {w}
                                       </span>
                                    ))}
                                 </span>

                                 <Slider
                                    key={'sl-' + i.toString()}
                                    value={[i1, i2]}
                                    valueLabelDisplay="auto"
                                    style={{ width: '50vw !important' }}
                                    onChange={(
                                       event,
                                       newValue,
                                       activeThumb,
                                    ) => {
                                       newValue = [
                                          Math.round(newValue[0]),
                                          Math.round(newValue[1]),
                                       ]
                                       const result = adjustSpanValue(
                                          newValue as [number, number],
                                          activeThumb,
                                          sortSpans_position(spanIndices),
                                          i,
                                          tag,
                                          annotation,
                                       )
                                       console.debug(result)
                                       setSpanIndices(result)
                                    }}
                                    onMouseUp={() =>
                                       setSpanIndices(spanIndices)
                                    }
                                    step={1}
                                    marks
                                    min={0}
                                    max={annotation.length}
                                    disableSwap
                                    getAriaValueText={valueText}
                                 />
                              </div>
                           </div>
                        ),
                     )}
                     <Row gutter={16}>
                        <Card
                           hoverable
                           style={{
                              left: '10%',
                              width: '30vw',
                              margin: '10px',
                           }}
                        >
                           {TAG_SET.map((tag) => (
                              <Button
                                 icon={<PlusCircleOutlined />}
                                 onClick={() => {
                                    setSpanIndices(
                                       addSpan(spanIndices, annotation, tag),
                                    )
                                 }}
                                 type="primary"
                                 value="large"
                                 style={{ margin: '10px' }}
                              >
                                 {tag}
                              </Button>
                           ))}
                        </Card>
                        <Card
                           hoverable
                           style={{
                              left: '10%',
                              width: '40vw',
                              margin: '10px',
                           }}
                        >
                           <div
                              aria-description={
                                 'Here you see, which tag will be set next, use the BIG keys on the keyboard to change it'
                              }
                           >
                              <Meta
                                 title={
                                    <span>
                                       On selecting text
                                       <br />
                                       the text will get a tag
                                    </span>
                                 }
                                 description={
                                    <div
                                       style={{
                                          padding: '10px',
                                          margin: '10px',
                                       }}
                                    >
                                       <span className={'tag span_' + kind}>
                                          {kind}
                                       </span>
                                    </div>
                                 }
                              />
                              Use the keyboard to change:{' '}
                              <KeySelect
                                 row
                                 set={TAG_SET}
                                 onSelect={setKind}
                                 hints={hints}
                              />
                           </div>
                        </Card>
                     </Row>
              {success && <CheckOutlined />}    </div>
                  {errors?.map((e) => (
                     <div style={{ background: 'red' }}>{e}</div>
                  ))}
               </div>
            )}
         </ClickBoundary>
      )
   },
)

export default AnnotationSpan
