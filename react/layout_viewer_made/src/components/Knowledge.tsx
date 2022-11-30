import Search from 'antd/lib/input/Search'
import Router from 'next/router'
import React, { useContext, useEffect, useState } from 'react'
import { choice } from '../helpers/array'
import SceletonGraph from './2DSceleton'
import { DocumentContext } from '../contexts/DocumentContext.tsx'

const STD_SEARCH = 'premise'

export const Knowledge = ({ service, slot }) => {
   const context = useContext<DocumentContext>(DocumentContext)

   const [search, setSearch] = useState(STD_SEARCH)
   useEffect(() => {
      if (search !== STD_SEARCH)
         service.save('search').then((val) => context.setValueMetas(slot, val))
   }, [search])
   return (
      <>
         <Search
            onSearch={(search) => setSearch(search)}
            name="id"
            placeholder='What do you want to "know" about?'
            style={{
               zIndex: 123,
               position: 'absolute',
               top: '0px',
               left: '0px',
               margin: '1%',
               right: '1%',
            }}
         />
         <SceletonGraph data={context.value[slot][1]} />
      </>
   )
}
