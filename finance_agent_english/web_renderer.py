#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Renderer - Convert Markdown reports to self-contained HTML for browser viewing
"""

import os
import re
import glob
import socket
from datetime import datetime

try:
    import markdown
    _HAS_MARKDOWN = True
except ImportError:
    _HAS_MARKDOWN = False


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  /* ===== Light Mode (Default) ===== */
  :root {{
    --bg: #f0f2f5;
    --card-bg: #ffffff;
    --text: #0f172a;
    --text-secondary: #475569;
    --border: #e2e8f0;
    --accent: #1e40af;
    --accent-light: #3b82f6;
    --accent-soft: #dbeafe;
    --table-header: #1e3a5f;
    --table-header-text: #f1f5f9;
    --table-stripe: #f8fafc;
    --table-border: #cbd5e1;
    --green: #059669;
    --green-bg: #ecfdf5;
    --green-border: #a7f3d0;
    --red: #dc2626;
    --red-bg: #fef2f2;
    --red-border: #fecaca;
    --yellow: #d97706;
    --yellow-bg: #fffbeb;
    --yellow-border: #fde68a;
    --blue-bg: #eff6ff;
    --blue-border: #bfdbfe;
    --section-alt-bg: #fafbfc;
    --card-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --card-shadow-hover: 0 4px 12px rgba(0,0,0,0.08);
  }}

  /* ===== Dark Mode ===== */
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #f1f5f9;
      --text-secondary: #94a3b8;
      --border: #334155;
      --accent: #60a5fa;
      --accent-light: #93c5fd;
      --accent-soft: #1e3a5f;
      --table-header: #0f2744;
      --table-header-text: #e2e8f0;
      --table-stripe: #1a2332;
      --table-border: #334155;
      --green: #34d399;
      --green-bg: #064e3b;
      --green-border: #065f46;
      --red: #f87171;
      --red-bg: #7f1d1d;
      --red-border: #991b1b;
      --yellow: #fbbf24;
      --yellow-bg: #78350f;
      --yellow-border: #92400e;
      --blue-bg: #1e3a5f;
      --blue-border: #1e40af;
      --section-alt-bg: #182230;
      --card-shadow: 0 1px 3px rgba(0,0,0,0.3);
      --card-shadow-hover: 0 4px 12px rgba(0,0,0,0.4);
    }}
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.75;
    padding: 24px;
    font-size: 16px;
  }}

  .container {{
    max-width: 980px;
    margin: 0 auto;
    background: var(--card-bg);
    border-radius: 10px;
    box-shadow: var(--card-shadow);
    padding: 44px 52px;
  }}

  /* ===== Headings ===== */
  h1 {{
    font-size: 1.9em;
    color: var(--accent);
    border-bottom: 3px solid var(--accent);
    padding-bottom: 14px;
    margin-bottom: 28px;
    letter-spacing: 0.01em;
  }}

  h2 {{
    font-size: 1.35em;
    color: var(--accent);
    padding: 14px 0 10px 16px;
    margin-top: 40px;
    margin-bottom: 20px;
    border-left: 4px solid var(--accent-light);
    background: linear-gradient(90deg, var(--accent-soft) 0%, transparent 100%);
    border-radius: 0 6px 6px 0;
  }}

  h3 {{
    font-size: 1.15em;
    color: var(--text);
    margin-top: 28px;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px dashed var(--border);
  }}

  h4 {{
    font-size: 1.05em;
    color: var(--text-secondary);
    margin-top: 20px;
    margin-bottom: 10px;
  }}

  p {{ margin-bottom: 14px; }}

  strong {{ color: var(--text); font-weight: 600; }}

  ul, ol {{
    margin: 12px 0 16px 28px;
  }}

  li {{ margin-bottom: 5px; }}

  hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 32px 0;
  }}

  blockquote {{
    border-left: 4px solid var(--accent-light);
    background: var(--accent-soft);
    padding: 14px 22px;
    margin: 18px 0;
    border-radius: 0 6px 6px 0;
    color: var(--text-secondary);
  }}

  code {{
    background: var(--accent-soft);
    color: var(--accent);
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 0.9em;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
  }}

  pre {{
    background: #0f172a;
    color: #e2e8f0;
    padding: 18px 22px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 16px 0;
    font-size: 0.88em;
    line-height: 1.6;
  }}

  pre code {{
    background: none;
    padding: 0;
    color: inherit;
  }}

  /* ===== Enhanced Tables ===== */
  table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 18px 0;
    font-size: 0.93em;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    border: 1px solid var(--table-border);
  }}

  th {{
    background: var(--table-header);
    color: var(--table-header-text);
    padding: 11px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 0.9em;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    position: sticky;
    top: 0;
    z-index: 1;
  }}

  th:first-child {{ border-radius: 7px 0 0 0; }}
  th:last-child {{ border-radius: 0 7px 0 0; }}

  td {{
    padding: 10px 16px;
    border-bottom: 1px solid var(--table-border);
    vertical-align: middle;
  }}

  tr:last-child td:first-child {{ border-radius: 0 0 0 7px; }}
  tr:last-child td:last-child {{ border-radius: 0 0 7px 0; }}

  tr:nth-child(even) td {{
    background: var(--table-stripe);
  }}

  tr:hover td {{
    background: var(--accent-soft);
  }}

  /* ===== Color Markers ===== */
  .up {{
    color: var(--green);
    font-weight: 600;
  }}

  .down {{
    color: var(--red);
    font-weight: 600;
  }}

  .warn {{
    color: var(--yellow);
    font-weight: 600;
  }}

  .up-bg {{
    background: var(--green-bg) !important;
  }}

  .down-bg {{
    background: var(--red-bg) !important;
  }}

  /* ===== Badges (Pill Labels) ===== */
  .badge {{
    display: inline-block;
    padding: 3px 11px;
    border-radius: 12px;
    font-size: 0.83em;
    font-weight: 600;
    line-height: 1.5;
    white-space: nowrap;
  }}

  .badge-green {{
    background: var(--green-bg);
    color: var(--green);
    border: 1px solid var(--green-border);
  }}

  .badge-red {{
    background: var(--red-bg);
    color: var(--red);
    border: 1px solid var(--red-border);
  }}

  .badge-yellow {{
    background: var(--yellow-bg);
    color: var(--yellow);
    border: 1px solid var(--yellow-border);
  }}

  .badge-blue {{
    background: var(--blue-bg);
    color: var(--accent);
    border: 1px solid var(--blue-border);
  }}

  /* ===== Risk Indicators ===== */
  .risk-high {{
    border-left: 4px solid var(--red);
    padding: 10px 14px;
    margin: 8px 0;
    background: var(--red-bg);
    border-radius: 0 6px 6px 0;
  }}

  .risk-medium {{
    border-left: 4px solid var(--yellow);
    padding: 10px 14px;
    margin: 8px 0;
    background: var(--yellow-bg);
    border-radius: 0 6px 6px 0;
  }}

  .risk-low {{
    border-left: 4px solid var(--green);
    padding: 10px 14px;
    margin: 8px 0;
    background: var(--green-bg);
    border-radius: 0 6px 6px 0;
  }}

  /* ===== Stock Summary Card ===== */
  .stock-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px 24px;
    margin: 20px 0;
    box-shadow: var(--card-shadow);
    transition: box-shadow 0.2s;
  }}

  .stock-card:hover {{
    box-shadow: var(--card-shadow-hover);
  }}

  .stock-card h4 {{
    margin-top: 0;
    font-size: 1.1em;
    color: var(--accent);
  }}

  /* ===== CSS Bar Chart (for allocation) ===== */
  .bar-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 6px 0;
    font-size: 0.9em;
  }}

  .bar-label {{
    min-width: 130px;
    font-weight: 600;
    color: var(--text);
  }}

  .bar-track {{
    flex: 1;
    height: 22px;
    background: var(--table-stripe);
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid var(--table-border);
  }}

  .bar-fill {{
    height: 100%;
    border-radius: 3px;
    transition: width 0.6s ease;
  }}

  .bar-fill-tech {{ background: linear-gradient(90deg, #3b82f6, #60a5fa); }}
  .bar-fill-finance {{ background: linear-gradient(90deg, #059669, #34d399); }}
  .bar-fill-defensive {{ background: linear-gradient(90deg, #8b5cf6, #a78bfa); }}
  .bar-fill-value {{ background: linear-gradient(90deg, #f59e0b, #fbbf24); }}
  .bar-fill-alt {{ background: linear-gradient(90deg, #f97316, #fb923c); }}
  .bar-fill-cash {{ background: linear-gradient(90deg, #94a3b8, #cbd5e1); }}

  .bar-pct {{
    min-width: 48px;
    text-align: right;
    font-weight: 600;
    color: var(--text);
  }}

  /* ===== Highlight Box ===== */
  .highlight-box {{
    background: var(--accent-soft);
    border: 1px solid var(--blue-border);
    border-radius: 8px;
    padding: 16px 20px;
    margin: 16px 0;
  }}

  .highlight-box.warning {{
    background: var(--yellow-bg);
    border-color: var(--yellow-border);
  }}

  .highlight-box.danger {{
    background: var(--red-bg);
    border-color: var(--red-border);
    border-left: 4px solid var(--red);
  }}

  /* ===== Geo Alert Box (Top Headlines) ===== */
  .geo-alert {{
    background: var(--red-bg);
    border: 1px solid var(--red-border);
    border-left: 5px solid var(--red);
    border-radius: 8px;
    padding: 18px 22px;
    margin: 20px 0;
  }}

  .geo-alert h3, .geo-alert h4 {{
    color: var(--red);
    margin-top: 0;
  }}

  /* ===== Table of Contents Box ===== */
  .toc-box {{
    background: var(--accent-soft);
    border: 1px solid var(--blue-border);
    border-radius: 8px;
    padding: 14px 22px;
    margin: 16px 0;
    font-size: 0.93em;
    line-height: 2;
  }}

  /* ===== Bull / Bear Table ===== */
  .bull-bear-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 18px 0;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--table-border);
  }}

  .bull-bear-table th:first-child {{
    background: var(--green);
    color: #fff;
  }}

  .bull-bear-table th:last-child {{
    background: var(--red);
    color: #fff;
  }}

  /* ===== Support / Resistance Table ===== */
  .sr-table td:first-child {{
    font-weight: 600;
    white-space: nowrap;
  }}

  .sr-table .sr-resist-major {{ color: var(--red); }}
  .sr-table .sr-resist-minor {{ color: var(--yellow); }}
  .sr-table .sr-support-minor {{ color: var(--green); }}
  .sr-table .sr-support-major {{ color: var(--accent-light); }}

  /* ===== Stock Section Separator ===== */
  .stock-divider {{
    border: none;
    border-top: 2px dashed var(--border);
    margin: 40px 0 32px;
  }}

  /* ===== Links ===== */
  a {{
    color: var(--accent-light);
    text-decoration: none;
    font-weight: 500;
  }}

  a:hover {{
    text-decoration: underline;
  }}

  .meta {{
    color: var(--text-secondary);
    font-size: 0.9em;
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }}

  /* ===== Responsive ===== */
  @media (max-width: 640px) {{
    body {{ padding: 10px; font-size: 15px; }}
    .container {{ padding: 22px; border-radius: 6px; }}
    h1 {{ font-size: 1.4em; }}
    h2 {{ font-size: 1.15em; margin-top: 28px; }}
    table {{ font-size: 0.82em; }}
    th, td {{ padding: 7px 10px; }}
    .bar-label {{ min-width: 90px; font-size: 0.82em; }}
  }}
</style>
</head>
<body>
<div class="container">
<p class="meta">Generated: {generated_time}</p>
{body}
</div>
</body>
</html>"""


