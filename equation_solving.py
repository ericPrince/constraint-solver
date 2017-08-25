from __future__ import print_function, division

#from operator import methodcaller # TODO: can use this for sort key

#try:
#    import queue
#except:
#    import Queue as queue
    
# for sorted insertion: heapq, bisect, blist, sortedcontainers...
from blist import blist#, sortedlist
from sortedcontainers import SortedList as sortedlist

from constraint_solver import solve_numeric

#------------------------------------------------------------------------------
# Variable, Equation, and Equation Set
#------------------------------------------------------------------------------

class Var (object):
    __slots__ = ( 'eqns',        # equations that are available
                  'all_eqns',    # all equations
                  
                  'solved_by',   # equation set that solves this
                  'required_by', # equation sets that require this to be solved
                  
                  'val',         # value of this variable
                  'name',        # name of this variable
                  'parent', )    # containing parent (like a geom or constraint)
    
    def __init__(self, name, val, parent=None):
        self.solved_by   = None
        self.required_by = set()
        
        self.eqns     = set()
        self.all_eqns = set()
        
        self.val    = val
        self.name   = name
        self.parent = parent
    
    def delete(self):
        """Delete this variable by deleting all equations it appears in"""
        all_eqns = self.all_eqns.copy()
        for eqn in all_eqns:
            eqn.delete()
    
    def reset(self):
        """Reset this variable by adding all eqns back to it"""
        self.eqns = self.all_eqns.copy()
        
        self.solved_by   = None
        self.required_by = set()
    
    def remove(self, eqn):
        """Remove an equation from this variable"""
        self.eqns.discard(eqn)
        self.all_eqns.discard(eqn)
    
    def set_solved(self, eqn_set):
        """This variable is (or will be) solved by the given equation set"""
        self.solved_by = eqn_set
        
        for eqn in self.eqns:
            eqn.vars.discard(self)
        
        self.eqns -= eqn_set.eqns
    
    def __str__(self):
        return 'Var:' + self.name + '=' + str(self.val)
            

class Eqn (object):
    __slots__ = ( 'vars',      # set of active vars
                  'all_vars',  # set of all vars
                  'var_list',  # list of vars in order
                  
                  'f',         # function to plug variables into
                  'name',      # name of this function
                  'parent',    # parent (constraint)
                  
                  'eqn_set', ) # equation set that solves this
    
    def __init__(self, name, f, vars, parent=None):
        self.vars     = set(vars)
        self.all_vars = set(vars)
        self.var_list = list(vars)
        
        self.f       = f
        self.name    = name
        self.parent  = parent
        
        self.eqn_set = None
        
        # add this equation to each var
        for var in vars:
            var.eqns.add(self)
            var.all_eqns.add(self)
    
    def __call__(self):
        """Evaluate this equation with the current variable values"""
        return self.f(*[var.val for var in self.var_list])
    
    def delete(self):
        """Delete this equation by removing it from variables and eqn set"""
        for var  in self.all_vars:
            var.remove(self)
        
        # clear references to vars (keep list jic?)
        self.vars     = set()
        self.all_vars = set()
    
    def reset(self):
        """Reset this equation by adding all vars back to it"""
        self.vars = self.all_vars.copy()
        self.eqn_set = None
    
    def __str__(self):
        return 'Eqn:' + self.name

