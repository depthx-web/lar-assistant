import { useUI } from "../UI";

export default function ModelsScreen() {
  const { tr, outage, setOutage } = useUI();
  return (
    <section className="screen" id="s-models" aria-labelledby="h-models">
      <div className="pagehead">
        <div>
          <h1 id="h-models" className="t">{tr("Models & System")}</h1>
          <p className="sub t">{tr("Choose which local model handles each task")}</p>
        </div>
        {" "}
        <div className="actions">
          <button className="btn" id="simOutage" onClick={() => setOutage(!outage)}>
            <svg className="i">
              <use href="#i-alert"></use>
            </svg>
            <span className="t" id="simTx">{tr(outage ? "Restore Ollama" : "Simulate Ollama outage")}</span>
          </button>
        </div>
      </div>
      {" "}
      <div className="alert" id="outage" role="alert" hidden={!outage}>
        <svg className="i" style={{color: "var(--crit)", marginTop: "2px"}}>
          <use href="#i-alert"></use>
        </svg>
        {" "}
        <div>
          <h3 className="t">{tr("Ollama unavailable")}</h3>
          <p className="t">{tr("The application cannot currently communicate with the local AI service. Check that Ollama is running.")}</p>
          {" "}
          <div className="actions" style={{marginTop: "8px"}}>
            <button className="btn sm">
              <svg className="i">
                <use href="#i-refresh"></use>
              </svg>
              <span className="t">{tr("Retry")}</span>
            </button>
            <details>
              <summary className="faint" style={{cursor: "pointer"}}>
                <span className="t">{tr("Technical details")}</span>
              </summary>
              <div className="mono faint" style={{marginTop: "6px"}}>
                {"connect ECONNREFUSED 127.0.0.1:11434"}
              </div>
            </details>
          </div>
        </div>
      </div>
      {" "}
      <div className="grid2">
        <div className="tbl">
          <table>
            <thead>
              <tr>
                <th className="t">{tr("Role")}</th>
                <th className="t">{tr("Model")}</th>
                <th className="t">{tr("Status")}</th>
                <th className="t">{tr("Context")}</th>
                <th className="t">{tr("Memory")}</th>
                <th className="t">{tr("Speed")}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="t">{tr("General chat")}</td>
                <td>
                  <select className="field mono" aria-label="General chat model">
                    <option>
                      {"qwen2.5:14b"}
                    </option>
                    <option>
                      {"qwen2.5:7b"}
                    </option>
                    <option>
                      {"llama3.1:8b"}
                    </option>
                  </select>
                </td>
                <td>
                  <span className={"badge st-model t " + (outage ? "b-crit" : "b-ok")}>{tr(outage ? "Unavailable" : "Ready")}</span>
                </td>
                <td className="mono">
                  {"32k"}
                </td>
                <td className="mono">
                  {"9.4 GB"}
                </td>
                <td className="mono">
                  {"14 tok/s"}
                </td>
              </tr>
              <tr>
                <td className="t">{tr("Literature analysis")}</td>
                <td>
                  <select className="field mono" aria-label="Literature analysis model">
                    <option>
                      {"qwen2.5:14b"}
                    </option>
                    <option>
                      {"qwen2.5:7b"}
                    </option>
                    <option>
                      {"llama3.1:8b"}
                    </option>
                  </select>
                </td>
                <td>
                  <span className={"badge st-model t " + (outage ? "b-crit" : "b-ok")}>{tr(outage ? "Unavailable" : "Ready")}</span>
                </td>
                <td className="mono">
                  {"32k"}
                </td>
                <td className="mono">
                  {"9.4 GB"}
                </td>
                <td className="mono">
                  {"14 tok/s"}
                </td>
              </tr>
              <tr>
                <td className="t">{tr("Academic writing")}</td>
                <td>
                  <select className="field mono" aria-label="Academic writing model">
                    <option>
                      {"qwen2.5:14b"}
                    </option>
                    <option>
                      {"qwen2.5:7b"}
                    </option>
                    <option>
                      {"llama3.1:8b"}
                    </option>
                  </select>
                </td>
                <td>
                  <span className={"badge st-model t " + (outage ? "b-crit" : "b-ok")}>{tr(outage ? "Unavailable" : "Ready")}</span>
                </td>
                <td className="mono">
                  {"32k"}
                </td>
                <td className="mono">
                  {"9.4 GB"}
                </td>
                <td className="mono">
                  {"14 tok/s"}
                </td>
              </tr>
              <tr>
                <td className="t">{tr("Summarization")}</td>
                <td>
                  <select className="field mono" aria-label="Summarization model">
                    <option>
                      {"qwen2.5:7b"}
                    </option>
                    <option>
                      {"qwen2.5:14b"}
                    </option>
                    <option>
                      {"llama3.1:8b"}
                    </option>
                  </select>
                </td>
                <td>
                  <span className={"badge st-model t " + (outage ? "b-crit" : "b-ok")}>{tr(outage ? "Unavailable" : "Ready")}</span>
                </td>
                <td className="mono">
                  {"32k"}
                </td>
                <td className="mono">
                  {"5.1 GB"}
                </td>
                <td className="mono">
                  {"28 tok/s"}
                </td>
              </tr>
              <tr>
                <td className="t">{tr("Embeddings")}</td>
                <td>
                  <select className="field mono" aria-label="Embedding model">
                    <option>
                      {"nomic-embed-text"}
                    </option>
                    <option>
                      {"bge-m3"}
                    </option>
                  </select>
                </td>
                <td>
                  <span className={"badge st-model t " + (outage ? "b-crit" : "b-ok")}>{tr(outage ? "Unavailable" : "Ready")}</span>
                </td>
                <td className="mono">
                  {"8k"}
                </td>
                <td className="mono">
                  {"0.6 GB"}
                </td>
                <td className="mono">
                  {"fast"}
                </td>
              </tr>
              <tr>
                <td className="t">{tr("Classification")}</td>
                <td>
                  <select className="field mono" aria-label="Classification model">
                    <option>
                      {"qwen2.5:7b"}
                    </option>
                    <option>
                      {"llama3.1:8b"}
                    </option>
                  </select>
                </td>
                <td>
                  <span className={"badge st-model t " + (outage ? "b-crit" : "b-ok")}>{tr(outage ? "Unavailable" : "Ready")}</span>
                </td>
                <td className="mono">
                  {"8k"}
                </td>
                <td className="mono">
                  {"5.1 GB"}
                </td>
                <td className="mono">
                  {"28 tok/s"}
                </td>
              </tr>
              <tr>
                <td className="t">{tr("Journal evaluation")}</td>
                <td>
                  <select className="field mono" aria-label="Journal evaluation model">
                    <option>
                      {"qwen2.5:14b"}
                    </option>
                    <option>
                      {"qwen2.5:7b"}
                    </option>
                  </select>
                </td>
                <td>
                  <span className={"badge st-model t " + (outage ? "b-crit" : "b-ok")}>{tr(outage ? "Unavailable" : "Ready")}</span>
                </td>
                <td className="mono">
                  {"32k"}
                </td>
                <td className="mono">
                  {"9.4 GB"}
                </td>
                <td className="mono">
                  {"14 tok/s"}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        {" "}
        <section className="box">
          <header>
            <h2 className="t">{tr("System status")}</h2>
          </header>
          <div className="in">
            <div className="kv">
              <span className="t">{tr("Backend")}</span>
              <span className="s">
                <i className="dot"></i>
                <span className="t">{tr("Online")}</span>
              </span>
            </div>
            {" "}
            <div className="kv">
              <span className="t">{tr("Database")}</span>
              <span className="s">
                <i className="dot"></i>
                <span className="t">{tr("Connected")}</span>
              </span>
            </div>
            {" "}
            <div className="kv">
              <span>
                {"Ollama"}
              </span>
              <span className="s">
                <i className={"dot dyn-ollama" + (outage ? " crit" : "")}></i>
                <span className="t dyn-ollama-tx">{tr(outage ? "Disconnected" : "Connected")}</span>
              </span>
            </div>
            {" "}
            <div className="kv">
              <span className="t">{tr("Embedding")}</span>
              <span className="s">
                <i className="dot"></i>
                <span className="t">{tr("Ready")}</span>
              </span>
            </div>
            {" "}
            <div className="kv">
              <span className="t">{tr("Vector DB")}</span>
              <span className="s">
                <i className="dot"></i>
                <span className="t">{tr("Ready")}</span>
              </span>
            </div>
            {" "}
            <div className="kv">
              <span>
                {"OCR"}
              </span>
              <span className="s">
                <i className="dot"></i>
                <span className="t">{tr("Ready")}</span>
              </span>
            </div>
            {" "}
            <div className="kv">
              <span className="t">{tr("Storage")}</span>
              <span className="s">
                <i className="dot"></i>
                <span className="t">{tr("Ready")}</span>
              </span>
            </div>
          </div>
        </section>
      </div>
    </section>
  );
}
