import pandas as pd
import requests
import io


def execute_hardened_scrape():
    url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    print("[INIT] Starting hardened extraction...")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"

        html_stream = io.StringIO(response.text)

        # --- TASK A: STANDINGS (with fallback keys + explicit failure message) ---
        print("[STAGE 1] Extracting standings...")
        found_standings = False
        for match_key in ["Pts", "Pld", "GD"]:
            try:
                tables = pd.read_html(html_stream, match=match_key)
                if tables:
                    pd.concat(tables, ignore_index=True).to_csv(
                        "live_form_2026.csv", index=False
                    )
                    print(f" -> Success using key: {match_key} "
                          f"({len(tables)} tables, saved live_form_2026.csv)")
                    found_standings = True
                    break
            except Exception as e:
                print(f" -> key '{match_key}' failed: {type(e).__name__}: {e}")
            finally:
                html_stream.seek(0)  # always reset, whether it errored or came up empty

        if not found_standings:
            print(" -> [STAGE 1] FAILED: no standings table matched any key.")

        # --- TASK B: VENUE CAPACITY (fixed: pick largest table, not [0]) ---
        print("[STAGE 2] Extracting venues...")
        html_stream.seek(0)
        try:
            venue_tables = pd.read_html(html_stream, match="Capacity")
            sizes = [len(t) for t in venue_tables]
            winner_idx = sizes.index(max(sizes))
            venues_df = venue_tables[winner_idx]
            venues_df.to_csv("venues_2026.csv", index=False)
            print(f" -> Venue data secured (table index {winner_idx} of "
                  f"{len(venue_tables)} candidates, shape={venues_df.shape})")
        except Exception as e:
            print(f" -> [STAGE 2] FAILED: {type(e).__name__}: {e}")

        # --- TASK C: MATCH SCHEDULE ---
        print("[STAGE 3] Extracting schedule...")
        html_stream.seek(0)
        try:
            schedule_tables = pd.read_html(html_stream, match="Date")
            sizes = [len(t) for t in schedule_tables]
            winner_idx = sizes.index(max(sizes))
            master_schedule = schedule_tables[winner_idx]
            master_schedule.to_csv("schedule_2026.csv", index=False)
            print(f" -> Schedule extracted (table index {winner_idx} of "
                  f"{len(schedule_tables)} candidates, shape={master_schedule.shape})")
        except Exception as e:
            print(f" -> [STAGE 3] FAILED: {type(e).__name__}: {e}")

    except Exception as e:
        print(f"[CRITICAL ERROR] Pipeline aborted: {type(e).__name__}: {e}")


if __name__ == "__main__":
    execute_hardened_scrape()