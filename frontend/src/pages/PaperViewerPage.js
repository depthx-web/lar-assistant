import { jsx as _jsx } from "react/jsx-runtime";
import { useParams, useNavigate } from "react-router-dom";
import PaperViewer from "../components/paper/PaperViewer";
export default function PaperViewerPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const docId = Number(id) || 0;
    return _jsx(PaperViewer, { docId: docId, onClose: () => navigate("/papers") });
}
