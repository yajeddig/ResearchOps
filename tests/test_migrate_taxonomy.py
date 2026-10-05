"""Tests for scripts/migrate_taxonomy.py (P3: LLM dry-run to CSV, deterministic apply)."""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import migrate_taxonomy as mt  # noqa: E402
from utils import frontmatter  # noqa: E402
from utils.taxonomy import Taxonomy  # noqa: E402

TAXONOMY = Taxonomy()


class _Block:
    def __init__(self, type_, **kw):
        self.type = type_
        self.__dict__.update(kw)


class _Response:
    def __init__(self, payload=None, stop_reason="end_turn"):
        self.stop_reason = stop_reason
        self.content = [_Block("text", text=json.dumps(payload))] if payload is not None else []


class FakeClient:
    """Answers by card title; records every request."""

    def __init__(self, answers):
        self.answers = answers
        self.calls = []
        client = self

        class _Messages:
            def create(self, **kwargs):
                client.calls.append(kwargs)
                for title, answer in client.answers.items():
                    if f"TITLE: {title}" in kwargs["messages"][0]["content"]:
                        if isinstance(answer, Exception):
                            raise answer
                        return answer
                raise AssertionError("unexpected card")

        class _Beta:
            messages = _Messages()

        self.beta = _Beta()


def _facets(category, confidence=0.9, tags=("pinn",), sectors=(), candidates=()):
    return _Response({
        "category": category, "confidence": confidence, "tags": list(tags),
        "sectors": list(sectors), "new_tag_candidates": list(candidates),
    })


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@t", cwd=tmp_path)
    git("config", "user.name", "t", cwd=tmp_path)
    cards = {
        "content/Data_Science/a.md": {"title": "Card A", "category": "Data_Science", "tags": ["Free Text"]},
        "content/Data_Science/b.md": {"title": "Card B", "category": "Data_Science", "tags": []},
        "content/Process_Engineering/c.md": {"title": "Card C", "category": "Process_Engineering", "tags": []},
    }
    for rel, meta in cards.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        # realistic length: git only reports a rename above ~50% similarity
        body = f"## Body of {meta['title']}\n" + "".join(f"Paragraph {i} of a real card.\n" for i in range(40))
        path.write_text(frontmatter.dump(meta, body), encoding="utf-8")
    git("add", ".", cwd=tmp_path)
    git("commit", "-q", "-m", "seed", cwd=tmp_path)
    return tmp_path


class TestDryRun:
    def test_writes_csv_and_touches_no_card(self, repo):
        client = FakeClient({
            "Card A": _facets("Hybrid_SciML", tags=("pinn", "ude"), candidates=("latent-sde",)),
            "Card B": _facets("ML_Industrial_Data", confidence=0.4),
            "Card C": _facets("Process_Modeling", sectors=("sector:wwtp",)),
        })
        csv_path = repo / "data" / "taxonomy_migration.csv"

        rows = mt.dry_run(client, TAXONOMY, repo, csv_path, limit=None)

        assert {r["path"]: r["new_category"] for r in rows} == {
            "content/Data_Science/a.md": "Hybrid_SciML",
            "content/Data_Science/b.md": "ML_Industrial_Data",
            "content/Process_Engineering/c.md": "Process_Modeling",
        }
        row_a = next(r for r in rows if r["path"].endswith("a.md"))
        assert row_a["tags"] == "pinn;ude" and row_a["new_tag_candidates"] == "latent-sde"
        assert next(r for r in rows if r["path"].endswith("b.md"))["low_confidence"] == "yes"
        result = subprocess.run(["git", "status", "--porcelain", "content"], cwd=repo, capture_output=True, text=True)
        assert result.stdout == ""

    def test_request_shape_structured_output_and_cached_system(self, repo):
        client = FakeClient({t: _facets("Process_Modeling") for t in ("Card A", "Card B", "Card C")})
        mt.dry_run(client, TAXONOMY, repo, repo / "data" / "m.csv", limit=1)

        call = client.calls[0]
        assert call["output_config"]["format"]["type"] == "json_schema"
        assert call["system"][0]["cache_control"] == {"type": "ephemeral"}
        assert "tool_choice" not in call
        # the card text is sent, the old category is not (it would anchor the answer)
        assert "Data_Science" not in call["messages"][0]["content"]

    def test_resume_skips_classified_cards_and_retries_failures(self, repo):
        csv_path = repo / "data" / "m.csv"
        first = FakeClient({
            "Card A": _facets("Hybrid_SciML"),
            "Card B": RuntimeError("overloaded"),
            "Card C": _Response(stop_reason="max_tokens"),
        })
        rows = mt.dry_run(first, TAXONOMY, repo, csv_path, limit=None)
        assert [r["path"] for r in rows] == ["content/Data_Science/a.md"]

        second = FakeClient({t: _facets("Process_Modeling") for t in ("Card A", "Card B", "Card C")})
        rows = mt.dry_run(second, TAXONOMY, repo, csv_path, limit=None)

        assert len(rows) == 3
        assert len(second.calls) == 2  # card A not re-classified


