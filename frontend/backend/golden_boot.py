import requests
from collections import defaultdict
import pandas as pd

OPENFOOTBALL_2026_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"


def build_golden_boot_leaderboard(url: str = OPENFOOTBALL_2026_URL) -> pd.DataFrame:
    """
    Builds the Golden Boot leaderboard directly from the same openfootball
    feed already used for fixtures/results - NOT a separate data source.

    Rules applied:
      - Own goals (owngoal: True) are EXCLUDED from the scorer's tally -
        they're not personal achievements, they should not count toward
        Golden Boot.
      - Penalties (penalty: True) ARE counted - real tournament Golden Boot
        rules count penalty goals same as open-play goals.
    """
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    matches = resp.json()["matches"]

    goal_counts = defaultdict(int)
    penalty_counts = defaultdict(int)
    team_of_player = {}  # best-effort, for display purposes only
    own_goals_excluded = 0

    for m in matches:
        team1, team2 = m.get("team1"), m.get("team2")
        for side, team in (("goals1", team1), ("goals2", team2)):
            for g in (m.get(side) or []):
                name = g["name"]
                if g.get("owngoal"):
                    own_goals_excluded += 1
                    continue  # do NOT credit the scorer's own-goal tally
                goal_counts[name] += 1
                team_of_player.setdefault(name, team)
                if g.get("penalty"):
                    penalty_counts[name] += 1

    leaderboard = pd.DataFrame([
        {
            "player": name,
            "team": team_of_player.get(name, "Unknown"),
            "goals": count,
            "penalties": penalty_counts.get(name, 0),
        }
        for name, count in goal_counts.items()
    ])

    leaderboard = leaderboard.sort_values(
        by=["goals", "player"], ascending=[False, True]
    ).reset_index(drop=True)
    leaderboard.insert(0, "rank", leaderboard.index + 1)

    print(f"[GoldenBoot] Processed {len(matches)} matches, "
          f"{own_goals_excluded} own goal(s) correctly excluded from scorer tallies.")

    return leaderboard


if __name__ == "__main__":
    board = build_golden_boot_leaderboard()
    print("\n=== TOP 10 GOLDEN BOOT ===")
    print(board.head(10).to_string(index=False))
