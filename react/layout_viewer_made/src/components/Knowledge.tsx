import Search from 'antd/lib/input/Search'
import Router from 'next/router'
import React, { useContext, useEffect, useState } from 'react'
import { choice } from '../helpers/array'
import SceletonGraph from './2DSceleton'
import { DocumentContext } from '../contexts/DocumentContext.tsx'

export const Knowledge = ({ service, slot }) => {
   const context = useContext<DocumentContext>(DocumentContext)

   const [search, setSearch] = useState(choice(['bad', 'false', 'ugly']))
   useEffect(() => {
      service.save('search').then()
   }, [search])
   return (
      <>
         <Search
            onSearch={(search) => setSearch(search)}
            name="id"
            placeholder="Put URL to be scanned as document"
            style={{
               zIndex: 123,
               position: 'absolute',
               top: '0px',
               left: '0px',
               margin: '1%',
            }}
         />
         <SceletonGraph data={context.value[slot][1]} />
      </>
   )
}
