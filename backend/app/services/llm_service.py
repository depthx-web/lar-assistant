"""LLM service for manuscript compliance and evaluation."""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ai.registry import get_provider_class

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-powered manuscript analysis."""

    def __init__(self, db: Session, model_name: str = "qwen2.5:3b-instruct"):
        self.db = db
        self.model_name = model_name
        self.provider = None

    def _ensure_provider(self) -> bool:
        if self.provider is not None:
            return True
        try:
            provider_cls = get_provider_class("ollama")
            self.provider = provider_cls()
            return True
        except (KeyError, Exception) as e:
            logger.warning(f"LLM provider not available: {e}")
            self.provider = None
            return False

    def check_requirements(self, requirements, content, title=""):
        if not requirements:
            return []
        if not self._ensure_provider():
            return [{"requirement_id": r.get("id"), "key": r.get("key", ""), "status": "UNKNOWN", "confidence": 0.0, "details": "LLM unavailable", "evidence": None} for r in requirements]
        try:
            prompt = self._build_requirement_prompt(requirements, content, title)
            response = self.provider.generate(prompt=prompt, model=self.model_name, temperature=0.1, max_tokens=2000)
            return self._parse_requirement_response(response, requirements)
        except Exception as e:
            logger.exception(f"Requirement check failed: {e}")
            return [{"requirement_id": r.get("id"), "key": r.get("key", "unknown"), "status": "UNKNOWN", "confidence": 0.0, "details": f"Error: {e}", "evidence": None} for r in requirements]

    def detect_rejection_risks(self, content, score, style_issues, title=""):
        if not self._ensure_provider():
            return []
        try:
            issues_summary = json.dumps(style_issues[:5], indent=2) if style_issues else "None"
            prompt = self._build_risk_prompt(content, score, issues_summary, title)
            response = self.provider.generate(prompt=prompt, model=self.model_name, temperature=0.2, max_tokens=1500)
            return self._parse_risk_response(response)
        except Exception as e:
            logger.warning(f"Rejection risk detection failed: {e}")
            return []

    def _build_requirement_prompt(self, requirements, content, title):
        reqs = "\n".join(f"[{i+1}] {r.get('key', 'UNKNOWN')}: {r.get('description', '')} (Type: {r.get('requirement_type', 'MANDATORY')})" for i, r in enumerate(requirements))
        return f"""You are an academic manuscript compliance checker. Evaluate this manuscript against journal requirements.

Manuscript Title: {title}

Requirements:
{reqs}

Manuscript Content (first 4000 chars):
{content[:4000]}

For each requirement determine: status (PASS/FAIL/WARNING/NOT_APPLICABLE), confidence (0.0-1.0), details, and evidence.

Respond in JSON: {{"results": [{{"requirement_id": <id>, "key": "<key>", "status": "<PASS|FAIL|WARNING|NOT_APPLICABLE>", "confidence": <0.0-1.0>, "details": "<explanation>", "evidence": "<quoted text or null>"}}]}}

Be thorough and evidence-based. Only PASS if clearly met."""

    def _build_style_prompt(self, content, style_profile, title):
        return f"""You are a journal style analyst. Compare manuscript to style profile.

Manuscript Title: {title}

Journal Style Profile:
{style_profile}

Manuscript Content (first 3000 chars):
{content[:3000]}

Identify issues: structure, voice, tone, citation, terminology, paragraph length.

Respond in JSON: {{"issues": [{{"type": "<type>", "severity": "<high|medium|low>", "message": "<description>", "suggestion": "<how to fix>"}}]}}

If no issues: {{"issues": []}}"""

    def _build_risk_prompt(self, content, score, style_issues, title):
        return f"""You are a journal editor assessing rejection risk.

Manuscript Title: {title}
Overall Compliance Score: {score:.0f}%
Style Issues: {style_issues}

Manuscript Content (first 3000 chars):
{content[:3000]}

Assess risks: structural, scientific, methodology, writing, citation.

Respond in JSON: {{"risks": [{{"type": "<type>", "severity": "<high|medium|low>", "message": "<description>", "recommendation": "<what to do>"}}]}}

