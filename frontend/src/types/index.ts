export interface DocumentMetadata {
  id: number;
  title: string | null;
  authors: string | null;
  doi: string | null;
  journal: string | null;
  year: number | null;
  source_url: string | null;
  local_path: string | null;
  file_hash: string;
  document_type: string;
  processing_status: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  documents: DocumentMetadata[];
  total: number;
}

export interface SearchChunkResult {
  chunk_id: string;
  document_id: number;
  content: string;
  similarity: number;
  page?: number | null;
  section?: string | null;
  source?: string | null;
}

export interface SearchResponse {
  query: string;
  results: SearchChunkResult[];
  total: number;
}

export interface RAGSource {
  source_id: number;
  chunk_id: string;
  document_id: number;
  document_title: string;
  similarity: number;
  content_preview: string;
}

export interface RAGResponse {
  answer: string;
  sources: RAGSource[];
  context_used: number;
  model: string;
  question: string;
  error?: string | null;
}

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ModelInfo {
  name: string;
  provider: string;
  available: boolean;
}

export interface JournalInfo {
  id: number;
  name: string;
  slug: string;
  publisher: string | null;
  issn: string | null;
  official_url: string | null;
  author_guidelines_url: string | null;
  scope: string | null;
  reference_style: string | null;
  created_at: string;
  updated_at: string;
}

export interface RequirementInfo {
  id: number;
  key: string;
  description: string;
  requirement_type: string;
  evidence_level: string;
  value: string | null;
  source_url: string | null;
  source_title: string | null;
  confidence: string | null;
  retrieved_at: string | null;
}

export interface JournalDetail extends JournalInfo {
  article_types: string | null;
  word_limits: string | null;
  style_guide: string | null;
  rejection_patterns: string | null;
  requirements: RequirementInfo[];
}

export interface ManuscriptInfo {
  id: number;
  title: string;
  document_id: number | null;
  journal_id: number | null;
  analysis_status: string;
  overall_compliance_score: number | null;
  mandatory_compliance_score: number | null;
  created_at: string;
  updated_at: string;
  analyzed_at: string | null;
}

export interface StyleIssue {
  type: string;
  severity: string;
  message: string;
  suggestion?: string | null;
}

export interface RejectionRisk {
  type: string;
  severity: string;
  message: string;
  recommendation?: string | null;
}

export interface ManuscriptDetail extends ManuscriptInfo {
  requirement_checks?: RequirementCheck[];
  style_issues?: StyleIssue[];
  rejection_risks?: RejectionRisk[];
}

export interface RequirementCheck {
  requirement_id: number;
  key: string;
  status: string;
  confidence: number;
  details?: string | null;
  evidence?: string | null;
}

export interface SystemComponentStatus {
  name: string;
  status: "ok" | "error" | "unavailable";
  detail?: string | null;
}

export interface SystemStatusResponse {
  status: "ok" | "degraded";
  components: Record<string, SystemComponentStatus>;
  uptime_check: boolean;
}

export interface QueueJob {
  id: number;
  job_type: string;
  status: string;
  progress: number;
  created_at: string;
  error?: string | null;
}

export interface QueueResponse {
  jobs: QueueJob[];
  total: number;
  active: number;
}

export interface ModelRoleAssignment {
  role: string;
  model_name: string | null;
  provider: string | null;
}
