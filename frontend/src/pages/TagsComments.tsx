import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Input } from "../components/ui/Input";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { Alert } from "../components/ui/Alert";
import { Tags, MessageSquare, Loader2, Plus, Trash2, Check } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";

interface Tag {
  id: number;
  tag_name: string;
  label?: string;
  version_id: number;
  is_baseline: boolean;
  created_at: string;
}

interface Comment {
  id: number;
  version_id?: number;
  content: string;
  is_resolved: boolean;
  created_at: string;
}

export default function TagsCommentsPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [manuscriptId, setManuscriptId] = useState("");
  const [tags, setTags] = useState<Tag[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(false);
  const [showTagModal, setShowTagModal] = useState(false);
  const [showCommentModal, setShowCommentModal] = useState(false);
  const [tagName, setTagName] = useState("");
  const [commentText, setCommentText] = useState("");
  const [versionId, setVersionId] = useState("");

  const loadData = async () => {
    if (!manuscriptId) return;
    setLoading(true);
    try {
      const [tagsRes, commentsRes] = await Promise.all([
        api.get(`/manuscripts/${manuscriptId}/tags`),
        api.get(`/manuscripts/${manuscriptId}/comments`),
      ]);
      setTags(tagsRes.data.tags || []);
      setComments(commentsRes.data.comments || []);
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    } finally {
      setLoading(false);
    }
  };

  const handleAddTag = async () => {
    if (!tagName.trim()) return;
    try {
      await api.post(`/manuscripts/${manuscriptId}/tags`, {
        tag_name: tagName.trim(),
        version_id: versionId ? Number(versionId) : null,
        label: tagName.trim(),
        is_baseline: false,
      });
      setShowTagModal(false);
      setTagName("");
      setVersionId("");
      loadData();
      addToast({ variant: "success", title: t("common.saved") });
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    }
  };

  const handleAddComment = async () => {
    if (!commentText.trim()) return;
    try {
      await api.post(`/manuscripts/${manuscriptId}/comments`, {
        content: commentText.trim(),
        version_id: versionId ? Number(versionId) : null,
      });
      setShowCommentModal(false);
      setCommentText("");
      setVersionId("");
      loadData();
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    }
  };

  const handleDeleteTag = async (tagId: number) => {
    if (!confirm(t("tags_comments.confirm_delete_tag"))) return;
    try {
      await api.delete(`/manuscripts/${manuscriptId}/tags/${tagId}`);
      loadData();
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm(t("tags_comments.confirm_delete_comment"))) return;
    try {
      await api.delete(`/manuscripts/${manuscriptId}/comments/${commentId}`);
      loadData();
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader title={t("tags_comments.title")} subtitle={t("tags_comments.subtitle")} />

      <Card title={t("manuscripts.select") || "Select Manuscript"}>
        <div className="flex gap-3">
          <Input
            type="number"
            placeholder={t("manuscripts.select")}
            value={manuscriptId}
            onChange={(e) => setManuscriptId(e.target.value)}
            className="flex-1"
          />
          <Button onClick={loadData} disabled={!manuscriptId || loading}>
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {t("journals.load")}
          </Button>
        </div>
      </Card>

      {manuscriptId && (
        <>
          <div className="grid grid-cols-2 gap-6">
            {/* Tags */}
            <Card
              title={t("tags_comments.title")}
              action={
                <Button size="sm" onClick={() => setShowTagModal(true)}>
                  <Plus className="w-4 h-4" />
                  {t("tags_comments.add_tag")}
                </Button>
              }
            >
              {tags.length === 0 ? (
                <EmptyState
                  icon={<Tags className="w-10 h-10" />}
                  title={t("tags_comments.no_tags")}
                  description={t("tags_comments.no_tags_desc")}
                />
              ) : (
                <div className="space-y-2">
                  {tags.map((tag) => (
                    <div key={tag.id} className="flex items-center justify-between p-3 bg-surface-2 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Badge variant={tag.is_baseline ? "success" : "info"}>{tag.tag_name}</Badge>
                        {tag.label && <span className="text-sm text-text-muted">{tag.label}</span>}
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => handleDeleteTag(tag.id)} className="text-error">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Comments */}
            <Card
              title={`${t("nav.chat")} (${comments.filter((c) => !c.is_resolved).length})`}
              action={
                <Button size="sm" onClick={() => setShowCommentModal(true)}>
                  <Plus className="w-4 h-4" />
                  {t("tags_comments.add_comment")}
                </Button>
              }
            >
              {comments.length === 0 ? (
                <EmptyState
                  icon={<MessageSquare className="w-10 h-10" />}
                  title={t("tags_comments.no_comments")}
                  description={t("tags_comments.no_comments_desc")}
                />
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {comments.map((comment) => (
                    <div key={comment.id} className="p-3 bg-surface-2 rounded-lg">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm text-text flex-1">{comment.content}</p>
                        <div className="flex items-center gap-1 shrink-0">
                          {comment.is_resolved ? (
                            <Check className="w-4 h-4 text-success" />
                          ) : (
                            <Badge variant="warning" className="text-xs">{t("tags_comments.unresolved")}</Badge>
                          )}
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteComment(comment.id)} className="text-error shrink-0">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <p className="text-xs text-text-faint mt-1">{new Date(comment.created_at).toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </>
      )}

      <Modal
        open={showTagModal}
        onClose={() => setShowTagModal(false)}
        title={t("tags_comments.add_tag")}
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowTagModal(false)}>{t("common.cancel")}</Button>
            <Button onClick={handleAddTag}>{t("common.save")}</Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input label={t("tags_comments.tag_name")} value={tagName} onChange={(e) => setTagName(e.target.value)} />
          <Input label={t("tags_comments.version")} value={versionId} onChange={(e) => setVersionId(e.target.value)} placeholder="Version ID (optional)" />
        </div>
      </Modal>

      <Modal
        open={showCommentModal}
        onClose={() => setShowCommentModal(false)}
        title={t("tags_comments.add_comment")}
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowCommentModal(false)}>{t("common.cancel")}</Button>
            <Button onClick={handleAddComment}>{t("common.save")}</Button>
          </>
        }
      >
        <div className="space-y-4">
          <textarea
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            placeholder={t("tags_comments.comment_text")}
            className="w-full h-32 px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary resize-none"
          />
          <Input label={t("tags_comments.version")} value={versionId} onChange={(e) => setVersionId(e.target.value)} placeholder="Version ID (optional)" />
        </div>
      </Modal>
    </div>
  );
}
