"""Typer CLI interface for the simulation engine."""

import json
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table

import ai_simulation_engine.simulations  # noqa: F401
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.services.ai_service import AIService
from ai_simulation_engine.services.simulation_service import SimulationService
from ai_simulation_engine.services.visualization_service import VisualizationService
from ai_simulation_engine.schemas.simulation import validate_spec_dict
from ai_simulation_engine.models.simulation import SimulationSpec


app = typer.Typer(
    name="ai-sim",
    help="AI Mathematical & Physics Simulation Platform CLI",
    add_completion=False,
)
console = Console()


@app.command("list")
def list_simulations():
    """List all registered simulations in the engine."""
    registered = SimulationRegistry.list_registered()
    table = Table(title="Registered Simulations")
    table.add_column("Domain", style="cyan")
    table.add_column("Simulation Type", style="magenta")
    table.add_column("Class", style="green")

    for sim in registered:
        table.add_row(sim["domain"], sim["simulation_type"], sim["class"])

    console.print(table)


@app.command("generate")
def generate_spec(
    prompt: str = typer.Argument(..., help="Natural language simulation description"),
    provider: str = typer.Option("mock", "--provider", "-p", help="AI provider (mock | openai)"),
):
    """Generate a structured JSON simulation spec from natural language prompt."""
    try:
        spec = AIService.generate_spec_from_prompt(prompt, provider_name=provider)
        console.print_json(data=spec.model_dump())
    except Exception as e:
        console.print(f"[bold red]Error generating spec:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("validate")
def validate_spec(
    spec_path: str = typer.Argument(..., help="Path to simulation spec JSON file"),
):
    """Validate a simulation spec JSON file against schema."""
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        spec = validate_spec_dict(data)
        console.print(f"[bold green]Valid Spec![/bold green] domain='{spec.domain}', type='{spec.simulation_type}'")
    except Exception as e:
        console.print(f"[bold red]Validation Failed:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("run")
def run_simulation(
    domain: str = typer.Option("mathematics", "--domain", "-d", help="Simulation domain"),
    type_name: str = typer.Option("function_plot", "--type", "-t", help="Simulation type"),
    spec_path: Optional[str] = typer.Option(None, "--spec", "-s", help="Path to JSON spec file"),
):
    """Run a simulation from CLI flags or spec file."""
    try:
        if spec_path:
            with open(spec_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            spec = validate_spec_dict(data)
        else:
            # Default fallback spec based on domain/type
            params = {}
            if type_name == "projectile_motion":
                params = {"initial_velocity": 20.0, "launch_angle": 45.0}
            elif type_name == "function_plot":
                params = {"expression": "sin(x)"}
            elif type_name == "optical_prism":
                params = {"apex_angle": 60.0, "refractive_index": 1.5, "incident_angle": 30.0}
            elif type_name == "prism_dispersion":
                params = {"apex_angle": 60.0, "incident_angle": 30.0, "cauchy_b": 1.5, "cauchy_c": 0.004}

            spec = SimulationSpec(
                simulation_type=type_name,
                domain=domain,
                parameters=params,
            )

        result = SimulationService.execute_simulation(spec)
        console.print(f"[bold green]Simulation Completed![/bold green]")
        console.print_json(data=result.summary)
    except Exception as e:
        console.print(f"[bold red]Execution Failed:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("visualize")
def visualize_simulation(
    domain: str = typer.Option("mechanics", "--domain", "-d"),
    type_name: str = typer.Option("projectile_motion", "--type", "-t"),
    output: str = typer.Option("outputs/sim_plot.png", "--output", "-o", help="Output PNG file path"),
):
    """Run a simulation and render visualization graphic file."""
    try:
        params = {}
        if type_name == "projectile_motion":
            params = {"initial_velocity": 20.0, "launch_angle": 45.0}
        elif type_name == "function_plot":
            params = {"expression": "sin(x)"}
        elif type_name == "optical_prism":
            params = {"apex_angle": 60.0, "refractive_index": 1.5, "incident_angle": 30.0}
        elif type_name == "prism_dispersion":
            params = {"apex_angle": 60.0, "incident_angle": 30.0, "cauchy_b": 1.5, "cauchy_c": 0.004}

        spec = SimulationSpec(
            simulation_type=type_name,
            domain=domain,
            parameters=params,
        )

        result = SimulationService.execute_simulation(spec)
        out_file = VisualizationService.render_result(result, output_path=output)
        console.print(f"[bold green]Visualization Rendered Successfully:[/bold green] {out_file}")
    except Exception as e:
        console.print(f"[bold red]Visualization Failed:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
