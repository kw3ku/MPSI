import unittest

from mpsi import score_statement


class TestMPSI(unittest.TestCase):
    def test_hawkish_statement_scores_high(self):
        result = score_statement(
            "Inflation remains elevated and policy tightening may continue."
        )
        self.assertGreater(result["normalized_score"], 55)
        self.assertEqual(result["label"], "hawkish")

    def test_dovish_statement_scores_low(self):
        result = score_statement(
            "The committee supports easing as conditions show softening."
        )
        self.assertLess(result["normalized_score"], 45)
        self.assertEqual(result["label"], "dovish")

    def test_neutral_without_lexicon_terms(self):
        result = score_statement("The committee met and discussed current conditions.")
        self.assertEqual(result["normalized_score"], 50.0)
        self.assertEqual(result["label"], "neutral")

    def test_empty_statement_is_neutral(self):
        result = score_statement("")
        self.assertEqual(result["normalized_score"], 50.0)
        self.assertEqual(result["label"], "neutral")

    def test_non_string_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            score_statement(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
