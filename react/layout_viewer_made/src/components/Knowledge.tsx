import { useRouter } from 'next/router'
import React, { useContext, useEffect, useState } from 'react'
import SceletonGraph from './2DSceleton'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import { Input, TourProps } from 'antd'

const STD_SEARCH = 'premise'

export const Knowledge = ({ service, slot }) => {
   const context = useContext<DocumentContext>(DocumentContext)
   const router = useRouter()

   const [search, setSearch] = useState(router.query.search ?? STD_SEARCH)
   useEffect(() => {
      if (search !== STD_SEARCH)
         service.save(search, search, (val) => context.setValueMetas(slot, val))
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
                  left: '10vw',
                  margin: '1%',
                  width: '80%',
                  zIndex: 100,
               }}
               defaultValue={''}
               placeholder='What do you want to "know" about?'
            />
         </div>

         <div
            style={{ height: '100vh', width: '100vw' }}
            aria-description={'Graph'}
            aria-multiline={`Here you can see the result. You can drag the nodes to stay where you dragged them.
                     You can zoom in and out. the red relines mark polar pairs and the green lines mark equality between the concept.
                     As everything, it's not perfect.
                     
                     But as you see in the standard example, where it searches for "premise"
                     `}
            aria-modal={false}
         >
                         <SceletonGraph data={context.meta[slot]} />

         </div>
      </div>
   )
}
