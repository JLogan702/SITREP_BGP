
import pandas as pd

INPUT_CSV = "filtered_jira_report_stories_only.csv"
OUTPUT_CSV = "data/backlog_health.csv"

VALID_TEAMS = [
    "Engineering - Product",
    "Engineering - Platform",
    "Engineering - AI Ops",
    "Design",
    "Data Science"
]

df = pd.read_csv(INPUT_CSV)

def is_backlog(sprint):
    return pd.isna(sprint) or ("Backlog" in str(sprint)) or ("Sprint" not in str(sprint))

records = []

for team in VALID_TEAMS:
    team_df = df[
        (df["Components"] == team) &
        (df["Issue Type"] == "Story") &
        (df["Status"] != "Done") &
        (df["Sprint"].apply(is_backlog))
    ]

    if team_df.empty:
        status_breakdown = {}
        records.append({
            "Team": team,
            "Ready": 0,
            "New": 0,
            "Grooming": 0,
            "Total": 0,
            "Ungroomed %": 100,
            "Status": "Red",
            "Explanation": "This team has no backlog story tickets.",
            "Status Breakdown": status_breakdown
        })
        continue

    ready = team_df[team_df["Status"] == "Ready for Development"].shape[0]
    new = team_df[team_df["Status"] == "New"].shape[0]
    grooming = team_df[team_df["Status"] == "Grooming"].shape[0]
    total = team_df.shape[0]
    percent_ready = (ready / total) * 100 if total > 0 else 0
    ungroomed = 100 - percent_ready

    if percent_ready >= 80:
        status = "Green"
    elif percent_ready >= 50:
        status = "Yellow"
    else:
        status = "Red"

    status_breakdown = team_df["Status"].value_counts().to_dict()
    records.append({
        "Team": team,
        "Ready": ready,
        "New": new,
        "Grooming": grooming,
        "Total": total,
        "Ungroomed %": round(ungroomed, 1),
        "Status": status,
        "Explanation": f"Only {ready} of {total} story tickets are ready for development."
    })

df_out = pd.DataFrame(records)
df_out.to_csv(OUTPUT_CSV, index=False)