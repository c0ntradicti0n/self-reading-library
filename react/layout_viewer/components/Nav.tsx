import React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/Button';


export default class Nav extends React.Component<any, any> {
    state = {
        whereTo: ""
    }
    static async getInitialProps({query}) {

        return {A: "HALLO!"}
    }

    render() {
        return (
            <div className="Nav__container" style={{position: "absolute", zIndex: 10000}}>
                <Button variant="contained" onClick={() => this.props.forward()}>I have read it</Button>

                <form onSubmit={() => this.props.goto(this.state.whereTo)}>
                    <TextField
                               name="whereTo"
                               value={this.state.whereTo}
                               onChange={(e) => this.setState({whereTo: (e.target as HTMLTextAreaElement).value})}
                    />
                </form>
            </div>
        );
    }
}