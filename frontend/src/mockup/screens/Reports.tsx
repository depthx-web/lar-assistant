import { useUI } from "../UI";

export default function ReportsScreen() {
  const { tr } = useUI();
  return (
    <section className="screen" id="s-reports" aria-labelledby="h-reports">
      <div className="pagehead">
        <div>
          <h1 id="h-reports" className="t">{tr("Reports")}</h1>
          <p className="sub t">{tr("Generated analyses you can view, export and save")}</p>
        </div>
      </div>
      {" "}
      <div className="tbl">
        <table>
          <thead>
            <tr>
              <th className="t">{tr("Report")}</th>
              <th className="t">{tr("Subject")}</th>
              <th className="t">{tr("Generated")}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="t">{tr("Manuscript analysis")}</td>
              <td>
                {"Hippocampal atrophy rates"}
              </td>
              <td className="mono">
                {"03 Oct 2026"}
              </td>
              <td>
                <span className="actions">
                  <button className="btn sm t">{tr("View")}</button>
                  <button className="btn sm t">{tr("Export")}</button>
                  <button className="btn sm t">{tr("Save")}</button>
                </span>
              </td>
            </tr>
            <tr>
              <td className="t">{tr("Journal compliance")}</td>
              <td>
                {"Journal of Applied Neuroimaging"}
              </td>
              <td className="mono">
                {"03 Oct 2026"}
              </td>
              <td>
                <span className="actions">
                  <button className="btn sm t">{tr("View")}</button>
                  <button className="btn sm t">{tr("Export")}</button>
                  <button className="btn sm t">{tr("Save")}</button>
                </span>
              </td>
            </tr>
            <tr>
              <td className="t">{tr("Scientific completeness")}</td>
              <td>
                {"Hippocampal atrophy rates"}
              </td>
              <td className="mono">
                {"01 Oct 2026"}
              </td>
              <td>
                <span className="actions">
                  <button className="btn sm t">{tr("View")}</button>
                  <button className="btn sm t">{tr("Export")}</button>
                  <button className="btn sm t">{tr("Save")}</button>
                </span>
              </td>
            </tr>
            <tr>
              <td className="t">{tr("Citation analysis")}</td>
              <td>
                {"Hippocampal atrophy rates"}
              </td>
              <td className="mono">
                {"01 Oct 2026"}
              </td>
              <td>
                <span className="actions">
                  <button className="btn sm t">{tr("View")}</button>
                  <button className="btn sm t">{tr("Export")}</button>
                  <button className="btn sm t">{tr("Save")}</button>
                </span>
              </td>
            </tr>
            <tr>
              <td className="t">{tr("Evidence report")}</td>
              <td>
                {"Discussion section"}
              </td>
              <td className="mono">
                {"30 Sep 2026"}
              </td>
              <td>
                <span className="actions">
                  <button className="btn sm t">{tr("View")}</button>
                  <button className="btn sm t">{tr("Export")}</button>
                  <button className="btn sm t">{tr("Save")}</button>
                </span>
              </td>
            </tr>
            <tr>
              <td className="t">{tr("Rejection pattern analysis")}</td>
              <td>
                {"Journal of Applied Neuroimaging"}
              </td>
              <td className="mono">
                {"28 Sep 2026"}
              </td>
              <td>
                <span className="actions">
                  <button className="btn sm t">{tr("View")}</button>
                  <button className="btn sm t">{tr("Export")}</button>
                  <button className="btn sm t">{tr("Save")}</button>
                </span>
              </td>
            </tr>
            <tr>
              <td className="t">{tr("Final submission report")}</td>
              <td>
                <span className="faint t">{tr("Available after all blocking issues are resolved")}</span>
              </td>
              <td className="mono faint">
                {"—"}
              </td>
              <td>
                <button className="btn sm t" disabled>{tr("View")}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}
