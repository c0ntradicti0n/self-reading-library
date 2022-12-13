import { useRouter } from 'next/router'
import React, { useContext, useEffect, useState } from 'react'
import SceletonGraph from './2DSceleton'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import { Input } from 'antd'

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
      <>
         <Input.Search
            onSearch={(search) => setSearch(search)}
            allowClear
            style={{
               position: 'absolute',
               top: '0px',
               left: '0px',
               margin: '1%',
               width: '90%',
               zIndex: 5768,
            }}
            defaultValue={''}
            placeholder='What do you want to "know" about?'
         />

         <SceletonGraph data={context.meta[slot]} />
      </>
   )
}
