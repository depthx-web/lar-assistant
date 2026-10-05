import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Input } from "../components/ui/Input";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { Tags, MessageSquare, Loader2, Plus, Trash2, Check } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
export default function TagsCommentsPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [manuscriptId, setManuscriptId] = useState("");
    const [tags, setTags] = useState([]);
    const [comments, setComments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showTagModal, setShowTagModal] = useState(false);
    const [showCommentModal, setShowCommentModal] = useState(false);
    const [tagName, setTagName] = useState("");
    const [commentText, setCommentText] = useState("");
    const [versionId, setVersionId] = useState("");
    const loadData = async () => {
        if (!manuscriptId)
            return;
        setLoading(true);
        try {
            const [tagsRes, commentsRes] = await Promise.all([
                api.get(`/manuscripts/${manuscriptId}/tags`),
                api.get(`/manuscripts/${manuscriptId}/comments`),
            ]);
            setTags(tagsRes.data.tags || []);
            setComments(commentsRes.data.comments || []);
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
        finally {
            setLoading(false);
        }
    };
    const handleAddTag = async () => {
        if (!tagName.trim())
            return;
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
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
    };
    const handleAddComment = async () => {
        if (!commentText.trim())
            return;
        try {
            await api.post(`/manuscripts/${manuscriptId}/comments`, {
                content: commentText.trim(),
                version_id: versionId ? Number(versionId) : null,
            });
            setShowCommentModal(false);
            setCommentText("");
            setVersionId("");
            loadData();
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
    };
    const handleDeleteTag = async (tagId) => {
        if (!confirm(t("tags_comments.confirm_delete_tag")))
            return;
        try {
            await api.delete(`/manuscripts/${manuscriptId}/tags/${tagId}`);
            loadData();
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
    };
    const handleDeleteComment = async (commentId) => {
        if (!confirm(t("tags_comments.confirm_delete_comment")))
            return;
        try {
            await api.delete(`/manuscripts/${manuscriptId}/comments/${commentId}`);
            loadData();
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
    };
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("tags_comments.title"), subtitle: t("tags_comments.subtitle") }), _jsx(Card, { title: t("manuscripts.select") || "Select Manuscript", children: _jsxs("div", { className: "flex gap-3", children: [_jsx(Input, { type: "number", placeholder: t("manuscripts.select"), value: manuscriptId, onChange: (e) => setManuscriptId(e.target.value), className: "flex-1" }), _jsxs(Button, { onClick: loadData, disabled: !manuscriptId || loading, children: [loading && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("journals.load")] })] }) }), manuscriptId && (_jsx(_Fragment, { children: _jsxs("div", { className: "grid grid-cols-2 gap-6", children: [_jsx(Card, { title: t("tags_comments.title"), action: _jsxs(Button, { size: "sm", onClick: () => setShowTagModal(true), children: [_jsx(Plus, { className: "w-4 h-4" }), t("tags_comments.add_tag")] }), children: tags.length === 0 ? (_jsx(EmptyState, { icon: _jsx(Tags, { className: "w-10 h-10" }), title: t("tags_comments.no_tags"), description: t("tags_comments.no_tags_desc") })) : (_jsx("div", { className: "space-y-2", children: tags.map((tag) => (_jsxs("div", { className: "flex items-center justify-between p-3 bg-surface-2 rounded-lg", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Badge, { variant: tag.is_baseline ? "success" : "info", children: tag.tag_name }), tag.label && _jsx("span", { className: "text-sm text-text-muted", children: tag.label })] }), _jsx(Button, { variant: "ghost", size: "sm", onClick: () => handleDeleteTag(tag.id), className: "text-error", children: _jsx(Trash2, { className: "w-4 h-4" }) })] }, tag.id))) })) }), _jsx(Card, { title: `${t("nav.chat")} (${comments.filter((c) => !c.is_resolved).length})`, action: _jsxs(Button, { size: "sm", onClick: () => setShowCommentModal(true), children: [_jsx(Plus, { className: "w-4 h-4" }), t("tags_comments.add_comment")] }), children: comments.length === 0 ? (_jsx(EmptyState, { icon: _jsx(MessageSquare, { className: "w-10 h-10" }), title: t("tags_comments.no_comments"), description: t("tags_comments.no_comments_desc") })) : (_jsx("div", { className: "space-y-2 max-h-96 overflow-y-auto", children: comments.map((comment) => (_jsxs("div", { className: "p-3 bg-surface-2 rounded-lg", children: [_jsxs("div", { className: "flex items-start justify-between gap-2", children: [_jsx("p", { className: "text-sm text-text flex-1", children: comment.content }), _jsxs("div", { className: "flex items-center gap-1 shrink-0", children: [comment.is_resolved ? (_jsx(Check, { className: "w-4 h-4 text-success" })) : (_jsx(Badge, { variant: "warning", className: "text-xs", children: t("tags_comments.unresolved") })), _jsx(Button, { variant: "ghost", size: "sm", onClick: () => handleDeleteComment(comment.id), className: "text-error shrink-0", children: _jsx(Trash2, { className: "w-4 h-4" }) })] })] }), _jsx("p", { className: "text-xs text-text-faint mt-1", children: new Date(comment.created_at).toLocaleString() })] }, comment.id))) })) })] }) })), _jsx(Modal, { open: showTagModal, onClose: () => setShowTagModal(false), title: t("tags_comments.add_tag"), footer: _jsxs(_Fragment, { children: [_jsx(Button, { variant: "ghost", onClick: () => setShowTagModal(false), children: t("common.cancel") }), _jsx(Button, { onClick: handleAddTag, children: t("common.save") })] }), children: _jsxs("div", { className: "space-y-4", children: [_jsx(Input, { label: t("tags_comments.tag_name"), value: tagName, onChange: (e) => setTagName(e.target.value) }), _jsx(Input, { label: t("tags_comments.version"), value: versionId, onChange: (e) => setVersionId(e.target.value), placeholder: "Version ID (optional)" })] }) }), _jsx(Modal, { open: showCommentModal, onClose: () => setShowCommentModal(false), title: t("tags_comments.add_comment"), footer: _jsxs(_Fragment, { children: [_jsx(Button, { variant: "ghost", onClick: () => setShowCommentModal(false), children: t("common.cancel") }), _jsx(Button, { onClick: handleAddComment, children: t("common.save") })] }), children: _jsxs("div", { className: "space-y-4", children: [_jsx("textarea", { value: commentText, onChange: (e) => setCommentText(e.target.value), placeholder: t("tags_comments.comment_text"), className: "w-full h-32 px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary resize-none" }), _jsx(Input, { label: t("tags_comments.version"), value: versionId, onChange: (e) => setVersionId(e.target.value), placeholder: "Version ID (optional)" })] }) })] }));
}
