import { useState, useEffect } from "react";
import "../css/UI.css";
import axios from "axios";
import Cookies from "js-cookie";

function MainUI() {
  const [currentTrack, setCurrentTrack] = useState({});
  const [currentArtists, setCurrentArtists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentURI, setCurrentURI] = useState(
    "spotify:track:0pZx4Doj3fwVM1PNr2TWmD"
  );
  const [prevURI, setPrevURI] = useState(""); // Add state for previous URI
  const [isPlaying, setIsPlaying] = useState(false);
  const [aiSelection, setAISelection] = useState(true);
  const [weathercon, setWeatherCon] = useState("SUNNY");
  const [emotion, setEmotion] = useState("happy");

  // useEffect(() => {
  //   queue_song();
  // }, []);

  useEffect(() => {
    const fetchCurrentTrack = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/current-track/adamjtroup/${currentURI}`
        );

        if (response.status === 401) {
          const data = await response.json();
          const url = data.auth_url;
          console.log(url);
          const newWindow = window.open(url, "_blank");
        } else if (response.status === 204) {
          // Do nothing, same song
        } else {
          const data = await response.json();
          setCurrentTrack(data.track);
          setCurrentArtists(data.artists);
          setCurrentURI(data.track.item.uri);
          setIsPlaying(data.track.is_playing);
          console.log(data);

          // Check if the current URI is different from the previous URI
          if (data.track.item.uri !== prevURI && !loading) {
            setPrevURI(data.track.item.uri); // Update prevURI to the new URI
            queue_song();
          }

          setLoading(false);
        }
      } catch (error) {
        console.error("Error fetching current track:", error);
      }
    };

    // Fetch current track initially
    fetchCurrentTrack();

    // Polling interval (e.g., every 5 seconds)
    const intervalId = setInterval(() => {
      fetchCurrentTrack();
    }, 4000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [currentURI, prevURI]); // Add currentURI and prevURI as dependencies of useEffect

  const queue_song = async () => {
    if (Cookies.get("emotion")) {
      setEmotion(Cookies.get("emotion"));
    }
    if (Cookies.get("weathercon")) {
      setWeatherCon(Cookies.get("weathercon"));
    }
    if (aiSelection) {
      try {
        console.log(weathercon, emotion);
        const response = await fetch(`http://127.0.0.1:8000/api/queue`, {
          body: JSON.stringify({
            username: "adamjtroup",
            weather: weathercon.toLowerCase(),
            mood: emotion,
          }),
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
        });

        if (response.status === 200) {
          const data = await response.json();
          const queued_uri = data.song.available_markets.uri;
          setPrevURI(queued_uri); // This ensures we keep track of the newly queued song URI
        }
      } catch (error) {
        console.error("Error queuing song:", error);
      }
    }
  };

  const getPopularityColor = (popularity) => {
    if (popularity <= 33) {
      return "red";
    } else if (popularity <= 66) {
      return "silver";
    } else if (popularity <= 89.999999) {
      return "green";
    } else {
      return "gold";
    }
  };

  const getRandomImage = (images) => {
    if (images.length === 0) return ""; // Fallback if there are no images
    const randomIndex = Math.floor(Math.random() * images.length);
    return images[randomIndex].url;
  };

  const skipSong = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/skip-song/adamjtroup`,
        {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
        }
      );

      if (response.status === 200) {
        //
      }
    } catch (error) {
      console.error("Error fetching current track:", error);
    }
  };
  const pauseSong = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/pause-song/adamjtroup`,
        {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
        }
      );

      if (response.status === 200) {
        setIsPlaying(false);
      }
    } catch (error) {
      console.error("Error fetching current track:", error);
    }
  };
  const playSong = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/play-song/adamjtroup`,
        {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
        }
      );

      if (response.status === 200) {
        setIsPlaying(true);
      }
    } catch (error) {
      console.error("Error fetching current track:", error);
    }
  };
  const rewindSong = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/rewind-song/adamjtroup`,
        {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
        }
      );

      if (response.status === 200) {
        //
      }
    } catch (error) {
      console.error("Error fetching current track:", error);
    }
  };

  const handleAiSelectionChange = (e) => {
    setAISelection(e.target.checked);
  };

  return (
    <>
      <div className="main-ui">
        {loading ? (
          <p>Loading</p>
        ) : (
          <>
            <div className="ai-select-container">
              <label htmlFor="ai-select">AI Song Selection:</label>
              <input
                type="checkbox"
                checked={aiSelection}
                id="ai-select"
                onChange={(e) => {
                  handleAiSelectionChange(e);
                }}
              />
            </div>
            <p className="curr-playing">Currently playing:</p>
            <div className="album-cover-container">
              <img
                src={currentTrack.item.album.images[0].url}
                id="album-cover"
              />
            </div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="50"
              height="50"
              fill="currentColor"
              className="bi bi-play-circle skip-btn"
              viewBox="0 0 16 16"
              onClick={skipSong}
            >
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16" />
              <path d="M4.271 5.055a.5.5 0 0 1 .52.038L7.5 7.028V5.5a.5.5 0 0 1 .79-.407L11 7.028V5.5a.5.5 0 0 1 1 0v5a.5.5 0 0 1-1 0V8.972l-2.71 1.935a.5.5 0 0 1-.79-.407V8.972l-2.71 1.935A.5.5 0 0 1 4 10.5v-5a.5.5 0 0 1 .271-.445" />
            </svg>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="50"
              height="50"
              fill="currentColor"
              className="bi bi-skip-backward-circle rewind-btn"
              viewBox="0 0 16 16"
              onClick={rewindSong}
            >
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16" />
              <path d="M11.729 5.055a.5.5 0 0 0-.52.038L8.5 7.028V5.5a.5.5 0 0 0-.79-.407L5 7.028V5.5a.5.5 0 0 0-1 0v5a.5.5 0 0 0 1 0V8.972l2.71 1.935a.5.5 0 0 0 .79-.407V8.972l2.71 1.935A.5.5 0 0 0 12 10.5v-5a.5.5 0 0 0-.271-.445" />
            </svg>
            <div className="music-info">
              <div>
                <p>{currentTrack.item.name}</p>
                {isPlaying ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="50"
                    height="50"
                    fill="currentColor"
                    className="bi bi-pause-circle pause-btn"
                    viewBox="0 0 16 16"
                    onClick={pauseSong}
                  >
                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16" />
                    <path d="M5 6.25a1.25 1.25 0 1 1 2.5 0v3.5a1.25 1.25 0 1 1-2.5 0zm3.5 0a1.25 1.25 0 1 1 2.5 0v3.5a1.25 1.25 0 1 1-2.5 0z" />
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="50"
                    height="50"
                    fill="currentColor"
                    className="bi bi-play-circle play-btn"
                    viewBox="0 0 16 16"
                    onClick={playSong}
                  >
                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16" />
                    <path d="M6.271 5.055a.5.5 0 0 1 .52.038l3.5 2.5a.5.5 0 0 1 0 .814l-3.5 2.5A.5.5 0 0 1 6 10.5v-5a.5.5 0 0 1 .271-.445" />
                  </svg>
                )}
                <div>
                  {currentArtists.map((artist, index) => (
                    <span key={index} className="artist-name">
                      <a
                        href={artist.external_urls.spotify}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {artist.name}
                      </a>
                      {index !== currentArtists.length - 1 && ", "}
                      <div className="info-card">
                        <p>{artist.name}</p>
                        <img
                          src={getRandomImage(artist.images)}
                          alt={artist.name}
                          id="artist-img"
                        />
                        <p>
                          Popularity:
                          <span
                            className={`popularity ${getPopularityColor(
                              artist.popularity
                            )}`}
                          >
                            {artist.popularity} / 100
                          </span>
                        </p>
                      </div>
                    </span>
                  ))}
                </div>
              </div>
            </div>{" "}
          </>
        )}
      </div>
    </>
  );
}

export default MainUI;
