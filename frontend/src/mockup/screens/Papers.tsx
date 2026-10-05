import { useUI } from "../UI";

export default function PapersScreen() {
  const { tr } = useUI();
  return (
    <section className="screen" id="s-papers" aria-labelledby="h-papers">
      <div className="pagehead">
        <div>
          <h1 id="h-papers" className="t">{tr("Papers")}</h1>
          <p className="sub t">{tr("Your research library")}</p>
        </div>
        {" "}
        <div className="actions">
          <button className="btn">
            <svg className="i">
              <use href="#i-cite"></use>
            </svg>
            <span className="t">{tr("Import from URL")}</span>
          </button>
          <button className="btn pri">
            <svg className="i">
              <use href="#i-upload"></use>
            </svg>
            <span className="t">{tr("Upload PDF")}</span>
          </button>
        </div>
      </div>
      {" "}
      <div className="drop">
        <svg className="i">
          <use href="#i-upload"></use>
        </svg>
        <div>
          <b className="t">{tr("Drop PDF files here")}</b>
          {" "}
          <span className="t">{tr("or use Upload PDF. Text, sections and embeddings are prepared automatically.")}</span>
        </div>
      </div>
      {" "}
      <div className="toolbar">
        <input className="field srch" id="paperSearch" type="search" placeholder={tr("Search title, author, DOI")} data-p="Search title, author, DOI" aria-label="Search papers" />
        {" "}
        <div className="chips" role="group" aria-label="Filter">
          <button className="chip t" data-f="all" aria-pressed="true">{tr("All")}</button>
          {" "}
          <button className="chip t" data-f="ready" aria-pressed="false">{tr("Ready")}</button>
          {" "}
          <button className="chip t" data-f="proc" aria-pressed="false">{tr("Processing")}</button>
          {" "}
          <button className="chip t" data-f="fail" aria-pressed="false">{tr("Needs attention")}</button>
        </div>
      </div>
      {" "}
      <div className="tbl">
        <table id="paperTbl">
          <thead>
            <tr>
              <th data-sort="0" className="t">{tr("Title")}</th>
              <th data-sort="1" className="t">{tr("Year")}</th>
              <th data-sort="2" className="t">{tr("Journal")}</th>
              <th className="t">{tr("DOI")}</th>
              <th className="t">{tr("Tags")}</th>
              <th data-sort="5" className="t">{tr("Status")}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr className="clk" data-status="ready" data-go="viewer">
              <td>
                <div className="ttl">
                  {"Longitudinal hippocampal volume change in mild cognitive impairment"}
                </div>
                <div className="au">
                  {"Haddad, Lindqvist, Okafor"}
                </div>
              </td>
              <td className="mono">
                {"2023"}
              </td>
              <td>
                {"Journal of Applied Neuroimaging"}
              </td>
              <td className="mono">
                {"10.5555/jan.2023.0412"}
              </td>
              <td>
                <span className="tag">
                  {"MRI"}
                </span>
                {" "}
                <span className="tag">
                  {"cohort"}
                </span>
              </td>
              <td>
                <span className="badge b-ok t">{tr("Ready")}</span>
              </td>
              <td>
                <button className="btn sm">
                  <svg className="i">
                    <use href="#i-spark"></use>
                  </svg>
                  <span className="t">{tr("Analyze")}</span>
                </button>
              </td>
            </tr>
            <tr className="clk" data-status="proc" data-go="viewer">
              <td>
                <div className="ttl">
                  {"APOE ε4 status and rate of memory decline: a multi-site cohort"}
                </div>
                <div className="au">
                  {"Varga, Nakamura"}
                </div>
              </td>
              <td className="mono">
                {"2022"}
              </td>
              <td>
                {"Clinical Cognitive Neuroscience"}
              </td>
              <td className="mono">
                {"10.5555/ccn.2022.0187"}
              </td>
              <td>
                <span className="tag">
                  {"genetics"}
                </span>
              </td>
              <td>
                <span className="badge b-info t">{tr("Processing")}</span>
                <div className="prog" style={{width: "96px", marginTop: "5px"}}>
                  <i style={{width: "80%"}}></i>
                </div>
              </td>
              <td></td>
            </tr>
            <tr className="clk" data-status="ready" data-go="viewer">
              <td>
                <div className="ttl">
                  {"Segmentation reliability across 3T scanner vendors"}
                </div>
                <div className="au">
                  {"Brandt, Osei, Tran"}
                </div>
              </td>
              <td className="mono">
                {"2021"}
              </td>
              <td>
                {"Journal of Applied Neuroimaging"}
              </td>
              <td className="mono">
                {"10.5555/jan.2021.0098"}
              </td>
              <td>
                <span className="tag">
                  {"methods"}
                </span>
                {" "}
                <span className="tag">
                  {"MRI"}
                </span>
              </td>
              <td>
                <span className="badge b-ok t">{tr("Ready")}</span>
              </td>
              <td>
                <button className="btn sm">
                  <svg className="i">
                    <use href="#i-spark"></use>
                  </svg>
                  <span className="t">{tr("Analyze")}</span>
                </button>
              </td>
            </tr>
            <tr className="clk" data-status="fail" data-go="viewer">
              <td>
                <div className="ttl">
                  {"Cerebrospinal biomarkers and early structural change"}
                </div>
                <div className="au">
                  {"Idowu, Petrov"}
                </div>
              </td>
              <td className="mono">
                {"2020"}
              </td>
              <td>
                {"Brain & Behaviour Imaging"}
              </td>
              <td className="mono">
                {"10.5555/bbi.2020.0331"}
              </td>
              <td>
                <span className="tag">
                  {"biomarkers"}
                </span>
              </td>
              <td>
                <span className="badge b-crit">
                  <svg className="i">
                    <use href="#i-alert"></use>
                  </svg>
                  <span className="t">{tr("Failed")}</span>
                </span>
              </td>
              <td>
                <button className="btn sm">
                  <svg className="i">
                    <use href="#i-refresh"></use>
                  </svg>
                  <span className="t">{tr("Retry")}</span>
                </button>
              </td>
            </tr>
            <tr className="clk" data-status="ready" data-go="viewer">
              <td>
                <div className="ttl">
                  {"Cognitive reserve moderates structural decline in older adults"}
                </div>
                <div className="au">
                  {"Svensson, Adeyemi"}
                </div>
              </td>
              <td className="mono">
                {"2019"}
              </td>
              <td>
                {"Clinical Cognitive Neuroscience"}
              </td>
              <td className="mono">
                {"10.5555/ccn.2019.0054"}
              </td>
              <td>
                <span className="tag">
                  {"reserve"}
                </span>
              </td>
              <td>
                <span className="badge b-ok t">{tr("Ready")}</span>
              </td>
              <td>
                <button className="btn sm">
                  <svg className="i">
                    <use href="#i-spark"></use>
                  </svg>
                  <span className="t">{tr("Analyze")}</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        {" "}
        <div className="pager">
          <span>
            {"1–5 / 12"}
          </span>
          <span className="actions">
            <button className="btn sm" disabled>
              {"‹"}
            </button>
            <button className="btn sm">
              {"›"}
            </button>
          </span>
        </div>
      </div>
    </section>
  );
}
