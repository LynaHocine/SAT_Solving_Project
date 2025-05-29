#parser_dimacs.py

def parse_dimacs(filename):
    formula = []
    with open(filename, 'r') as f:
        for line in f:
            line.strip()
            if line.startswith('c') or line.startswith('p'):
                continue
            if line =='':
                continue
            literals = list(map(int, line.split()))
            clause = [lit for lit in literals if lit != 0]
            formula.append(clause)

    return formula
