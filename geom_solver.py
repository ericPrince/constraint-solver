from __future__ import print_function

from equation_solving import EqnSet, split_equation_set, solve_eqn_sets

class GeometrySolver (object):
    __slots__ = ( 'vars',          # all vars
                  'eqns',          # all equations
                  'eqn_sets',      # equation sets to be solved (includes uc_set)
                  
                  'modified_vars', # set of vars which have been modified since update
                  'modified',      # true if eqn/var has been deleted (need reset)
                  'modified_uc',   # true if underconstrained set has been modified
                  
                  'geometry',      # all geometry
                  'constraints',   # all constraints
                  
                  'uc_set')        # underconstrained set
    
    def __init__(self):
        self.vars     = set()
        self.eqns     = set()
        
        self.modified_vars = set()
        self.modified      = False
        self.modified_uc   = False
        
        self.geometry    = set()
        self.constraints = set()
        
        self.uc_set = EqnSet()
        self.eqn_sets = {self.uc_set}
        
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
        
        Sets `modified_uc` to True
        """
        self.constraints.add(cstr)
        self.eqns.update(cstr.equations)
        
        for eqn in cstr.equations:
            self.uc_set.add(eqn)
        
        self.modified_uc = True
    
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
        return var not in self.uc_set.solves
    
    #--------------------------------------------
    # update, solve, reset
    #--------------------------------------------
    
    def update(self):
        """Reset, split the unconstrained equation set, and solve all equation sets"""
        
        if self.modified:
            self.reset() # note: this will cause self.modified_uc to be True
        
        if self.modified_uc:
            # split uc set if possible...
            self.eqn_sets.discard(self.uc_set)
            
            new_sets, self.uc_set = split_equation_set(self.uc_set)
            
            self.eqn_sets |= new_sets
            self.eqn_sets.add(self.uc_set)
            
            self.modified_uc = False
        
        # solve!
        self.solve()
    
    def solve(self):
        """Solve all equation sets"""
        print('~~~~~')
        print(len(self.eqn_sets))
        print(len(self.uc_set.eqns))
        print(self.uc_set.is_solvable())
        print(len(self.uc_set.vars))
        print('~~~~~')
        solve_eqn_sets(self.eqn_sets, self.modified_vars)
        self.modified_vars = set()  
    
    def reset(self):
        """
        Reset all variables, equations, and equation sets
        
        After this, the only equation set will be a single 
        underconstrained set which contains all equations
        
        Also, `self.modified_uc` will be set to True
        """
        self.uc_set = EqnSet() # underconstrained set
        self.eqn_sets = {self.uc_set}
        
        for var in self.vars:
            var.reset()
        
        for eqn in self.eqns:
            eqn.reset()
        
        for eqn in self.eqns:
            self.uc_set.add(eqn)
        
        self.modified    = False
        self.modified_uc = True
        self.modified_vars = set(self.vars)
    
#    def reset_uc(self):
#        pass
    
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
    
#------------------------------------------------------------------------------
    
def main():
    import timeit
    import sys
    import matplotlib.pyplot as plt
    from matplotlib import animation
    import geom2d
    
    geometry, variables, constraints, all_vars = geom2d.problem2()
    
    solver = GeometrySolver()
    
    for g in geometry:
        solver.add_geometry(g)
    
    for v in variables:
        solver.add_variable(v)
    
    for c in constraints:
        solver.add_constraint(c)
    
    # unsolved system
    solver.draw()
    plt.axis('equal')
    plt.show()
    
    # solved system
    solver.update()
    solver.draw()
    plt.axis('equal')
    plt.show()
    
    # change circle radius
    solver.modify_set_constraint(constraints[2], 0.75) # TODO?
    solver.delete_constraint(constraints[10])
#    solver.add_constraint(geom2d.PointOnCircle('f12', geometry[3], geometry[4]))
#    solver.modified=True
#    solver.reset()
    solver.update()
    print(solver.is_satisfied())
    print('@@@@@@@@')
    for eqn_set in solver.eqn_sets:
        print(sorted(eqn.name for eqn in eqn_set.eqns))
    print('@@@@@@@@')
    solver.draw()
    plt.axis('equal')
    sys.stdout.flush()
    plt.show()
    
#    solver.modify_set_constraint(constraints[2], 0.74)
    solver.add_constraint(geom2d.PointOnCircle('f12', geometry[3], geometry[4]))
    solver.modified = True
    solver.update()
    print(solver.is_satisfied())
    print('@@@@@@@@')
    for eqn_set in solver.eqn_sets:
        print(sorted(eqn.name for eqn in eqn_set.eqns))
    print('@@@@@@@@')
    solver.draw()
    plt.axis('equal')
    sys.stdout.flush()
    plt.show()
    
    # delete a constraint
#    cstr_del = constraints[-1] # f19: set dy
#    cstr_del = constraints[12] # f15: line length
#    cstr_del = constraints[9] #  f11: tangent line circle
#    cstr_del = constraints[7] #  f9:  set y dist to dy
    cstr_del = constraints[10] # f12: point on circle
    
#    solver.delete_constraint(cstr_del)

    # animate (and time)
    MAX = 1.0
    N = 100
    
    fig = plt.figure()
    def animate(f):
        fig.clear()
        t = timeit.default_timer()
        
        solver.modify_set_constraint(constraints[2], (MAX * (f + 1))/(N + 1))
        solver.update()
        
        t = timeit.default_timer() - t
        
        print(t)
        print(solver.is_satisfied())
        print('-----')
        
        solver.draw()
        plt.axis('equal')
    
    anim = animation.FuncAnimation(fig, animate, xrange(N), repeat=False)
    plt.show()
    
    sys.stdout.flush()
    
#    for f in xrange(N):
#        t = timeit.default_timer()
#        
#        solver.modify_set_constraint(constraints[2], (MAX * (f + 1))/(N + 1))
#        solver.update()
#        
#        t = timeit.default_timer() - t
#        
#        print(t)
#        print(solver.is_satisfied())
#        print('-----')


    # TODO: adding a constraint has issues with update because
    #   the solves/requires aspects of vars have already been set

    # add back the deleted constraint
#    solver.add_constraint(geom2d.PointOnCircle('f12', geometry[3], geometry[4]))

#    for eqn in cstr_del.equations:
#        eqn.vars     = set(eqn.var_list)
#        eqn.all_vars = set(eqn.var_list)
#    solver.add_constraint(cstr_del) # TODO!
    solver.modified = True # TODO: issue has to do with variables/eqns in uc set not being reset!
#    solver.reset()
    print('++++')          #   but also need to improve robustness of solver
    print(len(solver.uc_set.vars))
    print('++++')
#    for eqn in solver.uc_set.eqns:
#        for var in solver.uc_set.vars:
#            if var in eqn.all_vars:
#                eqn.vars.add(var)
    solver.update()
    print(solver.is_satisfied())
    print('@@@@@@@@')
    for eqn_set in solver.eqn_sets:
        print(sorted(eqn.name for eqn in eqn_set.eqns))
    print('@@@@@@@@')
    solver.draw()
    plt.axis('equal')
    sys.stdout.flush()
    plt.show()

    # delete the circle (c1)
    solver.delete_geometry(geometry[4])
    solver.update()
    solver.draw()
    plt.axis('equal')
    plt.show()
    
if __name__ == '__main__':
    main()