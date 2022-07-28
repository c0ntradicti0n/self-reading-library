import {useEffect, useState} from "react";
import PropTypes from "prop-types";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import Typography from "@mui/material/Typography";
import {styled as sty} from "@mui/material/styles";
import {Slider} from "@mui/material";
import {getSpans} from "../src/util/annotation";
import {ThreeDots} from "react-loader-spinner";

const BootstrapDialog = sty(Dialog)(({theme}) => ({
    "& .MuiDialogContent-root": {
        padding: theme.spacing(2),
        maxWidth: "90%",
        overflow: "auto",
        wordWrap: "normal",
        display: "flex",
        flex: "1 1 auto",
        flexWrap: "wrap",
    },
    "& .MuiDialogActions-root": {
        padding: theme.spacing(1),
    },
}));

const test_annotation = [
    ["the", "B-SUBJ"],
    ["lazy", "I-SUBJ"],
    ["yellow", "I-SUBJ"],
    ["socks", "I-SUBJ"],
    ["glued", "B-CONTRAST"],
    ["on", "B-CONTRAST"],
    ["the", "B-CONTRAST"],
    ["wall", "B-CONTRAST"],
    [".", "O"],
    ["the", "B-SUBJ"],
    ["lazy", "I-SUBJ"],
    ["yellow", "I-SUBJ"],
    ["socks", "I-SUBJ"],
    ["glued", "B-CONTRAST"],
    ["on", "B-CONTRAST"],
    ["the", "B-CONTRAST"],
    ["wall", "gutterBottomB-CONTRAST"],
    [".", ""],
];

const minDistance = 1;

const BootstrapDialogTitle = (props) => {
    const {children, onClose, ...other} = props;

    return (
        <DialogTitle sx={{m: 0, p: 2}} {...other}>
            {children}
            {onClose ? (
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    sx={{
                        position: "absolute",
                        right: 8,
                        top: 8,
                        color: (theme) => theme.palette.grey[500],
                    }}
                >
                    <CloseIcon/>
                </IconButton>
            ) : null}
        </DialogTitle>
    );
};

BootstrapDialogTitle.propTypes = {
    children: PropTypes.node,
    onClose: PropTypes.func.isRequired,
};

function AnnotationTable(props: { annotation: string[][], spans: [string, number, number, string[]][] }) {


    return <div style={{display: "flex", flexWrap: "wrap"}}>
        {props.annotation.map(([word, tag], index) => {
                let span_no = props.spans.find(
                    ([tag, begin, end, text]) =>
                        index >= begin && index < end)?.[0] ?? "O"
                return <span key={index} className={"tag span_" + span_no}>
                {word}
            </span>

            }
        )}</div>

        ;
}

const spans2annotation = (annotation, spans) => {
    const new_annotation = annotation.map(([word, tag], index) => {
        let [_tag, begin, end, text] = spans.find(
            ([tag, begin, end, text]) =>
                index >= begin && index < end) ?? [null, null, null, null]
        if (tag == null)
            return [word, "O"]
        let prefix = ""
        if (index === begin)
            prefix = "B-"
        if (index === end - 1)
            prefix = "L-"
        if (index === begin && index === end - 1)
            prefix = "U-"
        if (index > begin && index < end - 1)
            prefix = "I-"
        return [word, prefix + _tag]
    })
    return new_annotation
}

function valuetext(value) {
    return `${value}°C`;
}

function adjustSpanValue(newValue: number | number[] | number[], activeThumb: number, spanIndices: [string, number, number, string[]][], i: number, tag: string, annotation: [string, string]) {
    if (!Array.isArray(newValue)) {
        return;
    }
    let value: number[] = null;

    if (newValue[1] - newValue[0] < minDistance) {
        if (activeThumb === 0) {
            const clamped = Math.min(
                newValue[0],
                100 - minDistance
            );
            value = [clamped, clamped + minDistance];
        } else {
            const clamped = Math.max(newValue[1], minDistance);
            value = [clamped - minDistance, clamped];
        }
    } else {
        value = newValue;
    }

    // @ts-ignore
    spanIndices[i] = [
        tag,
        ...value,
        annotation.slice(value[0], value[1]).map(([w, t]) => w),
    ];

    // @ts-ignore

    for (let [j, span] of [...spanIndices.entries()].reverse()) {
        span = spanIndices[j]
        console.log(spanIndices, span)
        if (span[2] > value[0] && span[2] < value[1] && i > j) {
            span[2] = value[0];
            spanIndices[j] = span;
        }

        if (span[1] < value[1] && span[1] > value[0] && j > i) {
            span[1] = value[1];
            spanIndices[j] = span;
        }
    }

    // @ts-ignore
    spanIndices = spanIndices.map(([tag, begin, end, words]) => [
        tag,
        begin, end,
        annotation.slice(begin, end).map(([w, t]) => w),
    ]);
    return spanIndices;
}

