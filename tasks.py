"""Maintenance tasks for the project."""

import json
import os
import sys
import tempfile
import tomllib

import invoke

try:
    from jupyter_client import kernelspec
except ImportError:
    raise RuntimeError('Install the "ipykernel" package first') from None


def _ensure_venv():
    # Source: https://stackoverflow.com/questions/1871549/how-to-determine-if-python-is-running-inside-a-virtualenv  # pylint:disable=C0301
    if sys.prefix == sys.base_prefix:
        raise RuntimeError("Run this command in an activated `virtualenv`")


def _get_pyproject_name():
    with open("pyproject.toml", "rb") as fp:
        data = tomllib.load(fp)

    try:
        project_name = data["tool"]["poetry"]["name"]
    except KeyError:
        raise RuntimeError('"pyproject.toml" seems to be malformed') from None

    return project_name


@invoke.task
def install_kernel(_c):
    """Install the activated `virtualenv` as a `jupyter kernel`.
    This helper task
    """
    _ensure_venv()
    project_name = _get_pyproject_name()

    with tempfile.TemporaryDirectory() as tmpdir:
        spec = {
            "argv": [
                sys.prefix + "/bin/python",
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": project_name,
            "env": {"PATH": os.environ["PATH"]},
            "interrupt_mode": "signal",
            "language": "python",
            "metadata": {"debugger": True},
        }

        with open(os.path.join(tmpdir, "kernel.json"), "w", encoding="utf-8") as fp:
            json.dump(spec, fp, indent=4)

        manager = kernelspec.KernelSpecManager()
        manager.install_kernel_spec(tmpdir, kernel_name=project_name, user=True)


@invoke.task
def remove_kernel(_c):
    """Remove the `jupyter kernel` corresponding to the activated `virtualenv`."""
    _ensure_venv()
    project_name = _get_pyproject_name()

    manager = kernelspec.KernelSpecManager()
    manager.remove_kernel_spec(project_name)