class EqnSet (object):
    __slots__ = ( 'eqns',       # unsolved eqns in this set
                  'vars',       # unsolved vars in this set
                  'all_vars',   # all vars in this set
                  
                  'solves',     # set of  variables this eqn set solves
                  'requires', ) # set of variables that need to be solved for this to be solvable
    
    def __init__(self):
        self.eqns     = set()
        self.vars     = set()
        self.all_vars = set()
        
        self.solves   = set()
        self.requires = set()
        
    def add(self, eqn):
        """Add an equation to this equation set"""
        self.eqns.add(eqn)
        self.vars     |= eqn.vars
        self.all_vars |= eqn.all_vars
        return self
    
    def frontier(self):
        """Generator of equation sets that are reachable from this one"""
        
        # create set of all reachable equations

        f_eqns = set()
        
        for var in self.vars:
            f_eqns |= var.eqns
            
        f_eqns -= self.eqns
        
        # use those equations to create reachable equation sets
        
        for eqn in f_eqns:
            yield self.copy().add(eqn)
    
    def copy(self):
        """
        Copy the equations and vars of this set to a new set
        
        note: `solves` and `requires` will be empty sets
        """
        eqn_set2 = EqnSet()
        eqn_set2.eqns = self.eqns.copy()
        eqn_set2.vars = self.vars.copy()
        eqn_set2.all_vars = self.all_vars.copy()

        return eqn_set2
    
    def degrees_of_freedom(self):
        """The number of degrees of freedom of this set (#var - #eq)"""
        return len(self.vars) - len(self.eqns)
    
    def key(self, nEq):
        """
        Sorting key: value of key is higher for sets with more degrees of freedom
        
        `nEq` is meant to be the total number of equations in a larger set
        and should be at least `len(self.eqns) + 1`, and should be the same
        for the key for all equation sets being used
        """
        # last term is tie-breaker to value sets with more equations
        # TODO: could replace nEq with a large number
        return -self.degrees_of_freedom() + len(self.eqns)/nEq
    
    def is_solvable(self):
        """Does the number of equations equal the number of variables?"""
        return len(self.vars) == len(self.eqns)
    
    def is_empty(self):
        """Does this equation set have no equations?"""
        return len(self.eqns) == 0
    
    def is_satisfied(self):
        """Are all equations currently satisfied?"""
        return all(eqn() < 1.0e-6 for eqn in self.eqns) # TODO: tolerance parameter
    
    def set_solved(self):
        """Set solves and requires based on the current state"""
        self.solves = self.vars.copy()
        self.requires = self.all_vars - self.vars
        
        for var in self.requires:
            var.required_by.add(self)
        
        for var in self.solves:
            var.set_solved(self)
        
        for eqn in self.eqns:
            eqn.eqn_set = self
    
    def discard(self, eqn_set):
        """
        All vars and eqns in eqn_set don't have to be dealt with
        
        Meant to be used when splitting equation sets into small
        solvable ones, where the input eqn_set is solvable
        """
        self.vars -= eqn_set.vars
        self.eqns -= eqn_set.eqns
    
    def __bool__(self):
        return not self.is_empty() # True if not empty
    
    def __str__(self):
        return 'Eqn_Set:\n eqns: [' + ', '.join([str(eqn) for eqn in self.eqns]) \
                    + ']\n vars: [' + ', '.join([str(var) for var in self.vars]) \
                    + ']\n reqs: [' + ', '.join([str(var) for var in self.requires]) \
                    + ']'

#------------------------------------------------------------------------------
# Equation Set Splitting
#------------------------------------------------------------------------------

# TODO:
# to add a constraint, figure out which (one or more) of the
# unsolved sets are affected, combine them, and then run through
# the split function (and then solve, i guess)
#
# add ability to have groups of constraints pre-solved algebraically
#
# add optional sympy representation of constraints
# optional sympy solver??

def split_equation_set(eqn_set):
    """Split an equation set up into smaller solvable equation sets"""
    
    # used for tiebreaker of priority key
    nEq = len(eqn_set.eqns)
    
    solve_sets = set()
    underconstrained_set = EqnSet()
    
    # keep track of what has been visited
    unique_eqn_combos = set()
    unsolved_eqns     = set(eqn_set.eqns)
    
    # Initialize priority queue with the equations in the input set
    pq = sortedlist([EqnSet().add(eqn) for eqn in eqn_set.eqns],
                    key=lambda p: p.key(nEq))
    
    while pq:
        eqn_set = pq.pop()
        
        if eqn_set.is_solvable():
            # set this equation set as solved
            solve_sets.add(eqn_set)
            eqn_set.set_solved()
            unsolved_eqns.difference_update(eqn_set.eqns)

            # discard this equation set from all sets in the pq
            for p in pq:
                p.discard(eqn_set)

            # delete any empty eqn sets and re-sort the pq
            pq = sortedlist(filter(lambda p: not p.is_empty(), pq), 
                            key=lambda p: p.key(nEq))
            
            unique_eqn_combos = set(frozenset(eqs.eqns | eqs.vars) for eqs in pq)

        else:
            # add the frontier to the pq
            for eqs in eqn_set.frontier():
                eqn_combo = frozenset(eqs.eqns | eqs.vars)
                if eqn_combo not in unique_eqn_combos:
                    unique_eqn_combos.add(eqn_combo)
                    pq.add(eqs)

    # create eqn set(s) of underconstrained systems
    # TODO: can create multiple unconstrained sets, just have to 
    #   modify other code
    underconstrained_set = EqnSet()
    for eqn in unsolved_eqns:
        underconstrained_set.add(eqn)

    underconstrained_set.set_solved()


    return solve_sets, underconstrained_set


#------------------------------------------------------------------------------
# Solving Split Equation Sets
#------------------------------------------------------------------------------

def solve_eqn_set(eqn_set):
    """Solve a single equation set"""
    # TODO: add other methods (ie analytic, sympy, ...)
    
#    # if 1 equation and 1 variable, use the exact solution?
#    if len(eqn_set.eqns) == 1 and len(eqn_set.solves) == 1:
#        for eqn in eqn_set.eqns:
#            eqn.var_list[0].val -= eqn()
#            return True
    
    return solve_numeric(eqn_set, 1.0e-8)

def solve_eqn_sets(solve_sets, modified_vars):
    """
    Solve a group of equation sets in which only certain variables
    have been modified.
    """
    
    # were all equation sets solved successfully?
    all_success = True
    
    # track modified and solved vars
    modified_vars = set(modified_vars) # TODO: need to copy?
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
            
            if not solve_eqn_set(eqn_set):
                all_success = False
                print('FAIL')
            
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
    pass # return modified_vars
        
    return all_success