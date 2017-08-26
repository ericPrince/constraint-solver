#------------------------------------------------------------------------------
# Variable, Equation, and Equation Set
#------------------------------------------------------------------------------

# TODO: additions to variable arch:
#   - constants: easy way to define updatable/modifyable constants
#   - dependent variables: do things like set two angles as equal?? hmm
# implement these as subclasses of Var?
#   -> in case of constant, it wouldn't have to be added to the solve structure?

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