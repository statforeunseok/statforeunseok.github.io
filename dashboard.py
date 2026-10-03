import sqlite3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from html import escape


DB_PATH = Path(__file__).parent / "src" / "social_emv.db"

HOST = "0.0.0.0"
PORT = 8001


def get_posts():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    posts = connection.execute("""
        SELECT
            platform,
            post_id,
            author,
            post_url,
            text,
            impressions,
            views,
            likes,
            comments,
            shares,
            saves,
            engagements,
            engagement_rate,
            cpm,
            emv,
            created_at
        FROM posts
        ORDER BY created_at DESC
    """).fetchall()

    connection.close()

    return [dict(row) for row in posts]


def dashboard_html():
    posts = get_posts()

    # Convert SQLite data to JSON for browser JavaScript
    posts_json = json.dumps(posts, ensure_ascii=False)

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

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
    max-width: 1400px;
    margin: auto;
    padding: 35px 25px;
}}

h1 {{
    margin: 0;
    font-size: 32px;
}}

.subtitle {{
    color: #94a3b8;
    margin-top: 8px;
    margin-bottom: 28px;
}}

.toolbar {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 25px;
}}

select,
button {{
    background: #1e293b;
    color: white;
    border: 1px solid #475569;
    border-radius: 10px;
    padding: 11px 16px;
    font-size: 14px;
    cursor: pointer;
}}

button:hover {{
    background: #334155;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 25px;
}}

.card {{
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px;
}}

.label {{
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 10px;
}}

.value {{
    font-size: 30px;
    font-weight: bold;
}}

.green {{
    color: #22c55e;
}}

.blue {{
    color: #38bdf8;
}}

.orange {{
    color: #f59e0b;
}}

.purple {{
    color: #a78bfa;
}}

.grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 25px;
    margin-bottom: 25px;
}}

.section {{
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 25px;
    overflow-x: auto;
}}

.section h2 {{
    margin-top: 0;
}}

.chart {{
    min-height: 280px;
}}

.bar-row {{
    display: grid;
    grid-template-columns: 100px 1fr 110px;
    align-items: center;
    gap: 12px;
    margin: 18px 0;
}}

.bar-label {{
    font-weight: bold;
    text-transform: capitalize;
}}

.bar-background {{
    height: 28px;
    background: #334155;
    border-radius: 8px;
    overflow: hidden;
}}

.bar {{
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(
        90deg,
        #38bdf8,
        #8b5cf6
    );
    transition: width 0.4s ease;
}}

