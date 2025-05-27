import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
OUTPUT_DIR = os.path.join(BASE_DIR, 'docs')

# Load data
readiness_csv = os.path.join(DATA_DIR, 'sprint_readiness.csv')
backlog_csv = os.path.join(DATA_DIR, 'backlog_health.csv')
overall_csv = os.path.join(DATA_DIR, 'overall_health.csv')

readiness_data = pd.read_csv(readiness_csv)
backlog_data = pd.read_csv(backlog_csv)
overall_data = pd.read_csv(overall_csv)

# Determine overall program status
team_statuses = overall_data['Status'].tolist()
if 'Red' in team_statuses:
    program_status = 'Red'
    program_light = 'img/blinking_stoplight_red.gif'
elif 'Yellow' in team_statuses:
    program_status = 'Yellow'
    program_light = 'img/blinking_stoplight_yellow.gif'
else:
    program_status = 'Green'
    program_light = 'img/blinking_stoplight_green.gif'

# Prepare Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
timestamp = datetime.now().strftime("%B %d, %Y @ %I:%M %p")

# Render summary page -> docs/index.html
template = env.get_template('summary_page.html')
output = template.render(
    program_status=program_status,
    program_light=program_light,
    readiness=readiness_data.to_dict(orient='records'),
    grooming=backlog_data.to_dict(orient='records'),
    last_updated=timestamp
)


with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as f:
    f.write(output)

print("✅ Dashboard pages generated successfully.")
