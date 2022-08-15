import * as React from "react";
import {useContext, useEffect, useState} from "react";
import AudiobookPlayer from "./AudiobookPlayer";
import {Button} from "@mui/material";
import {Audio} from "react-loader-spinner";
import {DocumentContext} from "../contexts/DocumentContext.tsx";
import AudiobookService from "../resources/AudiobookService";

const Audiobook = () => {
    const context = useContext<DocumentContext>(DocumentContext);
    const [service] = useState(new AudiobookService());

    const [exists, setExists] = useState(false);
    const [checked, setChecked] = useState(false);
    const [audioPath, setaudioPath] = useState("");
    const [id, setId] = useState("");
    const [intervalIds, setIntervalIds] = useState<number[]>([]);
    const addIntervallId = (n) => setIntervalIds([...intervalIds, n]);

    const existsCall = async () => {
        console.log("ID", context.id);
        await service.exists(context.value, (res) => {
            console.log(res);
            setExists(true);
            setId(id);
            setaudioPath(res.audio_path);
            intervalIds.map((id) => clearInterval(id));
        });
        setChecked(true);
    };

    console.log(context, "AUDIOBOOK");

    useEffect(() => {
        if (context.value) {
            existsCall();
            const intervalId = window.setInterval(existsCall, 20000);
            addIntervallId(intervalId);
            return () => intervalIds.map((id) => clearInterval(id));
        }
    }, [context.value]);

    const load = async () => {
        if (props.id && state.id != context.id) {
            console.log("Request audiobook for", context.id);
            await service.fetch_one(context.id, (res) => {
                console.log(res);
                setExists(true);
                setId(id);
                setaudioPath(res.audio_path);
                intervalIds.map((id) => clearInterval(id));
            });
        }
    };

    return (
        <div>
            {checked === null ? (
                <Audio height="80"/>
            ) : exists ? (
                <AudiobookPlayer id={audioPath}></AudiobookPlayer>
            ) : (
                <Button onClick={load}>Create (more recent) Audiobook</Button>
            )}
        </div>
    );
};

export default Audiobook;
