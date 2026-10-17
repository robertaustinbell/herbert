import unittest
import test_check_template

LINK = "https://github.com/robertaustinbell/herbert-hermes-canary"


class CompanionLinkTests(test_check_template.CanaryHarness):
    def test_approved_public_companion_link_is_not_private_identity(self):
        result = self.run_copy()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unapproved_personal_home_path_is_still_rejected(self):
        # Source-specific identity checks belong to the private maintainer gate.
        def mutate(clone):
            path = clone / "README.md"
            path.write_text(path.read_text() + "\n" + "/" + "Users/example/private-note" + "\n")
        result = self.run_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private path in README.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
