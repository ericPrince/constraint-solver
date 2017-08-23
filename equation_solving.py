from __future__ import print_function

#import heapq
#import bisect # insort

from constraint_solver import solve_numeric

#------------------------------------------------------------------------------

class Var (object):
    def __init__(self, name, val, parent=None):
        self.solved_by   = None  # equation set that solves this
        self.required_by = set() # equation sets that require this to be solved
        
        self.eqns     = set() # equations that are available
        self.all_eqns = set() # all equations
        
        self.val    = val    # value of this variable
        self.name   = name   # name of this variable
        self.parent = parent # containing parent (like a geom or constraint)
    
    def delete(self):
        '''Delete this variable by deleting all equations it appears in'''
        all_eqns = self.all_eqns.copy()
        for eqn in all_eqns:
            eqn.delete()
        
        # TODO: update solved_by and required_by
    
    def reset(self):
        '''Reset this variable by adding all eqns back to it?'''
        self.eqns = self.all_eqns.copy()
        
        self.solved_by   = None
        self.required_by = set()
    
    def remove(self, eqn):
        '''Remove an equation from this variable'''
        self.eqns.discard(eqn)
        self.all_eqns.discard(eqn) # XXX removing this fixes it - seemingly, maybe just reconstrains everything after delete
                                    # my guess is this is being used in 2 different ways (solving + deleting)        
        # TODO: as long as its ok by the parent technically
    
    def set_solved(self, eqn_set):
        '''This variable is solved by the given equation set'''
        self.solved_by = eqn_set
        
        for eqn in self.eqns:
            eqn.vars.discard(self)
        
        self.eqns -= eqn_set.eqns
    
    def __str__(self):
        return 'Var:' + self.name + '=' + str(self.val)
            

class Eqn (object):
    def __init__(self, name, f, vars, parent=None):
        self.vars     = set(vars)  # set of active vars
        self.all_vars = set(vars)  # set of all vars
        self.var_list = list(vars) # list of vars in order
        
        self.f       = f      # function to plug variables into
        self.name    = name   # name of this function
        self.parent  = parent # parent (constraint)
        
        self.eqn_set = None # equation set that solves this
        
        # add this equation to each var
        for var in vars:
            var.eqns.add(self)
            var.all_eqns.add(self)
    
    def __call__(self):
        '''Evaluate this equation with the current variable values'''
        return self.f(*[var.val for var in self.var_list])
    
    def delete(self):
        '''Delete this equation by removing it from variables and eqn set'''
        for var  in self.all_vars:
            var.remove(self)
        
        # clear references to vars (keep list jic?)
        self.vars     = set()
        self.all_vars = set()
    
    def reset(self):
        '''Reset this equation by adding all vars back to it?'''
        self.vars = self.all_vars.copy()
        self.eqn_set = None
    
    def __str__(self):
        return 'Eqn:' + self.name

