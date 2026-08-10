import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, List, Optional

from . import TESTS_PATH

# socket.getfqdn() and socket.gethostbyname() can be slow on macOS;
# hence, extend the timeout
DEFAULT_TEST_TIMEOUT: int = 120 if sys.platform == "darwin" else 25


@dataclass
class CLIRunner:
    """
    Wrapper of subprocess.run to compose cmd's for ansible-rulebook CLI
    """

    cwd: str = TESTS_PATH
    base_cmd: str = "ansible-rulebook"
    inventory: str = os.path.join(TESTS_PATH, "default_inventory.yml")
    rules: Optional[str] = None
    sources: Optional[str] = None
    extra_vars: Optional[str] = None
    envvars: Optional[str] = None
    proc_id: Optional[str] = None
    verbose: bool = False
    debug: bool = False
    timeout: float = 30.0  # Increased from 10.0 for better reliability
    env: Optional[dict[str, str]] = None

    def __post_init__(self) -> None:
        self.env = os.environ.copy() if self.env is None else self.env

    def _process_args(self) -> List[str]:
        args = [
            self.base_cmd,
        ]

        args.extend(["-i", self.inventory])

        if self.rules:
            args.extend(["--rulebook", self.rules])
        if self.sources:
            args.extend(["-S", self.sources])
        if self.extra_vars:
            args.extend(["--vars", self.extra_vars])
        if self.envvars:
            args.extend(["--env-vars", self.envvars])
        if self.proc_id:
            args.extend(["--id", self.proc_id])
        if self.verbose:
            args.append("-v")
        if self.debug:
            args.append("-vv")

        return args

    def run(self) -> subprocess.CompletedProcess[Any]:
        args = self._process_args()
        print("Running command: ", " ".join(args))

        # Set up environment with unbuffered output for more reliable stdout capture
        env = self.env.copy() if self.env else os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        return subprocess.run(
            args,
            cwd=self.cwd,
            capture_output=True,
            timeout=self.timeout,
            check=True,
            env=env,
        )

    def run_in_background(self) -> subprocess.Popen[bytes]:
        args = self._process_args()
        print("Running command: ", " ".join(args))
        return subprocess.Popen(
            args,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
        )
