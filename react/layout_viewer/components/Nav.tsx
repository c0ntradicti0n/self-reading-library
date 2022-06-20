import React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/Button';
import {Link} from "@mui/material";
import Router from "next/router";

interface Props {
    forward: () => any
    goto: (string) => any
    upload: (form_data) => any

}

export default class Nav extends React.Component<Props, any> {
    state = {
        whereTo: ""
    }

    static async getInitialProps({query}) {

        return {A: "initial props nav"}
    }

    render() {
        return (
            <div className="Nav" style={{position: "absolute", zIndex: 10000, width: "100%"}}>
                <div style={{float: "left"}}>
                    <Button variant="contained" onClick={() => this.props.forward()}>I have read it</Button>
                </div>
                <div style={{float: "left"}}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',

                    }}>

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
                        <form onSubmit={(e) => {
                            console.log(e)
                            Router.push({
                                pathname: '/difference/', query: {id: (e.target as HTMLTextAreaElement).value}
                            })
                        }}>

                            <input type="file" id="myfile" name="myfile"/>
                        </form>
                        <a href={"/library"}>Library</a>
                        {' '}
                        <a style={{margin: "30px"}}
                           href={"/difference?id=http://differencebetween.info"}>Random <i>differencebetween.info</i> article</a>

                    </div>


                </div>
            </div>
        )
            ;
    }
}