class TestApply:
    def _write_csv(self, repo, rows):
        csv_path = repo / "data" / "m.csv"
        csv_path.parent.mkdir(exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=mt.FIELDS)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in mt.FIELDS})
        return csv_path

    def test_moves_with_git_and_rewrites_frontmatter(self, repo):
        csv_path = self._write_csv(repo, [
            {"path": "content/Data_Science/a.md", "old_category": "Data_Science", "new_category": "Hybrid_SciML",
             "confidence": "0.91", "tags": "pinn;ude", "sectors": "sector:wwtp"},
            {"path": "content/Data_Science/b.md", "old_category": "Data_Science", "new_category": "ML_Industrial_Data",
             "confidence": "0.80", "tags": "anomaly-detection"},
            {"path": "content/Process_Engineering/c.md", "old_category": "Process_Engineering",
             "new_category": "Process_Modeling", "confidence": "0.70", "tags": "asm"},
        ])

        applied, errors = mt.apply(TAXONOMY, repo, csv_path)

        assert (applied, errors) == (3, [])
        moved = repo / "content" / "Hybrid_SciML" / "a.md"
        meta, body = frontmatter.parse(moved.read_text(encoding="utf-8"))
        assert meta["category"] == "Hybrid_SciML"
        assert meta["legacy_category"] == "Data_Science"
        assert meta["tags"] == ["pinn", "ude"]
        assert meta["sectors"] == ["sector:wwtp"]
        assert meta["confidence"] == 0.91
        assert "projects" not in meta
        assert body.startswith("## Body of Card A") and body.count("Paragraph") == 40
        assert not (repo / "content" / "Data_Science").exists()  # emptied folder removed
        status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True).stdout
        assert "R  content/Data_Science/a.md -> content/Hybrid_SciML/a.md" in status

    def test_invalid_row_aborts_before_touching_anything(self, repo):
        csv_path = self._write_csv(repo, [
            {"path": "content/Data_Science/a.md", "old_category": "Data_Science", "new_category": "Hybrid_SciML",
             "confidence": "0.9", "tags": "pinn"},
            {"path": "content/Data_Science/b.md", "old_category": "Data_Science", "new_category": "Hybrid_SciML",
             "confidence": "0.9", "tags": "not-in-vocabulary"},
        ])

        applied, errors = mt.apply(TAXONOMY, repo, csv_path)

        assert applied == 0
        assert len(errors) == 1 and "not-in-vocabulary" in errors[0]
        assert (repo / "content" / "Data_Science" / "a.md").exists()
        assert not (repo / "content" / "Hybrid_SciML").exists()

    def test_unknown_category_rejected(self, repo):
        csv_path = self._write_csv(repo, [
            {"path": "content/Data_Science/a.md", "old_category": "Data_Science", "new_category": "Data_Science",
             "confidence": "0.9", "tags": "pinn"},
        ])
        applied, errors = mt.apply(TAXONOMY, repo, csv_path)
        assert applied == 0 and "catégorie inconnue" in errors[0]

    def test_hand_edited_inbox_row_is_accepted(self, repo):
        csv_path = self._write_csv(repo, [
            {"path": "content/Data_Science/a.md", "old_category": "Data_Science", "new_category": "_Inbox",
             "confidence": "0.3", "tags": "pinn"},
        ])
        applied, errors = mt.apply(TAXONOMY, repo, csv_path)
        assert (applied, errors) == (1, [])
        assert (repo / "content" / "_Inbox" / "a.md").exists()


def test_summary_counts_moves_and_candidates():
    rows = [
        {"old_category": "Data_Science", "new_category": "Hybrid_SciML", "low_confidence": "", "new_tag_candidates": "a;b"},
        {"old_category": "Data_Science", "new_category": "Hybrid_SciML", "low_confidence": "yes", "new_tag_candidates": "a"},
    ]
    summary = mt.summarize(rows)
    assert "Data_Science → Hybrid_SciML | 2" in summary
    assert "Confiance basse (< seuil, à vérifier) : 1" in summary
    assert "a (2)" in summary
