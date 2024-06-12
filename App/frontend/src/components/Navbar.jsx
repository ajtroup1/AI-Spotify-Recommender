import { useState } from "react";
import "../css/App.css";

function Navbar() {
  return (
    <>
      <div className="navbar-main">
        <div className="nav-logo-container">
          <img
            id="navbar-logo"
            src="https://static-00.iconduck.com/assets.00/youtube-music-icon-2048x2048-11gyian5.png"
          />
          <h2>AI Spotify Recommender</h2>
        </div>
        <div className=""></div>
      </div>
    </>
  );
}

export default Navbar;
