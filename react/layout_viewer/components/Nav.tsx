import React from "react";
import Button from "@mui/material/Button";
import Router from "next/router";
import Url2Difference from "./Url2Difference";
import DownloadFile from "./DownloadFile"
import styled from "styled-components";

interface Props {
    forward: () => any;
    goto: (string) => any;
    upload: (form_data) => any;
    data: any;
}

const NAV = styled.div`
  margin-left: auto; 
  margin-right: 0;
  align: left;
  background: #fff !important;
  z-index: 10000;
  width: 17%;
  column-count: 1;
  flex-flow: column wrap;
  padding: 3%;
`;


export default class Nav extends React.Component<Props, any> {
    state = {
        whereTo: "",
    };

    render() {
        return (
            <NAV>
                <h3>Other interactive formats</h3>
                <div>
                    <DownloadFile id={this.props.data?.value?.value} kind="audiobook">Audiobook</DownloadFile>
                </div>
                <div>
                    <DownloadFile id={this.props.data?.value?.value} kind="pdf">PDF</DownloadFile>
                </div>
                <div>
                    <Button href={"/upload_annotation?id=" + this.props?.data?.value?.value} >Improve layout recognition</Button>
                </div>
                <h3>Navigate to other document</h3>

                <h5>Random</h5>
                <div>
                    <Button
                        onClick={() => this.props.forward()}
                    >
                    I have read it
                    </Button>
                </div>

                <h5>Read custom page here, paste URL</h5>
                <div>
                    <Url2Difference/>
                </div>

                <h5>Upload your own document</h5>
                <div>
                    <form
                        onSubmit={(e) => {
                            console.log(e);
                            Router.push({
                                pathname: "/difference/",
                                query: {id: (e.target as HTMLTextAreaElement).value},
                            });
                        }}
                    >
                        <input type="file" id="myfile" name="myfile"/>
                    </form>
                </div>
                <h3>Navigate to 3D-Library</h3>

                <div>
                    <Button href={"/library"}>Library</Button>
                </div>
            </NAV>
        );
    }
}
