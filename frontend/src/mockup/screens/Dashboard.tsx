import { useUI } from "../UI";

export default function DashboardScreen() {
  const { tr, outage } = useUI();
  return (
    <section className="screen" id="s-dashboard" aria-labelledby="h-dashboard">
      <div className="pagehead">
        <div>
          <h1 id="h-dashboard" className="t">{tr("Research Overview")}</h1>
          <p className="sub t">{tr("What is happening in your project right now")}</p>
        </div>
        {" "}
        <div className="actions">
          <button className="btn" data-go="papers">
            <svg className="i">
              <use href="#i-upload"></use>
            </svg>
            <span className="t">{tr("Upload paper")}</span>
          </button>
          <button className="btn pri" data-go="manuscript">
            <svg className="i">
              <use href="#i-edit"></use>
            </svg>
            <span className="t">{tr("Continue writing")}</span>
          </button>
        </div>
      </div>
      {" "}
      <div className="stats">
        <div className="stat">
          <b>
            {"3"}
          </b>
          <span className="t">{tr("Active projects")}</span>
        </div>
        {" "}
        <div className="stat">
          <b>
            {"12"}
          </b>
          <span className="t">{tr("Papers")}</span>
        </div>
        {" "}
        <div className="stat">
          <b>
            {"2"}
          </b>
          <span className="t">{tr("Manuscripts")}</span>
        </div>
        {" "}
        <div className="stat">
          <b>
            {"4"}
          </b>
          <span className="t">{tr("Journal profiles")}</span>
        </div>
      </div>
      {" "}
      <ol className="flow" aria-label="Research workflow">
        <li className="done">
          <div className="st">
            <svg className="i">
              <use href="#i-check"></use>
            </svg>
            <span className="t">{tr("Done")}</span>
          </div>
          <div className="nm t">{tr("Import papers")}</div>
        </li>
        {" "}
        <li className="done">
          <div className="st">
            <svg className="i">
              <use href="#i-check"></use>
            </svg>
            <span className="t">{tr("Done")}</span>
          </div>
          <div className="nm t">{tr("Build knowledge base")}</div>
        </li>
        {" "}
        <li className="done">
          <div className="st">
            <svg className="i">
              <use href="#i-check"></use>
            </svg>
            <span className="t">{tr("Done")}</span>
          </div>
          <div className="nm t">{tr("Ask the literature")}</div>
        </li>
        {" "}
        <li className="now" aria-current="step">
          <div className="st">
            <span className="t">{tr("In progress")}</span>
          </div>
          <div className="nm t">{tr("Write manuscript")}</div>
        </li>
        {" "}
        <li className="next">
          <div className="st">
            <span className="t">{tr("Next")}</span>
          </div>
          <div className="nm t">{tr("Check journal fit")}</div>
        </li>
        {" "}
        <li className="next">
          <div className="st">
            <span className="t">{tr("Next")}</span>
          </div>
          <div className="nm t">{tr("Final submission review")}</div>
        </li>
      </ol>
      {" "}
      <div className="grid2">
        <div className="stack">
          <section className="box">
            <header>
              <h2 className="t">{tr("Attention required")}</h2>
              <button className="btn ghost sm" data-go="compliance">
                <span className="t">{tr("Open compliance")}</span>
                <svg className="i flip">
                  <use href="#i-chev"></use>
                </svg>
              </button>
            </header>
            {" "}
            <div className="in">
              <div className="row">
                <span className="sev blocking"></span>
                <div className="grow">
                  <div className="tt t">{tr("Structured Methods section is missing")}</div>
                  <div className="faint">
                    {"Manuscript: Hippocampal atrophy rates · Methods"}
                  </div>
                </div>
                <span className="badge b-crit t">{tr("Blocking")}</span>
              </div>
              {" "}
              <div className="row">
                <span className="sev critical"></span>
                <div className="grow">
                  <div className="tt t">{tr("2 unsupported claims in the Discussion")}</div>
                  <div className="faint">
                    {"No direct evidence in the knowledge base"}
                  </div>
                </div>
                <span className="badge b-warn t">{tr("Critical")}</span>
              </div>
              {" "}
              <div className="row">
                <span className="sev warning"></span>
                <div className="grow">
                  <div className="tt t">{tr("1 missing citation in the Introduction")}</div>
                  <div className="faint">
                    {"Paragraph 3 · Sentence 2"}
                  </div>
                </div>
                <span className="badge b-mute t">{tr("Warning")}</span>
              </div>
              {" "}
              <div className="row">
                <span className="sev warning"></span>
                <div className="grow">
                  <div className="tt t">{tr("Journal profile needs verification")}</div>
                  <div className="faint">
                    {"Journal of Applied Neuroimaging · last verified 94 days ago"}
                  </div>
                </div>
                <span className="badge b-mute t">{tr("Warning")}</span>
              </div>
            </div>
          </section>
          {" "}
          <section className="box">
            <header>
              <h2 className="t">{tr("Recent papers")}</h2>
              <button className="btn ghost sm" data-go="papers">
                <span className="t">{tr("All papers")}</span>
                <svg className="i flip">
                  <use href="#i-chev"></use>
                </svg>
              </button>
            </header>
            {" "}
            <div className="in">
              <div className="row">
                <svg className="i faint">
                  <use href="#i-paper"></use>
                </svg>
                <div className="grow">
                  <div className="tt">
                    {"Longitudinal hippocampal volume change in mild cognitive impairment"}
                  </div>
                  <div className="faint">
                    {"Haddad, Lindqvist, Okafor · 2023"}
                  </div>
                </div>
                <span className="badge b-ok t">{tr("Ready")}</span>
              </div>
              {" "}
              <div className="row">
                <svg className="i faint">
                  <use href="#i-paper"></use>
                </svg>
                <div className="grow">
                  <div className="tt">
                    {"APOE ε4 status and rate of memory decline: a multi-site cohort"}
                  </div>
                  <div className="faint">
                    {"Varga, Nakamura · 2022"}
                  </div>
                </div>
                <span className="badge b-info t">{tr("Processing")}</span>
              </div>
              {" "}
              <div className="row">
                <svg className="i faint">
                  <use href="#i-paper"></use>
                </svg>
                <div className="grow">
                  <div className="tt">
                    {"Segmentation reliability across 3T scanner vendors"}
                  </div>
                  <div className="faint">
                    {"Brandt, Osei, Tran · 2021"}
                  </div>
                </div>
                <span className="badge b-ok t">{tr("Ready")}</span>
              </div>
            </div>
          </section>
          {" "}
          <section className="box">
            <header>
              <h2 className="t">{tr("Recent activity")}</h2>
            </header>
            {" "}
            <div className="in">
              <div className="row">
                <div className="grow t">{tr("Paper imported")}</div>
                <span className="faint">
                  {"12 min"}
                </span>
              </div>
              {" "}
              <div className="row">
                <div className="grow t">{tr("PDF processed")}</div>
                <span className="faint">
                  {"48 min"}
                </span>
              </div>
              {" "}
              <div className="row">
                <div className="grow t">{tr("Manuscript analyzed")}</div>
                <span className="faint">
                  {"Yesterday"}
                </span>
              </div>
              {" "}
              <div className="row">
                <div className="grow t">{tr("Journal requirements updated")}</div>
                <span className="faint">
                  {"2 days"}
                </span>
              </div>
            </div>
          </section>
        </div>
        {" "}
        <div className="stack">
          <section className="box">
            <header>
              <h2 className="t">{tr("Processing queue")}</h2>
            </header>
            {" "}
            <div className="in">
              <div className="row">
                <div className="grow">
                  <div className="tt">
                    {"Varga & Nakamura 2022"}
                  </div>
                  <div className="prog" style={{margin: "6px 0 3px"}}>
                    <i style={{width: "80%"}}></i>
                  </div>
                  <div className="faint">
                    <span className="t">{tr("Extracting sections")}</span>
                    {" · 80%"}
                  </div>
                </div>
              </div>
              {" "}
              <div className="row">
                <div className="grow">
                  <div className="tt">
                    {"Brandt et al. 2021 (scan)"}
                  </div>
                  <div className="prog" style={{margin: "6px 0 3px"}}>
                    <i style={{width: "40%"}}></i>
                  </div>
                  <div className="faint">
                    <span className="t">{tr("Generating embeddings")}</span>
                    {" · 40%"}
                  </div>
                </div>
              </div>
              {" "}
              <div className="row">
                <div className="grow">
                  <div className="tt">
                    {"Haddad et al. 2023"}
                  </div>
                </div>
                <span className="badge b-ok">
                  <svg className="i">
                    <use href="#i-check"></use>
                  </svg>
                  <span className="t">{tr("Completed")}</span>
                </span>
              </div>
            </div>
          </section>
          {" "}
          <section className="box">
            <header>
              <h2 className="t">{tr("System status")}</h2>
              <button className="btn ghost sm" data-go="models">
                <span className="t">{tr("Details")}</span>
              </button>
            </header>
            {" "}
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
                <span className="t">{tr("Vector DB")}</span>
                <span className="s">
                  <i className="dot"></i>
                  <span className="t">{tr("Ready")}</span>
                </span>
              </div>
            </div>
          </section>
          {" "}
          <section className="box">
            <header>
              <h2 className="t">{tr("AI model status")}</h2>
            </header>
            {" "}
            <div className="in">
              <div className="kv">
                <span className="t">{tr("Academic writing")}</span>
                <span className="mono">
                  {"qwen2.5:14b"}
                </span>
              </div>
              {" "}
              <div className="kv">
                <span className="t">{tr("Embeddings")}</span>
                <span className="mono">
                  {"nomic-embed-text"}
                </span>
              </div>
              {" "}
              <div className="kv">
                <span className="t">{tr("Journal evaluation")}</span>
                <span className="mono">
                  {"qwen2.5:14b"}
                </span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </section>
  );
}
