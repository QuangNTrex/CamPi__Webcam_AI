import { useState } from "react";

function App() {
  const [angle, setAngle] = useState(90);
  const [status, setStatus] = useState("");

  const API_URL = "http://192.168.10.1:8000"; // 🔥 đổi IP Raspberry Pi

  // Gửi góc đến server
  const sendAngle = async () => {
    try {
      const res = await fetch(`${API_URL}/servo/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ angle: 180 - Number(angle) }),
      });

      const data = await res.json();
      setStatus(`Moved to ${data.angle}°`);
    } catch (err) {
      setStatus("Error sending request");
      console.error(err);
    }
  };

  const sendAngleNomally = async () => {
    try {
      const res = await fetch(`${API_URL}/servo/set`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ angle: 180 - Number(angle) }),
      });

      const data = await res.json();
      setStatus(`Moved to ${data.angle}°`);
    } catch (err) {
      setStatus("Error sending request");
      console.error(err);
    }
  };

  // Lấy trạng thái hiện tại
  const getStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/servo/status`);
      const data = await res.json();
      setStatus(`Current angle: ${data.angle}°`);
    } catch (err) {
      setStatus("Error getting status");
    }
  };

  // Center servo
  const centerServo = async () => {
    await fetch(`${API_URL}/servo/center`, { method: "POST" });
    setStatus("Centered");
  };

  // Stop servo
  const stopServo = async () => {
    await fetch(`${API_URL}/servo/stop`, { method: "POST" });
    setStatus("Stopped");
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <img
        src={`${API_URL}/video`}
        style={{ width: "640px", imageRendering: "auto" }}
      />

      <h2>{angle}°</h2>

      <input
        type="range"
        min="0"
        max="180"
        value={angle}
        onChange={(e) => {
          //sendAngle();
          setAngle(e.target.value)
          
        }}
        style={{ width: "300px" }}
      />

      <div style={{ marginTop: "20px" }}>
        <button onClick={sendAngleNomally} style={{ marginLeft: "10px" }}>
          Send
        </button>
        <button onClick={sendAngle}>Send Slower</button>
        
      </div>

      <div style={{ marginTop: "20px" }}>
        <button onClick={centerServo}>Center</button>
        <button onClick={stopServo} style={{ marginLeft: "10px" }}>
          Stop
        </button>
      </div>

      {/* <p style={{ marginTop: "20px", color: "green" }}>{status}</p> */}
    </div>
  );
}

export default App;