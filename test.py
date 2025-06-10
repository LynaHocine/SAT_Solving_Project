import os
from recursive_solver import dpll
from parser_dimacs import parse_dimacs
from non_rec_bcp_watched import non_rec_dpll

def test_formula(folder, filename):
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        print(f"file not found : {filename}")

    formula = parse_dimacs(filepath)
    print (f" testing formula : {filename}")
    sat, model = dpll(formula, {})
    if sat:
        print(f"Satisfiable formula - Model : {model}")
    else:
        print("Unsatisfiable formula")

test_formula("test-formulas", "sat0.in" )

def test_solver2(folder, filename):
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filename}")
        return
    print(f"Testing formula: {filename}")
    sat, model = non_rec_dpll(filepath)
    if sat:
        print(f"Satisfiable formula – Model: {model}")
    else:
        print("Unsatisfiable formula")

test_solver2("test-formulas", "sat0.in")
