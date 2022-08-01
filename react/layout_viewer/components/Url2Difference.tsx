import React from 'react';
import Router from "next/router";
import {Button} from "@mui/material";


export default class Url2Difference extends React.Component {
    render() {
        return (
            <form onSubmit={(e) => {
                console.log(e)

                // @ts-ignore
                Router.push('/difference?id=' + (e.target.elements.id as HTMLTextAreaElement).value
                )
            }}>
                <input name="id" type="text" style={{
                    margin: "10px"
                }}/>
                <Button type="submit">Go</Button>
            </form>
        )
    }
}