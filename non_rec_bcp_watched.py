
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
                    watch_list[neg_lit].remove(id)
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

def all_vars_assigned(assignment, all_literals):
    return all(var in assignment or -var in assignment for var in all_literals)

def select_unassigned(assignment, all_literals):
    for var in all_literals:
        if var not in assignment and -var not in assignment:
            return var

def non_rec_dpll(filename):
    formula = parse_dimacs(filename)
    assignment = {}
    stack = []
    
    all_literals = set(abs(lit) for clause in formula for lit in clause)

    watch_list = defaultdict(set)
    watched ={}
    
    unit_literals = []
    #initializing watched literals per clause
    for id, clause in enumerate(formula):
        if(len(clause) >= 2):
            lit1, lit2 = clause[0], clause[1]
            watched[id]= (lit1, lit2)
            watch_list[lit1].add(id)
            watch_list[lit2].add(id)
        elif (len(clause) == 1):
            lit = clause[0]
            watched[id]=(lit,lit)
            watch_list[lit].add(id)
            unit_literals.append(lit)
        else:
            watched[id]=()


    if not bcp(assignment, watched, watch_list, formula, unit_literals):
        return False
    
    while True:
        success = bcp(assignment, watched, watch_list, formula, newly_assigned_literals=[])
        if not success:
            if not stack:
                return False
            lit, prev_assignment = stack.pop()
            assignment=prev_assignment.copy()
            assignment[-lit]=True
            if not bcp(assignment, watched, watch_list, formula, [-lit]):
                continue
        else:
            if all_vars_assigned(assignment,all_literals):
                return assignment
            
            unassigned = select_unassigned(assignment, all_literals)
            stack.append((unassigned, assignment.copy()))
            assignment[unassigned]= True

    return False

