import os
import csv
import ast
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "templates"
OUTPUT_DIR = "docs"

def render_template(template_name, context, output_name):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    html = template.render(context)
    with open(os.path.join(OUTPUT_DIR, output_name), "w") as f:
        f.write(html)

def main():
    with open("data/backlog_health.csv") as f:
        reader = csv.DictReader(f)
        backlog_data = list(reader)

    for row in backlog_data:
        if "Status Breakdown" not in row or not row["Status Breakdown"]:
            row["Status Breakdown"] = {}
        elif isinstance(row["Status Breakdown"], str):
            try:
                row["Status Breakdown"] = ast.literal_eval(row["Status Breakdown"])
            except Exception:
                row["Status Breakdown"] = {}

    context = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "backlog_data": backlog_data
    }

    render_template("backlog_health.html", context, "backlog_health.html")

if __name__ == "__main__":
    import pandas as pd
    main()