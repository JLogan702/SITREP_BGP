
import pandas as pd
import os

# File paths
INPUT_CSV = "../filtered_jira_report_stories_only.csv"
OUTPUT_CSV = "../data/sprint_readiness.csv"

READY_STATUSES = {"To Do", "Ready for Development"}
NOT_READY_STATUSES = {"New", "Grooming"}
CURRENT_SPRINT = "Sprint 6"

VALID_TEAMS = [
    "Engineering - Product",
    "Engineering - Platform",
    "Engineering - AI Ops",
    "Design",
    "Data Science"
]

# Load data
df = pd.read_csv(INPUT_CSV)

# Filter: Story only, not Done, in future sprints
df = df[
    (df['Issue Type'].str.lower() == 'story') &
    (df['Status'].str.lower() != 'done') &
    (df['Sprint'].str.contains("Sprint", na=False)) &
    (~df['Sprint'].str.contains(CURRENT_SPRINT, na=False))
]

results = []
for team in VALID_TEAMS:
    team_df = df[df['Components'] == team]
    total = len(team_df)

    ready = team_df['Status'].isin(READY_STATUSES).sum()
    grooming = team_df['Status'].str.lower().eq("grooming").sum()
    new = team_df['Status'].str.lower().eq("new").sum()
    not_ready = grooming + new

    if total == 0:
        ready_pct = 0
        status = "Red"
        explanation = "No sprint-ready stories found."
        summary = "This team has no story tickets assigned to upcoming sprints."
    else:
        ready_pct = round((ready / total) * 100)
        if ready_pct >= 80:
            status = "Green"
            explanation = "Most stories are dev-ready."
        elif ready_pct >= 50:
            status = "Yellow"
            explanation = "Several stories are not yet groomed or ready."
        else:
            status = "Red"
            explanation = "Most stories in the sprint are still New or Grooming."

        summary = (
            f"{ready} of {total} stories are in 'To Do' or 'Ready for Development'. "
            f"{new} are still in 'New', {grooming} in 'Grooming'. "
            f"Sprint readiness may be impacted."
        )

    results.append({
        "Team": team,
        "Ready %": ready_pct,
        "Status": status,
        "Explanation": explanation,
        "Ready Count": ready,
        "New Count": new,
        "Grooming Count": grooming,
        "Not Ready Count": not_ready,
        "Total Count": total,
        "Summary": summary
    })

# Export CSV
out_df = pd.DataFrame(results)
out_df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ sprint_readiness.csv updated with issue breakdown and executive summaries.")
