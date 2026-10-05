import { useUI } from "../UI";

export default function JournalsScreen() {
  const { tr } = useUI();
  return (
    <section className="screen" id="s-journals" aria-labelledby="h-journals">
      <div className="pagehead">
        <div>
          <h1 id="h-journals">
            {"Journal of Applied Neuroimaging"}
          </h1>
          {" "}
          <div className="meta">
            <span>
              {"Meridian Academic Press"}
            </span>
            <span className="sep">
              {"|"}
            </span>
            <span>
              {"ISSN "}
              <span className="mono">
                {"2398-0000"}
              </span>
            </span>
            <span className="sep">
              {"|"}
            </span>
            <span>
              <span className="t">{tr("Last verified")}</span>
              {" 12 Sep 2026"}
            </span>
          </div>
        </div>
        {" "}
        <div className="actions">
          <select className="field" aria-label="Journal">
            <option>
              {"Journal of Applied Neuroimaging"}
            </option>
            <option>
              {"Brain & Behaviour Imaging"}
            </option>
            <option>
              {"Clinical Cognitive Neuroscience"}
            </option>
          </select>
          <button className="btn pri">
            <svg className="i">
              <use href="#i-refresh"></use>
            </svg>
            <span className="t">{tr("Re-verify sources")}</span>
          </button>
        </div>
      </div>
      {" "}
      <div className="tabgroup">
        <div className="tabs" role="tablist">
          <button role="tab" data-tab="ov" aria-selected="false" className="t">{tr("Overview")}</button>
          {" "}
          <button role="tab" data-tab="rq" aria-selected="true" className="t">{tr("Requirements")}</button>
          {" "}
          <button role="tab" data-tab="st" aria-selected="false" className="t">{tr("Style")}</button>
          {" "}
          <button role="tab" data-tab="rj" aria-selected="false" className="t">{tr("Rejection patterns")}</button>
          {" "}
          <button role="tab" data-tab="ex" aria-selected="false" className="t">{tr("Example papers")}</button>
          {" "}
          <button role="tab" data-tab="so" aria-selected="false" className="t">{tr("Sources")}</button>
          {" "}
          <button role="tab" data-tab="hi" aria-selected="false" className="t">{tr("Compliance history")}</button>
        </div>
        {" "}
        <div data-pane="ov" hidden style={{paddingTop: "16px"}}>
          <div className="grid2">
            <div className="stack">
              <section className="box">
                <header>
                  <h2 className="t">{tr("Scope")}</h2>
                </header>
                <div className="in">
                  <p style={{padding: "8px 0"}}>
                    {"Original clinical and methodological research on structural and functional brain imaging in neurological and psychiatric populations. Reviews are by invitation. Case reports are not considered."}
                  </p>
                </div>
              </section>
              {" "}
              <section className="box">
                <header>
                  <h2 className="t">{tr("Official guidelines")}</h2>
                </header>
                <div className="in">
                  <div className="kv">
                    <span>
                      {"Author guidelines"}
                    </span>
                    <span className="faint">
                      {"v2026.2"}
                    </span>
                  </div>
                  <div className="kv">
                    <span>
                      {"Reporting checklist"}
                    </span>
                    <span className="faint">
                      {"v2025.4"}
                    </span>
                  </div>
                </div>
              </section>
            </div>
            {" "}
            <section className="box">
              <header>
                <h2 className="t">{tr("Profile summary")}</h2>
              </header>
              <div className="in">
                <div className="kv">
                  <span className="t">{tr("Requirements")}</span>
                  <span className="mono">
                    {"24"}
                  </span>
                </div>
                <div className="kv">
                  <span className="t">{tr("Observed patterns")}</span>
                  <span className="mono">
                    {"9"}
                  </span>
                </div>
                <div className="kv">
                  <span className="t">{tr("Example papers")}</span>
                  <span className="mono">
                    {"20"}
                  </span>
                </div>
                <div className="kv">
                  <span className="t">{tr("Sources")}</span>
                  <span className="mono">
                    {"6"}
                  </span>
                </div>
              </div>
            </section>
          </div>
        </div>
        {" "}
        <div data-pane="rq" style={{paddingTop: "16px"}}>
          <div className="legend">
            <div>
              <span className="badge b-official t">{tr("Official requirement")}</span>
              <span className="t">{tr("Stated by the journal")}</span>
            </div>
            {" "}
            <div>
              <span className="badge b-observed t">{tr("Observed pattern")}</span>
              <span className="t">{tr("Seen in published papers")}</span>
            </div>
            {" "}
            <div>
              <span className="badge b-model">
                <svg className="i">
                  <use href="#i-spark"></use>
                </svg>
                <span className="t">{tr("Model assessment")}</span>
              </span>
              <span className="t">{tr("Inferred by the AI, not journal policy")}</span>
            </div>
          </div>
          {" "}
          <div className="tbl">
            <table>
              <thead>
                <tr>
                  <th className="t">{tr("Requirement")}</th>
                  <th className="t">{tr("Type")}</th>
                  <th className="t">{tr("Basis")}</th>
                  <th className="t">{tr("Status")}</th>
                  <th className="t">{tr("Source")}</th>
                  <th className="t">{tr("Verified")}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    {"Structured abstract, 250 words maximum"}
                  </td>
                  <td>
                    <span className="badge b-crit t">{tr("Mandatory")}</span>
                  </td>
                  <td>
                    <span className="badge b-official t">{tr("Official requirement")}</span>
                  </td>
                  <td>
                    <span className="badge b-ok t">{tr("Met")}</span>
                  </td>
                  <td className="faint">
                    {"Author guidelines §2.1"}
                  </td>
                  <td className="mono">
                    {"12 Sep 2026"}
                  </td>
                </tr>
                <tr>
                  <td>
                    {"Methods report scanner, sequence and acquisition parameters"}
                  </td>
                  <td>
                    <span className="badge b-crit t">{tr("Mandatory")}</span>
                  </td>
                  <td>
                    <span className="badge b-official t">{tr("Official requirement")}</span>
                  </td>
                  <td>
                    <span className="badge b-crit t">{tr("Not met")}</span>
                  </td>
                  <td className="faint">
                    {"Author guidelines §3.2"}
                  </td>
                  <td className="mono">
                    {"12 Sep 2026"}
                  </td>
                </tr>
                <tr>
                  <td>
                    {"Data availability statement"}
                  </td>
                  <td>
                    <span className="badge b-crit t">{tr("Mandatory")}</span>
                  </td>
                  <td>
                    <span className="badge b-official t">{tr("Official requirement")}</span>
                  </td>
                  <td>
                    <span className="badge b-crit t">{tr("Not met")}</span>
                  </td>
                  <td className="faint">
                    {"Author guidelines §5"}
                  </td>
                  <td className="mono">
                    {"12 Sep 2026"}
                  </td>
                </tr>
                <tr>
                  <td>
                    {"Vancouver reference style"}
                  </td>
                  <td>
                    <span className="badge b-crit t">{tr("Mandatory")}</span>
                  </td>
                  <td>
                    <span className="badge b-official t">{tr("Official requirement")}</span>
                  </td>
                  <td>
                    <span className="badge b-ok t">{tr("Met")}</span>
                  </td>
                  <td className="faint">
                    {"Author guidelines §6.4"}
                  </td>
                  <td className="mono">
                    {"12 Sep 2026"}
                  </td>
                </tr>
                <tr>
                  <td>
                    {"Limitations paragraph in the Discussion"}
                  </td>
                  <td>
                    <span className="badge b-info t">{tr("Recommended")}</span>
                  </td>
                  <td>
                    <span className="badge b-observed t">{tr("Observed pattern")}</span>
                  </td>
                  <td>
                    <span className="badge b-warn t">{tr("Needs review")}</span>
                  </td>
                  <td className="faint">
                    {"14 of 20 sampled papers"}
                  </td>
                  <td className="mono">
                    {"02 Oct 2026"}
                  </td>
                </tr>
                <tr>
                  <td>
                    {"Effect sizes reported with confidence intervals"}
                  </td>
                  <td>
                    <span className="badge b-mute t">{tr("Quality")}</span>
                  </td>
                  <td>
                    <span className="badge b-model">
                      <svg className="i">
                        <use href="#i-spark"></use>
                      </svg>
                      <span className="t">{tr("Model assessment")}</span>
                    </span>
                  </td>
                  <td>
                    <span className="badge b-warn t">{tr("Needs review")}</span>
                  </td>
                  <td className="faint">
                    {"qwen2.5:14b"}
                  </td>
                  <td className="mono">
                    {"02 Oct 2026"}
                  </td>
                </tr>
                <tr>
                  <td>
                    {"Avoid causal wording for cross-sectional associations"}
                  </td>
                  <td>
                    <span className="badge b-warn t">{tr("Warning")}</span>
                  </td>
                  <td>
                    <span className="badge b-model">
                      <svg className="i">
                        <use href="#i-spark"></use>
                      </svg>
                      <span className="t">{tr("Model assessment")}</span>
                    </span>
                  </td>
                  <td>
                    <span className="badge b-warn t">{tr("Needs review")}</span>
                  </td>
                  <td className="faint">
                    {"qwen2.5:14b"}
                  </td>
                  <td className="mono">
                    {"02 Oct 2026"}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        {" "}
        <div data-pane="st" hidden style={{paddingTop: "16px"}}>
          <section className="box">
            <header>
              <h2 className="t">{tr("Style guide")}</h2>
            </header>
            <div className="in">
              <div className="kv">
                <span>
                  {"Reference style"}
                </span>
                <span>
                  {"Vancouver, numbered"}
                </span>
              </div>
              <div className="kv">
                <span>
                  {"Spelling"}
                </span>
                <span>
                  {"British English"}
                </span>
              </div>
              <div className="kv">
                <span>
                  {"Headings"}
                </span>
                <span>
                  {"Three levels, sentence case"}
                </span>
              </div>
            </div>
          </section>
        </div>
        {" "}
        <div data-pane="rj" hidden style={{paddingTop: "16px"}}>
          <section className="box">
            <header>
              <h2 className="t">{tr("Rejection patterns")}</h2>
              <span className="badge b-observed t">{tr("Observed pattern")}</span>
            </header>
            <div className="in">
              <div className="row">
                <div className="grow">
                  <div className="tt">
                    {"Underpowered samples without justification"}
                  </div>
                  <div className="faint">
                    {"Cited in 7 of 18 public decision letters"}
                  </div>
                </div>
              </div>
              {" "}
              <div className="row">
                <div className="grow">
                  <div className="tt">
                    {"Scanner heterogeneity not addressed"}
                  </div>
                  <div className="faint">
                    {"Cited in 5 of 18 public decision letters"}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
        {" "}
        <div data-pane="ex" hidden style={{paddingTop: "16px"}}>
          <section className="box">
            <header>
              <h2 className="t">{tr("Example papers")}</h2>
            </header>
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
                    {"2023"}
                  </div>
                </div>
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
                    {"2021"}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
        {" "}
        <div data-pane="so" hidden style={{paddingTop: "16px"}}>
          <section className="box">
            <header>
              <h2 className="t">{tr("Sources")}</h2>
            </header>
            <div className="in">
              <div className="kv">
                <span>
                  {"Author guidelines"}
                </span>
                <span className="faint">
                  {"Checked 12 Sep 2026"}
                </span>
              </div>
              <div className="kv">
                <span>
                  {"Reporting checklist"}
                </span>
                <span className="faint">
                  {"Checked 12 Sep 2026"}
                </span>
              </div>
              <div className="kv">
                <span>
                  {"20 published papers"}
                </span>
                <span className="faint">
                  {"Sampled 02 Oct 2026"}
                </span>
              </div>
            </div>
          </section>
        </div>
        {" "}
        <div data-pane="hi" hidden style={{paddingTop: "16px"}}>
          <section className="box">
            <header>
              <h2 className="t">{tr("Compliance history")}</h2>
            </header>
            <div className="in">
              <div className="kv">
                <span>
                  {"Hippocampal atrophy rates · check #4"}
                </span>
                <span className="badge b-crit t">{tr("Not ready")}</span>
              </div>
              <div className="kv">
                <span>
                  {"Hippocampal atrophy rates · check #3"}
                </span>
                <span className="badge b-crit t">{tr("Not ready")}</span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </section>
  );
}
