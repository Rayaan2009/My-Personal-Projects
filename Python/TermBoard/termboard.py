#!/usr/bin/env python3
"""
TermBoard - A modern, colourful terminal dashboard for devs.
Shows live CPU, memory, network stats + your GitHub stars count.

Controls:
    Q or Ctrl+C  Quit the dashboard

Dependencies:
    pip install rich psutil requests
"""

import os
import time
import socket
import psutil
import requests
from datetime import datetime
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.layout import Layout
from rich.align import Align

# Config
REFRESH_SEC = 1.0
GITHUB_USER = "Rayaan2009"  # change with your GitHub username :)

console = Console()

def get_system_info():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    net = psutil.net_io_counters()
    return {
        "cpu": cpu,
        "mem_used": mem.used // (1024 ** 2),
        "mem_total": mem.total // (1024 ** 2),
        "net_sent": net.bytes_sent // 1024,
        "net_recv": net.bytes_recv // 1024,
    }

def get_github_stars():
    try:
        resp = requests.get(f"https://api.github.com/users/{GITHUB_USER}/repos")
        resp.raise_for_status()
        data = resp.json()
        stars = sum(repo.get("stargazers_count", 0) for repo in data)
        return stars
    except Exception:
        return None

def make_dashboard():
    sysinfo = get_system_info()
    stars = get_github_stars()

    # CPU / Memory Table
    sys_table = Table(title="System", expand=True)
    sys_table.add_column("Metric", justify="right")
    sys_table.add_column("Value", justify="left")
    sys_table.add_row("CPU Usage", f"{sysinfo['cpu']} %")
    sys_table.add_row("Memory", f"{sysinfo['mem_used']} / {sysinfo['mem_total']} MB")
    sys_table.add_row("Network Sent", f"{sysinfo['net_sent']} KB")
    sys_table.add_row("Network Recv", f"{sysinfo['net_recv']} KB")

    # GitHub Panel
    gh_panel = Panel(
        Align.center(
            f"⭐ Total Stars: {stars if stars is not None else 'N/A'}",
            vertical="middle"
        ),
        title="GitHub",
        border_style="yellow",
        expand=True
    )

    # Clock
    now = datetime.now().strftime("%H:%M:%S")
    clock_panel = Panel(Align.center(now, vertical="middle"), title="Clock", expand=True)

    # Layout
    layout = Layout()
    layout.split_column(
        Layout(name="upper", ratio=3),
        Layout(name="lower", ratio=1),
    )
    layout["upper"].split_row(
        Layout(Panel(sys_table, title="[bold cyan]System Monitor", expand=True)),
        Layout(gh_panel),
    )
    layout["lower"].update(clock_panel)

    return layout

def main():
    console.clear()
    with Live(make_dashboard(), refresh_per_second=4, console=console) as live:
        try:
            while True:
                time.sleep(REFRESH_SEC)
                live.update(make_dashboard())
        except KeyboardInterrupt:
            console.print("\n[bold red]Exiting TermBoard...[/bold red]")

if __name__ == "__main__":
    main()
