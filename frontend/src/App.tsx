import { Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import Papers from "./pages/Papers";
import PaperViewerPage from "./pages/PaperViewerPage";
import Journals from "./pages/Journals";
import Manuscripts from "./pages/Manuscripts";
import Compliance from "./pages/Compliance";
import Models from "./pages/Models";
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
      <Route element={<AppLayout />} >
        <Route path="/" element={<Dashboard />} />
        <Route path="/papers" element={<Papers />} />
        <Route path="/papers/:id/viewer" element={<PaperViewerPage />} />
        <Route path="/journals" element={<Journals />} />
        <Route path="/manuscripts" element={<Manuscripts />} />
        <Route path="/workflow" element={<Workflow />} />
        <Route path="/evaluations" element={<Evaluations />} />
        <Route path="/response-letters" element={<ResponseLetters />} />
        <Route path="/tags-comments" element={<TagsComments />} />
        <Route path="/diff" element={<DiffPage />} />
        <Route path="/exports" element={<Exports />} />
        <Route path="/submission" element={<Submission />} />
        <Route path="/improvements" element={<Improvements />} />
        <Route path="/compliance" element={<Compliance />} />
        <Route path="/models" element={<Models />} />
        <Route path="/status" element={<Status />} />
        <Route path="/chat" element={<Chat />} />
      </Route>
    </Routes>
  );
}
