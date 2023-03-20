import { useRouter } from 'next/router'
import React, { useContext, useEffect, useState } from 'react'
import SceletonGraph from './2DSceleton'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import { Input } from 'antd'
import { ThreeDots } from 'react-loader-spinner'

const STD_SEARCH = 'premise'

export const Knowledge2 = ({ service, slot }) => {
   const context = useContext<DocumentContext>(DocumentContext)
   const router = useRouter()

   const [search, setSearch] = useState(router.query.search ?? STD_SEARCH)
   const [loading, setLoading] = useState(false)
   useEffect(() => {
      if (search !== STD_SEARCH) {
         setLoading(true)
         service.save(search, search, (val) => {
            context.setValueMetas(slot, val)
            setLoading(false)
         })
      }
   }, [search])
   return (
      <div
         aria-description={'Relations of distinctions'}
         aria-multiline={`Differences can be networking, because a difference maybe
                     alsways builds on another, so a net can built from A-vs-B and a defining A and b defining B.
                     Then there should be in a some other subject A' and in b some subject B'. The nature of
                     and extent of this relation can be explored with this diagram.`}
         aria-modal={false}
      >
         <div
            aria-description={'Search'}
            aria-multiline={`Here you can type, what you would like to get the difference-net for`}
            aria-modal={false}
         >
            <Input.Search
               onSearch={(search) => setSearch(search)}
               allowClear
               style={{
                  position: 'absolute',
                  top: '0px',
                  left: '24vw',
                  margin: '1%',
                  width: '70%',
                  zIndex: 100,
               }}
               defaultValue={''}
               placeholder='What do you want to "know" about?'
            />
         </div>

         {loading && (
            <div
               style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  margin: '1%',
                  width: '70%',
                  zIndex: 100,
               }}
            >
               <ThreeDots />
            </div>
         )}

         <div
            style={{ height: '100vh', width: '100vw' }}
            aria-description={'Graph'}
            aria-multiline={`Here you can see the result. You can drag the nodes to stay where you dragged them.
                     You can zoom in and out. the red relines mark polar pairs and the green lines mark equality between the concept.
                     As everything, it's not perfect.
                     
                     But as you see in the standard example, where it searches for "premise", it reveils the relation 
                     between "premise" and "truth" as well as "conclusion" and "validity", that in logic premises
                     must be true as correct statemants about the world and the conclusion must be drawn by logically 
                     valid steps. That you learn in the first logic couse in philosophy.
                     `}
            aria-modal={false}
         >
            <SceletonGraph
               graphData={context.meta[slot]}
               onExpand={async (node) => {
                  return (await service.change(node.label))[1]
               }}
            />
         </div>
      </div>
   )
}
