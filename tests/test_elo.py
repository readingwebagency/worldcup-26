from logic.match import simulate_match

def test_spain_win_rate():
    results = [simulate_match("Spain", 2165, "England", 2020) for _ in range(1000)]
    spain_wins = sum(1 for r in results if r["winner"] == "Spain")
    win_rate = spain_wins / 1000

    assert 0.60 <= win_rate <= 0.80, f"Expected ~70% but got {win_rate:.1%}"