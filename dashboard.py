import sqlite3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from html import escape

DB_PATH = Path(__file__).parent / "social_emv.db"
HOST = "0.0.0.0"
PORT = 8000


def get_database_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
    """).fetchall()

    if not tables:
        conn.close()
        return [], {}

    table_name = tables[0]["name"]

    columns = conn.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()

    column_names = [c["name"] for c in columns]

    rows = conn.execute(
        f'SELECT * FROM "{table_name}" ORDER BY rowid DESC'
    ).fetchall()

    data = [dict(row) for row in rows]

    conn.close()

    return column_names, {
        "table": table_name,
        "rows": data,
    }


def find_value(row, names, default=0):
    for name in names:
        for key in row:
            if key.lower() == name.lower():
                value = row[key]
                if value is not None:
                    return value
    return default


def number(value):
    try:
        return float(value or 0)
    except (ValueError, TypeError):
        return 0


def dashboard_html():
    columns, database = get_database_data()
    rows = database.get("rows", [])
    table_name = database.get("table", "unknown")

    total_emv = 0
    total_views = 0
    total_engagements = 0
    total_posts = len(rows)

    platform_stats = {}

    for row in rows:
        emv = number(find_value(row, [
            "emv",
            "EMV",
            "earned_media_value"
        ]))

        views = number(find_value(row, [
            "views",
            "view",
            "impressions"
        ]))

        engagements = number(find_value(row, [
            "engagements",
            "engagement",
            "total_engagements"
        ]))

        platform = find_value(row, [
            "platform",
            "Platform"
        ], "unknown")

        total_emv += emv
        total_views += views
        total_engagements += engagements

        platform = str(platform)

        if platform not in platform_stats:
            platform_stats[platform] = {
                "posts": 0,
                "emv": 0,
                "engagements": 0,
            }

        platform_stats[platform]["posts"] += 1
        platform_stats[platform]["emv"] += emv
        platform_stats[platform]["engagements"] += engagements

    engagement_rate = (
        total_engagements / total_views * 100
        if total_views
        else 0
    )

    platform_html = ""

    for platform, stats in platform_stats.items():
        platform_html += f"""
        <tr>
            <td>{escape(platform)}</td>
            <td>{stats["posts"]:,}</td>
            <td>${stats["emv"]:,.2f}</td>
            <td>{stats["engagements"]:,}</td>
        </tr>
        """

    rows_html = ""

    for row in rows:
        platform = find_value(row, ["platform"], "-")
        post_id = find_value(row, ["post_id"], "-")
        views = number(find_value(row, ["views", "impressions"]))
        engagements = number(find_value(row, ["engagements"]))
        emv = number(find_value(row, ["emv"]))

        rows_html += f"""
        <tr>
            <td>{escape(str(platform))}</td>
            <td>{escape(str(post_id))}</td>
            <td>{views:,.0f}</td>
            <td>{engagements:,.0f}</td>
            <td>${emv:,.2f}</td>
        </tr>
        """

    if not rows_html:
        rows_html = """
        <tr>
            <td colspan="5">ยังไม่มีข้อมูลในฐานข้อมูล</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Social EMV Dashboard</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
}}

.container {{
    max-width: 1200px;
    margin: auto;
    padding: 35px 20px;
}}

.header {{
    margin-bottom: 30px;
}}

.header h1 {{
    margin: 0;
    font-size: 32px;
}}

.header p {{
    color: #94a3b8;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 30px;
}}

.card {{
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px;
}}

.card-title {{
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 10px;
}}

.card-value {{
    font-size: 28px;
    font-weight: bold;
}}

.emv {{
    color: #22c55e;
}}

.engagement {{
    color: #f59e0b;
}}

.views {{
    color: #38bdf8;
}}

.rate {{
    color: #a78bfa;
}}

.section {{
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 25px;
}}

.section h2 {{
    margin-top: 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    text-align: left;
    padding: 13px;
    border-bottom: 1px solid #334155;
}}

th {{
    color: #94a3b8;
    font-size: 13px;
}}

td {{
    color: #e2e8f0;
}}

.badge {{
    display: inline-block;
    background: #334155;
    padding: 5px 10px;
    border-radius: 999px;
}}

.footer {{
    color: #64748b;
    font-size: 13px;
    margin-top: 25px;
}}

@media (max-width: 800px) {{
    .cards {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 500px) {{
    .cards {{
        grid-template-columns: 1fr;
    }}

    table {{
        font-size: 12px;
    }}
}}

</style>
</head>

<body>

<div class="container">

<div class="header">
    <h1>📊 Social EMV Dashboard</h1>
    <p>Social Media Earned Media Value Tracker</p>
</div>

<div class="cards">

<div class="card">
    <div class="card-title">TOTAL EMV</div>
    <div class="card-value emv">${total_emv:,.2f}</div>
</div>

<div class="card">
    <div class="card-title">TOTAL ENGAGEMENTS</div>
    <div class="card-value engagement">
        {total_engagements:,.0f}
    </div>
</div>

<div class="card">
    <div class="card-title">TOTAL VIEWS</div>
    <div class="card-value views">
        {total_views:,.0f}
    </div>
</div>

<div class="card">
    <div class="card-title">ENGAGEMENT RATE</div>
    <div class="card-value rate">
        {engagement_rate:.2f}%
    </div>
</div>

</div>

<div class="section">

<h2>📱 Platform Performance</h2>

<table>
<thead>
<tr>
    <th>Platform</th>
    <th>Posts</th>
    <th>EMV</th>
    <th>Engagements</th>
</tr>
</thead>

<tbody>
{platform_html}
</tbody>

</table>

</div>

<div class="section">

<h2>📝 Posts</h2>

<table>

<thead>
<tr>
    <th>Platform</th>
    <th>Post ID</th>
    <th>Views</th>
    <th>Engagements</th>
    <th>EMV</th>
</tr>
</thead>

<tbody>
{rows_html}
</tbody>

</table>

</div>

<div class="footer">
    Database: {escape(table_name)} · {total_posts} posts
</div>

</div>

</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            html = dashboard_html()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            self.wfile.write(html.encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[Dashboard] {args[0]}")


if __name__ == "__main__":
    print("=" * 40)
    print("       SOCIAL EMV DASHBOARD")
    print("=" * 40)
    print()
    print("Dashboard running on port 8000")
    print("Open the forwarded port in GitHub Codespaces")
    print()

    server = HTTPServer((HOST, PORT), DashboardHandler)
    server.serve_forever()
