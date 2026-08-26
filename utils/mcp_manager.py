# utils/mcp_manager.py

import socket
import subprocess
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


MCP_SERVERS = {
    "ICD-10": {
        "module": "mcp.servers.icd10_server:app",
        "port": 8002,
    },
    "Tariff": {
        "module": "mcp.servers.tariff_server:app",
        "port": 8003,
    },
    "Calculation": {
        "module": "mcp.servers.calculation_server:app",
        "port": 8004,
    },
}


_processes = []


def is_port_open(
    host: str,
    port: int,
) -> bool:

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as sock:

        sock.settimeout(0.5)

        return (
            sock.connect_ex(
                (host, port)
            )
            == 0
        )


def start_mcp_servers():

    global _processes

    for name, config in MCP_SERVERS.items():

        port = config["port"]

        # ----------------------------------------------------
        # Already running
        # ----------------------------------------------------

        if is_port_open(
            "127.0.0.1",
            port,
        ):

            print(
                f"{name} MCP already running on port {port}."
            )

            continue

        # ----------------------------------------------------
        # Start server
        # ----------------------------------------------------

        print(
            f"Starting {name} MCP on port {port}..."
        )

        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                config["module"],
                "--host",
                "0.0.0.0",
                "--port",
                str(port),
            ],
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        _processes.append(process)

    # --------------------------------------------------------
    # Wait for servers
    # --------------------------------------------------------

    timeout = 15
    start_time = time.time()

    while time.time() - start_time < timeout:

        all_running = all(
            is_port_open(
                "127.0.0.1",
                config["port"],
            )
            for config in MCP_SERVERS.values()
        )

        if all_running:

            print(
                "All ClaimGuard MCP servers are ready."
            )

            return True

        time.sleep(0.5)

    # --------------------------------------------------------
    # Timeout
    # --------------------------------------------------------

    failed_servers = [
        name
        for name, config in MCP_SERVERS.items()
        if not is_port_open(
            "127.0.0.1",
            config["port"],
        )
    ]

    raise RuntimeError(
        "The following MCP servers failed to start: "
        + ", ".join(failed_servers)
    )


def stop_mcp_servers():

    global _processes

    for process in _processes:

        if process.poll() is None:

            process.terminate()

    _processes = []