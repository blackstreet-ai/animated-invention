"""TopicGenerationAgent – orchestrates discovery & scoring of video-essay ideas.

This scaffold focuses on coordination logic; sub-agents remain stubs until
implemented.  Follows project ADK commenting guidelines for beginners.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional
from functools import lru_cache

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState

# ---------------------------------------------------------------------------
# Stub fallbacks (replace with real implementations later)
# ---------------------------------------------------------------------------

def _stub(name: str, **_: Any) -> Dict[str, Any]:
    """Return a predictable placeholder payload."""

    return {"agent": name, "data": f"[STUB] {name} output"}


class _AsyncStub(BaseAgent):
    """Minimal async-capable stub agent."""

    async def run_async(self, **kwargs: Any) -> Dict[str, Any]:  # noqa: D401
        return _stub(self.__class__.__name__, **kwargs)

    # Needed to satisfy BaseAgent abstract interface – no sync use here.
    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        return state


# Attempt to import real sub-agents, else fall back to stubs
try:
    from video_pipeline.agents.trend_analysis_agent import TrendAnalysisAgent  # type: ignore
except Exception:  # pragma: no cover
    TrendAnalysisAgent = _AsyncStub  # type: ignore

try:
    from video_pipeline.agents.competitor_research_agent import CompetitorResearchAgent  # type: ignore
except Exception:  # pragma: no cover
    CompetitorResearchAgent = _AsyncStub  # type: ignore

try:
    from video_pipeline.agents.keyword_research_agent import KeywordResearchAgent  # type: ignore
except Exception:  # pragma: no cover
    KeywordResearchAgent = _AsyncStub  # type: ignore

try:
    from video_pipeline.agents.ideation_agent import IdeationAgent  # type: ignore
except Exception:  # pragma: no cover
    IdeationAgent = _AsyncStub  # type: ignore

try:
    from video_pipeline.agents.scoring_agent import ScoringAgent  # type: ignore
except Exception:  # pragma: no cover
    ScoringAgent = _AsyncStub  # type: ignore


class TopicGenerationAgent(BaseAgent):
    """Main orchestrator for generating & evaluating topics."""

    def __init__(
        self,
        name: str = "TopicGenerationAgent",
        *,
        topic_count: int = 10,
        scoring_weights: Optional[Dict[str, float]] = None,
        content_type: str = "educational",
        notion_db_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:  # noqa: D401
        super().__init__(name=name, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.topic_count = topic_count
        self.scoring_weights = scoring_weights or {}
        self.content_type = content_type
        self.notion_db_id = notion_db_id

        # Instantiate sub-agents
        self.trend_agent = TrendAnalysisAgent(name="TrendAnalysisAgent")
        self.comp_agent = CompetitorResearchAgent(name="CompetitorResearchAgent")
        self.keyword_agent = KeywordResearchAgent(name="KeywordResearchAgent")
        self.ideation_agent = IdeationAgent(name="IdeationAgent")
        self.scoring_agent = ScoringAgent(name="ScoringAgent")

        # -------------------------------------------------------------
        # Rate-limit semaphore (e.g. API quotas). 1 = serialize, >1 parallel.
        # In real usage expose via config; hard-coded to 3 for stub stage.
        # -------------------------------------------------------------
        self._rate_sem = asyncio.Semaphore(3)

    # ------------------------------------------------------------------
    # Core execution (sync wrapper around async orchestration)
    # ------------------------------------------------------------------
    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        # Gather user context
        niche = state.topic or "general"
        competitors: List[str] = state.metadata.get("competitors", [])
        audience = state.metadata.get("target_audience", "general")

        async def orchestrate() -> List[Dict[str, Any]]:  # noqa: D401
            # Parallel data collection
            async def limited(coro):  # helper respects semaphore
                async with self._rate_sem:
                    return await coro

            trend_task = limited(self.trend_agent.run_async(niche=niche))
            comp_task = limited(
                self.comp_agent.run_async(niche=niche, competitors=competitors)
            )
            keyword_task = limited(self.keyword_agent.run_async(niche=niche))

            trend, comp, keywords = await asyncio.gather(trend_task, comp_task, keyword_task)

            # Ideation – over-generate
            ideas = await self.ideation_agent.run_async(
                niche=niche,
                audience=audience,
                context={"trend": trend, "competition": comp, "keywords": keywords},
                content_type=self.content_type,
                count=self.topic_count * 2,
            )

            # Scoring & selection
            scored = await self.scoring_agent.run_async(
                ideas=ideas,
                aux_data={"trend": trend, "competition": comp, "keywords": keywords},
                weights=self.scoring_weights,
                top_n=self.topic_count,
            )
            # Ensure *iterable* then uniform format
            if isinstance(scored, (str, dict)):
                scored = [scored]
            return [self._format_rec(item) for item in scored]

        # Execute orchestrator coroutine
        recommendations = asyncio.run(orchestrate())
        state.metadata["topic_recommendations"] = recommendations
        self._maybe_push_to_notion(recommendations)
        return state

    # ------------------------------------------------------------------
    # Notion MCP integration – placeholder
    # ------------------------------------------------------------------
    def _maybe_push_to_notion(self, topics: List[Dict[str, Any]]) -> None:  # noqa: D401
        if not self.notion_db_id:
            return
        try:
            # Delayed import; project still runs without MCP SDK.
            from mcp_client import push_to_notion  # type: ignore

            push_to_notion(database_id=self.notion_db_id, rows=topics)
            self.logger.info("Pushed %d topics to Notion", len(topics))
        except Exception as exc:  # pragma: no cover
            self.logger.warning("Failed to push topics to Notion: %s", exc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _format_rec(self, raw: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        """Ensure each recommendation dict contains required keys."""

        return {
            "title": raw.get("title", "Untitled Topic") if isinstance(raw, dict) else "Untitled Topic",
            "core_argument": raw.get("core_argument", "TBD") if isinstance(raw, dict) else "TBD",
            "keywords": raw.get("keywords", []) if isinstance(raw, dict) else [],
            "score": raw.get("score", 0.0) if isinstance(raw, dict) else 0.0,
            "rationale": raw.get("rationale", raw.get("data", raw)) if isinstance(raw, dict) else raw,
        }

    # Simple TTL-less in-memory cache decorator example (optional)
    @staticmethod
    @lru_cache(maxsize=128)
    def _cached_expensive_call(key: str) -> str:  # noqa: D401
        """Stub for future expensive operations (e.g. external API)."""

        return f"cached_result_for_{key}"
