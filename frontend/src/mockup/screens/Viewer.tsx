import { useUI } from "../UI";

export default function ViewerScreen() {
  const { tr } = useUI();
  return (
    <section className="screen panes" id="s-viewer" aria-labelledby="h-viewer">
      <div className="dochead">
        <div>
          <button className="btn ghost sm" data-go="papers" style={{marginInlineStart: "-8px"}}>
            <svg className="i flip">
              <use href="#i-back"></use>
            </svg>
            <span className="t">{tr("Papers")}</span>
          </button>
          {" "}
          <h1 id="h-viewer">
            {"Longitudinal hippocampal volume change in mild cognitive impairment"}
          </h1>
          {" "}
          <div className="meta">
            <span>
              {"Haddad, Lindqvist, Okafor"}
            </span>
            <span className="sep">
              {"|"}
            </span>
            <span>
              {"Journal of Applied Neuroimaging"}
            </span>
            <span className="sep">
              {"|"}
            </span>
            <span>
              {"2023"}
            </span>
            <span className="sep">
              {"|"}
            </span>
            <span className="mono">
              {"10.5555/jan.2023.0412"}
            </span>
          </div>
        </div>
        {" "}
        <div className="actions">
          <span className="badge b-ok t">{tr("Ready")}</span>
          <button className="btn">
            <svg className="i">
              <use href="#i-search"></use>
            </svg>
            <span className="t">{tr("Find in paper")}</span>
          </button>
          <button className="btn">
            <span className="t">{tr("Summarize")}</span>
          </button>
        </div>
      </div>
      {" "}
      <div className="pbody">
        <div className="pane l outline" role="navigation" aria-label="Sections">
          <div className="h-label" style={{padding: "4px 10px 8px"}}>
            <span className="t">{tr("Sections")}</span>
          </div>
          {" "}
          <button>
            <span className="t">{tr("Abstract")}</span>
            <span className="pg">
              {"1"}
            </span>
          </button>
          {" "}
          <button>
            <span className="t">{tr("Introduction")}</span>
            <span className="pg">
              {"2"}
            </span>
          </button>
          {" "}
          <button aria-current="true">
            <span className="t">{tr("Methods")}</span>
            <span className="pg">
              {"5"}
            </span>
          </button>
          {" "}
          <button>
            <span className="t">{tr("Results")}</span>
            <span className="pg">
              {"8"}
            </span>
          </button>
          {" "}
          <button>
            <span className="t">{tr("Discussion")}</span>
            <span className="pg">
              {"11"}
            </span>
          </button>
          {" "}
          <button>
            <span className="t">{tr("References")}</span>
            <span className="pg">
              {"14"}
            </span>
          </button>
        </div>
        {" "}
        <div className="pane c">
          <article className="page">
            <div className="lead">
              {"PAGE 7 · "}
              <span className="t">{tr("Methods")}</span>
            </div>
            {" "}
            <h3>
              {"2.3 Image acquisition"}
            </h3>
            {" "}
            <p>
              {"All participants were scanned on 3T systems using a T1-weighted magnetization-prepared sequence. "}
              <mark>
                {"Acquisition used a 1 mm isotropic voxel size, a repetition time of 2300 ms and an echo time of 2.98 ms"}
              </mark>
              {" at each of the four sites "}
              <span className="cite">
                {"[4]"}
              </span>
              {"."}
            </p>
            {" "}
            <div className="selbar" role="toolbar" aria-label="Selection actions">
              <button className="t">{tr("Ask AI")}</button>
              <button className="t">{tr("Summarize")}</button>
              <button className="t">{tr("Add to notes")}</button>
            </div>
            {" "}
            <p>
              {"Scans were visually inspected for motion artefacts before processing. Cortical and subcortical volumes were estimated with an automated pipeline, and hippocampal volumes were normalised to total intracranial volume "}
              <span className="cite">
                {"[7]"}
              </span>
              {"."}
            </p>
            {" "}
            <p>
              {"Follow-up scans were acquired at 12 and 24 months. Participants with fewer than two usable scans were excluded from the longitudinal analysis."}
            </p>
          </article>
        </div>
        {" "}
        <aside className="pane r" aria-label="AI assistant">
          <div className="aihead">
            <div className="h-label">
              <span className="t">{tr("Ask about")}</span>
            </div>
            {" "}
            <div className="scope" role="radiogroup" aria-label="Scope">
              <label>
                <input type="radio" name="sc1" defaultChecked />
                <span className="t">{tr("Current paper")}</span>
              </label>
              {" "}
              <label>
                <input type="radio" name="sc1" />
                <span className="t">{tr("Selected papers")}</span>
              </label>
              {" "}
              <label>
                <input type="radio" name="sc1" />
                <span className="t">{tr("Current journal")}</span>
              </label>
              {" "}
              <label>
                <input type="radio" name="sc1" />
                <span className="t">{tr("Current manuscript")}</span>
              </label>
              {" "}
              <label>
                <input type="radio" name="sc1" />
                <span className="t">{tr("Entire knowledge base")}</span>
              </label>
              {" "}
              <label>
                <input type="radio" name="sc1" />
                <span className="t">{tr("General AI")}</span>
              </label>
            </div>
          </div>
          {" "}
          <div className="thread">
            <div className="q">
              {"What was the MRI acquisition protocol, and which software processed the scans?"}
            </div>
            {" "}
            <div className="ans">
              <p>
                {"The scans were T1-weighted on 3T scanners with 1 mm isotropic voxels, TR 2300 ms and TE 2.98 ms "}
                <span className="cite">
                  {"[1]"}
                </span>
                {". The paper does not name the processing software "}
                <span className="cite">
                  {"[2]"}
                </span>
                {"."}
              </p>
              {" "}
              <div className="evi">
                <span className="badge b-ok">
                  <svg className="i">
                    <use href="#i-check"></use>
                  </svg>
                  <span className="t">{tr("Direct evidence")}</span>
                </span>
                {" "}
                <dl>
                  <dt className="t">{tr("Paper")}</dt>
                  <dd>
                    {"Haddad et al. 2023"}
                  </dd>
                  <dt className="t">{tr("Page")}</dt>
                  <dd className="mono">
                    {"7"}
                  </dd>
                  <dt className="t">{tr("Section")}</dt>
                  <dd className="t">{tr("Methods")}</dd>
                </dl>
              </div>
              {" "}
              <div className="evi">
                <span className="badge b-warn">
                  <svg className="i">
                    <use href="#i-alert"></use>
                  </svg>
                  <span className="t">{tr("Inference")}</span>
                </span>
                {" "}
                <div className="note t">{tr("The pipeline resembles common surface-based tools, but the paper never states which one. Treat this as a guess, not a finding.")}</div>
              </div>
              {" "}
              <div className="tools">
                <button className="btn ghost sm">
                  <svg className="i">
                    <use href="#i-copy"></use>
                  </svg>
                  <span className="t">{tr("Copy")}</span>
                </button>
                <button className="btn ghost sm">
                  <svg className="i">
                    <use href="#i-refresh"></use>
                  </svg>
                  <span className="t">{tr("Regenerate")}</span>
                </button>
              </div>
            </div>
          </div>
          {" "}
          <div className="composer">
            <div className="qa">
              <button className="chip t">{tr("Summarize")}</button>
              <button className="chip t">{tr("Extract results")}</button>
              <button className="chip t">{tr("Extract methodology")}</button>
              <button className="chip t">{tr("Extract limitations")}</button>
            </div>
            {" "}
            <div className="inbox">
              <textarea id="aiInput1" placeholder={tr("Ask about this paper")} data-p="Ask about this paper" aria-label="Ask about this paper" defaultValue={""} />
              <button className="btn pri" aria-label="Send">
                <svg className="i">
                  <use href="#i-send"></use>
                </svg>
              </button>
            </div>
            {" "}
            <div className="faint" style={{marginTop: "6px", fontSize: "12px"}}>
              <kbd>
                {"Ctrl /"}
              </kbd>
              {" "}
              <span className="t">{tr("Focus AI assistant")}</span>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