def _simple_md_to_html(md: str) -> str:
    """Zero-dependency Markdown -> HTML fallback (used when `markdown` package is not installed)."""
    lines = md.split('\n')
    out = []
    in_code = False
    code_buf = []
    in_table = False
    table_rows = []
    in_list = False

    def escape_html(s: str) -> str:
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def inline_fmt(s: str) -> str:
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
        s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
        s = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', s)
        return s

    for line in lines:
        if line.startswith('```'):
            if in_code:
                out.append(f'<pre><code>{escape_html(chr(10).join(code_buf))}</code></pre>')
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_buf.append(line)
            continue

        stripped = line.strip()

        # Table
        if stripped.startswith('|') and stripped.endswith('|'):
            if in_list:
                out.append('</ul>')
                in_list = False
            in_table = True
            cells = [c.strip() for c in stripped[1:-1].split('|')]
            if all(set(c) <= set('- :') for c in cells):
                continue
            tag = 'th' if len(table_rows) == 0 else 'td'
            row_html = ''.join(f'<{tag}>{inline_fmt(escape_html(c))}</{tag}>' for c in cells)
            table_rows.append(f'<tr>{row_html}</tr>')
            continue
        elif in_table:
            out.append(f'<table>{"".join(table_rows)}</table>')
            table_rows = []
            in_table = False

        # List
        is_list_item = stripped.startswith('- ') or stripped.startswith('* ')
        if is_list_item:
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'<li>{inline_fmt(escape_html(stripped[2:]))}</li>')
            continue

        if in_list:
            if stripped == '':
                continue
            out.append('</ul>')
            in_list = False

        if stripped.startswith('# '):
            out.append(f'<h1>{inline_fmt(escape_html(stripped[2:]))}</h1>')
        elif stripped.startswith('## '):
            out.append(f'<h2>{inline_fmt(escape_html(stripped[3:]))}</h2>')
        elif stripped.startswith('### '):
            out.append(f'<h3>{inline_fmt(escape_html(stripped[4:]))}</h3>')
        elif stripped.startswith('#### '):
            out.append(f'<h4>{inline_fmt(escape_html(stripped[5:]))}</h4>')
        elif stripped.startswith('> '):
            out.append(f'<blockquote>{inline_fmt(escape_html(stripped[2:]))}</blockquote>')
        elif stripped == '':
            out.append('<br>')
        else:
            out.append(f'<p>{inline_fmt(escape_html(stripped))}</p>')

    if in_table:
        out.append(f'<table>{"".join(table_rows)}</table>')
    if in_code and code_buf:
        out.append(f'<pre><code>{escape_html(chr(10).join(code_buf))}</code></pre>')
    if in_list:
        out.append('</ul>')

    return '\n'.join(out)


