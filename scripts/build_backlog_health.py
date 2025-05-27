import pandas as pd
import os

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
        records.append({
            "Team": team,
            "Ready": 0,
            "New": 0,
            "Grooming": 0,
            "Total": 0,
            "Ungroomed %": 100,
            "Backlog Status": "Red",
            "Explanation_Backlog": "This team has no backlog story tickets.",
            "Status Breakdown": {}
        })
        continue

    ready_count = len(team_df[team_df["Status"] == "Ready for Development"])
    new_count = len(team_df[team_df["Status"] == "New"])
    grooming_count = len(team_df[team_df["Status"] == "Grooming"])
    total_count = len(team_df)

    ungroomed_percent = 100 if total_count == 0 else round(100 * (1 - (ready_count / total_count)), 1)
    if ready_count == 0:
        status = "Red"
    elif ungroomed_percent <= 20:
        status = "Green"
    elif ungroomed_percent <= 50:
        status = "Yellow"
    else:
        status = "Red"

    explanation = f"{ready_count} of {total_count} story tickets are marked 'Ready for Development'."
    status_breakdown = team_df["Status"].value_counts().to_dict()

    records.append({
        "Team": team,
        "Ready": ready_count,
        "New": new_count,
        "Grooming": grooming_count,
        "Total": total_count,
        "Ungroomed %": ungroomed_percent,
        "Backlog Status": status,
        "Explanation_Backlog": explanation,
        "Status Breakdown": status_breakdown
    })

output_df = pd.DataFrame(records)
output_df.to_csv(OUTPUT_CSV, index=False)