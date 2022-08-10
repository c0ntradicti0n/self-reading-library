import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import Typography from "@mui/material/Typography";
import { styled as sty } from "@mui/material/styles";
import { Slider } from "@mui/material";
import { ThreeDots } from "react-loader-spinner";
import {
  addSpan,
  adjustSpanValue,
  getSpans,
  popSpan,
  spans2annotation,
} from "../helpers/span_tools";

const BootstrapDialog = sty(Dialog)(({ theme }) => ({
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

export function AnnotationTable(props: {
  annotation: string[][];
  spans: [string, number, number, string[]][];
}) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap" }}>
      {props.annotation.map(([word, tag], index) => {
        let span_no =
          props.spans.find(
            ([, begin, end]) => index >= begin && index < end
          )?.[0] ?? "O";
        return (
          <span key={index} className={"tag span_" + span_no}>
            {word}
          </span>
        );
      })}
    </div>
  );
}

const BootstrapDialogTitle = (props) => {
  const { children, onClose, ...other } = props;

  return (
    <DialogTitle sx={{ m: 0, p: 2 }} {...other}>
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
          <CloseIcon />
        </IconButton>
      ) : null}
    </DialogTitle>
  );
};

BootstrapDialogTitle.propTypes = {
  children: PropTypes.node,
  onClose: PropTypes.func.isRequired,
};

export default function SpanAnnotation({
  value,
  meta,
  text,
  onClose,
  service,
}) {
  const [open, setOpen] = useState(true);
  const [annotation, setAnnotation] = useState(null);

  // @ts-ignore
  const [spanIndices, setSpanIndices] = useState<
    [string, number, number, string[]][]
  >([]);
  useEffect(() => {
    (async () => {
      await service.fetch_one([value, text, meta["pdf_path"]], (res) => {
        setAnnotation(res);
        setSpanIndices(getSpans(res));
      });
    })();
  }, []);

  const handleClickOpen = () => {
    setOpen(true);
  };
  const handleCloseSave = () => {
    console.log("save");
    (async () => {
      await service.save(
        value,
        spans2annotation(annotation, spanIndices),
        () => {
          console.log("saved");
        }
      );
    })();
    setOpen(false);
    onClose();
  };

  const handleCloseDiscard = () => {
    setOpen(false);
    console.log("close discard");
    onClose();
  };

  console.log(spanIndices);
  return (
    <div
      onClick={(e) => {
        e.stopPropagation();
        e.preventDefault();
        console.log("stop it! click");
      }}
      onMouseUp={(e) => {
        e.stopPropagation();
        e.preventDefault();
        console.log("stop it! up");
      }}
      onChange={(e) => {
        e.stopPropagation();
        e.preventDefault();
        console.log("stop it! change");
      }}
      onBlur={(e) => {
        e.stopPropagation();
        e.preventDefault();
        console.log("stop it! blur");
      }}
    >
      <Button variant="outlined" onClick={handleClickOpen}>
        Open dialog
      </Button>
      <BootstrapDialog
        aria-labelledby="customized-dialog-title"
        open={open}
        fullWidth
        maxWidth={"xl"}
        style={{ marginRight: "30%" }}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          console.log("stop it!");
        }}
      >
        <BootstrapDialogTitle onClose={() => console.log("Closing dialogue")}>
          Teach the difference
        </BootstrapDialogTitle>
        <DialogContent dividers>
          {!annotation ? (
            <ThreeDots />
          ) : (
            <>
              <Typography gutterBottom>
                <AnnotationTable
                  annotation={annotation}
                  spans={spanIndices}
                ></AnnotationTable>
              </Typography>
              <Typography gutterBottom>
                {spanIndices.map(([tag, i1, i2, ws], i) => (
                  <div key={i}>
                    <Button
                      startIcon="minus"
                      onClick={() => {
                        popSpan(spanIndices, i, setSpanIndices);
                      }}
                    ></Button>
                    <b>{tag}</b>
                    <br />
                    <div
                      style={{
                        marginRight: "0px",
                        marginLeft: "0px",
                      }}
                    >
                      <div
                        style={{
                          wordWrap: "break-word",
                          whiteSpace: "normal",
                          width: "80vw",
                        }}
                      >
                        {ws.map((w, iii) => (
                          <span key={iii} className={"tag span_" + tag}>
                            {w}
                          </span>
                        ))}
                      </div>

                      <Slider
                        aria-label="annotation"
                        value={spanIndices[i].slice(1, 3) as number[]}
                        valueLabelDisplay="auto"
                        onChange={(event, newValue, activeThumb) => {
                          console.log(
                            "changing slider",
                            event,
                            newValue,
                            activeThumb
                          );
                          setSpanIndices(
                            adjustSpanValue(
                              newValue,
                              activeThumb,
                              spanIndices,
                              i,
                              tag,
                              annotation
                            )
                          );
                          event.stopPropagation();
                          event.stopImmediatePropagation();
                          console.log("stop it!");
                          return false;
                        }}
                        onMouseUp={(event) => {
                          event.stopPropagation();
                          console.log("stop it!");
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
              <Button
                startIcon="add"
                onClick={() => {
                  setSpanIndices(addSpan(spanIndices, annotation));
                }}
              ></Button>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleCloseDiscard()}>
            Discard changes/Cancel
          </Button>
          <Button onClick={() => handleCloseSave()}>Save changes</Button>
        </DialogActions>
      </BootstrapDialog>
    </div>
  );
}