export default function SpanAnnotation({value, meta, text, onClose, service}) {
    const [open, setOpen] = useState(true);
    const [annotation, setAnnotation] = useState(null);
    const [corredted_text, setText] = useState(null);

    // @ts-ignore
    const [spanIndices, setSpanIndices] = useState<[string, number, number, string[]][]>([]);
    useEffect(() => {
        (async () => {
            await service.fetch_one([value, text, meta["pdf_path"]], (res) => {
                    setAnnotation(res)
                    setSpanIndices(getSpans(res))
                    const words = (res.map(([word, tag]) => word))
                    console.log(words)
                    setText(words.join(" "))
                }
            );
        })();
    }, []);

    const handleClickOpen = () => {
        setOpen(true);
    };
    const handleCloseSave = () => {
        console.log("save");
        (async () => {
            await service.save(value, spans2annotation(annotation, spanIndices), () => {
                    console.log("saved");
                }
            );
        })();
        setOpen(false);
        onClose();
    };

    const handleCloseDiscard = () => {
        setOpen(false);
        onClose();
    };


    console.log(spanIndices)
    return (<div>
            <Button variant="outlined" onClick={handleClickOpen}>
                Open dialog
            </Button>
            <BootstrapDialog
                onClose={handleCloseDiscard}
                aria-labelledby="customized-dialog-title"
                open={open}
                fullWidth
                maxWidth={"xxl"}
            >
                <BootstrapDialogTitle
                    onClose={handleCloseDiscard}
                >
                    Teach the difference
                </BootstrapDialogTitle>
                <DialogContent dividers>

                    {
                        (!annotation) ? <ThreeDots/> :
                            <>
                                <Typography gutterBottom>
                                    <AnnotationTable annotation={annotation} spans={spanIndices}></AnnotationTable>
                                </Typography>
                                <Typography gutterBottom>
                                    {spanIndices.map(([tag, i1, i2, ws], i) => (
                                        <div>
                                            <Button startIcon="minus" onClick={() => {
                                                spanIndices.splice(i, 1)
                                                setSpanIndices([...spanIndices])
                                            }
                                            }></Button>
                                            <b>{tag}</b>
                                            <br/>
                                            <div style={{
                                                marginRight: "0px",
                                                marginLeft: "0px"

                                            }}>
                                                <div style={{
                                                    wordWrap: "break-word",
                                                    whiteSpace: "normal",
                                                    width: "80vw"
                                                }}>
                                                    {ws.map((w, iii) => <span key={iii}
                                                                              className={"tag span_" + tag}>{w}</span>)}
                                                </div>
                                                <Slider

                                                    aria-label="annotation"
                                                    value={spanIndices[i].slice(1, 3) as number[]}
                                                    valueLabelDisplay="auto"
                                                    onChange={(event, newValue, activeThumb) => {
                                                        console.log("changing slider", event, newValue, activeThumb)
                                                        setSpanIndices(adjustSpanValue(newValue, activeThumb, spanIndices, i, tag, annotation));
                                                    }}
                                                    step={1}
                                                    marks
                                                    min={0}
                                                    max={annotation.length}
                                                    disableSwap
                                                    getAriaValueText={valuetext}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </Typography>
                                <Button startIcon="add" onClick={() => {
                                    const tagOccurences = spanIndices.reduce((acc, e) => acc.set(e[0], (acc.get(e[0]) || 0) + 1), new Map());
                                    console.log(tagOccurences)
                                    let incompleteTags = [...tagOccurences.entries()].filter(([k, v]) => v < 2)
                                    console.log(incompleteTags)

                                    if (incompleteTags.every((val, i, arr) => val === arr[0] && val < 2))
                                        incompleteTags = [["SUBJECT", 0], ["CONTRAST", 0]]
                                    console.log(incompleteTags)

                                    let newSpanIndices = spanIndices
                                    const averageSpanLength = annotation.length / (spanIndices.length + incompleteTags.length)
                                    console.log(averageSpanLength, annotation.length, (spanIndices.length + incompleteTags.length), (spanIndices.length), (incompleteTags.length))
                                    incompleteTags.forEach(([k, v], i) => {
                                            let newSpan = [
                                                annotation.length - (incompleteTags.length - i) * averageSpanLength,
                                                annotation.length - (incompleteTags.length - i - 1) * averageSpanLength]
                                            console.log("newSpan", newSpan)
                                            return adjustSpanValue(
                                                newSpan,
                                                0, newSpanIndices, newSpanIndices.length, k, annotation)
                                        }
                                    )
                                    console.log(newSpanIndices)
                                    setSpanIndices([...newSpanIndices])
                                }
                                }></Button>
                            </>

                    }
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => handleCloseDiscard()}>
                        Discard changes/Cancel
                    </Button>
                    <Button onClick={() => handleCloseSave()}>
                        Save changes
                    </Button>

                </DialogActions>
            </BootstrapDialog>
        </div>
    )

}
