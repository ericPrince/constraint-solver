from __future__ import print_function

from equation_solving import EqnSet, split_equation_set, solve_eqn_sets

class GeometrySolver (object):
    __slots__ = ( 'vars',          # all vars
                  'eqns',          # all equations
                  'eqn_sets',      # equation sets to be solved (includes uc_set)
                  
                  'modified_vars',     # set of vars which have been modified since update
                  'modified',          # true if eqn/var has been deleted (need reset)
                  'modified_eqn_sets', # true if underconstrained set has been modified
                  
                  'geometry',      # all geometry
                  'constraints')   # all constraints
    
    def __init__(self):
        self.vars     = set()
        self.eqns     = set()
        
        self.modified_vars = set()
        self.modified      = False
        self.modified_eqn_sets   = set()
        
        self.geometry    = set()
        self.constraints = set()
        
        self.eqn_sets = {EqnSet()}
        
    #--------------------------------------------
    # geometry, variable: add, modify, delete
    #--------------------------------------------
        
    def add_geometry(self, geom):
        """Add a new geometry element"""
        self.geometry.add(geom)
        self.vars.update(geom.vars)
        self.modified_vars.update(geom.vars)
    
    def add_variable(self, var):
        """Add a new variable"""
        self.vars.add(var)
        self.modified_vars.add(var)
    
    def modify_variable(self, var, val):
        """
        Modify the value of a variable
        
        Signal that the variable has been modified for
        when `update` is called
        """
        var.val = val
        self.modified_vars.add(var)
    
    def delete_geometry(self, geom):
        """
        Delete a geometry element
        
        Sets `modified` to True
        """
        self.geometry.discard(geom)
        
        for var in geom.vars:
            self.delete_variable(var)
        
        self.modified = True
    
    def delete_variable(self, var):
        """
        Delete a variable
        
        Sets `modified` to True
        """
        self.vars.discard(var)
        self.eqns -= var.all_eqns
        var.delete()
        
        # TODO: also delete constraints
        self.modified = True
    
    #--------------------------------------------
    # constraint: add, modify, delete
    #--------------------------------------------
    
    def add_constraint(self, cstr):
        """
        Add a constraint (which can have multiple equations)
        """
        
        for eqn in cstr.equations:
            affected_eqn_sets = set(var.solved_by 
                                    if var.solved_by is not None
                                    else EqnSet().add(eqn)
                                    for var in eqn.vars 
                                    if var.solved_by is None 
                                        or not var.solved_by.is_solvable())

        self.combine_eqn_sets(affected_eqn_sets)
        
        self.constraints.add(cstr)
        self.eqns.update(cstr.equations)
        
        self.update() # TODO: why is this necessary?
#        self.modified = True
    
    def modify_set_constraint(self, cstr, val):
        """
        Modify the value of a "set" constraint
        
        Adds the variable that is set to the modified set
        """
        cstr.val     = val
        cstr.var.val = val
        self.modified_vars.add(cstr.var)
        # TODO: could change "set" constraint to a constraint
        #   that signals that its variable shouldn't change !?!?
    
    def delete_constraint(self, cstr):
        """
        Delete a constraint
        
        Set `modified` to True
        """
        self.constraints.discard(cstr)
        self.eqns.difference_update(cstr.equations)
        
        for eqn in cstr.equations:
            eqn.delete()
        
        self.modified = True
        
        # TODO: delete any variables with the constraint as the parent!
        # maybe make a children property?? - or do something with SetVar
    
    #--------------------------------------------
    # state: satisfied, constrained
    #--------------------------------------------
    
    def is_satisfied(self):
        """Are all equations satisfied?"""
        return all(eqn() < 1.0e-6 for eqn in self.eqns) # TODO: tolerance parameter
    
    def is_constrained(self, var):
        """
        Is `var` in a constrained equation set?
        
        note: only valid if up to date
        """
        # TODO: remove this function?
        return var.solved_by is not None and var.solved_by.is_solvable()
    
    #--------------------------------------------
    # update, solve, reset
    #--------------------------------------------
    
    def update(self):
        """Reset, split the unconstrained equation set, and solve all equation sets"""
        
        # Reset (combine all eqns into one set, and undo solve status)
        #   Do this iff the structure has been modified
        if self.modified:
            self.reset() # note: this will cause self.modified_uc to be True
        
        # Split (try to split modified equation sets into smaller ones)
        #   It is easier to solve smaller equation sets numerically
        for eqn_set in self.modified_eqn_sets:
            self.eqn_sets.discard(eqn_set)
            new_sets, _ = split_equation_set(eqn_set)
            self.eqn_sets.update(new_sets)
            
            # update modified vars
            self.modified_vars.update(var for var in eqn_set.vars 
                                      if var.solved_by in new_sets)
        
        self.modified_eqn_sets = set()
        
        # Solve (numerically re-solve and equation set that has modified vars)
        self.solve()
    
    def solve(self):
        """Solve all equation sets"""
        solve_eqn_sets(self.eqn_sets, self.modified_vars)
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
        self.eqn_sets.difference_update(eqn_sets)
        self.modified_eqn_sets.difference_update(eqn_sets)
        
        new_eqn_set = EqnSet()
        
        for eqn_set in eqn_sets:
            for eqn in eqn_set.eqns:
                new_eqn_set.add(eqn)
        
        self.eqn_sets.add(new_eqn_set)
        self.modified_eqn_sets.add(new_eqn_set)
        
        return new_eqn_set
    
    #--------------------------------------------
    # display
    #--------------------------------------------
    
    def draw(self):
        """Draw all geometry"""
        for g in self.geometry:
            g.draw()
    
    def __str__(self):
        return 'GeomSolver:' \
             + '\n    Vars:\n        ' \
             + '\n        '.join(str(var) for var in self.vars) \
             + '\n    Eqns:\n        ' \
             + '\n        '.join(str(eqn) for eqn in self.eqns) \
             \
             + '\n    EqnSets:\n        ' \
             + '\n        '.join('\n        '.join(
                      ['EqnSet:'] 
                      + ['    Eqns:'] + ['        ' + str(eqn) for eqn in eqn_set.eqns]
                      + ['    Vars:'] + ['        ' + str(var) for var in eqn_set.vars]
                      )
                      for eqn_set in self.eqn_sets) \
             \
             + '\n    Modified:\n        ' \
             + str(self.modified) \
             + '\n        ' + '\n        '.join(str(var) for var in self.modified_vars)
