import {useState} from "react";
import PropTypes from 'prop-types';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Typography from '@mui/material/Typography';
import {styled as sty} from '@mui/material/styles';
import styled from 'styled-components'
import {Slider} from "@mui/material";
import {getSpans} from "../src/util/annotation.js"

const BootstrapDialog = sty(Dialog)(({theme}) => ({
    '& .MuiDialogContent-root': {
        padding: theme.spacing(2),
        maxWidth: "80%",
                minWidth: "80%",

    },
    '& .MuiDialogActions-root': {
        padding: theme.spacing(1),
    },
}));


const annotation = [
    ["word", "tag"],
    ["the", "B-SUBJ"],
    ["lazy", "I-SUBJ"],
    ["yellow", "I-SUBJ"],
    ["socks", "I-SUBJ"],
    ["glued", "B-CONTRAST"],
    ["on", "B-CONTRAST"],
    ["the", "B-CONTRAST"],
    ["wall", "B-CONTRAST"],
    [".", ""],
        ["word", "tag"],
    ["the", "B-SUBJ"],
    ["lazy", "I-SUBJ"],
    ["yellow", "I-SUBJ"],
    ["socks", "I-SUBJ"],
    ["glued", "B-CONTRAST"],
    ["on", "B-CONTRAST"],
    ["the", "B-CONTRAST"],
    ["wall", "B-CONTRAST"],
    [".", ""]

]


const Table = styled.div`
  display:table;
  width:auto;
  background-color:#eee;
  border:1px solid  #666666;
  border-spacing:5px;
`;
const Rable = styled.div`

  float:left;/*fix for  buggy browsers*/
  display:table-column;
  minwidth:20px;
  background-color:#ccc;

`;
const Call = styled.div`
  display:table-row;
  width:auto;
  clear:both;
`;
const minDistance = 1


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
                        position: 'absolute',
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

function AnnotationTable(props: { annotation: string[][] }) {
    return <Table>{props.annotation.map(([word, tag]) => <Rable>
        <Call>{word}</Call>
        <Call>{tag}</Call>
    </Rable>)}</Table>
}

function valuetext(value) {
    return `${value}°C`;
}


export default function Spannotator({text, onClose}) {
    const [open, setOpen] = useState(true);
    const [spanIndices, setSpanIndices] = useState<[string, number, number][]>(getSpans(annotation));


    const handleClickOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
        onClose();
    };

    return (
        <div>
            <Button variant="outlined" onClick={handleClickOpen}>
                Open dialog
            </Button>
            <BootstrapDialog
                onClose={handleClose}
                aria-labelledby="customized-dialog-title"
                open={open}
                fullWidth
                maxWidth={"xl"}
            >
                <BootstrapDialogTitle id="customized-dialog-title" onClose={handleClose}>
                    Teach the difference
                </BootstrapDialogTitle>
                <DialogContent dividers>
                    <Typography gutterBottom>
                        {text}
                    </Typography>
                    <Typography gutterBottom>
                        <AnnotationTable annotation={annotation}></AnnotationTable>
                    </Typography>
                    <Typography gutterBottom>

                        {spanIndices.map(([tag, i1, i2], i) =>
                            <div>{tag}<Slider
                                aria-label="annotation"
                                value={spanIndices[i].slice(1,3) as number[]}
                                valueLabelDisplay="auto"
                                onChange={(event, newValue, activeThumb) => {
                                    if (!Array.isArray(newValue)) {
                                        return;
                                    }
                                    let value : number[] = null

                                    if (newValue[1] - newValue[0] < minDistance) {
                                        if (activeThumb === 0) {
                                            const clamped = Math.min(newValue[0], 100 - minDistance);
                                            value = ([clamped, clamped + minDistance]);
                                        } else {
                                            const clamped = Math.max(newValue[1], minDistance);
                                            value = ([clamped - minDistance, clamped]);
                                        }
                                    } else {
                                        value = (newValue);
                                    }

                                    console.log(value)

                                    spanIndices[i] = [tag, ...value]
                                    setSpanIndices(spanIndices)

                                }}
                                step={1}
                                marks
                                min={0}
                                max={annotation.length}
                                disableSwap
                                getAriaValueText={valuetext}


                            /></div>
                        )}</Typography>

                </DialogContent>
                <DialogActions>
                    <Button autoFocus onClick={handleClose}>
                        Save changes
                    </Button>
                </DialogActions>
            </BootstrapDialog>
        </div>
    );
}