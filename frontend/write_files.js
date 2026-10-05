const fs = require(" fs\);

// Badge.tsx
const badge = import { cn } from \./cn\;
interface BadgeProps {
 children: React.ReactNode;
 variant?: \default\ | \success\ | \warning\ | \error\ | \info\ | \muted\ | \official\;
 className?: string;
}
export function Badge({ children, variant = \default\, className }: BadgeProps) {
 const classes: Record<string, string> = {
 default: \b-info\,
 success: \b-ok\,
 warning: \b-warn\,
 error: \b-crit\,
 info: \b-info\,
 muted: \b-mute\,
 official: \b-official\,
 };
 return (
 <span className={cn(\badge\, classes[variant], className)}>
 {children}
 </span>
 );
}
;
fs.writeFileSync(\E:\\\\depthx\\\\lar-assistant\\\\frontend\\\\src\\\\components\\\\ui\\\\Badge.tsx\, badge);
console.log(\Badge written\);

// Dashboard.tsx
const dashboard = import { useEffect, useState } from \react\;
import { Link } from \react-router-dom\;
import api from \../lib/api\;
import { Card } from \../components/ui/Card\;
import { Badge } from \../components/ui/Badge\;
import { Button } from \../components/ui/Button\;
import { Progress } from \../components/ui/Progress\;
import { Skeleton } from \../components/ui/Skeleton\;
import { DocumentMetadata } from \../types\;
import { useI18n } from \../context/I18nContext\;

export default function DashboardPage() {
 const { t } = useI18n();
 const [docs, setDocs] = useState<DocumentMetadata[]>([]);
 const [journalCount, setJournalCount] = useState(0);
 const [manuscriptCount, setManuscriptCount] = useState(0);
 const [loading, setLoading] = useState(true);

 useEffect(() => {
 Promise.all([
 api.get(\/documents\).then((r) => r.data),
 api.get(\/journals?limit=1\).then((r) => r.data.total || 0).catch(() => 0),
 api.get(\/manuscripts?limit=1\).then((r) => r.data.total || 0).catch(() => 0),
 ]).then(([docsData, journalsTotal, manuscriptsTotal]) => {
 setDocs(docsData.documents ?? []);
 setJournalCount(typeof journalsTotal === \number\ ? journalsTotal : 0);
 setManuscriptCount(typeof manuscriptsTotal === \number\ ? manuscriptsTotal : 0);
 setLoading(false);
 }).catch(() => setLoading(false));
 }, []);

 if (loading) {
 return (
 <div className=\space-y-6\>
 <Skeleton className=\h-8 w-48\ />
 <div className=\grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4\>
 {[1, 2, 3, 4].map((i) => <Skeleton key={i} className=\h-28\ lines={3} />)}
 </div>
 </div>
 );
 }

 const completedDocs = docs.filter((d) => d.processing_status === \completed\);
 const processingDocs = docs.filter((d) => d.processing_status === \processing\);

 return (
 <div className=\screen\>
 <div className=\pagehead\>
 <div>
 <h1 className=\t\>{t(\dashboard.title\)}</h1>
 <p className=\sub\>{t(\dashboard.papers\)} · {docs.length}</p>
 </div>
 <div className=\actions\>
 <Link to=\/papers\>
 <Button variant=\secondary\ size=\sm\>
 <svg className=\i\><use href=\#i-upload\/></svg>
 <span className=\t\>{t(\dashboard.upload_paper\)}</span>
 </Button>
 </Link>
 <Link to=\/manuscripts\>
 <Button variant=\primary\ size=\sm\>
 <svg className=\i\><use href=\#i-edit\/></svg>
 <span className=\t\>{t(\dashboard.continue_writing\)}</span>
 </Button>
 </Link>
 </div>
 </div>
 <div className=\stats\>
 <div className=\stat\><b>{docs.length}</b><span className=\t\>{t(\dashboard.papers\)}</span></div>
 <div className=\stat\><b>{journalCount}</b><span className=\t\>{t(\dashboard.journals\)}</span></div>
 <div className=\stat\><b>{manuscriptCount}</b><span className=\t\>{t(\dashboard.manuscripts\)}</span></div>
 <div className=\stat\><b>{completedDocs.length}</b><span className=\t\>{t(\dashboard.analyzed\)}</span></div>
 </div>
 <div className=\grid2\>
 <div className=\stack\>
 <Card title={t(\dashboard.attention_required\)}>
 <div className=\row\>
 <span className=\sev blocking\ />
 <div className=\grow\>
 <div className=\tt t\>{t(\dashboard.missing_methods\)}</div>
 <div className=\faint\>Manuscript: Hippocampal atrophy rates</div>
 </div>
 <Badge variant=\error\>{t(\common.blocking\)}</Badge>
 </div>
 <div className=\row\>
 <span className=\sev critical\ />
 <div className=\grow\>
 <div className=\tt t\>{t(\dashboard.unsupported_claims\)}</div>
 <div className=\faint\>{t(\dashboard.no_evidence\)}</div>
 </div>
 <Badge variant=\warning\>{t(\common.critical\)}</Badge>
 </div>
 </Card>
 <Card title={t(\dashboard.recent_papers\)}>
 <div className=\in\>
 {docs.slice(0, 3).map((doc) => (
 <div key={doc.id} className=\row\>
 <svg className=\i faint\><use href=\#i-paper\/></svg>
 <div className=\grow\>
 <div className=\tt\>{doc.title || doc.file_hash.slice(0, 12)}</div>
 <div className=\faint\>{doc.authors} · {doc.year || \2023\}</div>
 </div>
 <Badge variant={doc.processing_status === \completed\ ? \success\ : \info\}>
 {doc.processing_status === \completed\ ? t(\papers.status_ready\) : t(\papers.status_processing\)}
 </Badge>
 </div>
 ))}
 </div>
 </Card>
 <Card title={t(\dashboard.recent_activity\)}>
 <div className=\in\>
 <div className=\row\><div className=\grow t\>{t(\dashboard.paper_imported\)}</div><span className=\faint\>12 min</span></div>
 <div className=\row\><div className=\grow t\>{t(\dashboard.pdf_processed\)}</div><span className=\faint\>48 min</span></div>
 <div className=\row\><div className=\grow t\>{t(\dashboard.manuscript_analyzed\)}</div><span className=\faint\>{t(\common.yesterday\)}</span></div>
 </div>
 </Card>
 </div>
 <div className=\stack\>
 <Card title={t(\dashboard.processing_queue\)}>
 <div className=\in\>
 {processingDocs.slice(0, 2).map((doc) => (
 <div key={doc.id} className=\row\>
 <div className=\grow\>
 <div className=\tt\>{doc.authors || doc.file_hash.slice(0, 12)}</div>
 <Progress value={75} showLabel size=\sm\ />
 </div>
 </div>
 ))}
 {completedDocs.slice(0, 1).map((doc) => (
 <div key={doc.id} className=\row\>
 <div className=\grow\><div className=\tt\>{doc.authors || doc.file_hash.slice(0, 12)}</div></div>
 <Badge variant=\success\><svg className=\i\><use href=\#i-check\/></svg><span className=\t\>{t(\common.completed\)}</span></Badge>
 </div>
 ))}
 </div>
 </Card>
 <Card title={t(\dashboard.system_status\)}>
 <div className=\in\>
 <div className=\kv\><span className=\t\>UI Engine</span><span className=\s\><i className=\dot\></i><span className=\t\>Online</span></span></div>
 <div className=\kv\><span className=\t\>Database</span><span className=\s\><i className=\dot\></i><span className=\t\>Connected</span></span></div>
 <div className=\kv\><span>Ollama</span><span className=\s\><i className=\dot\></i><span className=\t\>Connected</span></span></div>
 <div className=\kv\><span className=\t\>Vector DB</span><span className=\s\><i className=\dot\></i><span className=\t\>Ready</span></span></div>
 </div>
 </Card>
 </div>
 </div>
 </div>
 );
}
;
fs.writeFileSync(\E:\\\\depthx\\\\lar-assistant\\\\frontend\\\\src\\\\pages\\\\Dashboard.tsx\, dashboard);
console.log(\Dashboard written\);
