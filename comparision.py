import os
import time
from recursive_solver import dpll
from non_rec_bcp_watched import non_rec_dpll
from cdcl_solver import cdcl

TEST_FOLDER = "test-formulas"
OUTPUT_FILE = "results.txt"

SOLVERS = [
    #("Solver1", dpll),
    ("Solver2", non_rec_dpll),
    ("Solver3", cdcl)
]

def run_with_timer(solver, filename):
    start = time.time()
    try:
        result = solver(os.path.join(TEST_FOLDER, filename))
        elapsed = time.time() - start
        if isinstance(result, tuple) and len(result) >= 2:
            sat = result[0]
        else:
            sat = False
        return ("SAT" if sat else "UNSAT"), f"{elapsed:.3f}"
    except Exception:
        return ("ERROR", "-")

def pad(s, width):
    return str(s).ljust(width)

def main():
    files = sorted(f for f in os.listdir(TEST_FOLDER) if f.endswith(".in"))

    col_widths = [20, 12, 10, 12]
    headers = ["File", "Solver", "Result", "Time (s)"]

    border_top =    "╔" + "╦".join("═" * w for w in col_widths) + "╗"
    border_middle = "╠" + "╬".join("═" * w for w in col_widths) + "╣"
    border_bottom = "╚" + "╩".join("═" * w for w in col_widths) + "╝"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(border_top + "\n")
        out.write("║" + "║".join(pad(h, w) for h, w in zip(headers, col_widths)) + "║\n")
        out.write(border_middle + "\n")

        for file in files:
            for solver_name, solver_fn in SOLVERS:
                result, time_taken = run_with_timer(solver_fn, file)
                line = "║" + "║".join([
                    pad(file, col_widths[0]),
                    pad(solver_name, col_widths[1]),
                    pad(result, col_widths[2]),
                    pad(time_taken, col_widths[3]),
                ]) + "║\n"
                out.write(line)

        out.write(border_bottom + "\n")

    print(f"Results saved in readable format to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
