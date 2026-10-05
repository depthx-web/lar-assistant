import { useState } from "react";
import { useUI } from "../UI";

export default function ManuscriptScreen() {
  const { tr } = useUI();
  const [sugg, setSugg] = useState<null | "accepted" | "rejected">(null);
  return (
    <section className="screen panes" id="s-manuscript" aria-labelledby="h-manuscript">
      <div className="dochead">
        <div>
          <h1 id="h-manuscript">
            {"Hippocampal atrophy rates and cognitive decline in mild cognitive impairment"}
          </h1>
          {" "}
          <div className="meta">
            <span>
              <span className="t">{tr("Target journal")}</span>
              {": Journal of Applied Neuroimaging"}
            </span>
            <span className="sep">
              {"|"}
            </span>
            <span>
              {"3,412 "}
              <span className="t">{tr("words")}</span>
            </span>
          </div>
        </div>
        {" "}
        <div className="actions">
          <span className="badge b-mute">
            <span className="t">{tr("Status")}</span>
            {":\u00a0"}
            <span className="t">{tr("Draft")}</span>
          </span>
          <button className="btn">
            <svg className="i">
              <use href="#i-clock"></use>
            </svg>
            <span className="t">{tr("Version history")}</span>
          </button>
          <button className="btn pri" data-go="compliance">
            <svg className="i">
              <use href="#i-shield"></use>
            </svg>
            <span className="t">{tr("Run compliance check")}</span>
          </button>
        </div>
      </div>
      {" "}
      <div className="pbody">
        <div className="pane l outline" role="navigation" aria-label="Outline">
          <div className="h-label" style={{padding: "4px 10px 8px"}}>
            <span className="t">{tr("Outline")}</span>
          </div>
          {" "}
          <button>
            <span className="t">{tr("Abstract")}</span>
          </button>
          {" "}
          <button>
            <span className="t">{tr("Introduction")}</span>
            <i className="pip w" title="1 warning"></i>
          </button>
          {" "}
          <button>
            <span className="t">{tr("Methods")}</span>
            <i className="pip" title="Blocking issue"></i>
          </button>
          {" "}
          <button>
            <span className="t">{tr("Results")}</span>
          </button>
          {" "}
          <button aria-current="true">
            <span className="t">{tr("Discussion")}</span>
            <i className="pip w" title="2 issues"></i>
          </button>
          {" "}
          <button>
            <span className="t">{tr("Conclusion")}</span>
          </button>
          {" "}
          <button>
            <span className="t">{tr("References")}</span>
          </button>
        </div>
        {" "}
        <div className="pane c" style={{position: "relative"}}>
          <div className="edtool" role="toolbar" aria-label="Formatting">
            <select aria-label="Block style">
              <option>
                {"Paragraph"}
              </option>
              <option>
                {"Heading 2"}
              </option>
              <option>
                {"Heading 3"}
              </option>
            </select>
            {" "}
            <span className="sepv"></span>
            {" "}
            <button className="iconbtn" aria-label="Bold" style={{fontWeight: "700"}}>
              {"B"}
            </button>
            <button className="iconbtn" aria-label="Italic" style={{fontStyle: "italic", fontFamily: "var(--read)"}}>
              {"I"}
            </button>
            {" "}
            <button className="iconbtn" aria-label="List">
              <svg className="i">
                <use href="#i-list"></use>
              </svg>
            </button>
            <button className="iconbtn" aria-label="Table">
              <svg className="i">
                <use href="#i-table"></use>
              </svg>
            </button>
            {" "}
            <button className="iconbtn" aria-label="Insert citation">
              <svg className="i">
                <use href="#i-cite"></use>
              </svg>
            </button>
            <button className="iconbtn" aria-label="Comment">
              <svg className="i">
                <use href="#i-comment"></use>
              </svg>
            </button>
            {" "}
            <span className="sepv"></span>
            {" "}
            <button className="iconbtn" aria-label="Undo">
              <svg className="i">
                <use href="#i-undo"></use>
              </svg>
            </button>
            <button className="iconbtn" aria-label="Redo">
              <svg className="i flip" style={{transform: "scaleX(-1)"}}>
                <use href="#i-undo"></use>
              </svg>
            </button>
            {" "}
            <span className="saved">
              <i className="dot"></i>
              <span className="t">{tr("Saved")}</span>
              {" 14:32"}
            </span>
          </div>
          {" "}
          <article className="page" style={{marginTop: "18px"}}>
            <h3 className="t">{tr("Discussion")}</h3>
            {" "}
            <p>
              {"In this cohort, participants with mild cognitive impairment lost hippocampal volume faster than age-matched controls, in line with earlier longitudinal reports "}
              <span className="cite">
                {"[3,7]"}
              </span>
              {". The difference was largest in the first twelve months of follow-up."}
            </p>
            {" "}
            <p id="ms-claim">
              <span className={sugg === "accepted" ? "" : "unsup"} id="claimTxt">{sugg === "accepted" ? "Annualised hippocampal atrophy of 3.1% was associated with faster decline in APOE ε4 carriers. This association may contribute to conversion to dementia, although the present design cannot establish causation." : "Annualised hippocampal atrophy of 3.1% therefore explains the faster decline observed in APOE ε4 carriers, and this effect is clearly the main driver of conversion to dementia."}</span>
            </p>
            {" "}
            <p>
              {"Several limitations should be considered. Follow-up was restricted to 24 months, and scanner differences between sites may have added variance to the volumetric estimates."}
            </p>
          </article>
        </div>
        {" "}
        <aside className="pane r tabgroup" aria-label="AI assistant">
          <div className="tabs" role="tablist" style={{paddingInline: "6px"}}>
            <button role="tab" data-tab="sg" aria-selected="true" className="t">{tr("Suggestions")}</button>
            {" "}
            <button role="tab" data-tab="ev" aria-selected="false" className="t">{tr("Evidence")}</button>
            {" "}
            <button role="tab" data-tab="is" aria-selected="false">
              <span className="t">{tr("Issues")}</span>
              {" 3"}
            </button>
            {" "}
            <button role="tab" data-tab="co" aria-selected="false" className="t">{tr("Compliance")}</button>
          </div>
          {" "}
          <div data-pane="sg" className="paneBody">
            <div style={{padding: "12px 14px 0"}}>
              <div className="h-label">
                <span className="t">{tr("Selected: Discussion, paragraph 2")}</span>
              </div>
              {" "}
              <div className="chips" style={{marginTop: "8px"}}>
                <button className="chip t">{tr("Improve clarity")}</button>
                <button className="chip t">{tr("Grammar")}</button>
                <button className="chip t">{tr("More concise")}</button>
                <button className="chip t">{tr("Expand")}</button>
                <button className="chip t">{tr("Check consistency")}</button>
                <button className="chip t">{tr("Find unsupported claim")}</button>
                <button className="chip t">{tr("Suggest citation")}</button>
                <button className="chip t">{tr("Compare with journal style")}</button>
              </div>
            </div>
            {" "}
            <div className={"sugg" + (sugg ? " done" : "")} id="sugg1">
              <div className="blk">
                <span className="lab t">{tr("Original")}</span>
                <del>
                  {"Annualised hippocampal atrophy of 3.1% therefore explains the faster decline observed in APOE ε4 carriers, and this effect is clearly the main driver of conversion to dementia."}
                </del>
              </div>
              {" "}
              <div className="blk">
                <span className="lab t">{tr("Suggestion")}</span>
                <ins>
                  {"Annualised hippocampal atrophy of 3.1% was associated with faster decline in APOE ε4 carriers. This association may contribute to conversion to dementia, although the present design cannot establish causation."}
                </ins>
              </div>
              {" "}
              <div className="blk">
                <span className="lab t">{tr("Why")}</span>
                <span className="muted t">{tr("The original claims causation and has no supporting source in your knowledge base.")}</span>
              </div>
              {" "}
              <div className="foot" id="suggFoot">
                {sugg ? (
                  <>
                    <span className="muted">{tr(sugg === "accepted" ? "Applied. The Discussion text has been updated." : "Rejected. The original text is unchanged.")}</span>
                    <button className="btn sm" style={{ marginInlineStart: "auto" }} onClick={() => setSugg(null)}>{tr("Undo")}</button>
                  </>
                ) : (
                  <>
                <button className="btn sm ok" id="accept" onClick={() => setSugg("accepted")}>
                  <svg className="i">
                    <use href="#i-check"></use>
                  </svg>
                  <span className="t">{tr("Accept")}</span>
                </button>
                <button className="btn sm bad" id="reject" onClick={() => setSugg("rejected")}>
                  <svg className="i">
                    <use href="#i-x"></use>
                  </svg>
                  <span className="t">{tr("Reject")}</span>
                </button>
                <span className="faint t" style={{marginInlineStart: "auto", fontSize: "12px"}}>{tr("Nothing changes until you accept")}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          {" "}
          <div data-pane="ev" hidden className="paneBody" style={{padding: "12px 14px"}}>
            <div className="evi">
              <span className="badge b-mute t">{tr("General knowledge")}</span>
              <div className="note t">{tr("“Hippocampal atrophy is associated with cognitive decline” is widely reported, but no paper in your knowledge base states it for this cohort.")}</div>
            </div>
            {" "}
            <div className="evi">
              <span className="badge b-ok">
                <svg className="i">
                  <use href="#i-check"></use>
                </svg>
                <span className="t">{tr("Direct evidence")}</span>
              </span>
              <dl>
                <dt className="t">{tr("Paper")}</dt>
                <dd>
                  {"Haddad et al. 2023"}
                </dd>
                <dt className="t">{tr("Page")}</dt>
                <dd className="mono">
                  {"9"}
                </dd>
                <dt className="t">{tr("Section")}</dt>
                <dd className="t">{tr("Results")}</dd>
              </dl>
            </div>
          </div>
          {" "}
          <div data-pane="is" hidden className="paneBody" style={{padding: "6px 14px"}}>
            <div className="row">
              <span className="sev critical"></span>
              <div className="grow">
                <div className="tt t">{tr("Unsupported claim: “main driver of conversion”")}</div>
                <div className="faint">
                  {"Discussion ¶2"}
                </div>
              </div>
            </div>
            {" "}
            <div className="row">
              <span className="sev warning"></span>
              <div className="grow">
                <div className="tt t">{tr("Causal wording for an observational design")}</div>
                <div className="faint">
                  {"Discussion ¶2"}
                </div>
              </div>
            </div>
            {" "}
            <div className="row">
              <span className="sev blocking"></span>
              <div className="grow">
                <div className="tt t">{tr("Structured Methods section is missing")}</div>
                <div className="faint">
                  {"Methods"}
                </div>
              </div>
            </div>
          </div>
          {" "}
          <div data-pane="co" hidden className="paneBody" style={{padding: "12px 14px"}}>
            <div className="h-label">
              <span className="t">{tr("Submission readiness")}</span>
            </div>
            {" "}
            <div className="verdict no" style={{margin: "8px 0 10px"}}>
              <svg className="i">
                <use href="#i-x"></use>
              </svg>
              <span className="t">{tr("NOT READY")}</span>
            </div>
            {" "}
            <p className="muted t">{tr("2 blocking issues remain.")}</p>
            {" "}
            <button className="btn" data-go="compliance" style={{marginTop: "10px"}}>
              <span className="t">{tr("Open compliance")}</span>
            </button>
          </div>
        </aside>
      </div>
    </section>
  );
}
