import unittest
import os
from logic.elo import win_probability, get_draw_rate, outcome_probs
from logic.lookup import build_lookup_table

class TestEloAndLookup(unittest.TestCase):

    def setUp(self):
        """Runs before every test - sets up a clean visual separator"""
        print(f"\n👉 Running: {self._testMethodName}")

    # ==========================================
    # 1. PURE MATH TESTS
    # ==========================================

    def test_win_probability_even_match(self):
        """Identical teams must split base win expectancy 50/50"""
        prob = win_probability(1800, 1800)
        print(f"   [CHECK] Base win expectancy for identical Elos (1800 vs 1800): {prob * 100:.1f}%")
        self.assertAlmostEqual(prob, 0.5)

    def test_draw_rate_symmetry(self):
        """Draw rate must be identical regardless of argument order"""
        rate_1 = get_draw_rate(2000, 1500)
        rate_2 = get_draw_rate(1500, 2000)
        print(f"   [CHECK] Order 1 (2000 vs 1500) Draw Rate: {rate_1 * 100:.2f}%")
        print(f"   [CHECK] Order 2 (1500 vs 2000) Draw Rate: {rate_2 * 100:.2f}%")
        self.assertEqual(rate_1, rate_2, "Draw rate calculation is asymmetric!")

    def test_probabilities_sum_to_one(self):
        """Win, Loss, and Draw probabilities must perfectly equal 1.0 everywhere"""
        # Close match
        p_win, p_draw, p_loss = outcome_probs(1800, 1800)
        total_1 = p_win + p_draw + p_loss
        print(f"   [CHECK] Even Matchup Total Probability Pool: {total_1 * 100:.1f}%")
        self.assertAlmostEqual(total_1, 1.0, places=5)
        
        # Severe blowout gap
        p_win, p_draw, p_loss = outcome_probs(2300, 1200)
        total_2 = p_win + p_draw + p_loss
        print(f"   [CHECK] Extreme Gap Matchup Total Probability Pool: {total_2 * 100:.1f}%")
        self.assertAlmostEqual(total_2, 1.0, places=5)

    # ==========================================
    # 2. LOOKUP TABLE STRUCTURAL TESTS
    # ==========================================

    def test_lookup_table_generation(self):
        """Verify the generated lookup table meets structural constraints"""
        teams_path = "data/teams.json"
        
        if not os.path.exists(teams_path):
            print(f"   [SKIP] '{teams_path}' not found. Skipping table matrix validation.")
            self.skipTest(f"Skipping lookup table tests; '{teams_path}' not found.")

        print(f"   [LOAD] Compiling matrix from {teams_path}...")
        lookup_table = build_lookup_table(teams_path)

        # A. Size Assert
        print(f"   [CHECK] Verifying total combination pairs. Found: {len(lookup_table)} matchups.")
        self.assertEqual(len(lookup_table), 1128, "Lookup table doesn't contain exactly 1,128 matchups!")

        # B. Key Structure and Sorting Assert
        print("   [CHECK] Verifying key formatting and alphabetical tuple invariants...")
        for key in lookup_table.keys():
            self.assertIsInstance(key, tuple)
            self.assertEqual(len(key), 2)
            self.assertEqual(key[0], sorted(list(key))[0], f"Key {key} is not alphabetically sorted!")

        # C. Value Structural Assert
        for pairing, values in lookup_table.items():
            p_win, p_draw, p_loss = values
            self.assertAlmostEqual(p_win + p_draw + p_loss, 1.0, places=5, 
                                   msg=f"Matchup {pairing} probabilities do not total 1.0!")
            
        print("   [SUCCESS] All 1,128 matchups verified: Alphabetized, unique, and normalized to 100%.")

if __name__ == "__main__":
    unittest.main()