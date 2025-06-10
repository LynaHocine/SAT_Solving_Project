
from collections import defaultdict, deque
from parser_dimacs import parse_dimacs


#implementing BCP with watched literals
def bcp(assignment, watched, watch_list,formula, newly_assigned_literals):
    #creating a queue for literals that have just been assigned
    propagation_queue = deque(newly_assigned_literals)

    #continuing the loop until there are no more literals to propagate
    while propagation_queue:
        #we pop one newly assigned literal
        lit = propagation_queue.pop()
        neg_lit = -lit #we get the negation of the literal
        #we copy the list of clauses watching this negated literal
        clauses_to_check = list(watch_list[neg_lit])

        #for each clause that watches this literal
        for id in clauses_to_check:
            clause = formula[id]
            w1, w2 = watched[id] # we get the two watched literals in the clause
            #we identify the other watched literal ( not the one just assigned )
            other = w2 if w1==neg_lit else w1

            found_new_watch = False #flagging to check if a new literal is found
            for l in clause:
                #if l is not the other literal watched and is either not assigned or already satisfied
                if l!= other and assignment.get(abs(l)) is None:
                    #we update the watched literals by replacing the current one with a new one
                    watched[id] = (other, l)
                    watch_list[l].add(id)
                    watch_list[neg_lit].remove(id)
                    found_new_watch= True
                    break # we found a replacement so no need to check further

            #if no new literal is found to watch
            if not found_new_watch:
                #If the other watched literal is assigned false , there is a conflict during the propagation
                val_other= assignment.get(abs(other))
                if (other > 0 and val_other is False) or (other < 0 and val_other is True):
                    #we have a conflict so the clause is falsified
                    return False
                elif val_other is None :
                    #we do unit propagation: the other watched literal must be true to satisfy the clause
                    assignment[abs(other)] = other > 0
                    propagation_queue.append(other) # we add the newly assigned literal to the queue
                    print(f"Propagating {other}, assignment: {assignment}")

    return True # no conflicts, propagation is successful

#Checking if all variables have been assigned a value
def all_vars_assigned(assignment, all_literals):
    #if the variable or it's negation is in the assignment , the it is assigned
    return all(var in assignment for var in all_literals)

#Choosing a variable that has not been assigned yet
def select_unassigned(assignment, all_literals):
    for var in all_literals:
        if var not in assignment:
            return var # return the first unassigned variable
    return None

#checking if the formula is satisfied under the current assignment
def formula_satisfied(formula, assignment):
    for clause in formula:
        if not any(
            (lit > 0 and assignment.get(abs(lit)) is True) or
            (lit < 0 and assignment.get(abs(lit)) is False )
            for lit in clause
        ):
            return False
    return True
    

#the main non-recursive DPLL solver
def non_rec_dpll(filename):
    formula = parse_dimacs(filename)
    assignment = {} #dictionary to store variable assignment
    stack = [] #stack for backtracking
    
    #Get all variables used in the formula
    all_vars = set(abs(lit) for clause in formula for lit in clause)
    watch_list = defaultdict(set) #maps the literal to the set of clause ids watching it
    watched ={} #maps clause id to two literals
    unit_literals = [] # list to store unit literals

    #initializing watched literals per clause
    for id, clause in enumerate(formula):
        if(len(clause) >= 2):
            lit1, lit2 = clause[0], clause[1]
            watched[id]= (lit1, lit2)
            watch_list[lit1].add(id)
            watch_list[lit2].add(id)
        elif (len(clause) == 1):
            #unit clause : we only have one literal
            lit = clause[0]
            watched[id]=(lit,lit) # both watched literals are the same in a unit clause
            watch_list[lit].add(id)
            unit_literals.append(lit)
        else:
            #Empty clause : unsatisfied
            return (False, None)

    #initial propagation of unit clauses
    if not bcp(assignment, watched, watch_list, formula, unit_literals):
        return (False, None) # we have conflict from the start , formula is UNSAT
    
    while True:
        if all_vars.issubset(assignment.keys()):
            #all variables are assigned
            if formula_satisfied(formula, assignment):
                return (True, assignment) #formula is SAT
            if not stack:
                return (False, None) # formula is UNSAT, no more backtracking options
            lit, prev_assignment, tried_true= stack.pop()
            if tried_true:
                #backtracking by trying the opposite assignment
                assignment = prev_assignment.copy()
                assignment[abs(lit)] = False
                stack.append((lit, assignment.copy(), False)) #we push the opposite assignment into the stack
                if not bcp(assignment, watched, watch_list, formula, [lit]):
                    continue # conflict , we continue backtracking

            else:
                #we already tried both assignments for this variable, we continue to the next backtracking option
                continue
        else:
            #select unassigned variable
            decision_var = select_unassigned(assignment, all_vars)
            stack.append((decision_var, assignment.copy(), True)) # we push the current state onto the stack
            assignment[decision_var] = True # we assign the vriable to True
            if not bcp(assignment, watched, watch_list, formula, [decision_var]):
                #conflict , we backtrack
                while stack:
                    lit, prev_assignment, tried_true = stack.pop()
                    if tried_true:
                        #we try the opposite assignment
                        assignment = prev_assignment.copy()
                        assignment[abs(lit)] = False
                        stack.append((lit, assignment.copy(), False))
                        if bcp(assignment, watched, watch_list, formula, [-abs(lit)]):
                            break # backtracking is successful, we break out of the loop
                else:
                    return (False, None) # no more backtracking options, formula is UNSAT