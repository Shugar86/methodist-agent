"""
Main CLI entry point for Methodist Agent.
Uses Typer for command-line interface.
"""

import logging
import shutil
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Add src to path when running as a module
sys.path.insert(0, str(Path(__file__).parent))

from core.config import (
    Config,
    load_config,
    get_data_dir,
    get_output_dir,
    get_skills_dir,
    get_templates_dir,
)
from core.environment_check import run_environment_check
from core.model_router import ModelRouter
from core.context_manager import ContextManager
from core.orchestrator import Orchestrator
from core.ui_text import (
    approval_prompt,
    approval_rejected,
    chat_goodbye,
    chat_hint_exit,
    error_agent_not_implemented,
    error_generic,
    error_pdf_processing,
    error_task_execution,
    info_data_dir,
    info_output_dir,
    info_skills_dir,
    info_templates_dir,
    onboarding_env_report,
    onboarding_first_step,
    onboarding_welcome,
    progress_adapting_document,
    progress_creating_document,
    progress_pdf,
    progress_searching,
    search_header_description,
    search_header_index,
    search_header_title,
    search_header_url,
    search_results_title,
    status_analyzing_request,
    status_executing_plan,
    success_document_adapted,
    success_document_created,
    success_pdf_ready,
    success_search_results,
    task_success,
    task_warning,
)
from windows.workspace import MethodistWorkspace

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="methodist-agent",
    help="🤖 AI-агент для помощи методистам учебных заведений",
    add_completion=True,
)
console = Console()

# Global state
_config: Optional[Config] = None
_model_router: Optional[ModelRouter] = None
_context_manager: Optional[ContextManager] = None
_orchestrator: Optional[Orchestrator] = None


def get_config() -> Config:
    """Get or load configuration."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def get_model_router() -> ModelRouter:
    """Get or create model router."""
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter(get_config())
    return _model_router


def get_context_manager() -> ContextManager:
    """Get or create context manager."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager(get_config())
    return _context_manager