def _post_process_html(html: str) -> str:
    """Apply post-processing to rendered HTML for color markers, badges, and bar charts."""
    # Convert [up]text[/up] → <span class="up">text</span>
    html = re.sub(r'\[up\]((?:(?!\[/up\]).)*?)\[/up\]', r'<span class="up">\1</span>', html)
    # Convert [down]text[/down] → <span class="down">text</span>
    html = re.sub(r'\[down\]((?:(?!\[/down\]).)*?)\[/down\]', r'<span class="down">\1</span>', html)
    # Convert [warn]text[/warn] → <span class="warn">text</span>
    html = re.sub(r'\[warn\]((?:(?!\[/warn\]).)*?)\[/warn\]', r'<span class="warn">\1</span>', html)

    # Convert [badge:green]text[/badge] → <span class="badge badge-green">text</span>
    for color in ('green', 'red', 'yellow', 'blue'):
        html = re.sub(
            rf'\[badge:{color}\]((?:(?!\[/badge\]).)*?)\[/badge\]',
            rf'<span class="badge badge-{color}">\1</span>',
            html
        )

    # Convert risk markers: [risk:high]...[/risk] etc.
    for level in ('high', 'medium', 'low'):
        html = re.sub(
            rf'\[risk:{level}\]((?:(?!\[/risk\]).)*?)\[/risk\]',
            rf'<div class="risk-{level}">\1</div>',
            html
        )

    # Convert bar chart markers in table cells:
    # [bar:tech:25] → bar chart span with percentage
    html = re.sub(
        r'\[bar:(\w+):(\d+)\]',
        r'<span class="bar-row"><span class="bar-track"><span class="bar-fill bar-fill-\1" style="width:\2%"></span></span><span class="bar-pct">\2%</span></span>',
        html
    )

    # Convert highlight boxes: [box]...[/box] → highlight-box, [box:warning]...[/box] etc.
    html = re.sub(
        r'\[box\]((?:(?!\[/box\]).)*?)\[/box\]',
        r'<div class="highlight-box">\1</div>',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'\[box:warning\]((?:(?!\[/box\]).)*?)\[/box\]',
        r'<div class="highlight-box warning">\1</div>',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'\[box:danger\]((?:(?!\[/box\]).)*?)\[/box\]',
        r'<div class="highlight-box danger">\1</div>',
        html,
        flags=re.DOTALL
    )

    return html


