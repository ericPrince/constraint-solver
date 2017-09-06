from __future__ import division

from solve_elements import EqnSet

from equation_solving import ( split_equation_set,
                               solve_eqn_sets,
                               solve_eqn_set )


class Solver (object):
    """Manager for solving systems of equations"""

    __slots__ = (
        'vars',               # all vars
        'eqns',               # all equations
        'eqn_sets',           # equation sets to be solved (includes uc_set)

        'modified_vars',      # set of vars modified since update
        'modified',           # true if eqn/var has been deleted (need reset)
        'modified_eqn_sets',  # true if underconstrained set has been modified

        'split_func',         # function that splits equation sets
        'solve_func',         # function that solves a single equation set

        'solve_tol',          # tolerance for deciding an equation is solved
    )

    def __init__(self, 
                 split_func = split_equation_set, 
                 solve_func = solve_eqn_set,
                 solve_tol  = 1.0e-6):
        self.vars     = set()
        self.eqns     = set()
        self.eqn_sets = {EqnSet()}
        
        self.modified_vars     = set()
        self.modified          = False
        self.modified_eqn_sets = set()
        
        self.split_func  = split_func
        self.solve_func  = solve_func
        
        self.solve_tol = solve_tol

    #--------------------------------------------
    # Variable: add, modify, delete
    #--------------------------------------------
    
    def add_variable(self, var):
        """Add a new variable"""
        self.vars.add(var)
        self.modified_vars.add(var)

    def add_variables(self, vars):
        """Add all variables in an iterable"""
        self.vars.update(vars)
        self.modified_vars.update(vars)

    def modify_variable(self, var, val):
        """Modify the value of a variable"""
        var.val = val
        self.modified_vars.add(var)

    def delete_variable(self, var):
        """Delete a variable, and all equations that reference it"""
        self.vars.discard(var)
        self.eqns -= var.all_eqns
        var.delete()

        self.modified = True

    #--------------------------------------------
    # constraint: add, modify, delete
    #--------------------------------------------

    def add_equation(self, eqn):
        """Add a new equation to the system"""
        return self.add_equations({eqn})

    def add_equations(self, eqns):
        """Add multiple equations"""

        # single uc eqn set:
        for eqn in eqns:
            uc_set = None
            for eqn_set in self.eqn_sets:
                if not eqn_set.is_constrained():
                    uc_set = eqn_set
                    break
            
            if not uc_set:
                uc_set = EqnSet()
                self.eqn_sets.add(uc_set)
            
            uc_set.add(eqn)
            self.modified_eqn_sets.add(uc_set)
                
        # multiple eqn sets:
#        affected_eqn_sets = set()
#
#        for eqn in eqns:
#            for var in eqn.vars:
#                if var.solved_by is None:
#                    affected_eqn_sets.add(EqnSet().add(eqn))
#                elif not var.solved_by.is_constrained():
#                    affected_eqn_sets.add(var.solved_by)
#
#        self.combine_eqn_sets(affected_eqn_sets)

        self.eqns.update(eqns)

    def delete_equation(self, eqn):
        """Delete an equation from the system"""
        self.eqns.discard(eqn)
        eqn.delete()

        self.modified = True

    def delete_equations(self, eqns):
        """Delete multiple equations"""
        self.eqns.difference_update(eqns)

        for eqn in eqns:
            eqn.delete()
        
        self.modified = True

    #--------------------------------------------
    # state: satisfied, constrained
    #--------------------------------------------

    def is_satisfied(self):
        """Are all equations satisfied?"""
        return all(eqn.is_satisfied(self.solve_tol) for eqn in self.eqns)

    #--------------------------------------------
    # update, solve, reset
    #--------------------------------------------

    def update(self):
        """Reset, split, and solve all equation sets"""

        # Reset (combine all eqns into one set, and undo solve status)
        #   Do this iff the structure has been modified
        if self.modified:
            self.reset()

        # Split (try to split modified equation sets into smaller ones)
        #   It is easier to solve smaller equation sets numerically
        for eqn_set in self.modified_eqn_sets:
            self.eqn_sets.discard(eqn_set)
            new_sets = self.split_func(eqn_set)
            self.eqn_sets.update(new_sets)

            # update modified vars
            self.modified_vars.update(var for var in eqn_set.vars
                                      if var.solved_by in new_sets)

        self.modified_eqn_sets = set()

        # Solve (re-solve any equation set that has modified vars)
        solve_eqn_sets(self.eqn_sets, self.modified_vars, self.solve_func)
        self.modified_vars = set()

    def reset(self):
        """
        Reset all variables, equations, and equation sets

        After this, the only equation set will be a single
        set which contains all equations
        """
        new_eqn_set = EqnSet()
        self.eqn_sets = {new_eqn_set}

        for var in self.vars:
            var.reset()

        for eqn in self.eqns:
            eqn.reset()

        for eqn in self.eqns:
            new_eqn_set.add(eqn)

        self.modified          = False
        self.modified_eqn_sets = {new_eqn_set}
        self.modified_vars     = set(self.vars)

    #--------------------------------------------
    # utility
    #--------------------------------------------

    def combine_eqn_sets(self, eqn_sets):
        """
        Combine equation sets into a single new one

        Old equation sets are removed from the solver,
        and the new one is added
        """
        
        # remove the input EqnSets from the solver
        self.eqn_sets.difference_update(eqn_sets)
        self.modified_eqn_sets.difference_update(eqn_sets)

        # create a new EqnSet and add all eqns contained in any of the
        # old EqnSets to it
        new_eqn_set = EqnSet()

        for eqn_set in eqn_sets:
            for eqn in eqn_set.eqns:
                new_eqn_set.add(eqn)

        # add the new EqnSet to the solver
        self.eqn_sets.add(new_eqn_set)
        self.modified_eqn_sets.add(new_eqn_set)
        
        
        # TODO: (how) does this work? - does it even matter?
        
        # change the ref of vars to the eqn set to be to the combined one
        for var in new_eqn_set.vars:
            # Vars shouldn't require any old EqnSets
            var.required_by.difference_update(eqn_sets)
            
            # add the new EqnSet to the solved_by/required_by of the Vars
            if var.solved_by in eqn_sets:
                var.solved_by = new_eqn_set
            elif var.solved_by is not None:
                var.required_by.add(new_eqn_set)
            else:
                # var is not solved yet
                pass

        return new_eqn_set

