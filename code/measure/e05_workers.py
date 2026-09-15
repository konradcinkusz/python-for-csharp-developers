#!/usr/bin/env python3
"""Experiment E5: uvicorn workers against concurrency, on a mocked upstream.

The question is trap 45 -- "more uvicorn workers is more throughput" -- and
the answer turns entirely on what the handler does while it holds the loop.
So one service is driven twice: through a handler that AWAITS a fixed delay
(the mocked upstream) and through one that BURNS bytecode. Nothing in the
second releases the GIL.

Two modes, and the split is what keeps the committed numbers trustworthy:

  * `--run` measures. It starts uvicorn as a real subprocess, drives it over
    a real socket, and writes measure/data/e05_workers.json.
  * With no argument it DERIVES figures/values/e05.tex from that committed
    JSON and touches nothing else. `make numbers` runs every script here on
    every build, and a latency benchmark re-run on every build is one whose
    committed numbers drift on a tree nobody edited -- `make verify` would
    fail for the wrong reason. Re-measuring is a deliberate act.

Three things the driver does on purpose, each of them paid for:

  * It does not share an event loop with the server. uvicorn runs in its own
    process, reached over a socket. The LangChain book's chapter 13 measured
    a driver on the server's own loop and recorded what it cost.
  * Every cell is compared with a CALIBRATION cell at the same concurrency:
    the same driver against a handler that returns at once. A cell within
    half of that ceiling is measuring the client, and the JSON records the
    flag rather than the author's confidence. The first run of this
    experiment flagged four cells and they were not quoted.
  * It speaks HTTP/1.1 over raw asyncio sockets rather than through a client
    library, for two reasons. A library's per-request cost was the first
    run's ceiling; and this one sets TCP_NODELAY and TCP_QUICKACK on its own
    socket, which is what removes the stall the `nagle` cells below measure
    from every other cell in the table.

Run from code/:
    uv run python measure/e05_workers.py --run     # measure, ~2 minutes
    uv run python measure/e05_workers.py           # derive the value file
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
RAW = CODE / "measure" / "data" / "e05_workers.json"
OUT = ROOT / "figures" / "values" / "e05.tex"

DELAY_SECONDS = 0.1
BURN_ROUNDS = 400_000
WORKERS = (1, 2, 4)
CONCURRENCIES = (1, 10, 40)
AWAIT_REQUESTS = {1: 40, 10: 200, 40: 800}
NOOP_REQUESTS = {1: 400, 10: 2000, 40: 4000}
CPU_REQUESTS = 200
CPU_CONCURRENCY = 40
NAGLE_REQUESTS = 20

QUICKACK = getattr(socket, "TCP_QUICKACK", None)


# --------------------------------------------------------------- the driver


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def quicken(sock: socket.socket) -> None:
    """Cancel this connection's PENDING delayed ACK.

    Placement is the whole of it, and it was measured rather than reasoned
    about: setting TCP_QUICKACK before the request does nothing (44.01 ms),
    and setting it after the response HEADERS have been read takes the same
    exchange to 0.45 ms. The option is not sticky and it is not a mode -- it
    fires an ACK the kernel is already sitting on, so it has to be set while
    that ACK is pending, which is after the read that revealed it.
    """
    if QUICKACK is not None:
        sock.setsockopt(socket.IPPROTO_TCP, QUICKACK, 1)


async def read_response(
    reader: asyncio.StreamReader, sock: socket.socket, quickack: bool
) -> None:
    head = await reader.readuntil(b"\r\n\r\n")
    if quickack:
        quicken(sock)
    length = 0
    for line in head.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            length = int(line.split(b":", 1)[1])
    if length:
        await reader.readexactly(length)


async def session(
    port: int, path: str, n: int, out: list[float], quickack: bool
) -> None:
    request = (
        f"GET {path} HTTP/1.1\r\nHost: bench\r\n"
        f"Connection: keep-alive\r\n\r\n"
    ).encode()
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    sock: socket.socket = writer.get_extra_info("socket")
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        writer.write(request)
        await writer.drain()
        await read_response(reader, sock, quickack)   # warm-up, not timed
        for _ in range(n):
            started = time.perf_counter()
            writer.write(request)
            await writer.drain()
            await read_response(reader, sock, quickack)
            out.append(time.perf_counter() - started)
    finally:
        writer.close()
        await writer.wait_closed()


async def drive(
    port: int, path: str, n: int, concurrency: int, quickack: bool = True
) -> dict[str, Any]:
    """`concurrency` keep-alive connections, each looping until n are done."""
    per = max(1, n // concurrency)
    latencies: list[float] = []
    wall = time.perf_counter()
    await asyncio.gather(
        *(
            session(port, path, per, latencies, quickack)
            for _ in range(concurrency)
        )
    )
    elapsed = time.perf_counter() - wall
    latencies.sort()
    done = len(latencies)
    return {
        "requests": done,
        "concurrency": concurrency,
        "seconds": elapsed,
        "rps": done / elapsed,
        "p50_ms": latencies[done // 2] * 1000,
        "p95_ms": latencies[min(done - 1, int(done * 0.95))] * 1000,
    }


async def ask_who(port: int, per: int) -> list[int]:
    """One keep-alive connection: the pid that answered each request."""
    request = (
        b"GET /who HTTP/1.1\r\nHost: bench\r\n"
        b"Connection: keep-alive\r\n\r\n"
    )
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    sock: socket.socket = writer.get_extra_info("socket")
    pids: list[int] = []
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        for _ in range(per):
            writer.write(request)
            await writer.drain()
            head = await reader.readuntil(b"\r\n\r\n")
            quicken(sock)
            length = 0
            for line in head.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    length = int(line.split(b":", 1)[1])
            body = await reader.readexactly(length)
            pids.append(int(json.loads(body)["pid"]))
    finally:
        writer.close()
        await writer.wait_closed()
    return pids


async def survey(port: int, connections: int, per: int) -> dict[str, Any]:
    """Which worker serves which connection, and does it ever change?

    This is the cell that explains the CPU row. Workers share one listening
    socket, so the kernel hands a new connection to whichever worker is in
    accept() first, and nothing moves it afterwards.
    """
    runs = await asyncio.gather(
        *(ask_who(port, per) for _ in range(connections))
    )
    counted = Counter(run[0] for run in runs)
    return {
        "connections": connections,
        "requests_each": per,
        "workers_reached": len(counted),
        "busiest_share": max(counted.values()),
        "pinned_per_connection": all(len(set(run)) == 1 for run in runs),
    }


# ------------------------------------------------------------- the service


def start_server(workers: int, port: int) -> subprocess.Popen[bytes]:
    env = dict(os.environ)
    env["E05_DELAY_SECONDS"] = str(DELAY_SECONDS)
    env["E05_BURN_ROUNDS"] = str(BURN_ROUNDS)
    return subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "measure.e05_app:app",
            "--host", "127.0.0.1", "--port", str(port),
            "--workers", str(workers),
            "--log-level", "warning", "--no-access-log",
        ],
        cwd=CODE,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_ready(port: int, deadline: float = 60.0) -> None:
    stop = time.perf_counter() + deadline
    while time.perf_counter() < stop:
        try:
            with socket.create_connection(("127.0.0.1", port), 2):
                return
        except OSError:
            time.sleep(0.2)
    raise SystemExit("E5: the server never became ready")


def pss_kib(pid: int) -> int:
    """Proportional set size of one process, or its RSS if PSS is absent.

    PSS rather than RSS on purpose: workers share pages with the process
    that spawned them, so summing RSS over the tree counts one page once per
    worker and answers a question nobody asked.
    """
    try:
        text = Path(f"/proc/{pid}/smaps_rollup").read_text(encoding="utf8")
        for line in text.splitlines():
            if line.startswith("Pss:"):
                return int(line.split()[1])
    except OSError:
        pass
    try:
        status = Path(f"/proc/{pid}/status").read_text(encoding="utf8")
    except OSError:
        return 0
    for line in status.splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1])
    return 0


def process_tree(pid: int) -> list[int]:
    pids = [pid]
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            status = (entry / "status").read_text(encoding="utf8")
        except OSError:
            continue
        for line in status.splitlines():
            if line.startswith("PPid:") and int(line.split()[1]) == pid:
                pids.append(int(entry.name))
    return pids


def burn_service_ms() -> float:
    """What one /cpu request costs, timed here, median of five.

    code/ goes on the path first: this file is run as a script, so
    sys.path[0] is measure/ and `measure.e05_app` -- the import string
    uvicorn is given, which resolves against code/ -- would not resolve
    here. One spelling of the module, in both places.
    """
    if str(CODE) not in sys.path:
        sys.path.insert(0, str(CODE))
    from measure.e05_app import burn

    samples: list[float] = []
    for _ in range(5):
        started = time.perf_counter()
        burn(BURN_ROUNDS)
        samples.append((time.perf_counter() - started) * 1000)
    samples.sort()
    return samples[2]


def measure_once() -> dict[str, Any]:
    started = time.perf_counter()
    burn_ms = burn_service_ms()
    cells: dict[str, Any] = {}
    memory: dict[str, Any] = {}
    distribution: dict[str, Any] = {}

    for workers in WORKERS:
        port = free_port()
        server = start_server(workers, port)
        try:
            wait_ready(port)
            # Every worker accepts at least one connection before anything
            # is timed, or the first cell pays for the last worker's import.
            asyncio.run(drive(port, "/noop", 64, 16))
            pids = process_tree(server.pid)
            memory[str(workers)] = {
                "processes": len(pids),
                "pss_kib": sum(pss_kib(p) for p in pids),
            }
            for concurrency in CONCURRENCIES:
                cells[f"noop.w{workers}.c{concurrency}"] = asyncio.run(
                    drive(port, "/noop", NOOP_REQUESTS[concurrency],
                          concurrency)
                )
                cells[f"await.w{workers}.c{concurrency}"] = asyncio.run(
                    drive(port, "/await", AWAIT_REQUESTS[concurrency],
                          concurrency)
                )
            cells[f"cpu.w{workers}.c{CPU_CONCURRENCY}"] = asyncio.run(
                drive(port, "/cpu", CPU_REQUESTS, CPU_CONCURRENCY)
            )
            # The artefact, measured rather than described: one connection,
            # one request at a time, with the client's delayed ACK left on
            # and then cancelled.
            for label, quickack in (("off", False), ("on", True)):
                cells[f"nagle.w{workers}.{label}"] = asyncio.run(
                    drive(port, "/noop", NAGLE_REQUESTS, 1,
                          quickack=quickack)
                )
            # And the same grid an ORDINARY client sees: no client on a
            # network sets TCP_QUICKACK, so these are the rows a deployment
            # actually gets, and the ones above are process parallelism with
            # the transport artefact taken out of them.
            cells[f"awaitplain.w{workers}.c{CPU_CONCURRENCY}"] = asyncio.run(
                drive(port, "/await", AWAIT_REQUESTS[CPU_CONCURRENCY],
                      CPU_CONCURRENCY, quickack=False)
            )
            cells[f"cpuplain.w{workers}.c{CPU_CONCURRENCY}"] = asyncio.run(
                drive(port, "/cpu", CPU_REQUESTS, CPU_CONCURRENCY,
                      quickack=False)
            )
            distribution[str(workers)] = asyncio.run(
                survey(port, CPU_CONCURRENCY, 5)
            )
        finally:
            server.terminate()
            server.wait(timeout=30)

    for name, cell in cells.items():
        if name.startswith(("noop.", "nagle.")):
            continue
        if name.startswith(("awaitplain.", "cpuplain.")):
            # These carry the artefact on purpose; the calibration cell is
            # measured with it removed, so the ratio would not mean anything.
            continue
        _kind, worker, conc = name.split(".")
        ceiling = cells[f"noop.{worker}.{conc}"]["rps"]
        cell["ceiling_rps"] = ceiling
        cell["client_bound"] = cell["rps"] > 0.5 * ceiling

    return {
        "measured_seconds": time.perf_counter() - started,
        "cores": os.cpu_count() or 0,
        "delay_seconds": DELAY_SECONDS,
        "burn_rounds": BURN_ROUNDS,
        "burn_ms": burn_ms,
        "python": sys.version.split()[0],
        "uname": os.uname().release,
        "cells": cells,
        "memory": memory,
        "distribution": distribution,
    }


# --------------------------------------------------------------- deriving


def emit(values: dict[str, str]) -> None:
    lines = ["% Generated by code/measure/e05_workers.py --- do not edit."]
    lines += [f"\\pyval{{{k}}}{{{v}}}" for k, v in values.items()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf8")
    for key, value in values.items():
        print(f"  {key:24} {value}")


def derive(raw: dict[str, Any]) -> None:
    cells: dict[str, Any] = raw["cells"]
    hi = CPU_CONCURRENCY
    aw1, aw4 = cells[f"await.w1.c{hi}"], cells[f"await.w4.c{hi}"]
    cp1, cp4 = cells[f"cpu.w1.c{hi}"], cells[f"cpu.w4.c{hi}"]
    pa1 = cells[f"awaitplain.w1.c{hi}"]
    pa4 = cells[f"awaitplain.w4.c{hi}"]
    dist = raw["distribution"]["4"]
    mem1, mem4 = raw["memory"]["1"], raw["memory"]["4"]
    ratio = mem4["pss_kib"] / mem1["pss_kib"]

    values = {
        "e05.cores": str(raw["cores"]),
        "e05.delay.ms": f"{raw['delay_seconds'] * 1000:.0f}",
        "e05.cpu.ms": f"{raw['burn_ms']:.0f}",
        "e05.conc.hi": str(hi),
        "e05.noop.rps": f"{cells[f'noop.w1.c{hi}']['rps']:.0f}",
        "e05.await.w1.c1.p50": f"{cells['await.w1.c1']['p50_ms']:.0f}",
        "e05.await.w1.rps": f"{aw1['rps']:.0f}",
        "e05.await.w1.p50": f"{aw1['p50_ms']:.0f}",
        "e05.await.w1.p95": f"{aw1['p95_ms']:.0f}",
        "e05.await.w4.rps": f"{aw4['rps']:.0f}",
        "e05.await.w4.p95": f"{aw4['p95_ms']:.0f}",
        "e05.await.ratio4": f"{aw4['rps'] / aw1['rps']:.2f}",
        "e05.cpu.w1.rps": f"{cp1['rps']:.0f}",
        "e05.cpu.w1.p95": f"{cp1['p95_ms']:.0f}",
        "e05.cpu.w4.rps": f"{cp4['rps']:.0f}",
        "e05.cpu.w4.p95": f"{cp4['p95_ms']:.0f}",
        "e05.cpu.ratio4": f"{cp4['rps'] / cp1['rps']:.2f}",
        "e05.pss.w1": f"{mem1['pss_kib'] / 1024:.0f}",
        "e05.pss.w4": f"{mem4['pss_kib'] / 1024:.0f}",
        "e05.pss.ratio4": f"{ratio:.1f}",
        "e05.nagle.w1": f"{cells['nagle.w1.off']['p50_ms']:.1f}",
        "e05.nagle.w4": f"{cells['nagle.w4.off']['p50_ms']:.0f}",
        "e05.nagle.w4.quick": f"{cells['nagle.w4.on']['p50_ms']:.1f}",
        "e05.plain.await.w1.rps": f"{pa1['rps']:.0f}",
        "e05.plain.await.w4.rps": f"{pa4['rps']:.0f}",
        "e05.plain.await.w4.p50": f"{pa4['p50_ms']:.0f}",
        "e05.dist.conns": str(dist["connections"]),
        "e05.dist.reached": str(dist["workers_reached"]),
        "e05.dist.busiest": str(dist["busiest_share"]),
    }
    emit(values)
    if not dist["pinned_per_connection"]:
        print("  NOTE: a connection changed worker; the pinning claim is off")
    flagged = [n for n, c in cells.items() if c.get("client_bound")]
    if flagged:
        print(f"  CLIENT-BOUND, do not quote: {', '.join(flagged)}")
    else:
        print("  calibration: no cell reaches half its own ceiling")


def main() -> int:
    if "--run" in sys.argv:
        raw = measure_once()
        RAW.parent.mkdir(parents=True, exist_ok=True)
        RAW.write_text(
            json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf8"
        )
        print(f"  measured in {raw['measured_seconds']:.0f} s -> {RAW.name}")
    if not RAW.is_file():
        raise SystemExit(
            "E5 has not been run on this tree. "
            "Run: uv run python measure/e05_workers.py --run"
        )
    derive(json.loads(RAW.read_text(encoding="utf8")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