If no risks: {{"risks": []}}"""

    def _parse_requirement_response(self, response, requirements):
        try:
            data = self._extract_json(response)
            results = data.get("results", [])
            req_map = {r.get("key"): r for r in requirements}
            mapped = []
            for r in results:
                key = r.get("key")
                orig = req_map.get(key, {})
                mapped.append({"requirement_id": r.get("requirement_id", orig.get("id")), "key": key or orig.get("key", "unknown"), "description": orig.get("description", ""), "status": r.get("status", "UNKNOWN"), "confidence": float(r.get("confidence", 0.0)), "details": r.get("details", ""), "evidence": r.get("evidence")})
            mentioned = {r.get("key") for r in mapped}
            for req in requirements:
                if req.get("key") not in mentioned:
                    mapped.append({"requirement_id": req.get("id"), "key": req.get("key", "unknown"), "description": req.get("description", ""), "status": "UNKNOWN", "confidence": 0.0, "details": "Not addressed", "evidence": None})
            return mapped
        except Exception as e:
            logger.warning(f"Parse failed: {e}")
            return [{"requirement_id": r.get("id"), "key": r.get("key", "unknown"), "description": r.get("description", ""), "status": "UNKNOWN", "confidence": 0.0, "details": f"Parse error: {e}", "evidence": None} for r in requirements]

    def _parse_style_response(self, response):
        try:
            data = self._extract_json(response)
            return [{"type": i.get("type", "other"), "severity": i.get("severity", "medium"), "message": i.get("message", ""), "suggestion": i.get("suggestion")} for i in data.get("issues", [])]
        except Exception as e:
            logger.warning(f"Parse failed: {e}")
            return []

    def _parse_risk_response(self, response):
        try:
            data = self._extract_json(response)
            return [{"type": r.get("type", "other"), "severity": r.get("severity", "medium"), "message": r.get("message", ""), "recommendation": r.get("recommendation")} for r in data.get("risks", [])]
        except Exception as e:
            logger.warning(f"Parse failed: {e}")
            return []

    def _parse_improvement_response(self, response):
        try:
            data = self._extract_json(response)
            return [{"priority": s.get("priority", "important"), "category": s.get("category", "content"), "suggestion": s.get("suggestion", ""), "rationale": s.get("rationale", ""), "effort": s.get("effort", "medium")} for s in data.get("suggestions", [])]
        except Exception as e:
            logger.warning(f"Parse failed: {e}")
            return []

    def generate_improvements(self, content, checks, style_issues, title=""):
        if not self._ensure_provider():
            return []
        try:
            checks_summary = json.dumps(checks[:5], indent=2) if checks else "None"
            issues_summary = json.dumps(style_issues[:5], indent=2) if style_issues else "None"
            prompt = self._build_improvement_prompt(content, checks_summary, issues_summary, title)
            response = self.provider.generate(prompt=prompt, model=self.model_name, temperature=0.5, max_tokens=2000)
            return self._parse_improvement_response(response)
        except Exception as e:
            logger.warning(f"Improvement generation failed: {e}")
            return []

    def _build_improvement_prompt(self, content, checks, style_issues, title):
        return f"""You are an academic writing improvement advisor. Suggest concrete improvements for this manuscript.

Manuscript Title: {title}

Manuscript Content (first 3000 chars):
{content[:3000]}

Compliance Checks:
{checks}

Style Issues:
{style_issues}

Suggest up to 8 actionable improvements with priority (high/medium/low), category (structure/content/clarity/style), suggestion text, rationale, and effort estimate (small/medium/large).

Respond in JSON: {{"suggestions": [{{"priority": "<high|medium|low>", "category": "<structure|content|clarity|style>", "suggestion": "<actionable improvement>", "rationale": "<why this matters>", "effort": "<small|medium|large>"}}]}}

If no issues: {{"suggestions": []}}"""

    def _parse_improvement_response(self, response):
        try:
            data = self._extract_json(response)
            return [{"priority": s.get("priority", "important"), "category": s.get("category", "content"), "suggestion": s.get("suggestion", ""), "rationale": s.get("rationale", ""), "effort": s.get("effort", "medium")} for s in data.get("suggestions", [])]
        except Exception as e:
            logger.warning(f"Parse failed: {e}")
            return []

    @staticmethod
    def _extract_json(text):
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not extract JSON: {text[:200]}")





