import React, { useContext, useEffect, useState } from "react";
import MacroComponentSwitch from "./../src/components/MacroComponentSwitch";

const Library = () => {
  return <MacroComponentSwitch component={"graph"} url={"/library"} />;
};

export default Library;
