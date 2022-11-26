import React, { useContext, useEffect, useState } from "react";
import MacroComponentSwitch from "./../src/components/MacroComponentSwitch";

const Annotation = () => {
  return <MacroComponentSwitch component={"annotation"} url={"/annotation"} />;
};

export default Annotation;