def get_orchestrator() -> Orchestrator:
    """Get or create orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator(get_config(), get_model_router(), get_context_manager())
    return _orchestrator


def print_banner():
    """Print welcome banner."""
    banner = Text()
    banner.append("🤖 ", style="bold cyan")
    banner.append("Методист-Агент", style="bold blue")
    banner.append(" v1.0.0\n", style="dim")
    banner.append(
        "Помогаю готовить рабочие программы, ведомости, презентации и отчёты\n", style="dim"
    )
    banner.append("─" * 50, style="dim")
    console.print(Panel(banner, border_style="blue"))


@app.command()
def init(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    check: bool = typer.Option(False, "--check", help="Run environment check only"),
):
    """Initialize agent configuration."""
    if check:
        report = run_environment_check()
        console.print(onboarding_env_report(report.to_user_string()))
        if not report.all_good:
            raise typer.Exit(code=1)
        raise typer.Exit()

    try:
        config = load_config(config_path)

        # Create directories
        data_dir = get_data_dir(config)
        templates_dir = get_templates_dir(config)
        skills_dir = get_skills_dir(config)
        output_dir = get_output_dir(config)

        # Copy bundled skills and templates if they exist
        project_root = Path(__file__).parent.parent
        bundled_skills = project_root / "skills"
        bundled_templates = project_root / "templates"

        if bundled_skills.exists():
            shutil.copytree(bundled_skills, skills_dir, dirs_exist_ok=True)
        if bundled_templates.exists():
            shutil.copytree(bundled_templates, templates_dir, dirs_exist_ok=True)

        console.print(onboarding_welcome())
        console.print("")
        report = run_environment_check()
        console.print(onboarding_env_report(report.to_user_string()))
        console.print("")
        console.print(onboarding_first_step())
        console.print(info_data_dir(data_dir))
        console.print(info_templates_dir(templates_dir))
        console.print(info_skills_dir(skills_dir))
        console.print(info_output_dir(output_dir))
    except Exception as e:
        logger.exception("Failed to initialize agent")
        console.print(error_generic("инициализировать агента", str(e)))
        raise typer.Exit(code=1)


@app.command()
def chat(
    message: Optional[str] = typer.Argument(None, help="Message to send to agent"),
    no_approval: bool = typer.Option(False, "--no-approval", "-y", help="Skip approval gates"),
):
    """Chat with the agent."""
    print_banner()

    orchestrator = get_orchestrator()
    context_manager = get_context_manager()

    if not context_manager._current_session:
        console.print(onboarding_welcome())
        console.print("")
        console.print(onboarding_first_step())
        console.print("")

    # Create session if none exists
    if not context_manager._current_session:
        context_manager.create_session("CLI Session")

    if message:
        # Single message mode
        _process_message(message, orchestrator, no_approval)
    else:
        # Interactive mode
        console.print(chat_hint_exit())

        while True:
            try:
                user_input = console.input("[bold green]Вы:[/bold green] ")

                if user_input.lower() in ["exit", "quit", "выход"]:
                    console.print(chat_goodbye())
                    break

                if not user_input.strip():
                    continue

                _process_message(user_input, orchestrator, no_approval)

            except KeyboardInterrupt:
                console.print("\n" + chat_goodbye())
                break
            except Exception as e:
                logger.exception("Failed to process message")
                console.print(f"[red]{error_generic('обработать сообщение', str(e))}[/red]")


def _process_message(user_input: str, orchestrator: Orchestrator, no_approval: bool):
    """Process a single user message."""
    try:
        context_manager = get_context_manager()

        # Add user message to context
        context_manager.add_message("user", user_input)

        # Create plan
        with console.status(f"[bold blue]{status_analyzing_request()}[/bold blue]"):
            plan = orchestrator.create_plan(user_input)

        # Present plan
        console.print("\n" + orchestrator.present_plan(plan))

        # Approval gate
        if plan.requires_approval and not no_approval:
            approval = console.input(f"\n[bold yellow]{approval_prompt()}[/bold yellow] ")
            if approval.lower() not in ["y", "yes", "да", "д"]:
                console.print(approval_rejected())
                orchestrator.reject_plan(plan)
                return

        orchestrator.approve_plan(plan)

        # Execute plan
        console.print(f"\n[bold green]{status_executing_plan()}[/bold green]\n")

        while not orchestrator.is_plan_complete(plan):
            task = orchestrator.get_next_task(plan)
            if not task:
                break

            with console.status(f"[bold blue]{task.description}...[/bold blue]"):
                result = _execute_task(task)

            orchestrator.mark_task_complete(task, result)

            if result:
                console.print(f"[green]{task_success(task.description)}[/green]")
                if isinstance(result, str) and len(result) < 500:
                    console.print(f"     [dim]{result}[/dim]")
            else:
                console.print(f"[yellow]{task_warning(task.description)}[/yellow]")

        # Show summary
        console.print("\n" + orchestrator.get_plan_summary(plan))

        # Add assistant response to context
        summary = orchestrator.get_plan_summary(plan)
        context_manager.add_message("assistant", summary)
    except Exception as e:
        logger.exception("Failed to process message")
        console.print(f"[red]{error_generic('обработать сообщение', str(e))}[/red]")


def _execute_task(task):
    """Execute a task using the appropriate specialist or fall back to LLM."""
    agent_name = task.agent
    params = task.parameters

    try:
        if agent_name == "document_specialist":
            from agents.document_specialist import DocumentSpecialist

            agent = DocumentSpecialist(get_config())
            return agent.execute(task.type, params)

        elif agent_name == "pdf_reader":
            from agents.pdf_reader import PDFReaderAgent

            agent = PDFReaderAgent(get_config())
            return agent.execute(task.type, params)

        elif agent_name == "web_search":
            from agents.web_search import WebSearchAgent

            agent = WebSearchAgent(get_config())
            return agent.execute(task.type, params)

        elif agent_name == "adaptation_agent":
            from agents.adaptation_agent import AdaptationAgent

            agent = AdaptationAgent(get_config())
            return agent.execute(task.type, params)

        else:
            # General task - use LLM directly
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant for educational methodists.",
                },
                {"role": "user", "content": params.get("user_input", "")},
            ]
            response = get_model_router().chat(messages)
            return response.content

    except ImportError:
        logger.exception("Failed to load agent %s", agent_name)
        return error_agent_not_implemented(agent_name)
    except Exception as e:
        logger.exception("Failed to execute task")
        return error_task_execution(str(e))


@app.command()
def create(
    template: str = typer.Argument(
        ..., help="Template name (curriculum, schedule, report, presentation)"
    ),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="Subject name"),
    hours: Optional[int] = typer.Option(None, "--hours", "-h", help="Total hours"),
):
    """Create a document from template."""
    console.print(f"[bold blue]{progress_creating_document(template)}[/bold blue]")

    params = {"template_name": template, "output": output, "subject": subject, "hours": hours}

    try:
        from agents.document_specialist import DocumentSpecialist

        agent = DocumentSpecialist(get_config())
        result = agent.create_from_template(params)
        if result.get("success") and result.get("path"):
            console.print(f"[green]{success_document_created(result['path'])}[/green]")
        else:
            console.print(
                f"[red]{error_generic('создать документ', result.get('error', ''))}[/red]"
            )
    except Exception as e:
        logger.exception("Failed to create document")
        console.print(f"[red]{error_generic('создать документ', str(e))}[/red]")


@app.command()
def adapt(
    input_file: str = typer.Argument(..., help="Input file to adapt"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="New template to apply"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Adapt an existing document to new requirements."""
    console.print(f"[bold blue]{progress_adapting_document(input_file)}[/bold blue]")

    params = {"input_file": input_file, "template": template, "output": output}

    try:
        from agents.adaptation_agent import AdaptationAgent

        agent = AdaptationAgent(get_config())
        result = agent.adapt_document(params)
        console.print(f"[green]{success_document_adapted(result)}[/green]")
    except Exception as e:
        logger.exception("Failed to adapt document")
        console.print(f"[red]{error_generic('адаптировать документ', str(e))}[/red]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    max_results: int = typer.Option(10, "--max", "-n", help="Maximum results"),
):
    """Search the web for methodological materials."""
    console.print(f"[bold blue]{progress_searching(query)}[/bold blue]\n")

    try:
        from agents.web_search import WebSearchAgent

        agent = WebSearchAgent(get_config())
        results = agent.search(query, max_results)

        if not results:
            results = []

        error_rows = [r for r in results if r.get("source") == "error"]
        if error_rows:
            console.print(
                f"[red]{error_generic('выполнить поиск', error_rows[0].get('snippet', ''))}[/red]"
            )
            return

        table = Table(title=search_results_title())
        table.add_column(search_header_index(), style="cyan", width=3)
        table.add_column(search_header_title(), style="green")
        table.add_column(search_header_url(), style="blue")
        table.add_column(search_header_description(), style="dim")

        for i, result in enumerate(results, 1):
            table.add_row(
                str(i),
                result.get("title", "N/A")[:50],
                result.get("url", "N/A")[:40],
                result.get("snippet", "")[:60],
            )

        console.print(table)
        console.print(f"[green]{success_search_results(len(results))}[/green]")
    except Exception as e:
        logger.exception("Failed to search")
        console.print(f"[red]{error_generic('выполнить поиск', str(e))}[/red]")