def render_report_html(markdown_text: str, title: str = "US Stock Deep Analysis Report") -> str:
    """Convert Markdown report to a self-contained HTML string."""
    # Ensure blank line before table rows so markdown parser recognizes them
    markdown_text = re.sub(r'([^\n|])\n(\|)', r'\1\n\n\2', markdown_text)
    if _HAS_MARKDOWN:
        body = markdown.markdown(
            markdown_text,
            extensions=["tables", "fenced_code", "toc"],
        )
    else:
        print("[WARN] `markdown` package not installed, using simplified rendering. Run: pip install markdown")
        body = _simple_md_to_html(markdown_text)

    body = _post_process_html(body)

    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return HTML_TEMPLATE.format(title=title, body=body, generated_time=generated_time)


def save_html_report(markdown_text: str, output_dir: str, timestamp: str = None) -> str:
    """Convert Markdown to HTML and save alongside the .md file. Returns HTML path."""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"US_Stock_Deep_Analysis_Report_{timestamp}.html"
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, filename)

    html_content = render_report_html(markdown_text)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_path


def get_file_url(path: str) -> str:
    """Return a file:// URL for the given path."""
    abs_path = os.path.abspath(path)
    return f"file://{abs_path}"


def get_http_url(html_path: str, port: int = 0) -> str:
    """Return an http://localhost URL for the given HTML file.
    If port is 0, picks the same port that serve_report() would use."""
    if port == 0:
        port = _pick_port()
    filename = os.path.basename(html_path)
    return f"http://127.0.0.1:{port}/{filename}"


