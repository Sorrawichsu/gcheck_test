#!/usr/bin/env python3

import os
import sys
import httpx
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Force UTF-8 output on Windows (e.g. cp874 Thai locale blocks unicode symbols)
os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

app = typer.Typer(
    name="gcheck",
    help="Check if websites are accessible and get a guide to access them",
    add_completion=False,
)
console = Console(force_terminal=True)


def get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] GOOGLE_API_KEY not set. Copy .env.example to .env and add your key.")
        raise typer.Exit(1)
    return genai.Client(api_key=api_key)


@app.command()
def ask(
    prompt: str = typer.Argument(..., help="What do you want to ask the agent?"),
):
    """Ask the agent a question or give it a task."""
    client = get_client()

    with Live(Spinner("dots", text="Thinking..."), console=console, transient=True):
        interaction = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=prompt,
            environment="remote",
        )

    console.print(Markdown(interaction.output_text))


@app.command()
def code(
    task: str = typer.Argument(..., help="Coding task for the agent to execute."),
):
    """Give the agent a coding task — it can write and run code."""
    client = get_client()

    console.print(f"[dim]Task:[/dim] {task}\n")

    with Live(Spinner("dots", text="Working..."), console=console, transient=True):
        interaction = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=task,
            environment="remote",
            tools=["code_execution", "google_search"],
        )

    console.print(Markdown(interaction.output_text))


@app.command()
def search(
    query: str = typer.Argument(..., help="What to search and summarize from the web."),
):
    """Search the web and get a summarized answer."""
    client = get_client()

    with Live(Spinner("dots", text="Searching..."), console=console, transient=True):
        interaction = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=f"Search the web and give me a clear summary about: {query}",
            environment="remote",
            tools=["google_search"],
        )

    console.print(Markdown(interaction.output_text))


@app.command()
def check(
    url: str = typer.Argument(..., help="Website URL to check (e.g. google.com or https://google.com)"),
):
    """Check if a website is accessible and get a checklist to access it if blocked."""
    if not url.startswith("http"):
        url = f"https://{url}"

    console.print(f"\nChecking [bold]{url}[/bold]...\n")

    accessible = False
    error_detail = ""
    status_code = None

    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            response = client.get(url)
            status_code = response.status_code
            if response.status_code < 400:
                accessible = True
            else:
                error_detail = f"HTTP {response.status_code}"
    except httpx.ConnectError:
        error_detail = "Connection refused or DNS resolution failed"
    except httpx.TimeoutException:
        error_detail = "Connection timed out"
    except Exception as e:
        error_detail = str(e)

    if accessible:
        console.print(Panel(
            f"[green]✓ Accessible[/green]\n\nHTTP {status_code} — The website is reachable from your location.",
            title="Result",
            border_style="green",
        ))
        return

    console.print(Panel(
        f"[red]✗ Blocked or Unreachable[/red]\n\n{error_detail}",
        title="Result",
        border_style="red",
    ))

    ai_client = get_client()
    prompt = (
        f"The website {url} is blocked or unreachable from the user's location. "
        f"Error: {error_detail}. "
        f"Give a concise markdown checklist of practical steps the user should follow to access this website. "
        f"Include options like VPN setup, DNS change, and browser settings. "
        f"Only output the checklist — no intro or explanation."
    )

    console.print()
    with Live(Spinner("dots", text="Generating checklist..."), console=console, transient=True):
        interaction = ai_client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=prompt,
            environment="remote",
        )

    console.print(Panel(
        Markdown(interaction.output_text),
        title="What to do",
        border_style="yellow",
    ))


if __name__ == "__main__":
    app()