.bar-value {{
    text-align: right;
    font-weight: bold;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th {{
    color: #94a3b8;
    font-size: 13px;
    text-align: left;
}}

th,
td {{
    padding: 13px;
    border-bottom: 1px solid #334155;
    white-space: nowrap;
}}

.platform {{
    text-transform: capitalize;
    font-weight: bold;
}}

.empty {{
    color: #94a3b8;
    text-align: center;
    padding: 40px;
}}

.footer {{
    color: #64748b;
    font-size: 13px;
    margin-top: 20px;
}}

@media (max-width: 900px) {{

    .cards {{
        grid-template-columns: repeat(2, 1fr);
    }}

    .grid {{
        grid-template-columns: 1fr;
    }}

}}

@media (max-width: 500px) {{

    .cards {{
        grid-template-columns: 1fr;
    }}

    .bar-row {{
        grid-template-columns: 75px 1fr 80px;
    }}

}}

</style>

</head>

<body>

<div class="container">

<h1>📊 Social EMV Dashboard</h1>

<div class="subtitle">
Social media performance & earned media value
</div>

<div class="toolbar">

<select id="platformFilter" onchange="updateDashboard()">
    <option value="all">All Platforms</option>
    <option value="tiktok">TikTok</option>
    <option value="instagram">Instagram</option>
    <option value="x">X</option>
</select>

<button onclick="location.reload()">
    🔄 Refresh Data
</button>

</div>


<!-- KPI CARDS -->

<div class="cards">

<div class="card">
<div class="label">TOTAL EMV</div>
<div id="totalEmv" class="value green">$0.00</div>
</div>

<div class="card">
<div class="label">TOTAL VIEWS</div>
<div id="totalViews" class="value blue">0</div>
</div>

<div class="card">
<div class="label">ENGAGEMENTS</div>
<div id="totalEngagements" class="value orange">0</div>
</div>

<div class="card">
<div class="label">ENGAGEMENT RATE</div>
<div id="engagementRate" class="value purple">0.00%</div>
</div>

</div>


<!-- SECOND KPI ROW -->

<div class="cards">

<div class="card">
<div class="label">❤️ LIKES</div>
<div id="totalLikes" class="value">0</div>
</div>

<div class="card">
<div class="label">💬 COMMENTS</div>
<div id="totalComments" class="value">0</div>
</div>

<div class="card">
<div class="label">🔄 SHARES</div>
<div id="totalShares" class="value">0</div>
</div>

<div class="card">
<div class="label">📝 POSTS</div>
<div id="totalPosts" class="value">0</div>
</div>

</div>


<!-- CHARTS -->

<div class="grid">

<div class="section">

<h2>💰 EMV by Platform</h2>

<div id="emvChart" class="chart"></div>

</div>


<div class="section">

<h2>📈 Engagements by Platform</h2>

<div id="engagementChart" class="chart"></div>

</div>

</div>


<!-- POSTS -->

<div class="section">

<h2>📝 Posts</h2>

<table>

<thead>

<tr>
<th>Platform</th>
<th>Post ID</th>
<th>Views</th>
<th>Likes</th>
<th>Comments</th>
<th>Shares</th>
<th>Engagements</th>
<th>Rate</th>
<th>EMV</th>
</tr>

</thead>

<tbody id="postTable"></tbody>

</table>

</div>


<div class="footer">
Database: src/social_emv.db
</div>

</div>


<script>

const posts = {posts_json};


function formatNumber(number) {{
    return Number(number || 0).toLocaleString();
}}


function formatMoney(number) {{
    return "$" + Number(number || 0).toLocaleString(
        undefined,
        {{
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }}
    );
}}


function calculateData(filteredPosts) {{

    let totalEmv = 0;
    let totalViews = 0;
    let totalEngagements = 0;
    let totalLikes = 0;
    let totalComments = 0;
    let totalShares = 0;

    filteredPosts.forEach(post => {{

        totalEmv += Number(post.emv || 0);
        totalViews += Number(post.views || 0);
        totalEngagements += Number(post.engagements || 0);
        totalLikes += Number(post.likes || 0);
        totalComments += Number(post.comments || 0);
        totalShares += Number(post.shares || 0);

    }});

    const rate =
        totalViews > 0
        ? (totalEngagements / totalViews) * 100
        : 0;

    document.getElementById("totalEmv").textContent =
        formatMoney(totalEmv);

    document.getElementById("totalViews").textContent =
        formatNumber(totalViews);

    document.getElementById("totalEngagements").textContent =
        formatNumber(totalEngagements);

    document.getElementById("engagementRate").textContent =
        rate.toFixed(2) + "%";

    document.getElementById("totalLikes").textContent =
        formatNumber(totalLikes);

    document.getElementById("totalComments").textContent =
        formatNumber(totalComments);

    document.getElementById("totalShares").textContent =
        formatNumber(totalShares);

    document.getElementById("totalPosts").textContent =
        filteredPosts.length;
}}


function getPlatformStats(filteredPosts) {{

    const stats = {{}};

    filteredPosts.forEach(post => {{

        const platform = post.platform;

        if (!stats[platform]) {{

            stats[platform] = {{
                emv: 0,
                engagements: 0
            }};

        }}

        stats[platform].emv +=
            Number(post.emv || 0);

        stats[platform].engagements +=
            Number(post.engagements || 0);

    }});

    return stats;
}}


function renderChart(elementId, stats, metric, money) {{

    const element =
        document.getElementById(elementId);

    const platforms =
        Object.keys(stats);

    if (platforms.length === 0) {{

        element.innerHTML =
            '<div class="empty">No data</div>';

        return;

    }}

    const values =
        platforms.map(
            platform => stats[platform][metric]
        );

    const max =
        Math.max(...values, 1);

    let html = "";

    platforms.forEach(platform => {{

        const value =
            stats[platform][metric];

        const width =
            (value / max) * 100;

        const displayValue =
            money
            ? formatMoney(value)
            : formatNumber(value);

        html += `
            <div class="bar-row">

                <div class="bar-label">
                    ${{platform}}
                </div>

                <div class="bar-background">

                    <div
                        class="bar"
                        style="width: ${{width}}%"
                    ></div>

                </div>

                <div class="bar-value">
                    ${{displayValue}}
                </div>

            </div>
        `;

    }});

    element.innerHTML = html;
}}


function renderTable(filteredPosts) {{

    const table =
        document.getElementById("postTable");

    if (filteredPosts.length === 0) {{

        table.innerHTML = `
            <tr>
                <td colspan="9" class="empty">
                    No posts found
                </td>
            </tr>
        `;

        return;

    }}

    let html = "";

    filteredPosts.forEach(post => {{

        const rate =
            Number(post.engagement_rate || 0) * 100;

        html += `

        <tr>

            <td class="platform">
                ${{escapeHtml(post.platform)}}
            </td>

            <td>
                ${{escapeHtml(post.post_id)}}
            </td>

            <td>
                ${{formatNumber(post.views)}}
            </td>

            <td>
                ${{formatNumber(post.likes)}}
            </td>

            <td>
                ${{formatNumber(post.comments)}}
            </td>

            <td>
                ${{formatNumber(post.shares)}}
            </td>

            <td>
                ${{formatNumber(post.engagements)}}
            </td>

            <td>
                ${{rate.toFixed(2)}}%
            </td>

            <td>
                ${{formatMoney(post.emv)}}
            </td>

        </tr>

        `;

    }});

    table.innerHTML = html;
}}


function escapeHtml(value) {{

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}}


function updateDashboard() {{

    const selected =
        document.getElementById(
            "platformFilter"
        ).value;

    let filteredPosts = posts;

    if (selected !== "all") {{

        filteredPosts =
            posts.filter(
                post =>
                    post.platform === selected
            );

    }}

    calculateData(filteredPosts);

    const stats =
        getPlatformStats(filteredPosts);

    renderChart(
        "emvChart",
        stats,
        "emv",
        true
    );

    renderChart(
        "engagementChart",
        stats,
        "engagements",
        false
    );

    renderTable(filteredPosts);

}}


updateDashboard();

</script>

</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        html = dashboard_html()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Cache-Control",
            "no-cache"
        )

        self.end_headers()

        self.wfile.write(
            html.encode("utf-8")
        )

    def log_message(self, format, *args):
        pass


print("========================================")
print("       SOCIAL EMV DASHBOARD")
print("========================================")
print()
print("Dashboard running on port 8001")
print()
print("Database:")
print(DB_PATH)
print()

server = HTTPServer(
    (HOST, PORT),
    DashboardHandler
)

server.serve_forever()
