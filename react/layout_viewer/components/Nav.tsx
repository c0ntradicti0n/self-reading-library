import React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/Button';
import {Link} from "@mui/material";

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
                        <form onSubmit={(e) => (typeof (e.target as HTMLTextAreaElement).value === "string") ?
                            this.props.goto(this.state.whereTo) : this.props.upload( (e.target as HTMLTextAreaElement).value)}>
                            <input type="text" style={{
                                margin: "10px"
                            }}/>
                            <input type="file" id="myfile" name="myfile"/>
                        </form>
                        <a href={"/library"}>Library</a>
                    </div>


                </div>
            </div>
        )
            ;
    }
}