class EqnSet (object):
    def __init__(self):
        self.eqns     = set() # unsolved eqns in this set
        self.vars     = set() # unsolved vars in this set
        self.all_vars = set() # all vars in this set
        
        self.solves   = set() # set of  variables this eqn set solves
        self.requires = set() # set of variables that need to be solved for this to be solved
        
    def add(self, eqn):
        '''Add an equation to this equation set'''
        self.eqns.add(eqn)
        self.vars     |= eqn.vars
        self.all_vars |= eqn.all_vars
        return self
    
    def frontier(self):
        '''Return a set of EqnSets that are reachable from this one'''
        
        ## create set of all reachable equations

        f_eqns = set()
        
        for var in self.vars:
            f_eqns |= var.eqns
            
        f_eqns -= self.eqns
        
        ## use those equations to create reachable equation sets
        
        for eqn in f_eqns:
            yield self.copy().add(eqn)
    
    def copy(self):
        eqn_set2 = EqnSet()
        eqn_set2.eqns = self.eqns.copy()
        eqn_set2.vars = self.vars.copy()
        eqn_set2.all_vars = self.all_vars.copy()

        return eqn_set2
    
    def key(self, nEq):
        '''Return the sorting key - value sets with fewer equations'''
        return - ( len(self.vars) - len(self.eqns) * (1 + 1.0/nEq) )
    
    def is_solvable(self):
        '''Does the number of equations equal the number of variables'''
        return len(self.vars) == len(self.eqns)
    
    def is_empty(self):
        return len(self.eqns) == 0
    
    def set_solved(self):
        '''Set solves and requires based on the current state'''
        self.solves = self.vars.copy()
        self.requires = self.all_vars - self.vars
        
        for var in self.requires:
            var.required_by.add(self)
        
        for var in self.solves:
            var.set_solved(self)
        
        for eqn in self.eqns:
            eqn.eqn_set = self
    
    def discard(self, eqn_set):
        '''All vars and eqns in eqn_set don't have to be dealt with'''
        self.vars -= eqn_set.vars
        self.eqns -= eqn_set.eqns
    
    def __str__(self):
        return 'Eqn_Set:\n eqns: [' + ', '.join([str(eqn) for eqn in self.eqns]) \
                    + ']\n vars: [' + ', '.join([str(var) for var in self.vars]) \
                    + ']\n reqs: [' + ', '.join([str(var) for var in self.requires]) \
                    + ']'

#------------------------------------------------------------------------------

# TODO: keep track of the set of solved equations.
#   when the solve queue is empty, use this to get the 
#   unsolved equations. use the connections between these
#   to group the unsolved equations, and then add those to
#   the final equation sets
#
# still use the frozen sets to prevent duplicates
# also look at the initial tree to figure out why (if??)
#   there is looping
# 
# to add a constraint, figure out which (one or more) of the
# unsolved sets are affected, combine them, and then run through
# the split function (and then solve, i guess)
#
# add ability to have groups of constraints pre-solved algebraically
#
# add optional sympy representation of constraints
# optional sympy solver??

# original
def split_equation_set_v1(eqn_set):
    '''Split an equation set up into smaller solvable equation sets'''
    
    nEq = len(eqn_set.eqns)
    
    solve_sets = set()
    underconstrained_set = EqnSet()
    
    # keep track of what has been visited
    unique_eqn_combos = set()
    unsolved_eqns     = set(eqn_set.eqns)
    
    ## Initialize priority queue with the equations in the input set
    pq = [EqnSet().add(eqn) for eqn in eqn_set.eqns]
    pq.sort( key=lambda p: p.key(nEq) )
    
    
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
            pq = filter(lambda p: not p.is_empty(), pq)
            pq.sort( key=lambda p: p.key(nEq) )
            
            unique_eqn_combos = set(frozenset(eqs.eqns | eqs.vars) for eqs in pq)

        else:
            # add the frontier to the pq
            for eqs in eqn_set.frontier():
                eqn_combo = frozenset(eqs.eqns | eqs.vars)
                if eqn_combo not in unique_eqn_combos:
                    unique_eqn_combos.add(eqn_combo)
                    pq.add(eqs)
                    
            pq.sort( key=lambda p: p.key(nEq) )

    # create eqn set(s) of underconstrained systems
    underconstrained_set = EqnSet()
    for eqn in unsolved_eqns:
        underconstrained_set.add(eqn)

    underconstrained_set.set_solved()


    return solve_sets, underconstrained_set