_SERVER_PORT_FILE = None


def _pick_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _load_server_port(output_dir: str):
    """Load previously saved server port, check if it's still alive."""
    port_file = os.path.join(output_dir, ".server_port")
    if not os.path.exists(port_file):
        return None
    try:
        with open(port_file) as f:
            port = int(f.read().strip())
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return port
    except Exception:
        return None


def _save_server_port(output_dir: str, port: int) -> None:
    port_file = os.path.join(output_dir, ".server_port")
    with open(port_file, "w") as f:
        f.write(str(port))


def start_background_server(output_dir: str) -> int:
    """Start a background HTTP server as a detached subprocess.
    Returns the port number. Server survives after this script exits.
    Reuses an existing server if one is already running.
    """
    existing = _load_server_port(output_dir)
    if existing is not None:
        return existing

    import subprocess
    import sys as _sys

    port = _pick_port()
    abs_dir = os.path.abspath(output_dir)

    script = (
        "import http.server, socketserver, os\n"
        "os.chdir(%r)\n"
        "class H(http.server.SimpleHTTPRequestHandler):\n"
        "    def __init__(self, *a, **kw):\n"
        "        super().__init__(*a, directory=%r, **kw)\n"
        "    def log_message(self, f, *a): pass\n"
        "class S(socketserver.TCPServer):\n"
        "    allow_reuse_address = True\n"
        "s = S(('127.0.0.1', %d), H)\n"
        "s.serve_forever()\n"
    ) % (abs_dir, abs_dir, port)

    subprocess.Popen(
        [_sys.executable, "-c", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    _save_server_port(output_dir, port)
    return port


def ensure_report_url(output_dir: str, html_filename: str) -> str:
    """Ensure the background HTTP server is running and return the URL.
    This is the URL that OpenClaw should link to — it's a real, working URL.
    """
    port = start_background_server(output_dir)
    return f"http://127.0.0.1:{port}/{html_filename}"


def serve_report(html_path: str, open_browser: bool = True) -> None:
    """Start a local HTTP server to serve the HTML report.
    Blocks until Ctrl+C is pressed.
    This is the recommended way to view reports (avoids file:// browser restrictions)."""
    import http.server
    import socketserver
    import webbrowser

    serve_dir = os.path.dirname(os.path.abspath(html_path))
    filename = os.path.basename(html_path)
    port = _pick_port()

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=serve_dir, **kwargs)

        def log_message(self, format, *args):
            pass

    class ReusableServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = ReusableServer(("127.0.0.1", port), QuietHandler)
    url = f"http://127.0.0.1:{port}/{filename}"

    if open_browser:
        webbrowser.open(url)

    print(f"Serving report at: {url}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


def open_report(path: str) -> None:
    """Open an HTML report file in the default browser."""
    import webbrowser
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        print(f"File not found: {abs_path}")
        return
    webbrowser.open(get_file_url(abs_path))
    print(f"Opened in browser: {abs_path}")


def list_reports(output_dir: str = "output") -> list:
    """List all HTML reports in the output directory, newest first."""
    pattern = os.path.join(output_dir, "US_Stock_Deep_Analysis_Report_*.html")
    files = glob.glob(pattern)
    files.sort(reverse=True)
    return files


def interactive_open(output_dir: str = "output") -> None:
    """Interactive CLI: list reports and let the user pick one to open."""
    reports = list_reports(output_dir)

    if not reports:
        print(f"No HTML reports found in {output_dir}/")
        print("Run 'python run_analysis.py' first to generate a report.")
        return

    print("\nAvailable Reports:")
    print("-" * 60)
    for i, path in enumerate(reports, 1):
        name = os.path.basename(path)
        size_kb = os.path.getsize(path) / 1024
        url = get_file_url(path)
        print(f"  [{i}] {name}  ({size_kb:.0f} KB)")
        print(f"      {url}")
    print("-" * 60)

    try:
        choice = input("\nEnter number to open (or q to quit): ").strip()
        if choice.lower() == "q":
            return
        idx = int(choice) - 1
        if 0 <= idx < len(reports):
            open_report(reports[idx])
        else:
            print("Invalid choice.")
    except (ValueError, EOFError):
        print("Cancelled.")
