"""Nox sessions for testing and code quality checks."""

import nox

import tomllib
from pathlib import Path

# Extract Python version from pyproject.toml
def get_python_version() -> str:
    path = Path("pyproject.toml")
    if not path.exists():
        return "3.12"  # Fallback
    
    with open(path, "rb") as f:
        data = tomllib.load(f)
        version = data.get("tool", {}).get("poetry", {}).get("dependencies", {}).get("python", "3.12")
        # Clean up version markers like ^3.12 or >=3.12
        return version.lstrip("^>=")


# Extract main dependencies from pyproject.toml
def get_main_deps() -> list[str]:
    path = Path("pyproject.toml")
    if not path.exists():
        return []
    
    with open(path, "rb") as f:
        data = tomllib.load(f)
        deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        # Return all keys except 'python'
        return [k for k in deps.keys() if k != "python"]

nox.options.sessions = ["lint", "format", "type_check", "test", "coverage"]
python_versions = [get_python_version()]

# Common dependencies for sessions
MAIN_DEPS = get_main_deps()


@nox.session(python=python_versions)
def lint(session: nox.Session) -> None:
    """Run ruff linter and fix safe issues."""
    session.install("ruff")
    session.run("ruff", "check", "--fix", "src/", "tests/", "flink-app/")


@nox.session(python=python_versions)
def format(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff")
    session.run("ruff", "format", "src/", "tests/", "flink-app/")


@nox.session(python=python_versions)
def type_check(session: nox.Session) -> None:
    """Run type checking with ty."""
    session.install("ty", "nox", *MAIN_DEPS)
    session.run("ty", "check")


@nox.session(python=python_versions)
def test(session: nox.Session) -> None:
    """Run tests with pytest."""
    session.install("pytest", "pytest-cov", *MAIN_DEPS)
    session.run("pytest", *session.posargs)


@nox.session(python=python_versions)
def coverage(session: nox.Session) -> None:
    """Generate coverage report."""
    session.install("pytest", "pytest-cov", *MAIN_DEPS)
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        *session.posargs,
    )
