"""
test_dice.py — Unit Tests for the Dice Class
=============================================
Run with:
    python -m pytest test_dice.py -v
    # or
    python -m unittest test_dice -v
"""

import unittest
from collections import Counter
from dice import Dice


class TestDiceInit(unittest.TestCase):
    """Tests for Dice.__init__ (constructor validation)."""

    # --- Happy-path construction ---

    def test_standard_six_sided_dice(self):
        """A fair 6-sided die should be created without errors."""
        probs = [1/6] * 6
        d = Dice(probs)
        self.assertEqual(d.num_faces, 6)
        self.assertEqual(d.probabilities, probs)

    def test_weighted_dice(self):
        """A biased die with valid probabilities should be created."""
        probs = [0.1, 0.2, 0.3, 0.1, 0.2, 0.1]
        d = Dice(probs)
        self.assertEqual(d.num_faces, 6)

    def test_single_face_dice(self):
        """A 1-sided die (prob=[1.0]) is degenerate but valid."""
        d = Dice([1.0])
        self.assertEqual(d.num_faces, 1)

    def test_four_sided_dice(self):
        """A 4-sided die should be created correctly."""
        probs = [0.25, 0.25, 0.25, 0.25]
        d = Dice(probs)
        self.assertEqual(d.num_faces, 4)

    def test_accepts_tuple_input(self):
        """Tuples should also be accepted as probabilities."""
        d = Dice((0.5, 0.5))
        self.assertEqual(d.num_faces, 2)

    def test_integer_probabilities(self):
        """Integer 0 and 1 values should be treated as floats."""
        d = Dice([0, 0, 1])          # face 3 always wins
        self.assertEqual(d.num_faces, 3)

    # --- Type errors ---

    def test_raises_type_error_for_non_list(self):
        """Non-list input should raise TypeError."""
        with self.assertRaises(TypeError):
            Dice("0.5,0.5")

    def test_raises_type_error_for_non_numeric_element(self):
        """A string element inside the list should raise TypeError."""
        with self.assertRaises(TypeError):
            Dice([0.5, "0.5"])

    def test_raises_type_error_for_none_element(self):
        """None inside the list should raise TypeError."""
        with self.assertRaises(TypeError):
            Dice([0.5, None, 0.5])

    # --- Value errors ---

    def test_raises_value_error_for_empty_list(self):
        """An empty probability list should raise ValueError."""
        with self.assertRaises(ValueError):
            Dice([])

    def test_raises_value_error_when_sum_exceeds_one(self):
        """Probabilities summing > 1 should raise ValueError."""
        with self.assertRaises(ValueError):
            Dice([0.5, 0.6])

    def test_raises_value_error_when_sum_below_one(self):
        """Probabilities summing < 1 should raise ValueError."""
        with self.assertRaises(ValueError):
            Dice([0.1, 0.2])

    def test_raises_value_error_for_negative_probability(self):
        """A negative probability value should raise ValueError."""
        with self.assertRaises(ValueError):
            Dice([-0.1, 0.6, 0.5])

    def test_floating_point_tolerance(self):
        """Probabilities that sum to 1 within 1e-6 should be accepted."""
        # 1/3 cannot be represented exactly in floating point
        probs = [1/3, 1/3, 1/3]
        d = Dice(probs)          # should NOT raise
        self.assertEqual(d.num_faces, 3)


class TestDiceRoll(unittest.TestCase):
    """Tests for Dice.roll()."""

    def setUp(self):
        self.fair_dice = Dice([1/6] * 6)
        self.biased_dice = Dice([0.1, 0.2, 0.3, 0.1, 0.2, 0.1])
        self.always_three = Dice([0, 0, 1, 0, 0, 0])

    def test_roll_returns_int(self):
        """roll() should return an integer."""
        result = self.fair_dice.roll()
        self.assertIsInstance(result, int)

    def test_roll_within_valid_range(self):
        """roll() must return a value between 1 and num_faces inclusive."""
        for _ in range(200):
            result = self.fair_dice.roll()
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 6)

    def test_deterministic_roll(self):
        """A die with probability 1 on one face always lands on that face."""
        for _ in range(50):
            self.assertEqual(self.always_three.roll(), 3)

    def test_biased_dice_within_range(self):
        """Biased dice rolls must still stay within valid face range."""
        for _ in range(200):
            result = self.biased_dice.roll()
            self.assertIn(result, [1, 2, 3, 4, 5, 6])

    def test_single_face_roll(self):
        """A 1-sided die must always return face 1."""
        d = Dice([1.0])
        for _ in range(20):
            self.assertEqual(d.roll(), 1)


