import pandas as pd
import os

# Load CSV
INPUT_CSV = "filtered_jira_report_stories_only.csv"
OUTPUT_HTML = "docs/index.html"

df = pd.read_csv(INPUT_CSV)

# Optional: Filter out TEP if 'Project' column exists
if "Project" in df.columns:
    df = df[df["Project"] != "TEP"]
else:
    print("⚠️ 'Project' column not found in CSV. Skipping TEP filter.")

# Map Components to Teams (if Component exists)
component_team_map = {
    "Engineering - Platform": "Engineering - Platform",
    "Engineering - Product": "Engineering - Product",
    "Engineering - AI Ops": "Engineering - AI Ops",
    "Design": "Design",
    "Data Science": "Data Science",
}

if "Component" in df.columns:
    df["Team"] = df["Component"].map(component_team_map)
else:
    print("⚠️ 'Component' column not found. Mapping team failed.")
    df["Team"] = "Unknown"

# Drop anything that didn’t map to a team
df = df[df["Team"].isin(component_team_map.values())]

# Define status buckets
ready_statuses = {"Ready for Development"}
grooming_statuses = {"Grooming"}
new_statuses = {"New"}

def categorize_status(status):
    if status in ready_statuses:
        return "Ready"
    elif status in grooming_statuses:
        return "Grooming"
    elif status in new_statuses:
        return "New"
    else:
        return "Other"

# Only keep Stories
if "Issue Type" in df.columns:
    df = df[df["Issue Type"] == "Story"]

# Remove anything marked Done
if "Status" in df.columns:
    df = df[df["Status"] != "Done"]
    df["Category"] = df["Status"].map(categorize_status)
else:
    print("❌ 'Status' column not found. Exiting.")
    exit(1)

# Classify sprint/backlog
df["In Sprint"] = df["Sprint"].notna()

# Aggregate metrics per team
results = []
for team in df["Team"].unique():
    team_df = df[df["Team"] == team]
    
    sprint_df = team_df[team_df["In Sprint"]]
    backlog_df = team_df[~team_df["In Sprint"]]

    # Sprint Readiness
    ready_count = sprint_df[sprint_df["Category"] == "Ready"].shape[0]
    total_sprint = sprint_df.shape[0]
    readiness_pct = round((ready_count / total_sprint) * 100, 1) if total_sprint else 0

    # Backlog Health
    total_backlog = backlog_df.shape[0]
    new_pct = round((backlog_df["Category"] == "New").sum() / total_backlog * 100, 1) if total_backlog else 0
    grooming_pct = round((backlog_df["Category"] == "Grooming").sum() / total_backlog * 100, 1) if total_backlog else 0
    ready_backlog_pct = round((backlog_df["Category"] == "Ready").sum() / total_backlog * 100, 1) if total_backlog else 0

    results.append({
        "Team": team,
        "Readiness %": readiness_pct,
        "Sprint Count": total_sprint,
        "Backlog Count": total_backlog,
        "Backlog - New %": new_pct,
        "Backlog - Grooming %": grooming_pct,
        "Backlog - Ready %": ready_backlog_pct
    })

# Build HTML
os.makedirs("docs", exist_ok=True)
with open(OUTPUT_HTML, "w") as f:
    f.write("<html><head><title>SITREP Dashboard</title></head><body>")
    f.write("<h1>🚦 Brand Growth Platform: Sprint Readiness & Backlog Health</h1>")
    for row in results:
        f.write(f"<h2>{row['Team']}</h2>")
        f.write("<ul>")
        f.write(f"<li>✅ Sprint Readiness: {row['Readiness %']}%</li>")
        f.write(f"<li>📦 Stories in Sprint: {row['Sprint Count']}</li>")
        f.write(f"<li>📚 Stories in Backlog: {row['Backlog Count']}</li>")
        f.write(f"<li>🆕 Backlog - New: {row['Backlog - New %']}%</li>")
        f.write(f"<li>🛠 Backlog - Grooming: {row['Backlog - Grooming %']}%</li>")
        f.write(f"<li>✅ Backlog - Ready: {row['Backlog - Ready %']}%</li>")
        f.write("</ul><hr>")
    f.write("</body></html>")

print(f"✅ Dashboard generated: {OUTPUT_HTML}")