@app.command()
def pdf(
    action: str = typer.Argument(..., help="Action: extract, convert, ocr"),
    input_file: str = typer.Argument(..., help="Input PDF file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Process PDF files."""
    console.print(f"[bold blue]{progress_pdf(action, input_file)}[/bold blue]")

    params = {"action": action, "input_file": input_file, "output": output}

    try:
        from agents.pdf_reader import PDFReaderAgent

        agent = PDFReaderAgent(get_config())
        result = agent.process(params)
        if result.get("success"):
            output_path = result.get("conversion", {}).get("output_path", input_file)
            console.print(f"[green]{success_pdf_ready(output_path)}[/green]")
        else:
            error = (
                result.get("error")
                or result.get("metadata_error")
                or result.get("text_error")
                or result.get("tables_error")
                or result.get("ocr_error")
                or result.get("conversion_error")
            )
            if error:
                console.print(f"[red]{error_generic('обработать PDF', error)}[/red]")
            else:
                console.print(f"[red]{error_pdf_processing('неизвестная ошибка')}[/red]")
    except Exception as e:
        logger.exception("Failed to process PDF")
        console.print(f"[red]{error_generic('обработать PDF', str(e))}[/red]")


@app.command()
def skills(
    list_all: bool = typer.Option(False, "--list", "-l", help="List all skills"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
):
    """Manage skills."""
    context_manager = get_context_manager()

    if list_all:
        all_skills = context_manager.get_all_skills()

        table = Table(title="Доступные Skills")
        table.add_column("Категория", style="cyan")
        table.add_column("Название", style="green")
        table.add_column("Триггеры", style="dim")

        for key, skill in all_skills.items():
            if category and skill.category != category:
                continue
            triggers = ", ".join(skill.triggers[:3]) if skill.triggers else "—"
            table.add_row(skill.category, skill.name, triggers)

        console.print(table)
    else:
        console.print("Используйте --list для просмотра skills")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current config"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Edit config file"),
):
    """Manage configuration."""
    config = get_config()

    if show:
        console.print_json(config.model_dump_json())
    elif edit:
        config_path = Path.home() / ".methodist-agent" / "config.yaml"
        console.print(f"Откройте файл в редакторе: {config_path}")
    else:
        console.print("Используйте --show или --edit")


@app.command()
def tray():
    """Launch system tray application."""
    console.print("[bold blue]🖥️ Запускаю System Tray...[/bold blue]")

    try:
        from windows.tray_app import TrayApp

        app = TrayApp(get_config())
        app.run()
    except Exception as e:
        logger.exception("Failed to launch tray")
        console.print(f"[red]❌ Ошибка запуска tray: {e}[/red]")
        console.print("[dim]Убедитесь, что установлены все зависимости Windows[/dim]")


@app.command()
def workspace():
    """Открыть рабочее пространство Методист-Агента."""
    console.print("[bold blue]Открываю рабочее пространство...[/bold blue]")
    ws = MethodistWorkspace()
    ws.run()


if __name__ == "__main__":
    app()
