import React from "react";
import Url2Difference from "../src/components/Url2Difference";
import UploadDocument from "../src/components/Upload";
import GoldenSnake from "../src/components/GoldenSnake";
import Audiobook from "../src/components/Audiobook";
import Captcha from "../src/components/Captcha";

const Annotation = () => {
  const id = null;
  const shortId = null;
  return (
    <>
      <GoldenSnake>
        <div>
          <a href="/library">Universe of documents</a>
        </div>

        <div>
          <a href={"/difference?id=" + id}>Read annotated paper</a>
        </div>
        <div>
          <Audiobook />
        </div>
        <div>
          <a href={shortId}>Original PDF</a>
        </div>
        <div>
          <a href={"/upload_annotation?id=" + id}>Improve layout recognition</a>
        </div>
        <div>
          <Captcha />
        </div>
        <div>
          <Url2Difference />
        </div>

        <UploadDocument />
      </GoldenSnake>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="100%"
        height="100%"
        viewBox="0 0  1020 630"
        preserveAspectRatio="xMinYMin meet"
      >
        <line id="e1_line" x1="179.00" y1="217.00" x2="343.00" y2="217.00" />
        <line id="e2_line" x1="179.00" y1="216.00" x2="179.00" y2="63.00" />
        <line id="e3_line" x1="344.00" y1="218.00" x2="345.00" y2="365.00" />
        <text x="179.00" y="200.00">
          xxxx NO BUTTON xxxx
        </text>

        <line id="e4_line" x1="345.00" y1="363.00" x2="181.00" y2="365.00" />
        <line id="e5_line" x1="182.00" y1="366.00" x2="183.00" y2="467.00" />
        <line id="e6_line" x1="183.00" y1="466.00" x2="240.00" y2="466.00" />
        <line id="e7_line" x1="241.00" y1="466.00" x2="243.00" y2="520.00" />
      </svg>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="100%"
        height="100%"
        viewBox="0 0  1020 630"
        preserveAspectRatio="xMinYMin meet"
      >
        <line id="e8_line" x1="625.00" y1="172.00" x2="629.00" y2="490.00" />
        <line id="e9_line" x1="520.00" y1="257.00" x2="890.00" y2="251.00" />
        <line id="e10_line" x1="818.00" y1="167.00" x2="824.00" y2="493.00" />
        <line id="e11_line" x1="516" y1="427" x2="900.00" y2="422.00" />
      </svg>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 240">
        <rect width="100%" height="100%" fill="lightblue"></rect>
        <g>
          <path
            id="Chile"
            fill="green"
            d="m480 222-3 0h-5l-6-14 3 3 4 5 8 4 7 2-1 3-4 0-3-2zm-30-207 11 10 5 1 7 5 6 3 1 3-4 10 6 2 6 1 4-1 4-5 0-6 3-1 3 4 0 5-4 4-3 3-5 6-6 9-1 5 0 7 1 6-1 1 0 4 0 3 8 6 0 4 4 3 0 3-3 8-7 4-10 1-6-1 2 4 0 5 2 3-3 2-5 1-6-2-2 2 3 6 4 2 2-2 3 3-4 2-3 4 1 6 0 3h-5l-3 3 0 5 7 5 5 1 0 6-5 4-1 7-4 2-1 3 4 7 5 4-2 0-5-1-12-1-4-4-2-5-3 0-3-2-3-7 3-3 0-4-2-3 1-5-1-8-2-4 2-1-1-2-3-1 1-3-3-2-4-7 2-1-3-8-1-7 0-6 3-2-3-6-2-6 3-4-1-5 2-6-1-6-2-1-5-11 2-7-2-6 1-6 3-6 3-4-2-3 1-2-2-11 6-3 1-7-1-2 4-6 8 2 4 5 2-5 6 0 1 1z"
          ></path>
        </g>
        <g>
          <path
            id="Canada"
            fill="orange"
            pathLength="100"
            d="m310 180-2-4 3-9-2-2-4 1-1-2-6 5-3 5-3 3-3 1-2 0-1 2h-9l-8 0-3 1-7 4v0l-1 0-2 1-2 1-2-1-5 1-4 1-2 1-2 2 2 1 2 0h0l0 2-5 1-3 1-2 1-3-1-2 0-3 2-5 2-3 0 2-2 4-4 4-2 1-2 1-3 4-4 1-4 1 4 4 1 2-2-1-5-1-2-4-1-4-1h-4l-3-1 0-1-1 1-1 0 2-2-2-1 2-2-1-2 2-2-5-1 0-4-1-1-3 0-4-1-2 1-2 2-3 1-3 3-5-2-4 1-4-2-5-1-3 0-1-1 1-3h-2l-1 2h-137l-5-6-2-3-7-3 1-6 4-4-4-3 3-5-2-4 3-3 5-3 3-4-5-4 1-7 1-4-2-3-1-2 1-3-7 2-8 3 0-4-1-3-3-2-4 0 37-32 25-20 6 1 3 3 4 1 6-2 7-2 5 1 9-2 8-1 0 2 5-1 4-3 2 1 1 5 10-4-4 4 6-1 3-2 5 0 4 2 8 2 5 1 4 0 3 3-9 3 6 1 12-1 4-1 1 3 7-3-2-2 5-2 5 0 4-1 2 1 2 3 5 0 5 3 7-1 6 0 2-3 5-1 5 2-4 5 6-4 3 0 6-6-2-3-3-2 6-6 8-4 5 1 2 2 0 6-6 3 7 1-4 6 9-4 2 4-4 4 1 4 7-4 7-5 5-6 6 0 5 1 4 3-2 3-5 3 1 3-2 3-11 4-7 1-3-2-3 3-7 5-3 3-8 4-7 0-5 2-3 4-6 1-9 5-9 7-5 5-5 7 6 1-2 6-1 5 7-1 7 3 3 2 2 3 5 2 4 3 8 0 5 1-4 5-2 6 0 7 4 6 5-2 6-6 2-10-2-3 9-3 8-4 5-4 2-4 0-5-3-5 9-6 1-5 4-9 4-1 7 2 4 1 5-2 3 2 4 3 0 2 8 1-3 5-2 7 4 1 2 4 8-3 8-7 4-3 1 5 3 8 2 7-3 4 5 3 3 3 7 2 2 2v5l3 1 1 2-2 7-4 2-4 2-9 2-8 5-9 1-10-1h-7l-5 0-6 5-7 3-10 8-8 6 5-1 11-8 12-5 8-1 3 3-6 4-1 7 0 5 6 3 9-1 7-7-1 5 3 2-7 4-12 4-6 3-7 5-4-1 2-5 10-5-8 0-6 1z"
          ></path>
        </g>
        <text font-size="60px">
          <textPath startOffset="36" href="#Canada">
            Canada
          </textPath>
        </text>
      </svg>
    </>
  );
};

export default Annotation;
