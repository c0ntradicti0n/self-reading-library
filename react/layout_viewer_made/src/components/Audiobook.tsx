import * as React from 'react'
import { useContext, useEffect, useState } from 'react'
import AudiobookPlayer from './AudiobookPlayer'
import { Button } from '@mui/material'
import { Audio } from 'react-loader-spinner'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import AudiobookService from '../resources/AudiobookService'

const Audiobook = () => {
  return null
  const context = useContext<DocumentContext>(DocumentContext)
  const [service] = useState(new AudiobookService())

  const [exists, setExists] = useState(false)
  const [checked, setChecked] = useState(false)
  const [audioPath, setaudioPath] = useState('')
  const [id, setId] = useState('')
  const [intervalIds, setIntervalIds] = useState<number[]>([])
  const addIntervallId = (n) => setIntervalIds([...intervalIds, n])

  const existsCall = async () => {
    await service.exists(context.value[props.slot], (res) => {
      console.log(res)
      setExists(true)
      setId(id)
      setaudioPath(res.audio_path)
      intervalIds.map((id) => clearInterval(id))
    })
    setChecked(true)
  }

  console.log(context, 'AUDIOBOOK')

  useEffect(() => {
    if (context.value[props.slot] && context.value[props.slot] !== id) {
      existsCall()
      const intervalId = window.setInterval(existsCall, 20000)
      addIntervallId(intervalId)
      return () => intervalIds.map((id) => clearInterval(intervalId))
    }
  }, [context.value[props.slot]])

  const load = async () => {
    if (context.value[props.slot] && id != context.value[props.slot]) {
      console.log('Request audiobook for', context.value[props.slot])
      await service.getOne(context.value[props.slot], (res) => {
        console.log(res)
        setExists(true)
        setId(id)
        setaudioPath(res.audio_path)
        intervalIds.map((id) => clearInterval(id))
      })
    }
  }

  return (
    <div>
      {checked === null ? (
        <Audio height="80" />
      ) : exists ? (
        <AudiobookPlayer id={audioPath}></AudiobookPlayer>
      ) : (
        <Button onClick={load}>Create (more recent) Audiobook</Button>
      )}
    </div>
  )
}

export default Audiobook
