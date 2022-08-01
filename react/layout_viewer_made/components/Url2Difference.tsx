import React from 'react';
import Router from "next/router";
import {Button} from "@mui/material";


export default class Url2Difference extends React.Component {
    state = {
        url: null
    }
    render() {
        return (
            <form  >
            <input onChange={(e) => this.setState({url: e.target.value})} name="id" type="text" style={{
                    margin: "10px"
                }}/>
                <Button href={"/difference?id=" +this.state.url } type="submit">Go</Button>
            </form>
        )
    }
}