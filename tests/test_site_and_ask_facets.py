"""P3 facet plumbing in the site builder and WF4's card index."""
import os
import sys
from pathlib import Path

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-fake")
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import build_site  # noqa: E402
import wf4_ask  # noqa: E402


def test_site_folds_sectors_into_tag_index():
    meta = build_site._clean_meta({"title": "x", "tags": ["pinn"], "sectors": ["sector:wwtp", "pinn"]})
    assert meta["tags"] == ["pinn", "sector:wwtp"]


def test_site_handles_legacy_card_without_sectors():
    meta = build_site._clean_meta({"title": "x", "tags": "[Experimental Design, Bayesian]"})
    assert meta["tags"] == ["Experimental Design", "Bayesian"]


def test_ask_index_includes_sectors():
    cards = [{"path": "content/Hybrid_SciML/a.md", "category": "Hybrid_SciML",
              "meta": {"title": "A", "date": "2026-10-01", "tags": ["pinn"], "sectors": ["sector:wwtp"]}}]
    assert wf4_ask.build_index(cards) == "[1] A | Hybrid_SciML | 2026-10-01 | pinn | sector:wwtp"