# version that tries to solve many eqn sets at a time
def split_equation_set_v2(eqn_set):
    '''Split an equation set up into smaller solvable equation sets'''
    
    nEq = len(eqn_set.eqns)
    
    solve_sets = set()
    underconstrained_set = EqnSet()
    
    # keep track of what has been visited
    unique_eqn_combos = set()
    unsolved_eqns     = set(eqn_set.eqns)
    
    ## Initialize priority queue with the equations in the input set
    pq = [EqnSet().add(eqn) for eqn in eqn_set.eqns]
    pq.sort( key=lambda p: p.key(nEq) )
    
    
    while pq:
        # try to solve as many eqn sets as possible
        eqn_set = None
        while pq and pq[-1].is_solvable():
            eqn_set = pq.pop()
            
            # set this equation set as solved
            solve_sets.add(eqn_set)
            eqn_set.set_solved()
            unsolved_eqns.difference_update(eqn_set.eqns)

            # discard this equation set from all sets in the pq
            for p in pq:
                p.discard(eqn_set)
        
        # then sort the pq if solves happened, otherwise add to the pq
        if eqn_set:
            # delete any empty eqn sets and re-sort the pq
            pq = filter(lambda p: not p.is_empty(), pq)
            pq.sort( key=lambda p: p.key(nEq) )
            
            unique_eqn_combos = set(frozenset(eqs.eqns | eqs.vars) for eqs in pq)
            
        else:
            eqn_set = pq.pop()
            
            # add the frontier to the pq
            for eqs in eqn_set.frontier():
                eqn_combo = frozenset(eqs.eqns | eqs.vars)
                if eqn_combo not in unique_eqn_combos:
                    unique_eqn_combos.add(eqn_combo)
                    pq.add(eqs)
            
            pq.sort( key=lambda p: p.key(nEq) )


    # create eqn set(s) of underconstrained systems
    underconstrained_set = EqnSet()
    for eqn in unsolved_eqns:
        underconstrained_set.add(eqn)

    underconstrained_set.set_solved()


    return solve_sets, underconstrained_set

