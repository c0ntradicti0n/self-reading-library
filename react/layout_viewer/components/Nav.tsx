import React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/Button';
import {Link} from "@mui/material";

interface Props {
    forward: () => any
}

export default class Nav extends React.Component<Props, any> {
    state = {
        whereTo: ""
    }

    static async getInitialProps({query}) {

        return {A: "HALLO!"}
    }

    render() {
        return (
            <div className="Nav__container" style={{position: "absolute", zIndex: 10000, width: "100%"}}>
                <div style={{float: "left"}}>
                    <Button variant="contained" onClick={() => this.props.forward()}>I have read it</Button>
                </div>
                <div style={{float: "left"}}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',

                    }}>
                        <form onSubmit={() => this.props.goto(this.state.whereTo)}>
                            <input type="text" style={{
                                margin: "10px",
                            }}/>
                        </form>
                        <a href={"/library"}>Library</a>
                    </div>


                </div>
            </div>
        )
            ;
    }
}