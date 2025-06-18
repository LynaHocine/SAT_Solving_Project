
from collections import defaultdict, deque
from parser_dimacs import parse_dimacs


#implementing BCP with watched literals
def bcp(assignment, watched, watch_list,formula, newly_assigned_literals, levels, reasons, current_level):
    #creating a queue for literals that have just been assigned
    propagation_queue = deque(newly_assigned_literals)
    visited =set(newly_assigned_literals)
    #continuing the loop until there are no more literals to propagate
    while propagation_queue:
        #we pop one newly assigned literal
        lit = propagation_queue.pop()
        current_val = assignment.get(abs(lit))
        #if the literal is already satisfied , we skip it
        if current_val is not None:
            if (lit > 0 and current_val is True) or (lit < 0 and current_val is False):
                continue
        
        #get the negation of this literal and the clauses that are watching it
        neg_lit = -lit
        clauses_to_check = list(watch_list[neg_lit])


        for id in clauses_to_check:
            clause = formula[id]
            w1, w2 = watched[id] # the two watched literals
            other = w2 if w1 == neg_lit else w1 #the other watched literal

            for_new_watch = False # flag to indicate whether we are able to move the watch

            #we try to find another literal to watch in the clause
            for l in clause:
                if l!= other and assignment.get(abs(l)) is None:
                    watched[id]= (other, l)
                    watch_list[l].add(id)
                    watch_list[neg_lit].remove(id)
                    found_new_watch = True
                    break
            
            #if no new literal was found to watch , we check the status of the other watched literal
            if not found_new_watch:
                val_other = assignment.get(abs(other))
                #other literal is false = clause unsatisfied = return conflict clause id
                if(other > 0 and val_other is False )or(other<0 and val_other is True):
                    return id
                
                #other literal is unassigned = uni clause = assign it
                elif val_other is None:
                    assignment[abs(other)] = other>0
                    levels[abs(other)]=current_level
                    reasons[abs(other)]=clause
                    #add this literal to the queue for propagation
                    if other not in visited:
                        propagation_queue.append(other)
                        visited.add(other)
    #no conflicts found during propagation
    return None
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
    
#resolve two clauses on a pivot literal
def resolve(c1, c2, pivot):
    pivot = abs(pivot)
    result = list(set(c1 + c2))
    result = [l for l in result if abs(l) != pivot]
    return result

#analyze a conflict and perform it's first learning
def analyze_conflict(conflict_clause, assigned_lits, levels, reasons, current_level):
    learned_clause = conflict_clause[:] # starting with the conflict clause
    seen = set() # we track all literals solved

    #we count how many literals in the clause are from the current decision level
    lit_num = sum(1 for lit in learned_clause if levels.get(abs(lit), -1)== current_level)

    #if there's more than one , we keep resolving
    while lit_num > 1:
        for lit in reversed(assigned_lits):
            if lit in seen:
                continue # we skip already used literals
            if -lit in learned_clause or lit in learned_clause:
                if levels.get(abs(lit), -1) == current_level:
                    pivot_lit = lit
                    break
        else:
            break

        reason = reasons.get(abs(pivot_lit)) # get the reason clause for this literal
        if reason is None:
            break # no reason = we stop

        seen.add(pivot_lit)
        
        learned_clause = resolve(learned_clause, reason, pivot_lit)

        lit_num = sum(1 for lit in learned_clause if levels.get(abs(lit), -1) == current_level)

    backtrack_level = 0
    for lit in learned_clause:
        l = levels.get(abs(lit), 0)
        if l!= current_level and l > backtrack_level:
            backtrack_level = l # we track the highest level to backtrack to
    
    return learned_clause, backtrack_level # return learned clause and level to backtrack



#the main non-recursive DPLL solver
def cdcl(filename):
    formula = parse_dimacs(filename)
    assignment = {} #dictionary to store variable assignment
    stack = [] #stack for backtracking
    levels = {}
    reasons = {}
    current_level = 0
    
    #Get all variables used in the formula
    all_vars = set(abs(lit) for clause in formula for lit in clause)
    watch_list = defaultdict(set) #maps the literal to the set of clause ids watching it
    watched ={} #maps clause id to two literals
    unit_literals = [] # list to store unit literals

    #initializing watched literals per clause
    for id, clause in enumerate(formula):
        if(len(clause) >= 2):
            #if the clause has two or more literals , we pick the first two to watch
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
    conflict = bcp(assignment, watched, watch_list, formula, unit_literals, levels, reasons, current_level)
    if conflict is not None:
        return (False, None) # conflict during initial propagation = UNSAT
    
    while True:
        #if all variables are assigned and formula is satisfied  we return SAT
        if all_vars.issubset(assignment.keys()):
            if formula_satisfied(formula, assignment):
                return (True, assignment)
            else:
                return (False, None)
        #we pick the next unassigned variable for decision
        decision_var = select_unassigned(assignment, all_vars)
        if decision_var is None:
            #all variables are assigned and we check the satisfaction
            if formula_satisfied(formula, assignment):
                return (True, assignment)
            else:
                return(False, None)
        
        #we make a decision by assigning the variable to True
        current_level+= 1
        assignment[decision_var]= True
        levels[decision_var] = current_level
        reasons[decision_var] = None
        stack.append((decision_var, True, current_level))

        #we propagate implications from decision
        lit = decision_var if assignment[decision_var] else -decision_var
        conflict = bcp(assignment, watched, watch_list, formula, [lit], levels, reasons, current_level)

        #we handle conflicts by learning new clauses
        while conflict is not None:
            conflict_clause = formula[conflict]
            assigned_lits = [lit if val else -lit for lit, val, _ in stack]
            learned_clause, backtrack_level = analyze_conflict(conflict_clause, assigned_lits, levels, reasons, current_level)

            if not learned_clause:
                return (False, None) # unsat: empty clause learned
            
            #we add the learnt clause to the formula
            formula.append(learned_clause)
            new_clause_id = len(formula)-1
            lit1 = learned_clause[0]
            lit2 = learned_clause[0] if len(learned_clause) == 1 else learned_clause[1]
            watched[new_clause_id]= (lit1, lit2)
            watch_list[lit1].add(new_clause_id)
            watch_list[lit2].add(new_clause_id)

            #we backtrack to the appropriate level
            current_level = backtrack_level
            assignment = {var:val for var, val in assignment.items() if levels.get(var, 0) <= current_level}
            levels = {var:lvl for var, lvl in levels.items() if lvl <= current_level}
            reasons = {var: rsn for var, rsn in reasons.items() if levels.get(var, 0)<= current_level}
            stack = [(lit, val, lvl) for lit, val, lvl in stack if lvl<= current_level]

            unassigned_lits = [lit for lit in learned_clause if abs(lit) not in assignment]

            if len(unassigned_lits) == 1:
                #unit clause after backtrack = propagate again
                lit = unassigned_lits[0]
                var = abs(lit)
                assignment[var] = lit > 0
                levels[var] = current_level
                reasons[var] = learned_clause
                conflict = bcp(assignment, watched, watch_list, formula, [lit], levels, reasons, current_level)
            else:
                #no further propagation necessary 
                conflict = None

