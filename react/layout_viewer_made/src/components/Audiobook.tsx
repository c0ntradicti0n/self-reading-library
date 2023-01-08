import * as React from 'react'
import { useContext, useEffect, useState } from 'react'
import AudiobookPlayer from './AudiobookPlayer'
import { Audio } from 'react-loader-spinner'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import AudiobookService from '../resources/AudiobookService'
import { NORMAL } from '../contexts/SLOTS'
import { Button } from 'antd'

const Audiobook = () => {
   const context = useContext<DocumentContext>(DocumentContext)
   const [service] = useState(new AudiobookService())

   const [exists, setExists] = useState(false)
   const [checked, setChecked] = useState(false)
   const [audioPath, setaudioPath] = useState('')
   const [id, setId] = useState('')
   const [intervalIds, setIntervalIds] = useState<number[]>([])
   const addIntervallId = (n) => setIntervalIds([...intervalIds, n])

   const existsCall = async () => {
      fetch(audioPath, { method: 'HEAD' }).then((res) => {
         if (res.ok) {
            setExists(true)
         } else {
            setExists(false)
         }
      })

      await service.exists(context.value[NORMAL], (res) => {
         setExists(true)
         setId(id)
         setaudioPath(res.audio_path)
         intervalIds.map((id) => clearInterval(id))
      })
      setChecked(true)
   }

   useEffect(() => {
      if (context.value[NORMAL] && context.value[NORMAL] !== id) {
         existsCall()
         const intervalId = window.setInterval(existsCall, 20000)
         addIntervallId(intervalId)
         return () => intervalIds.map((id) => clearInterval(intervalId))
      }
   }, [context.value[NORMAL]])

   const createAudio = async () => {
      if (context.value[NORMAL]) {
         console.debug('Request audiobook for', context.value[NORMAL])
         await service.getOne(context.value[NORMAL], (res) => {
            console.log(res)
            setExists(true)
            setId(id)
         })
      }
   }

   return (
      <>
         {checked === null ? (
            <Audio height="80" />
         ) : exists ? (
            <div style={{ height: '100px !important' }}>
               <AudiobookPlayer id={audioPath}></AudiobookPlayer>
            </div>
         ) : (
            <Button type="link" onClick={createAudio}>
               Make audiobook{' '}
            </Button>
         )}
      </>
   )
}

export default Audiobook