# version using blist.sortedlist
import blist
def split_equation_set_v3(eqn_set):
    '''Split an equation set up into smaller solvable equation sets'''
    
    nEq = len(eqn_set.eqns)
    
    solve_sets = set()
    underconstrained_set = EqnSet()
    
    # keep track of what has been visited
    unique_eqn_combos = set()
    unsolved_eqns     = set(eqn_set.eqns)
    
    ## Initialize priority queue with the equations in the input set
    pq = blist.sortedlist([EqnSet().add(eqn) for eqn in eqn_set.eqns],
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
            pq = blist.sortedlist(filter(lambda p: not p.is_empty(), pq),
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
    underconstrained_set = EqnSet()
    for eqn in unsolved_eqns:
        underconstrained_set.add(eqn)

    underconstrained_set.set_solved()


    return solve_sets, underconstrained_set


split_equation_set = split_equation_set_v3


#------------------------------------------------------------------------------ 


def solve_eqn_sets(solve_sets, modified_vars):
    '''
    Solve a group of equation sets in which only certain variables
    have been modified.
    '''
    
    modified_vars = set(modified_vars)
    solved_vars   = set()
    
    # start queue with all sets that don't require any vars to be solved
    q = [eqs for eqs in solve_sets if not eqs.requires]
    q = blist.blist(q) # use blist instead of list
    
    while q:
        # get the next set that is ready to solve
        eqn_set = q.pop(0)
        
        # solve the eqn_set *if necessary*
        if any(var in eqn_set.requires for var in modified_vars) \
        or any(var in eqn_set.solves   for var in modified_vars): #not eqn_set.requires: # TODO: check in the 2nd case if already solved!
            # TODO: test for success and deal with underconstrained set
            success = solve_numeric(eqn_set)
            if not success:
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
        
        # TODO: deal with underconstrained eqn set
        #   also, what about sets with deleted vars or constraints?
            
        # at this point, modified_vars contains all vars that were updated
        
        # also, eqn_set should be the final underconstrained set?
    
    
#------------------------------------------------------------------------------ 
    
from math import pi
import constraints_unsigned as cstr

def problem2():
    x0 = Var('x0', 0.0)
    y0 = Var('y0', 0.0)
    x1 = Var('x1', 1.0)
    y1 = Var('y1', 1.0)
    x2 = Var('x2', 2.0)
    y2 = Var('y2', 2.0)
    x3 = Var('x3', 3.0)
    y3 = Var('y3', 3.0)
    Lx1 = Var('Lx1', x3.val)
    Ly1 = Var('Ly1', y3.val)
    Lx2 = Var('Lx2', x2.val)
    Ly2 = Var('Ly2', y2.val)
    cx = Var('cx', x0.val)
    cy = Var('cy', y0.val)
    cr = Var('cr', 1.0)
    d1 = Var('d1', 1.0)
    a1 = Var('a1', pi/4.0)

    variables = {x0,y0,x1,y1,x2,y2,x3,y3,Lx1,Ly1,Lx2,Ly2,cx,cy,cr,d1,a1}

    r0 = 1.5
    d = 3.0
    a = pi/6.0
    dx = 3.0
    dy = 1.0

    f1  = Eqn('f1',  lambda x0                       : cstr.set_val([x0], 0.0)                               , [x0])
    f2  = Eqn('f2',  lambda y0                       : cstr.set_val([y0], 0.0)                               , [y0])
    f3  = Eqn('f3',  lambda cr                       : cstr.set_val([cr], r0)                                , [cr])
    f4  = Eqn('f4',  lambda d1                       : cstr.set_val([d1], d)                                 , [d1])
    f5  = Eqn('f5',  lambda a1                       : cstr.set_val([a1], a)                                 , [a1])
    f6  = Eqn('f6',  lambda cy,y0                    : cstr.set_val([cy], y0)                                , [cy,y0])
    f7  = Eqn('f7',  lambda cx,y0                    : cstr.set_val([cx], y0)                                , [cx,y0])
    f8  = Eqn('f8',  lambda y0,y1                    : cstr.vert_dist([y0,y1], dy)                           , [y0,y1])
    f9  = Eqn('f9',  lambda x0,x1                    : cstr.horz_dist([x0,x1], dx)                           , [x0,x1])
    f10 = Eqn('f10', lambda x1,y1,x3,y3,x2,y2,a1     : cstr.angle_point3([x1,y1,x3,y3,x2,y2], a1)            , [x1,y1,x3,y3,x2,y2,a1])
    f11 = Eqn('f11', lambda Lx1,Ly1,Lx2,Ly2,cx,cy,cr : cstr.tangent_line_circle([Lx1,Ly1,Lx2,Ly2,cx,cy], cr) , [Lx1,Ly1,Lx2,Ly2,cx,cy,cr])
    f12 = Eqn('f12', lambda x3,y3,cx,cy,cr           : cstr.point_on_circle([x3,y3,cx,cy], cr)               , [x3,y3,cx,cy,cr])
    f13 = Eqn('f13', lambda x3,Lx1                   : cstr.set_val([x3], Lx1)                               , [x3, Lx1])
    f14 = Eqn('f14', lambda y3,Ly1                   : cstr.set_val([y3], Ly1)                               , [y3, Ly1])
    f15 = Eqn('f15', lambda Lx1,Ly1,Lx2,Ly2,d1       : cstr.line_length([Lx1,Ly1,Lx2,Ly2], d1)               , [Lx1,Ly1,Lx2,Ly2,d1])
    f16 = Eqn('f16', lambda x2,Lx2                   : cstr.set_val([x2], Lx2)                               , [x2, Lx2])
    f17 = Eqn('f17', lambda y2,Ly2                   : cstr.set_val([y2], Ly2)                               , [y2, Ly2])

    equations = {f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17}

    eqn_set = EqnSet()
    for eqn in equations:
        eqn_set.add(eqn)
    
    solve_sets, uc_set = split_equation_set(eqn_set)
    
    solve_eqn_sets(solve_sets, variables)

def main():
    problem2()

if __name__ == '__main__':
    main()