class TestDiceRollMany(unittest.TestCase):
    """Tests for Dice.roll_many()."""

    def setUp(self):
        self.dice = Dice([1/6] * 6)
        self.always_five = Dice([0, 0, 0, 0, 1, 0])

    def test_roll_many_returns_list(self):
        """roll_many() should return a list."""
        self.assertIsInstance(self.dice.roll_many(5), list)

    def test_roll_many_correct_length(self):
        """roll_many(n) should return exactly n results."""
        for n in [1, 5, 10, 100]:
            self.assertEqual(len(self.dice.roll_many(n)), n)

    def test_roll_many_all_within_range(self):
        """Every value in roll_many() must be within [1, num_faces]."""
        results = self.dice.roll_many(500)
        for r in results:
            self.assertGreaterEqual(r, 1)
            self.assertLessEqual(r, 6)

    def test_roll_many_deterministic(self):
        """A die with prob=1 on face 5 should always return 5."""
        results = self.always_five.roll_many(20)
        self.assertTrue(all(r == 5 for r in results))

    def test_roll_many_raises_type_error_for_float(self):
        """Passing a float to roll_many should raise TypeError."""
        with self.assertRaises(TypeError):
            self.dice.roll_many(5.0)

    def test_roll_many_raises_type_error_for_string(self):
        """Passing a string to roll_many should raise TypeError."""
        with self.assertRaises(TypeError):
            self.dice.roll_many("ten")

    def test_roll_many_raises_value_error_for_zero(self):
        """roll_many(0) should raise ValueError."""
        with self.assertRaises(ValueError):
            self.dice.roll_many(0)

    def test_roll_many_raises_value_error_for_negative(self):
        """roll_many(-1) should raise ValueError."""
        with self.assertRaises(ValueError):
            self.dice.roll_many(-1)

    def test_roll_many_single_roll(self):
        """roll_many(1) should return a list with exactly one element."""
        result = self.dice.roll_many(1)
        self.assertEqual(len(result), 1)
        self.assertIn(result[0], [1, 2, 3, 4, 5, 6])


class TestDiceSummarize(unittest.TestCase):
    """Tests for Dice.summarize()."""

    def setUp(self):
        self.dice = Dice([1/6] * 6)
        self.always_two = Dice([0, 1, 0, 0, 0, 0])

    def test_summarize_returns_dict(self):
        """summarize() must return a dict."""
        self.assertIsInstance(self.dice.summarize(10), dict)

    def test_summarize_has_required_keys(self):
        """summarize() result must contain all required keys."""
        result = self.dice.summarize(10)
        for key in ["rolls", "counts", "frequencies", "num_faces", "number_of_rolls"]:
            self.assertIn(key, result)

    def test_summarize_rolls_length(self):
        """summarize()['rolls'] should have length equal to number_of_rolls."""
        result = self.dice.summarize(15)
        self.assertEqual(len(result["rolls"]), 15)

    def test_summarize_number_of_rolls_field(self):
        """summarize()['number_of_rolls'] should match the argument passed."""
        result = self.dice.summarize(42)
        self.assertEqual(result["number_of_rolls"], 42)

    def test_summarize_num_faces_field(self):
        """summarize()['num_faces'] should match dice.num_faces."""
        result = self.dice.summarize(10)
        self.assertEqual(result["num_faces"], 6)

    def test_summarize_counts_sum_equals_rolls(self):
        """Sum of all counts must equal number_of_rolls."""
        result = self.dice.summarize(100)
        self.assertEqual(sum(result["counts"].values()), 100)

    def test_summarize_frequencies_sum_to_one(self):
        """Observed frequencies must sum approximately to 1.0."""
        result = self.dice.summarize(100)
        total = sum(result["frequencies"].values())
        self.assertAlmostEqual(total, 1.0, places=5)

    def test_summarize_deterministic_counts(self):
        """A biased die with prob=1 on face 2 should count all rolls as face 2."""
        result = self.always_two.summarize(50)
        self.assertEqual(result["counts"][2], 50)
        for face in [1, 3, 4, 5, 6]:
            self.assertEqual(result["counts"][face], 0)

    def test_summarize_deterministic_frequency(self):
        """Frequency of the only possible face should be 1.0."""
        result = self.always_two.summarize(20)
        self.assertAlmostEqual(result["frequencies"][2], 1.0, places=5)

    def test_summarize_counts_keys_cover_all_faces(self):
        """counts dict must have a key for every face, even if count is 0."""
        result = self.dice.summarize(1)
        self.assertEqual(set(result["counts"].keys()), {1, 2, 3, 4, 5, 6})

    def test_summarize_raises_on_invalid_rolls(self):
        """summarize() should raise ValueError for invalid number_of_rolls."""
        with self.assertRaises(ValueError):
            self.dice.summarize(0)


class TestDiceStatisticalBias(unittest.TestCase):
    """
    Light statistical sanity checks.
    These are probabilistic; they use a very large sample to minimise flakiness.
    """

    def test_biased_face_appears_most(self):
        """Face 3 (prob=0.5) should be the most frequent in 5000 rolls."""
        probs = [0.1, 0.1, 0.5, 0.1, 0.1, 0.1]
        d = Dice(probs)
        rolls = d.roll_many(5000)
        counts = Counter(rolls)
        most_common_face = counts.most_common(1)[0][0]
        self.assertEqual(most_common_face, 3)

    def test_fair_dice_all_faces_appear(self):
        """With 600 rolls on a fair die, every face should appear at least once."""
        d = Dice([1/6] * 6)
        rolls = d.roll_many(600)
        unique_faces = set(rolls)
        self.assertEqual(unique_faces, {1, 2, 3, 4, 5, 6})


if __name__ == "__main__":
    unittest.main(verbosity=2)