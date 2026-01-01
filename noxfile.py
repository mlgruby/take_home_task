"""Nox sessions for testing and code quality checks."""

import nox

try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path

# Extract Python version from pyproject.toml (PEP 621)
def get_python_version() -> str:
    path = Path("pyproject.toml")
    if not path.exists():
        return "3.10"  # Fallback

    with open(path, "rb") as f:
        data = tomllib.load(f)
        # Parse '==3.10.*' or '>=3.10'
        version = data.get("project", {}).get("requires-python", "3.10")
        target_version = version.replace("==", "").replace(".*", "").lstrip("^>=")
        return target_version


# Extract main dependencies from pyproject.toml (PEP 621)
def get_main_deps() -> list[str]:
    path = Path("pyproject.toml")
    if not path.exists():
        return []

    with open(path, "rb") as f:
        data = tomllib.load(f)
        deps = data.get("project", {}).get("dependencies", [])
        return deps

nox.options.sessions = ["lint", "format", "type_check", "test", "test_flink", "coverage"]
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
def test_flink(session: nox.Session) -> None:
    """Run PyFlink tests with isolated dependencies."""
    session.install("-r", "flink-app/requirements.txt")
    session.run(
        "pytest",
        "--cov=flink-app/src",
        "--cov-report=term-missing",
        "flink-app/tests",
        *session.posargs,
        env={"PYTHONPATH": "flink-app"},
    )


@nox.session(python=python_versions)
def test(session: nox.Session) -> None:
    """Run tests with pytest."""
    session.install("pytest", "pytest-cov", *MAIN_DEPS)
    session.run("pytest", "--cov=src", "--cov-report=term-missing", *session.posargs)


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
