import { useContext, useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import Button from '@mui/material/Button'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Typography from '@mui/material/Typography'
import { Slider } from '@mui/material'
import { ThreeDots } from 'react-loader-spinner'
import { DocumentContext } from '../contexts/DocumentContext.tsx'

import {
  addSpan,
  adjustSpanValue,
  annotation2spans,
  popSpan,
  spans2annotation,
  valueText,
} from '../helpers/span_tools'
import { BootstrapDialogTitle } from './BootstrapDialogueTitle'
import { BootstrapDialog } from './BootstrapDialogue'

export function AnnotationTable(props: {
  annotation: string[][]
  spans: [string, number, number, string[]][]
}) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap' }}>
      {props.annotation.map(([word, tag], index) => {
        let span_no =
          props.spans.find(
            ([, begin, end]) => index >= begin && index < end
          )?.[0] ?? 'O'
        return (
          <span key={index} className={'tag span_' + span_no}>
            {word}
          </span>
        )
      })}
    </div>
  )
}

// @ts-ignore
BootstrapDialogTitle.propTypes = {
  children: PropTypes.node,
  onClose: PropTypes.func.isRequired,
}

export default function SpanAnnotation({ text, onClose, service }) {
  const [open, setOpen] = useState(true)
  const [annotation, setAnnotation] = useState(null)
  const context = useContext<DocumentContext>(DocumentContext)
  let { value, meta } = context

  console.log()

  // @ts-ignore
  const [spanIndices, setSpanIndices] = useState<
    [string, number, number, string[]][]
  >([])
  useEffect(() => {
    ;(async () => {
      await service.fetch_one([value, text, value], (res) => {
        setAnnotation(res)
        setSpanIndices([...annotation2spans(res)])
      })
    })()
  }, [])

  const handleClickOpen = () => {
    setOpen(true)
  }
  const handleCloseSave = () => {
    console.log('save')
    ;(async () => {
      await service.save(
        value,
        spans2annotation(annotation, spanIndices),
        () => {
          console.log('saved')
        }
      )
    })()
    setOpen(false)
    onClose()
  }

  const handleCloseDiscard = () => {
    setOpen(false)
    console.log('close discard')
    onClose()
  }

  console.log(spanIndices)
  return (
    <div
      onClick={(e) => {
        e.stopPropagation()
        e.preventDefault()
        console.log('stop it! click')
      }}
      onMouseUp={(e) => {
        e.stopPropagation()
        e.preventDefault()
        console.log('stop it! up')
      }}
      onChange={(e) => {
        e.stopPropagation()
        e.preventDefault()
        console.log('stop it! change')
      }}
      onBlur={(e) => {
        e.stopPropagation()
        e.preventDefault()
        console.log('stop it! blur')
      }}>
      <Button variant="outlined" onClick={handleClickOpen}>
        Open dialog
      </Button>
      <BootstrapDialog
        aria-labelledby="customized-dialog-title"
        open={open}
        fullWidth
        maxWidth={'xl'}
        style={{ marginRight: '30%' }}
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          console.log('stop it!')
        }}
      >
        <BootstrapDialogTitle onClose={() => handleCloseDiscard()}>
          Teach the difference
        </BootstrapDialogTitle>
        <DialogContent dividers>
          {!annotation ? (
            <ThreeDots />
          ) : (
            <>
              <Typography gutterBottom>
                <AnnotationTable
                  annotation={annotation}
                  spans={spanIndices}></AnnotationTable>
              </Typography>
              <Typography gutterBottom>
                {spanIndices.map(([tag, i1, i2, ws], i) => (
                  <div key={i}>
                    <Button
                      startIcon="minus"
                      onClick={() => {
                        popSpan(spanIndices, i, setSpanIndices)
                      }}></Button>
                    <b>{tag}</b>
                    <b>{spanIndices[i].slice(1, 3)}</b>
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
                        aria-label="annotation"
                        value={[i1, i2]}
                        valueLabelDisplay="auto"
                        style={{ width: '50vw !important' }}
                        onChange={(event, newValue, activeThumb) => {
                          const result = adjustSpanValue(
                            newValue as [number, number],
                            activeThumb,
                            spanIndices,
                            i,
                            tag,
                            annotation
                          )
                          console.log(result)
                          setSpanIndices(result)
                        }}
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
              </Typography>
              <Button
                startIcon="add"
                onClick={() => {
                  setSpanIndices(addSpan(spanIndices, annotation))
                }}></Button>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleCloseDiscard()}>
            Discard changes/Cancel
          </Button>
          <Button onClick={() => handleCloseSave()}>Save changes</Button>
        </DialogActions>
      </BootstrapDialog>
    </div>
  )
}
