import subprocess
from src.tools.decorator import tool


@tool
def shell_run(cmd: str):
    """
    Execute shell command

    cmd: shell command
    """

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    return result.stdout + result.stderr
