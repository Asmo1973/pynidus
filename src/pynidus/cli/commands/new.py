import typer
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def new(project_name: str = typer.Argument(..., help="Name of the project")):
    """
    Create a new Pynidus project.
    """
    project_path = Path(os.getcwd()) / project_name
    
    if project_path.exists():
        console.print(f"[bold red]Error:[/bold red] Directory {project_name} already exists.")
        raise typer.Exit(code=1)
    
    console.print(f"[bold green]Creating new Pynidus project:[/bold green] {project_name}")
    
    # Create directories
    (project_path / "src" / project_name).mkdir(parents=True)
    (project_path / "tests").mkdir(parents=True)
    
    # Create pyproject.toml
    pyproject_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "pynidus",
    "uvicorn",
]

[build-system]
requires = ["uv_build"]
build-backend = "uv_build"
"""
    (project_path / "pyproject.toml").write_text(pyproject_content)
    
    # Create main.py
    main_content = f"""from pynidus import NidusFactory, Module, Controller, Injectable, Get
import uvicorn

@Injectable()
class AppService:
    def get_hello(self) -> str:
        return "Hello World!"

@Controller()
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @Get("/")
    def get_hello(self):
        return {{"message": self.app_service.get_hello()}}

@Module(
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass

def bootstrap():
    app = NidusFactory.create(AppModule)
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    bootstrap()
"""
    (project_path / "src" / project_name / "main.py").write_text(main_content)
    
    # Create __init__.py
    (project_path / "src" / project_name / "__init__.py").touch()
    
    console.print(Panel(f"Project [bold cyan]{project_name}[/bold cyan] created successfully!\n\nRun:\n  cd {project_name}\n  uv run src/{project_name}/main.py", title="Success", border_style="green"))
