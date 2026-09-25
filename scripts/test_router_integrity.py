#!/usr/bin/env python3
"""Metadata and router integrity regressions (standard library only)."""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("router_under_test", ROOT / "scripts/generate_index.py")
assert SPEC is not None and SPEC.loader is not None
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)
SOURCE = "operating-thought/authority/least-privilege-capability-access.md"


class RouterIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="router-integrity-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        shutil.copytree(ROOT / "operating-thought", self.root / "operating-thought")
        self.page = self.root / SOURCE
        self.original = self.page.read_text(encoding="utf-8")

    def test_metadata_grammar_never_silently_drops_active_pages(self):
        for spelling in ("'active'", '"active"', "active # current", "'active' # current"):
            with self.subTest(spelling=spelling):
                self.page.write_text(self.original.replace("status: active", "status: " + spelling), encoding="utf-8")
                routed, unknown = GEN.discover_active_pages(self.root)
                self.assertIn(self.page, [path for _, path, _ in routed])
                self.assertEqual(unknown, [])
        for mutation in (
            self.original.replace("status: active", "status: active\n  - archived"),
            self.original.replace("status: active", "status: [active]"),
            self.original.replace("status: active", "status: |\n  active"),
            self.original.replace("status: active", "status: 'active"),
            self.original.replace("status: active", "status: active\nunsupported syntax"),
            self.original.replace("\n---\n", "\nnot-a-delimiter\n", 1),
        ):
            with self.subTest(mutation=mutation[:150]):
                self.page.write_text(mutation, encoding="utf-8")
                with self.assertRaises(ValueError):
                    GEN.parse_frontmatter(self.page)

    def test_required_schema_is_validated_before_status_filtering(self):
        meta = GEN.parse_frontmatter(self.page)
        for key in meta:
            # Every current field is part of this repository's required schema.
            changed = re.sub(r"(?m)^" + key + r":[^\n]*\n(?:  - [^\n]*\n)*", "", self.original, count=1)
            with self.subTest(missing=key):
                self.page.write_text(changed, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, key):
                    GEN.discover_active_pages(self.root)
        for status in ("active", "archived", "superseded", "typo"):
            for key, value in (("type", "wrong"), ("authority", "wrong"), ("confidence", "wrong"),
                               ("consult_when", "[]"), ("do_not_use_when", "[]"),
                               ("confidence_basis", "[]"), ("review_when", "[]"),
                               ("scope", "scalar-not-list"), ("router_summary", "[]")):
                changed = re.sub(r"(?m)^" + key + r":[^\n]*\n(?:  - [^\n]*\n)*", key + ": " + value + "\n", self.original, count=1)
                changed = changed.replace("status: active", "status: " + status)
                with self.subTest(status=status, key=key):
                    self.page.write_text(changed, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        GEN.discover_active_pages(self.root)
        for status in ("archived", "superseded"):
            self.page.write_text(self.original.replace("status: active", "status: " + status), encoding="utf-8")
            routed, unknown = GEN.discover_active_pages(self.root)
            self.assertNotIn(self.page, [path for _, path, _ in routed])
            self.assertEqual(unknown, [])

    def test_coverage_aggregates_metadata_errors_without_traceback(self):
        other = next(path for path in sorted((self.root / "operating-thought").rglob("*.md")) if path != self.page)
        self.page.write_text(self.original.replace("status: active", "status: active\nstatus: archived"), encoding="utf-8")
        other.write_text(other.read_text(encoding="utf-8").replace("confidence:", "not_confidence:", 1), encoding="utf-8")
        try:
            errors = GEN.coverage_errors(self.root)
        except ValueError as exc:
            self.fail("metadata errors escaped coverage: " + str(exc))
        self.assertTrue(any(self.page.name in error and "duplicate" in error for error in errors), errors)
        self.assertTrue(any(other.name in error and "confidence" in error for error in errors), errors)

    def test_normalized_duplicate_ids_are_rejected(self):
        duplicate = self.page.with_name("duplicate.md")
        duplicate.write_text(self.original.replace("id: least-privilege-capability-access", "id: 'least-privilege-capability-access'"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate operating thought id"):
            GEN.render(self.root)

    def test_router_triggers_are_bound_to_active_owner_and_role(self):
        index = GEN.render(self.root)
        meta = GEN.parse_frontmatter(self.page)
        block = GEN.page_block(self.root, self.page, meta)
        consult = "**Consult when:** " + GEN.join_triggers(meta["consult_when"])
        index_path = self.root / "index.md"
        index_path.write_text(index, encoding="utf-8")
        self.assertEqual(GEN.coverage_errors(self.root), [])
        mutants = {
            "wrong_owner": index.replace(consult, "", 1) + "\n### [Other](operating-thought/authority/other.md)\n\n" + consult + "\n",
            "comment_only": index.replace(block, "<!--\n" + block + "\n-->", 1),
            "fence_only": index.replace(block, "```markdown\n" + block + "\n```", 1),
            "tilde_fence_only": index.replace(block, "~~~~\n" + block + "\n~~~~", 1),
            "comment_trigger": index.replace(consult, "<!-- " + consult + " -->", 1),
            "fenced_trigger": index.replace(consult, "```\n" + consult + "\n```", 1),
            "unlinked_heading": index.replace(block.splitlines()[0], "### Owner without a link", 1),
        }
        # Swap both labels without replacing the newly substituted label again.
        mutants["role_reversal"] = index.replace("**Consult when:**", "**TEMP:**").replace("**Do not use when:**", "**Consult when:**").replace("**TEMP:**", "**Do not use when:**")
        for mutation, text in mutants.items():
            with self.subTest(mutation=mutation):
                index_path.write_text(text, encoding="utf-8")
                self.assertTrue(GEN.coverage_errors(self.root), mutation)

    def checker_copy(self):
        # A checkout under excluded-name ancestors must still be fully checked.
        clone = Path(self.temp.name) / ".hermes" / "archive" / "repo"
        shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns(".git", ".hermes", "__pycache__"))
        checker = "check_template.py" if (clone / "scripts/check_template.py").exists() else "check_agent_ops.py"
        return clone, [sys.executable, "scripts/" + checker]

    def test_checker_freshness_is_nonmutating(self):
        clone, command = self.checker_copy()
        index = clone / "index.md"
        index.write_text(index.read_text(encoding="utf-8") + "\nStale extra text.\n", encoding="utf-8")
        before = index.read_bytes()
        checked = subprocess.run(command, cwd=clone, text=True, capture_output=True)
        self.assertNotEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertIn("stale", checked.stdout + checked.stderr)
        self.assertEqual(index.read_bytes(), before, "checker rewrote the stale router")

    def test_checker_exclusions_are_relative_to_repository_root(self):
        clone, command = self.checker_copy()
        checked = subprocess.run(command, cwd=clone, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        (clone / "broken-router-test.md").write_text("[broken](not-a-real-file.md)\n", encoding="utf-8")
        checked = subprocess.run(command, cwd=clone, text=True, capture_output=True)
        self.assertNotEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertIn("broken link", checked.stdout)

    def test_checker_reports_multiple_parser_errors_without_traceback(self):
        clone, command = self.checker_copy()
        first = clone / SOURCE
        first.write_text(self.original.replace("status: active", "status: active\nstatus: archived"), encoding="utf-8")
        other = next(path for path in sorted((clone / "operating-thought").rglob("*.md")) if path != first)
        other.write_text(other.read_text(encoding="utf-8").replace("authority: adopted", "authority:\n  - adopted"), encoding="utf-8")
        checked = subprocess.run(command, cwd=clone, text=True, capture_output=True)
        self.assertNotEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertNotIn("Traceback", checked.stdout + checked.stderr)
        self.assertIn(first.name, checked.stdout)
        self.assertIn(other.name, checked.stdout)

    def test_generator_mutations_cannot_launder_router_coverage(self):
        clone, command = self.checker_copy()
        generator = clone / "scripts/generate_index.py"
        original = generator.read_text(encoding="utf-8")
        old = 'return "\\n\\n".join(block)'
        mutations = {
            "comment_only": original.replace(old, 'return "<!--\\n" + "\\n\\n".join(block) + "\\n-->"', 1),
            "wrong_owner": original.replace('rel = path.relative_to(root).as_posix()', 'rel = "operating-thought/authority/wrong-owner.md"', 1),
            "role_reversal": original.replace('block.append("**Consult when:** "', 'block.append("**TEMP:** "').replace('block.append("**Do not use when:** "', 'block.append("**Consult when:** "').replace('block.append("**TEMP:** "', 'block.append("**Do not use when:** "'),
        }
        for name, mutated in mutations.items():
            with self.subTest(mutation=name):
                self.assertNotEqual(mutated, original)
                generator.write_text(mutated, encoding="utf-8")
                generated = subprocess.run([sys.executable, "scripts/generate_index.py"], cwd=clone, text=True, capture_output=True)
                self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
                checked = subprocess.run(command, cwd=clone, text=True, capture_output=True)
                self.assertNotEqual(checked.returncode, 0, checked.stdout + checked.stderr)
                self.assertIn("router omitted", checked.stdout)
                self.assertNotIn("Traceback", checked.stdout + checked.stderr)

    def test_each_metadata_field_rejects_the_wrong_shape(self):
        for key, value in GEN.parse_frontmatter(self.page).items():
            replacement = "scalar-not-list" if isinstance(value, list) else "[]"
            changed = re.sub(r"(?m)^" + key + r":[^\n]*\n(?:  - [^\n]*\n)*", key + ": " + replacement + "\n", self.original, count=1)
            with self.subTest(field=key):
                self.page.write_text(changed, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, key):
                    GEN.discover_active_pages(self.root)

    def test_unknown_family_and_new_page_acceptance_are_discovered(self):
        extra = self.original.replace("id: least-privilege-capability-access", "id: additional-page")
        path = self.page.with_name("additional-page.md")
        path.write_text(extra, encoding="utf-8")
        rendered = GEN.render(self.root)
        self.assertIn(path.relative_to(self.root).as_posix(), rendered)
        (self.root / "index.md").write_text(rendered, encoding="utf-8")
        self.assertEqual(GEN.coverage_errors(self.root), [])
        unknown = self.root / "operating-thought/unknown"
        unknown.mkdir()
        path.rename(unknown / path.name)
        with self.assertRaisesRegex(ValueError, "not in a routed family"):
            GEN.render(self.root)
        self.assertTrue(any("not in a routed family" in error for error in GEN.coverage_errors(self.root)))

    def test_quoted_scalars_cannot_inject_lines_into_router_blocks(self):
        self.page.write_text(self.original.replace("status: active", 'status: "active\\narchived"'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "single-line"):
            GEN.parse_frontmatter(self.page)

    def test_duplicate_metadata_keys_are_rejected(self):
        self.page.write_text(self.original.replace("status: active", "status: active\nstatus: archived"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate.*status"):
            GEN.parse_frontmatter(self.page)


if __name__ == "__main__":
    unittest.main()
