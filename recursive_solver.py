#checking if the formula is satisfiable
def is_clause_satisfied(clause, assignment):
    for literal in clause :
        # val gets the current assignment
        val = assignment.get(abs(literal))
        #if the literal is positive and the variable is assigned true , the literal is true. (literal > 0 and val)
        #if the literal is negative and the variable is assigned false, the literal is true. ( literal < 0 and val)
        if val is not None and ((literal > 0 and val) or (literal < 0 and val)):
            return True
    # if no literal in the clause is satisfied , the clause is unsatisfied, so return false.
    return False

#checking if the formula is unsatisfiable
def is_clause_unsatisfied(clause, assignment):
    for literal in clause :
        #val gets the current assignment
        val = assignment.get(abs(literal))
        #if the literal is positive and the variable is assigned true, the clause is not unsatisfied.
        #if the literal is negative and the variable is assigned false, the clause is not unsatisfied.
        if val is not None and ((literal > 0 and (val)) and (literal < 0 and not val) ):
            return False
    #if all literals are assigned and they are all false, the clause is unsatisfied, so return true.
    return True

#choosing next variable to assign
def choose_next_variable (formula, assignment):
    #for every clause in our formula
    for clause in formula:
        #for every literal in the clause
        for literal in clause:
            #we get the number of the variable
            var = abs(literal)
            #if the variable is not assigned yet, we return it as the next option.
            if var not in assignment:
                return var
    #if every variable is assigned, we return None ( no variables left ).
    return None

#Implementing the recursive solver (DPLL Algorithm )
def dpll(formula, assignment = {}):

    #for every clause, we check if it is unsatisfied. If a clause is unsatisfied, the formula is UNSAT under our current assignment. We return false.
    for clause in formula:
        if is_clause_unsatisfied (clause, assignment):
            return False, {}
        
    #if all clauses are satisfied, a solution is found. we return true and the solution
    all_clauses_sat = all(is_clause_satisfied(clause, assignment) for clause in formula)
    if all_clauses_sat:
        return True, assignment
    
    #we choose a variable that is unassigned
    var = choose_next_variable(formula, assignment)
    if var is None:
        #if no variables are left, we return false.
        return False, {}
    
    #we try to assign the variable to true
    assignment[var]=True
    sat, result = dpll(formula, assignment.copy())
    #if the result is true, the formula is SAT.
    if sat:
        return True, result

    #if the result is false , we backtrack and assign the same variable to false.
    assignment[var]=False
    sat, result = dpll(formula, assignment.copy())
    #if the result is true, the formula is SAT.
    if sat:
        return True, result
    
    #if neither worked, the formula is UNSAT
    return False, {}