"""Which of these does the lock cost you? Time them and see.

    cd code && uv run python ch01/workloads.py

Four threads, three kinds of work, and one number that tells you everything:
how much longer four threads take than one. At 1.0 the four ran in parallel;
at 4.0 they ran one after another and the threads bought nothing.

The same file under the free-threaded interpreter answers a fourth question,
and that is experiment E1:

    python3.14t ch01/workloads.py

measure/e01_gil.py imports the functions below rather than copying them, so
the numbers the book prints came out of the file you are reading.
"""

import hashlib
import socket
import statistics
import sys
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

THREADS = 4
TRIALS = 3

# Sized so one unit of each takes about a fifth of a second. Small enough
# and the fixed cost of starting a thread swamps the answer, and the
# machine's own noise lands in the ratio rather than around it: at a tenth
# of this the four-thread free-threaded run came out FASTER than the
# one-thread run, which is not a finding, it is a measurement too small to
# make. Trials are few and the harness in measure/e01_gil.py repeats the
# whole file instead, so a reader's run stays short.
# Absolute times are a property of your machine; the RATIO is not.
CPU_STEPS = 4_000_000
DIGEST_BLOCKS = 192
BLOCK = b"x" * (1 << 20)
IO_DELAY = 0.05


# --8<-- [start:cpu]
def cpu() -> int:
    """Pure Python arithmetic. Every step of this is bytecode."""
    total = 0
    for i in range(CPU_STEPS):
        total += i * i
    return total
# --8<-- [end:cpu]


# --8<-- [start:digest]
def digest() -> str:
    """The same arithmetic, done inside a C extension instead."""
    h = hashlib.sha256()
    for _ in range(DIGEST_BLOCKS):
        h.update(BLOCK)
    return h.hexdigest()
# --8<-- [end:digest]


def _serve(listener: socket.socket, stop: threading.Event) -> None:
    """Answer every connection after IO_DELAY, each on its own thread."""
    def handle(conn: socket.socket) -> None:
        with conn:
            time.sleep(IO_DELAY)
            conn.sendall(b"1")

    while not stop.is_set():
        try:
            conn, _ = listener.accept()
        except OSError:
            return
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


# --8<-- [start:io]
def blocking_io(port: int) -> int:
    """A real socket read, not a sleep: the thread is parked in recv()."""
    with socket.create_connection(("127.0.0.1", port)) as sock:
        return len(sock.recv(1))
# --8<-- [end:io]


def time_threads(work: Callable[[], object], threads: int) -> float:
    """Median wall time for `threads` copies of `work`, run together."""
    runs: list[float] = []
    for _ in range(TRIALS + 1):
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=threads) as pool:
            futures = [pool.submit(work) for _ in range(threads)]
            for future in futures:
                future.result()
        runs.append(time.perf_counter() - start)
    # The first run is discarded: it pays for the pool's threads and for
    # whatever the operating system had to page in.
    return statistics.median(runs[1:])


def measure() -> list[tuple[str, float, float]]:
    """(name, one thread, THREADS threads) for each workload."""
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(THREADS * 2)
    port = int(listener.getsockname()[1])
    stop = threading.Event()
    server = threading.Thread(
        target=_serve, args=(listener, stop), daemon=True
    )
    server.start()
    try:
        jobs: list[tuple[str, Callable[[], object]]] = [
            ("cpu (pure Python)", cpu),
            ("io (socket read)", lambda: blocking_io(port)),
            ("digest (C extension)", digest),
        ]
        return [
            (name, time_threads(job, 1), time_threads(job, THREADS))
            for name, job in jobs
        ]
    finally:
        stop.set()
        listener.close()


def main() -> int:
    gil = sys._is_gil_enabled()  # pyright: ignore[reportPrivateUsage]
    print(f"GIL enabled: {gil}, threads: {THREADS}")
    print(f"{'workload':22} {'1 thread':>9} {'4 threads':>10} {'ratio':>7}")
    for name, one, many in measure():
        print(f"{name:22} {one:8.3f}s {many:9.3f}s {many / one:6.2f}x")
    return 0


if __name__ == "__main__":
    sys.exit(main())
