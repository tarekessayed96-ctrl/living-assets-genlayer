import { useEffect, useState } from "react";

const CONTRACT_ADDRESS =
  "0x75d4A841441E1A5d0218f1FA7fA7e30A81D1DbAC";

const DEMO_ASSET = {
  name: "Kylian Mbappé",
  type: "FOOTBALL_PLAYER",
  power: 72,
  level: 1,
  experience: 10,
  goals: 1,
  assists: 0,
  verified_events: 1,
  rejected_events: 0,
};

function App() {
  const [asset, setAsset] = useState(DEMO_ASSET);
  const [eventType, setEventType] = useState("GOAL");
  const [value, setValue] = useState(1);
  const [source1, setSource1] = useState("");
  const [source2, setSource2] = useState("");
  const [status, setStatus] = useState("READY");

  const xpProgress = Math.min((asset.experience % 100), 100);

  useEffect(() => {
    document.title = "Living Asset Intelligence Hub";
  }, []);

  const handleVerify = async (e) => {
    e.preventDefault();

    if (!source1 || !source2) {
      setStatus("TWO SOURCES REQUIRED");
      return;
    }

    setStatus("VERIFYING WITH GENLAYER...");

    // Frontend preview mode.
    // Contract connection will be added after the UI is ready.
    setTimeout(() => {
      setStatus("VERIFICATION REQUEST CREATED");
    }, 1800);
  };

  return (
    <div className="app">
      <div className="background-orb orb-one" />
      <div className="background-orb orb-two" />

      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">LA</div>
          <div>
            <div className="brand-name">LIVING ASSET</div>
            <div className="brand-subtitle">AI-VERIFIED DIGITAL IDENTITY</div>
          </div>
        </div>

        <div className="network">
          <span className="pulse" />
          GENLAYER STUDIONET
        </div>
      </header>

      <main className="container">

        <section className="hero">
          <div>
            <span className="eyebrow">AUTONOMOUS DIGITAL ASSET</span>
            <h1>
              Assets that <span>evolve</span> with reality.
            </h1>
            <p>
              Living Asset transforms verified real-world events into
              permanent, dynamic on-chain state.
            </p>
          </div>

          <div className="contract-card">
            <span>CONTRACT</span>
            <strong>
              {CONTRACT_ADDRESS.slice(0, 8)}...
              {CONTRACT_ADDRESS.slice(-6)}
            </strong>
          </div>
        </section>

        <section className="dashboard-grid">

          <div className="panel identity-panel">
            <div className="panel-label">ASSET IDENTITY</div>

            <div className="player">
              <div className="avatar">
                ⚡
              </div>

              <div>
                <h2>{asset.name}</h2>
                <p>{asset.type}</p>
              </div>
            </div>

            <div className="power">
              <div>
                <span>POWER</span>
                <strong>{asset.power}</strong>
              </div>

              <div className="power-bar">
                <div style={{ width: `${asset.power}%` }} />
              </div>
            </div>

            <div className="level-row">
              <div>
                <small>LEVEL</small>
                <strong>{asset.level}</strong>
              </div>

              <div className="xp">
                <div className="xp-header">
                  <small>EXPERIENCE</small>
                  <small>{asset.experience} XP</small>
                </div>

                <div className="xp-bar">
                  <div style={{ width: `${xpProgress}%` }} />
                </div>
              </div>
            </div>
          </div>

          <div className="panel stats-panel">
            <div className="panel-label">LIVE STATE</div>

            <div className="stats">
              <Stat label="GOALS" value={asset.goals} icon="⚽" />
              <Stat label="ASSISTS" value={asset.assists} icon="◈" />
              <Stat
                label="VERIFIED"
                value={asset.verified_events}
                icon="✓"
              />
              <Stat
                label="REJECTED"
                value={asset.rejected_events}
                icon="×"
              />
            </div>
          </div>

        </section>

        <section className="verification-layout">

          <div className="panel verify-panel">
            <div className="panel-heading">
              <div>
                <div className="panel-label">EVENT VERIFICATION</div>
                <h2>Feed reality into the asset</h2>
              </div>

              <div className="status">
                <span />
                {status}
              </div>
            </div>

            <form onSubmit={handleVerify}>

              <div className="form-grid">

                <label>
                  EVENT TYPE
                  <select
                    value={eventType}
                    onChange={(e) => setEventType(e.target.value)}
                  >
                    <option value="GOAL">GOAL</option>
                    <option value="ASSIST">ASSIST</option>
                  </select>
                </label>

                <label>
                  VALUE
                  <input
                    type="number"
                    min="1"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                  />
                </label>

              </div>

              <label>
                SOURCE 01
                <input
                  type="url"
                  placeholder="https://..."
                  value={source1}
                  onChange={(e) => setSource1(e.target.value)}
                />
              </label>

              <label>
                SOURCE 02
                <input
                  type="url"
                  placeholder="https://..."
                  value={source2}
                  onChange={(e) => setSource2(e.target.value)}
                />
              </label>

              <button type="submit">
                VERIFY EVENT
                <span>→</span>
              </button>

            </form>
          </div>

          <div className="panel architecture-panel">

            <div className="panel-label">VERIFICATION ENGINE</div>

            <h2>Reality → Consensus → State</h2>

            <div className="flow">

              <Flow
                number="01"
                title="REAL EVENT"
                text="A football event happens in the real world."
              />

              <Flow
                number="02"
                title="EVIDENCE"
                text="Independent sources provide verifiable evidence."
              />

              <Flow
                number="03"
                title="AI CONSENSUS"
                text="GenLayer validators evaluate the evidence."
              />

              <Flow
                number="04"
                title="LIVING STATE"
                text="The asset evolves when consensus is reached."
              />

            </div>
          </div>

        </section>

        <section className="panel philosophy">

          <div>
            <span className="eyebrow">THE PROTOCOL</span>
            <h2>
              Not a static NFT.
              <br />
              A digital asset with memory.
            </h2>
          </div>

          <p>
            Every verified event becomes part of the asset's evolving
            identity. The result is a digital object whose state is
            connected to independently verified reality.
          </p>

        </section>

        <footer>
          <span>LIVING ASSET PROTOCOL</span>
          <span>POWERED BY GENLAYER</span>
          <span>STUDIONET</span>
        </footer>

      </main>
    </div>
  );
}

function Stat({ label, value, icon }) {
  return (
    <div className="stat">
      <span className="stat-icon">{icon}</span>
      <strong>{value}</strong>
      <small>{label}</small>
    </div>
  );
}

function Flow({ number, title, text }) {
  return (
    <div className="flow-item">
      <div className="flow-number">{number}</div>

      <div>
        <strong>{title}</strong>
        <p>{text}</p>
      </div>
    </div>
  );
}

export default App;
