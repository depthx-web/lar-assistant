import { useParams, useNavigate } from "react-router-dom";
import PaperViewer from "../components/paper/PaperViewer";

export default function PaperViewerPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const docId = Number(id) || 0;

  return <PaperViewer docId={docId} onClose={() => navigate("/papers")} />;
}