

from collections import defaultdict
from parser_dimacs import parse_dimacs


#implementing BCP with watched literals
def bcp(assignment, watched, watch_list,formula, newly_assigned_literals):
    propagation_queue = list(newly_assigned_literals)

    while propagation_queue:
        lit = propagation_queue.pop()
        neg_lit = -lit
        clauses_to_check = watch_list[neg_lit].copy()
        for id in clauses_to_check:
            clause = formula[id]
            w1, w2 = watched[id]
            other = w2 if w1==neg_lit else w1

            found_new = False
            for l in clause:
                if l!= other and (l not in assignment or assignment[l] is True):
                    watched[id] = (other, l)
                    watch_list[l].add(id)
                    watch_list[neg_lit].remove[id]
                    found_new = True
                    break
            
            if not found_new :
                if other in assignment:
                    if assignment[other] is False:
                        return False
                else:
                    assignment[other] = True
                    propagation_queue.append(other)

    return True

    

def non_rec_dpll(filename):
    formula = parse_dimacs(filename)
    assignment = {}
    stack = []
    
    all_literals = set(abs(lit) for clause in formula for lit in clause)

    watch_list = defaultdict(set)
    watched ={}
    
    #initializing watched literals per clause
    for id, clause in enumerate(formula):
        if(len(clause) >= 2):
            lit1, lit2 = clause[0], clause[1]
            watched[id]= (lit1, lit2)
            watch_list[lit1].add(id)
            watch_list[lit2].add(id)
        elif (len(clause) == 1):
            lit = clause[0]
            watched[id]=(lit,)
            watch_list[lit].add(id)
        else:
            watched[id]=()
