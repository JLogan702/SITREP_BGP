
import pandas as pd
import os
from datetime import datetime

# Input CSV
INPUT_CSV = "filtered_jira_report_stories_only.csv"
OUTPUT_HTML = "docs/index.html"

# Load and filter data
df = pd.read_csv(INPUT_CSV)

# Drop TEP project and non-story types
df = df[df["Project"] != "TEP"]
df = df[df["Issue Type"].str.lower() == "story"]
df = df[df["Status"].str.lower() != "done"]

# Team-component mapping
team_map = {{
    "Engineering - Platform": "Engineering - Platform",
    "Engineering - AI Ops": "Engineering - AI Ops",
    "Engineering - Product": "Engineering - Product",
    "Design": "Design",
    "Data Science": "Data Science"
}}

df = df[df["Component/s"].notna()]
df["Team"] = df["Component/s"].map(team_map)

# Backlog = no sprint
backlog = df[df["Sprint"].isna()]
backlog_status_counts = backlog.groupby(["Team", "Status"]).size().unstack(fill_value=0)
backlog_totals = backlog.groupby("Team").size().rename("Backlog Total")

# Readiness = future sprints and status in Ready for Dev or To Do
future_sprints = df[df["Sprint"].str.contains("Sprint 7|Sprint 8", na=False)]
future_ready = future_sprints[future_sprints["Status"].isin(["Ready for Development", "To Do"])]
readiness = future_ready.groupby("Team").size() / future_sprints.groupby("Team").size()
readiness = (readiness.fillna(0) * 100).round().rename("Sprint Readiness %")

# Merge backlog and readiness
summary = pd.DataFrame(backlog_totals)
summary["New"] = backlog_status_counts.get("New", 0)
summary["Grooming"] = backlog_status_counts.get("Grooming", 0)
summary["Ready"] = backlog_status_counts.get("Ready for Development", 0)
summary["New %"] = (summary["New"] / summary["Backlog Total"] * 100).fillna(0).round()
summary["Grooming %"] = (summary["Grooming"] / summary["Backlog Total"] * 100).fillna(0).round()
summary["Ready %"] = (summary["Ready"] / summary["Backlog Total"] * 100).fillna(0).round()
summary["Sprint Readiness %"] = readiness
summary.reset_index(inplace=True)

# Generate dashboard
timestamp = datetime.now().strftime("%B %d, %Y %I:%M %p")

html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Brand Growth Platform Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f4f4f4;
            margin: 20px;
        }}
        h1, h2 {{
            text-align: center;
        }}
        select {{
            display: block;
            margin: 0 auto 20px;
            padding: 10px;
            font-size: 16px;
        }}
        .section {{ display: none; }}
        .active {{ display: block; }}
        
        .traffic-light {
            width: 30px;
            height: 90px;
            margin: 0 auto;
            background: #222;
            border-radius: 8px;
            padding: 5px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
        }
        .light {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            opacity: 0.3;
        }
        .light.green { background-color: #4CAF50; }
        .light.yellow { background-color: #FFC107; }
        .light.red { background-color: #F44336; }

        .light.blink {{
            animation: blink 1.5s infinite;
            opacity: 1 !important;
        }}

            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin: 0 auto;
            animation: blink 1.5s infinite;
        }}
        .green {{ background-color: #4CAF50; }}
        .yellow {{ background-color: #FFC107; }}
        .red {{ background-color: #F44336; }}
        
        @keyframes blink {
{
            50% {{ opacity: 0.4; }}
        }}
        .team-block {{
            background: #fff;
            padding: 15px;
            margin: 20px auto;
            border-radius: 8px;
            width: 85%;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        canvas {{
            max-width: 600px;
            margin: 20px auto;
            display: block;
        }}
        .updated {{
            text-align: center;
            font-style: italic;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>Brand Growth Platform Dashboard</h1>
    <div class="updated">Last Updated: {timestamp}</div>
    <select onchange="switchSection(this.value)">
        <option value="sitrep">📋 Situation Report</option>
        <option value="readiness">🚦 Sprint Readiness</option>
        <option value="backlog">📦 Backlog Health</option>
    </select>

    <div id="sitrep" class="section active">
        <h2>📋 Situation Report</h2>
        <p style="text-align:center;">This dashboard summarizes readiness and backlog health for all Clarvos teams. Green means go, yellow means room for concern, and red means get your act together.</p>
        <div style="text-align:center;">
            <canvas id="overallChart"></canvas>
        </div>
    </div>

    <div id="readiness" class="section">
        <h2>🚦 Sprint Readiness</h2>
"""

for _, row in summary.iterrows():
    team = row["Team"]
    pct = row["Sprint Readiness %"]
    color = "green" if pct >= 70 else "yellow" if pct >= 40 else "red"
    html += f"""
    <div class="team-block">
        <h3>{team}</h3>
        <p><strong>Readiness:</strong> {pct}%</p>

        <div class="traffic-light">
            <div class="light red { 'blink' if color == 'red' else '' }"></div>
            <div class="light yellow { 'blink' if color == 'yellow' else '' }"></div>
            <div class="light green { 'blink' if color == 'green' else '' }"></div>
        </div>

        <p>This metric reflects the percentage of Stories in future sprints that are marked as 'Ready for Development'. It indicates how prepared this team is for the next sprint.</p>
    </div>
    """

html += "<div id='backlog' class='section'><h2>📦 Backlog Health</h2>"

for _, row in summary.iterrows():
    team = row["Team"]
    color = "green" if row["Ready %"] >= 70 else "yellow" if row["Ready %"] >= 40 else "red"
    html += f"""
    <div class="team-block">
        <h3>{team}</h3>
        <p><strong>Total Backlog Items:</strong> {row['Backlog Total']}</p>
        <ul>
            <li>New: {row['New']} ({row['New %']}%)</li>
            <li>Grooming: {row['Grooming']} ({row['Grooming %']}%)</li>
            <li>Ready: {row['Ready']} ({row['Ready %']}%)</li>
        </ul>

        <div class="traffic-light">
            <div class="light red { 'blink' if color == 'red' else '' }"></div>
            <div class="light yellow { 'blink' if color == 'yellow' else '' }"></div>
            <div class="light green { 'blink' if color == 'green' else '' }"></div>
        </div>

        <p>This breakdown shows the team's total unslotted backlog and how much of it is groomed and ready. Lower 'New' percentage and higher 'Ready' is good.</p>
    </div>
    """

html += f"""
    </div>
    <script>
        function switchSection(id) {{
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(id).classList.add('active');
        }}
        const ctx = document.getElementById('overallChart');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {summary['Team'].tolist()},
                datasets: [
                    {{
                        label: 'Sprint Readiness %',
                        data: {summary['Sprint Readiness %'].fillna(0).tolist()},
                        backgroundColor: '#4CAF50'
                    }},
                    {{
                        label: 'Backlog Ready %',
                        data: {summary['Ready %'].fillna(0).tolist()},
                        backgroundColor: '#2196F3'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

# Write HTML file
os.makedirs("docs", exist_ok=True)
with open(OUTPUT_HTML, "w") as f:
    f.write(html)

print(f"✅ Dashboard generated to {OUTPUT_HTML}")
