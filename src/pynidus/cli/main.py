import typer
from pynidus.cli.commands import new, generate

app = typer.Typer(
    name="pynidus",
    help="CLI for Pynidus Microservices Framework",
    add_completion=False,
)

app.add_typer(new.app, name="new", help="Create a new Pynidus project")
app.add_typer(generate.app, name="generate", help="Generate components")

if __name__ == "__main__":
    app()
