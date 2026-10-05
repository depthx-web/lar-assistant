import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
    return (_jsx(Routes, { children: _jsxs(Route, { element: _jsx(AppLayout, {}), children: [_jsx(Route, { path: "/", element: _jsx(Dashboard, {}) }), _jsx(Route, { path: "/papers", element: _jsx(Papers, {}) }), _jsx(Route, { path: "/papers/:id/viewer", element: _jsx(PaperViewerPage, {}) }), _jsx(Route, { path: "/journals", element: _jsx(Journals, {}) }), _jsx(Route, { path: "/manuscripts", element: _jsx(Manuscripts, {}) }), _jsx(Route, { path: "/workflow", element: _jsx(Workflow, {}) }), _jsx(Route, { path: "/evaluations", element: _jsx(Evaluations, {}) }), _jsx(Route, { path: "/response-letters", element: _jsx(ResponseLetters, {}) }), _jsx(Route, { path: "/tags-comments", element: _jsx(TagsComments, {}) }), _jsx(Route, { path: "/diff", element: _jsx(DiffPage, {}) }), _jsx(Route, { path: "/exports", element: _jsx(Exports, {}) }), _jsx(Route, { path: "/submission", element: _jsx(Submission, {}) }), _jsx(Route, { path: "/improvements", element: _jsx(Improvements, {}) }), _jsx(Route, { path: "/compliance", element: _jsx(Compliance, {}) }), _jsx(Route, { path: "/models", element: _jsx(Models, {}) }), _jsx(Route, { path: "/status", element: _jsx(Status, {}) }), _jsx(Route, { path: "/chat", element: _jsx(Chat, {}) })] }) }));
}
