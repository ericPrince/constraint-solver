from __future__ import print_function, division

from operator import methodcaller
    
# for sorted insertion: heapq, bisect, blist, sortedcontainers...
from blist import blist#, sortedlist
from sortedcontainers import SortedList as sortedlist

from constraint_solver import solve_numeric
from solve_elements    import EqnSet

#------------------------------------------------------------------------------
# Equation Set Splitting
#------------------------------------------------------------------------------

# TODO:
# add ability to have groups of constraints pre-solved algebraically
#
# add optional sympy representation of constraints
# optional sympy solver??

def split_equation_set(eqn_set):
    """Split an equation set up into smaller solvable equation sets"""
    
    # used for tiebreaker of priority key
    nEq = len(eqn_set.eqns) + 1
    
    solve_sets = set()
    
    # keep track of what has been visited
    unique_eqn_combos = set()
    unsolved_eqns     = set(eqn_set.eqns)
    
    # Initialize priority queue with the equations in the input set
    pq = sortedlist([EqnSet().add(eqn) for eqn in eqn_set.eqns],
                     key = methodcaller('key', nEq))
    
    while pq:
        eqn_set = pq.pop()
        
        if eqn_set.is_constrained():
            # set this equation set as solved
            solve_sets.add(eqn_set)
            eqn_set.set_solved()
            unsolved_eqns.difference_update(eqn_set.eqns)

            # discard this equation set from all sets in the pq
            for p in pq:
                p.discard(eqn_set)

            # delete any empty eqn sets and re-sort the pq
            pq = sortedlist(filter(None, pq), 
                            key = methodcaller('key', nEq))
            
            unique_eqn_combos = set(frozenset(eqs.eqns | eqs.vars) for eqs in pq)

        else:
            # add the frontier to the pq
            for eqs in eqn_set.frontier():
                eqn_combo = frozenset(eqs.eqns | eqs.vars)
                if eqn_combo not in unique_eqn_combos:
                    unique_eqn_combos.add(eqn_combo)
                    pq.add(eqs)

    # create eqn set(s) of underconstrained systems
    # TODO: can create multiple unconstrained sets
    if unsolved_eqns:
        underconstrained_set = EqnSet()
        for eqn in unsolved_eqns:
            underconstrained_set.add(eqn)

        underconstrained_set.set_solved()
        solve_sets.add(underconstrained_set)
    
#    while unsolved_eqns:
#        eqn = unsolved_eqns.pop()
#        eqn_set = EqnSet()
#        
#        connected_eqns = {eqn}
#        
#        while connected_eqns:
#            eqn = connected_eqns.pop()
#            unsolved_eqns.discard(eqn)
#            eqn_set.add(eqn)
#            
#            for var in eqn.vars:
#                connected_eqns.update(eqn for eqn in var.eqns 
#                                          if  eqn not in eqn_set.eqns)
#        
#        eqn_set.set_solved()
#        solve_sets.add(eqn_set)

    return solve_sets




#------------------------------------------------------------------------------
# Solving Split Equation Sets
#------------------------------------------------------------------------------

def solve_eqn_set(eqn_set):
    """Solve a single equation set"""
    # TODO: add other methods (ie analytic, sympy, ...)
    return solve_numeric(eqn_set, 1.0e-8)

def solve_eqn_sets(solve_sets, modified_vars, solve_func=solve_eqn_set):
    """
    Solve a group of equation sets in which only certain variables
    have been modified.
    """
    
    # track modified and solved vars
    modified_vars = set(modified_vars) # don't really need to copy here...
    solved_vars   = set()
    
    # `q` represents the equation sets that are ready to be solved now
    # TODO: threading
    
    # start queue with all sets that don't require any vars to be solved
    q = [eqs for eqs in solve_sets if not eqs.requires]
    q = blist(q) # use blist instead of list
    
    while q:
        # get the next set that is ready to solve
        eqn_set = q.pop(0)
        
        # solve the eqn_set *if necessary*
        if (        any(var in eqn_set.requires for var in modified_vars)
                or (any(var in eqn_set.solves   for var in modified_vars) 
                    and not eqn_set.is_satisfied()) ):
            
            if not solve_func(eqn_set):
                print('FAIL')
                return eqn_set # return the eqn set that failed for reporting
            
            modified_vars |= eqn_set.solves
        
        # add all vars solved by this set to the set of solved vars
        solved_vars |= eqn_set.solves
        
        # create the frontier to add to the queue
        # TODO: much more efficient way to get the frontier
        #  1) don't look at eqn set if it has already been looked at
        #  2) keep track of linked list b/n eqn sets directly
        frontier = set()
        [ frontier.update(                                     # add to the frontier
                eqs for eqs in var.required_by                 # all eqn sets required by by the var
                if all(v in solved_vars for v in eqs.requires) # if all other required vars have been solved for
            ) for var in eqn_set.solves ]                      # for each var solved by this eqn set

        q += frontier
            
    # at this point, modified_vars contains all vars that were updated
    # also, eqn_set should be the final underconstrained set?
    pass