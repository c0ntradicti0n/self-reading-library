import React, {
  forwardRef,
  useCallback,
  useContext,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'
import { Button, Modal } from 'antd'
import { Slider } from '@mui/material'
import { ThreeDots } from 'react-loader-spinner'
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
import { MinusCircleOutlined, PlusCircleOutlined } from '@ant-design/icons'
import { CAPTCHA, NORMAL, Slot } from '../contexts/SLOTS'
import Resource from '../resources/Resource'
import SelectText from './SelectText'
import { KeySelect } from './KeySelect'
import { indexSubsequence } from '../helpers/array'
import { ClickBoundary } from './ClickBoundary'

export function AnnotationModal({ text, onClose, service }) {
  const ref = useRef(null) // ref => { current: null }
  const [open, setOpen] = useState(true)

  return (
    <div data-backdrop="false">
      <a onClick={() => setOpen(open)}>Captcha</a>
      {open ? (
        <Modal
          open={open}
          footer={[
            <Button
              key="back"
              onClick={() => {
                ref?.current?.onCloseDiscard()
              }}>
              Unclear
            </Button>,
            <Button
              key="submit"
              type="primary"
              onClick={() => {
                ref?.current?.onCloseSave()
              }}>
              Submit
            </Button>,
            <Button onClick={() => setOpen(false)}>Finish game</Button>,
          ]}>
          <AnnotationSpan
            ref={ref}
            onClose={() => setOpen(false)}
            text={text}
            service={service}
            slot={NORMAL}
          />
        </Modal>
      ) : null}
    </div>
  )
}

export function AnnotationTable(props: {
  annotation: string[][]
  spans: [string, number, number, string[]][]
}) {
  console.log('AnnotationTable', props)
  const sortedSpans = sortSpans_precedence(props.spans)
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap' }}>
      {props.annotation.map(([word, tag], index) => {
        let span_no =
          sortedSpans.find(
            ([, begin, end]) => index >= begin && index < end
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
    onClose: () => void
    service: Resource
    slot: Slot
    TAG_SET: string[]
  }
>(
  (
    {
      text = null,
      onClose = () => console.log('close span_annotation'),
      service,
      slot,
      TAG_SET = ['SUBJECT', 'CONTRAST'],
    },
    inputRef
  ) => {
    const [annotation, setAnnotation] = useState(null)
    const [errors, setErrors] = useState(null)
    const [kind, setKind] = useState(TAG_SET[0])

    const context = useContext<DocumentContext>(DocumentContext)
    let value = context.value[slot]
    let meta = context.meta[slot]

    console.log('AnnotationSpan', slot, value, meta, context)

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
          { doc_id: value, text: text, pdf_path: value }
        )
        return
      }
      if (meta?.annotation) {
        console.log(meta, meta?.annotation)
        initializeFromAnnotation(meta?.annotation)
      }
    }, [meta?.annotation])

    useImperativeHandle(inputRef, () => ({
      inputRef: inputRef,
      onCloseSave: onCloseSave,
      onCloseDiscard: onCloseDiscard,
    }))

    const onCloseSave = () => {
      console.log('save', annotation, spanIndices)
      const updatedAnnotation = spans2annotation(annotation, spanIndices)
      const newSpans = mergeSpans(spanIndices, updatedAnnotation)
      const newAnnotation = spans2annotation(annotation, newSpans)

      const _errors = validateSpans(newSpans, newAnnotation, TAG_SET)
      if (_errors.length > 0) {
        console.log('ERRORS', _errors)

        setErrors(_errors)
        return false
      }
      console.log('validated')
      ;(async () => {
        await service.change('[1].annotation', newAnnotation, (r) => {
          console.log('updated', r)
        })
        await service.save(value, newAnnotation, (r) => console.log('saved', r))
      })()
      onClose()
      return true
    }

    const onCloseDiscard = () => {
      console.log('close discard')
      service.cancel(value, {}, () => console.log('dicarded'))
      onClose()
      return true
    }

    console.log(spanIndices)
    return (
      <ClickBoundary>
        {!annotation ? (
          <>
            <pre>{JSON.stringify({ slot, context }, null, 2)}</pre>
            <ThreeDots />
          </>
        ) : (
          <div>
            <SelectText
              onSelect={(x) => {
                console.log('selected:', kind, x)
                if (!kind) {
                  alert(`First set the tag to be set ${kind}`)
                  return
                }
                const words = annotation.map(([w, t]) => w)
                const selectedWords = x
                  .split('\n')
                  .map((s) => s.split(' '))
                  .flat()
                  .map((s) => s.trim())
                const subIndexes = indexSubsequence(words, selectedWords)
                if (!subIndexes) {
                  alert(`Subsequence not found ${kind}`)
                  return
                }
                console.log('subIndexes', subIndexes)
                const newSpanIndices = sortSpans_position([
                  ...spanIndices,
                  [kind, ...subIndexes[0], words.slice(...subIndexes[0])],
                ])
                if (!newSpanIndices) {
                  console.log(
                    'Selection could not be found in annotation',
                    selectedWords,
                    words
                  )
                }
                console.log(
                  'new Span:',
                  newSpanIndices,
                  subIndexes[0],
                  words.slice(...subIndexes[0])
                )

                setSpanIndices(newSpanIndices)
              }}>
              <AnnotationTable annotation={annotation} spans={spanIndices} />
            </SelectText>
            {sortSpans_position(spanIndices).map(([tag, i1, i2, ws], i) => (
              <div
                key={
                  i.toString() + 'tag' + i1.toString() + '-' + i2.toString()
                }>
                <div style={{ width: '3%', display: 'inline-block' }}>
                  <Button
                    icon={<MinusCircleOutlined />}
                    onClick={() =>
                      setSpanIndices(
                        popSpan(sortSpans_position(spanIndices), i)
                      )
                    }
                  />
                </div>
                <div style={{ width: '3%', display: 'inline-block' }}>
                  {' '}
                  <b>
                    [{spanIndices[i][1]}:{spanIndices[i][2]}]
                  </b>
                </div>
                <b>{tag}</b>
                <br />
                <div
                  style={{
                    marginRight: '0px',
                    marginLeft: '0px',
                  }}>
                  <div
                    style={{
                      wordWrap: 'break-word',
                      whiteSpace: 'normal',
                      width: '50vw',
                    }}>
                    {ws.map((w, iii) => (
                      <span key={iii} className={'tag span_' + tag}>
                        {w}
                      </span>
                    ))}
                  </div>

                  <Slider
                    key={'sl-' + i.toString()}
                    value={[i1, i2]}
                    valueLabelDisplay="auto"
                    style={{ width: '50vw !important' }}
                    onChange={(event, newValue, activeThumb) => {
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
                        annotation
                      )
                      console.log(result)
                      setSpanIndices(result)
                    }}
                    onMouseUp={() => setSpanIndices(spanIndices)}
                    step={1}
                    marks
                    min={0}
                    max={annotation.length}
                    disableSwap
                    getAriaValueText={valueText}
                  />
                </div>
              </div>
            ))}
            {TAG_SET.map((tag) => (
              <Button
                icon={<PlusCircleOutlined />}
                onClick={() => {
                  setSpanIndices(addSpan(spanIndices, annotation, tag))
                }}>
                {tag}
              </Button>
            ))}
            <pre>{kind}</pre>
            <KeySelect set={TAG_SET} onSelect={setKind} />
            {errors?.map((e) => (
              <div style={{ background: 'red' }}>{e}</div>
            ))}
          </div>
        )}
      </ClickBoundary>
    )
  }
)

export default AnnotationSpan
