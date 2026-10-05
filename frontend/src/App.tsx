import { Routes, Route, Navigate } from "react-router-dom";
import Shell from "./mockup/Shell";
import DashboardScreen from "./mockup/screens/Dashboard";
import PapersScreen from "./mockup/screens/Papers";
import ViewerScreen from "./mockup/screens/Viewer";
import JournalsScreen from "./mockup/screens/Journals";
import ManuscriptScreen from "./mockup/screens/Manuscript";
import ComplianceScreen from "./mockup/screens/Compliance";
import ReportsScreen from "./mockup/screens/Reports";
import ModelsScreen from "./mockup/screens/Models";
import PaperViewerPage from "./pages/PaperViewerPage";
import Status from "./pages/Status";
import Chat from "./pages/Chat";
import Evaluations from "./pages/Evaluations";
import ResponseLetters from "./pages/ResponseLetters";
import TagsComments from "./pages/TagsComments";
import DiffPage from "./pages/Diff";
import Exports from "./pages/Exports";
import Submission from "./pages/Submission";
import Improvements from "./pages/Improvements";
import Workflow from "./pages/Workflow";

export default function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route path="/" element={<DashboardScreen />} />
        <Route path="/papers" element={<PapersScreen />} />
        <Route path="/viewer" element={<ViewerScreen />} />
        <Route path="/journals" element={<JournalsScreen />} />
        <Route path="/manuscripts" element={<ManuscriptScreen />} />
        <Route path="/compliance" element={<ComplianceScreen />} />
        <Route path="/reports" element={<ReportsScreen />} />
        <Route path="/models" element={<ModelsScreen />} />
        <Route path="/papers/:id/viewer" element={<PaperViewerPage />} />
        <Route path="/workflow" element={<Workflow />} />
        <Route path="/evaluations" element={<Evaluations />} />
        <Route path="/response-letters" element={<ResponseLetters />} />
        <Route path="/tags-comments" element={<TagsComments />} />
        <Route path="/diff" element={<DiffPage />} />
        <Route path="/exports" element={<Exports />} />
        <Route path="/submission" element={<Submission />} />
        <Route path="/improvements" element={<Improvements />} />
        <Route path="/status" element={<Status />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}