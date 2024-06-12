import { useState } from "react";
import "../css/App.css";
import Navbar from "./Navbar";
import MainUI from "./MainUI";
import Weather from "./Weather";
import Mood from "./Mood";

function App() {
  return (
    <>
      <div className="main">
        <Navbar />
        <MainUI />
        <Weather />
        <Mood />
      </div>
    </>
  );
}

export default App;
