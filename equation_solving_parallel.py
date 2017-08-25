import threading

try:
    import queue
except:
    import Queue as queue

from constraint_solver import solve_numeric

#------------------------------------------------------------------------------
# Solving Split Equation Sets
#------------------------------------------------------------------------------

def solve_eqn_set(eqn_set):
    """Solve a single equation set"""
    # TODO: add other methods (ie analytic, sympy, ...)
    return solve_numeric(eqn_set, 1.0e-8)


# TODO: threading couldddd work, but need lock on optimize.root if hybr solver

def solve_eqn_sets(solve_sets, modified_var_set):
    """
    Solve a group of equation sets in which only certain variables
    have been modified.
    """
    
    # `q` represents the equation sets that are ready to be solved now
    q = queue.Queue()
    
    class Solve_eqn_sets (threading.Thread):
        all_success   = True
        modified_vars = set(modified_var_set)
        solved_vars   = set()
    
        def run(self):
            # TODO: while loop end condition?
            while True:
                # get the next set that is ready to solve
                eqn_set = q.get()
                
                # solve the eqn_set *if necessary*
                if (        any(var in eqn_set.requires for var in Solve_eqn_sets.modified_vars)
                        or (any(var in eqn_set.solves for var in Solve_eqn_sets.modified_vars) 
                            and not eqn_set.is_satisfied()) ):
                    
                    if not solve_eqn_set(eqn_set):
                        Solve_eqn_sets.all_success = False
                        print('FAIL')
                    
                    Solve_eqn_sets.modified_vars |= eqn_set.solves
                
                # add all vars solved by this set to the set of solved vars
                Solve_eqn_sets.solved_vars |= eqn_set.solves
                
                # create the frontier to add to the queue
                # TODO: much more efficient way to get the frontier
                #  1) don't look at eqn set if it has already been looked at
                #  2) keep track of linked list b/n eqn sets directly
                frontier = set()
                [ frontier.update(                                     # add to the frontier
                        eqs for eqs in var.required_by                 # all eqn sets required by by the var
                        if all(v in Solve_eqn_sets.solved_vars for v in eqs.requires) # if all other required vars have been solved for
                    ) for var in eqn_set.solves ]                      # for each var solved by this eqn set
        
                for eqs in frontier:
                    q.put(eqs)
                
                q.task_done()
    
    # create the thread pool
    for _ in range(4):
        t = Solve_eqn_sets()
        t.daemon = True
        t.start()
    
    # start up the queue
    for eqs in solve_sets:
        if not eqs.requires:
            q.put(eqs)
    
    # wait for all tasks to be done
    q.join()
    
    # at this point, modified_vars contains all vars that were updated
    # also, eqn_set should be the final underconstrained set?
    pass # return modified_vars
        
    return Solve_eqn_sets.all_success