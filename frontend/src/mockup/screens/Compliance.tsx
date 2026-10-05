import { useUI } from "../UI";

export default function ComplianceScreen() {
  const { tr } = useUI();
  return (
    <section className="screen" id="s-compliance" aria-labelledby="h-compliance">
      <div className="pagehead">
        <div>
          <h1 id="h-compliance" className="t">{tr("Journal Compliance")}</h1>
          <p className="sub">
            {"Hippocampal atrophy rates · Journal of Applied Neuroimaging"}
          </p>
        </div>
        {" "}
        <div className="actions">
          <button className="btn">
            <span className="t">{tr("Export report")}</span>
          </button>
          <button className="btn pri">
            <svg className="i">
              <use href="#i-refresh"></use>
            </svg>
            <span className="t">{tr("Run compliance check")}</span>
          </button>
        </div>
      </div>
      {" "}
      <div className="gate">
        <div>
          <div className="h-label">
            <span className="t">{tr("Submission readiness")}</span>
          </div>
          {" "}
          <div className="verdict no">
            <svg className="i">
              <use href="#i-x"></use>
            </svg>
            <span className="t">{tr("NOT READY")}</span>
          </div>
          {" "}
          <p className="muted t" style={{marginTop: "10px", maxWidth: "340px"}}>{tr("This status covers known journal requirements and automated checks only. It does not predict acceptance.")}</p>
        </div>
        {" "}
        <div>
          <ul className="chk">
            <li>
              <svg className="i ok">
                <use href="#i-check"></use>
              </svg>
              <span className="t">{tr("Journal requirements checked")}</span>
            </li>
            {" "}
            <li>
              <svg className="i ok">
                <use href="#i-check"></use>
              </svg>
              <span className="t">{tr("Manuscript structure checked")}</span>
            </li>
            {" "}
            <li>
              <svg className="i ok">
                <use href="#i-check"></use>
              </svg>
              <span className="t">{tr("References checked")}</span>
            </li>
            {" "}
            <li>
              <svg className="i ok">
                <use href="#i-check"></use>
              </svg>
              <span className="t">{tr("Figures checked")}</span>
            </li>
            {" "}
            <li>
              <svg className="i no">
                <use href="#i-x"></use>
              </svg>
              <b className="t">{tr("2 blocking issues remain")}</b>
            </li>
          </ul>
        </div>
      </div>
      {" "}
      <section className="box" style={{marginBottom: "6px"}}>
        <header>
          <h2 className="t">{tr("Checks passed by area")}</h2>
        </header>
        <div className="in">
          <div className="meter">
            <span className="t">{tr("Mandatory requirements")}</span>
            <div className="prog crit">
              <i style={{width: "80%"}}></i>
            </div>
            <span className="v">
              {"16/20"}
            </span>
          </div>
          {" "}
          <div className="meter">
            <span className="t">{tr("Scientific completeness")}</span>
            <div className="prog warn">
              <i style={{width: "70%"}}></i>
            </div>
            <span className="v">
              {"7/10"}
            </span>
          </div>
          {" "}
          <div className="meter">
            <span className="t">{tr("Writing")}</span>
            <div className="prog ok">
              <i style={{width: "85%"}}></i>
            </div>
            <span className="v">
              {"17/20"}
            </span>
          </div>
          {" "}
          <div className="meter">
            <span className="t">{tr("References")}</span>
            <div className="prog warn">
              <i style={{width: "75%"}}></i>
            </div>
            <span className="v">
              {"30/40"}
            </span>
          </div>
          {" "}
          <div className="meter">
            <span className="t">{tr("Submission package")}</span>
            <div className="prog warn">
              <i style={{width: "70%"}}></i>
            </div>
            <span className="v">
              {"7/10"}
            </span>
          </div>
        </div>
      </section>
      {" "}
      <div className="group-h">
        <span className="badge b-crit t">{tr("Blocking")}</span>
        <span className="faint">
          {"2"}
        </span>
      </div>
      {" "}
      <details className="issue" open>
        <summary>
          <span className="sev blocking" style={{height: "20px"}}></span>
          <b className="t">{tr("Missing mandatory section: structured Methods")}</b>
          <span className="badge b-official t">{tr("Official requirement")}</span>
          <svg className="i ch flip">
            <use href="#i-chev"></use>
          </svg>
        </summary>
        {" "}
        <dl className="dd">
          <dt className="t">{tr("Why it matters")}</dt>
          <dd className="t">{tr("The journal rejects submissions that do not report scanner, sequence and acquisition parameters.")}</dd>
          <dt className="t">{tr("Evidence")}</dt>
          <dd>
            {"Author guidelines §3.2, verified 12 Sep 2026"}
          </dd>
          <dt className="t">{tr("Location")}</dt>
          <dd className="t">{tr("Methods")}</dd>
          <dt className="t">{tr("Suggested action")}</dt>
          <dd className="t">{tr("Add an “MRI acquisition” subsection with the parameters from the paper’s Methods.")}</dd>
        </dl>
      </details>
      {" "}
      <details className="issue">
        <summary>
          <span className="sev blocking" style={{height: "20px"}}></span>
          <b className="t">{tr("Data availability statement is absent")}</b>
          <span className="badge b-official t">{tr("Official requirement")}</span>
          <svg className="i ch flip">
            <use href="#i-chev"></use>
          </svg>
        </summary>
        {" "}
        <dl className="dd">
          <dt className="t">{tr("Why it matters")}</dt>
          <dd className="t">{tr("A statement is required before the editorial office will process the submission.")}</dd>
          <dt className="t">{tr("Evidence")}</dt>
          <dd>
            {"Author guidelines §5"}
          </dd>
          <dt className="t">{tr("Location")}</dt>
          <dd className="t">{tr("After Conclusion")}</dd>
          <dt className="t">{tr("Suggested action")}</dt>
          <dd className="t">{tr("State where the data can be accessed, or why it cannot be shared.")}</dd>
        </dl>
      </details>
      {" "}
      <div className="group-h">
        <span className="badge b-warn t">{tr("Critical")}</span>
        <span className="faint">
          {"1"}
        </span>
      </div>
      {" "}
      <details className="issue">
        <summary>
          <span className="sev critical" style={{height: "20px"}}></span>
          <b className="t">{tr("Unsupported claim: “main driver of conversion”")}</b>
          <span className="badge b-mute t">{tr("Needs review")}</span>
          <svg className="i ch flip">
            <use href="#i-chev"></use>
          </svg>
        </summary>
        {" "}
        <dl className="dd">
          <dt className="t">{tr("Why it matters")}</dt>
          <dd className="t">{tr("Reviewers will ask for a source or a design that supports a causal statement.")}</dd>
          <dt className="t">{tr("Evidence")}</dt>
          <dd className="t">{tr("No direct evidence found in the knowledge base.")}</dd>
          <dt className="t">{tr("Location")}</dt>
          <dd className="t">{tr("Discussion, paragraph 2")}</dd>
          <dt className="t">{tr("Suggested action")}</dt>
          <dd>
            <button className="btn sm" data-go="manuscript">
              <span className="t">{tr("Review suggestion")}</span>
            </button>
          </dd>
        </dl>
      </details>
      {" "}
      <div className="group-h">
        <span className="badge b-mute t">{tr("Warning")}</span>
        <span className="faint">
          {"1"}
        </span>
      </div>
      {" "}
      <details className="issue">
        <summary>
          <span className="sev warning" style={{height: "20px"}}></span>
          <b className="t">{tr("Effect sizes lack confidence intervals")}</b>
          <span className="badge b-model">
            <svg className="i">
              <use href="#i-spark"></use>
            </svg>
            <span className="t">{tr("Model assessment")}</span>
          </span>
          <svg className="i ch flip">
            <use href="#i-chev"></use>
          </svg>
        </summary>
        {" "}
        <dl className="dd">
          <dt className="t">{tr("Why it matters")}</dt>
          <dd className="t">{tr("This is the model’s judgement, not stated journal policy.")}</dd>
          <dt className="t">{tr("Evidence")}</dt>
          <dd>
            {"Results, Table 2"}
          </dd>
          <dt className="t">{tr("Location")}</dt>
          <dd className="t">{tr("Results")}</dd>
          <dt className="t">{tr("Suggested action")}</dt>
          <dd className="t">{tr("Report 95% confidence intervals beside each effect size.")}</dd>
        </dl>
      </details>
      {" "}
      <div className="group-h">
        <span className="badge b-info t">{tr("Suggestion")}</span>
        <span className="faint">
          {"1"}
        </span>
      </div>
      {" "}
      <details className="issue">
        <summary>
          <span className="sev suggestion" style={{height: "20px"}}></span>
          <b className="t">{tr("Add a limitations paragraph heading")}</b>
          <span className="badge b-observed t">{tr("Observed pattern")}</span>
          <svg className="i ch flip">
            <use href="#i-chev"></use>
          </svg>
        </summary>
        {" "}
        <dl className="dd">
          <dt className="t">{tr("Why it matters")}</dt>
          <dd className="t">{tr("14 of 20 sampled papers use a labelled limitations paragraph.")}</dd>
          <dt className="t">{tr("Evidence")}</dt>
          <dd className="t">{tr("Sampled papers, 02 Oct 2026")}</dd>
          <dt className="t">{tr("Location")}</dt>
          <dd className="t">{tr("Discussion, paragraph 3")}</dd>
          <dt className="t">{tr("Suggested action")}</dt>
          <dd className="t">{tr("Optional. Start the paragraph with a short heading.")}</dd>
        </dl>
      </details>
    </section>
  );
}
