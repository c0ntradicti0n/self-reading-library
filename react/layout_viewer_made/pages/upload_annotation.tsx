import React, { useContext, useEffect, useState } from "react";
import MacroComponentSwitch from "./../src/components/MacroComponentSwitch";

const Upload_Annotation = () => {
  return (
    <MacroComponentSwitch
      component={"upload_annotation"}
      url={"/upload_annotation"}
    />
  );
};

export default Upload_Annotation;
