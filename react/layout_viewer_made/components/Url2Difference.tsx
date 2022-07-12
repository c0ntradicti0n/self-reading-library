import React from 'react';
import Router from "next/router";


export default class Url2Difference extends React.Component {
    render() {
        return (
            <form onSubmit={(e) => {
                console.log(e)
                Router.push({
                    // @ts-ignore
                    pathname: '/difference/', query: {id: (e.target.elements.id as HTMLTextAreaElement).value}
                })
            }}>
            <input name="id" type="text" style={{
                    margin: "10px"
                }}/>
            </form>
        )
    }
}