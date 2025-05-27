
import pandas as pd

INPUT_CSV = "filtered_jira_report_stories_only.csv"
OUTPUT_CSV = "data/sprint_readiness.csv"

CURRENT_SPRINTS = ["Sprint 7", "Sprint 8"]

# For each team, define what statuses count as "ready"
TEAM_READY_RULES = {
    "Engineering - Product": ["Ready for Development"],
    "default": ["Ready for Development", "To Do"]
}

VALID_TEAMS = [
    "Engineering - Product",
    "Engineering - Platform",
    "Engineering - AI Ops",
    "Design",
    "Data Science"
]

df = pd.read_csv(INPUT_CSV)

def is_future_sprint(sprint_value):
    if pd.isna(sprint_value):
        return False
    return any(s in sprint_value for s in CURRENT_SPRINTS)

records = []

for team in VALID_TEAMS:
    team_df = df[
        (df["Components"] == team) &
        (df["Issue Type"] == "Story") &
        (df["Status"] != "Done") &
        (df["Sprint"].apply(is_future_sprint))
    ]

    if team_df.empty:
        records.append({
            "Team": team,
            "Ready Count": 0,
            "Total Count": 0,
            "Status": "Red",
            "Explanation": "This team has no story tickets in upcoming sprints."
        })
        continue

    ready_statuses = TEAM_READY_RULES.get(team, TEAM_READY_RULES["default"])
    ready_count = team_df[team_df["Status"].isin(ready_statuses)].shape[0]
    total_count = team_df.shape[0]
    percent_ready = (ready_count / total_count) * 100 if total_count > 0 else 0

    if percent_ready >= 80:
        status = "Green"
    elif percent_ready >= 50:
        status = "Yellow"
    else:
        status = "Red"

    records.append({
        "Team": team,
        "Ready Count": ready_count,
        "Total Count": total_count,
        "Status": status,
        "Explanation": f"{ready_count} of {total_count} story tickets are in statuses considered ready."
    })

df_out = pd.DataFrame(records)
df_out.to_csv(OUTPUT_CSV, index=False)
