import os
from recursive_solver import dpll
from parser_dimacs import parse_dimacs

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

test_formula("test-formulas", "sat1.in" )