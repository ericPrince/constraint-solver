from __future__ import print_function
import sys

from equation_solving import EqnSet, split_equation_set, solve_eqn_sets

class GeometrySolver (object):
    def __init__(self):
        self.vars     = set() # all vars
        self.eqns     = set() # all equations
        self.eqn_sets = set()
        
        self.modified_vars = set() # set of vars which have been modified since update
        self.modified      = False # true if eqn/var has been deleted (need reset)
        self.modified_uc   = False # true if underconstrained set has been modified
        
        self.geometry    = set() # all geometry
        self.constraints = set() # all constraints
        
        self.uc_set = EqnSet() # underconstrained set
        self.eqn_sets = {self.uc_set}
        
    #--------------------------------------------
        
    def add_geometry(self, geom):
        self.geometry.add(geom)
        self.vars.update(geom.vars)
        self.modified_vars.update(geom.vars)
        
#        self.modified_uc = True
    
    def add_variable(self, var):
        self.vars.add(var)
        self.modified_vars.add(var)
        
#        self.modified_uc = True
    
    def modify_variable(self, var, val):
        var.val = val
        self.modified_vars.add(var)
    
    def delete_geometry(self, geom):
        self.geometry.discard(geom)
        
        for var in geom.vars:
            self.delete_variable(var)
        
        self.modified = True
    
    def delete_variable(self, var):
        self.vars.discard(var)
        self.eqns -= var.all_eqns
        var.delete()
        
        # TODO: also delete constraints
        self.modified = True
    
    #--------------------------------------------
    
    def add_constraint(self, cstr):
        self.constraints.add(cstr)
        self.eqns.update(cstr.equations)
        
        for eqn in cstr.equations:
            self.uc_set.add(eqn)
        
        self.modified_uc = True
    
    def modify_set_constraint(self, cstr, val):
        cstr.val     = val
        cstr.var.val = val
        self.modified_vars.add(cstr.var)
    
    def delete_constraint(self, cstr):
        self.constraints.discard(cstr)
        self.eqns.difference_update(cstr.equations)
        
        for eqn in cstr.equations:
            eqn.delete()
        
        self.modified = True
        
        # TODO: delete any variables with the constraint as the parent!
        # maybe make a children property?? - or do something with SetVar
    
    #--------------------------------------------
    
    def is_constrained(self, var):
        # only valid if up to date
        return var not in self.uc_set.solves
    
    #--------------------------------------------
    
    def update(self):
        if self.modified:
            self.reset()
        
        if self.modified_uc:
            # split uc set if possible...
            self.eqn_sets.discard(self.uc_set)
            new_sets, self.uc_set = split_equation_set(self.uc_set)
            self.eqn_sets |= new_sets
            self.eqn_sets.add(self.uc_set)
            # TODO: deal with uc set correctly
            self.modified_uc = False
        
        # solve!
        self.solve()
    
    def solve(self):
        solve_eqn_sets(self.eqn_sets, self.modified_vars)
        self.modified_vars = set()  
    
    def reset(self):
        self.uc_set = EqnSet() # underconstrained set
        self.eqn_sets = {self.uc_set}
        
        for var in self.vars:
            var.reset()
        
        for eqn in self.eqns:
            eqn.reset()
        
        for eqn in self.eqns:
            self.uc_set.add(eqn)
        
        self.modified = False
        self.modified_uc = True
    
    def draw(self):
        for g in self.geometry:
            g.draw()
    
    def is_satisfied(self):
        return all(eqn() < 1.0e-6 for eqn in self.eqns)
    
#    def __str__(self):
#        return 'GeomSolver:' \
#             + '\n    Vars:\n        ' \
#             + '\n        '.join(str(var) for var in self.vars) \
#             + '\n    Eqns:\n        ' \
#             + '\n        '.join(str(eqn) for eqn in self.eqns) \
#             + '\n    EqnSets:\n        ' \
#             + '\n        '.join(str(eqn_set) for eqn_set in self.eqn_sets) \
#             + '\n    UCSet:\n        ' \
#             + str(self.uc_set) \
#             + '\n    Modified:\n        ' \
#             + str(self.modified) \
#             + '\n        ' + '\n        '.join(str(var) for var in self.modified_vars)
    
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
    
    
#    '\n        '.join(['EqnSet:'] 
#                      + [ ['    Eqns:'] 
#                          +  ['        ' + str(eqn) for eqn in eqn_set.eqns] ]
#                      + [ ['    Vars:']
#                          + ['        ' + str(var) for var in eqn_set.vars] ]
#                      for eqn_set in self.eqn_sets)
    
#------------------------------------------------------------------------------
    
def main():
    import timeit
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
#    print(solver)
#    sys.stdout.flush()
    solver.draw()
    plt.axis('equal')
    plt.show()
    
    # solved system
    solver.update()
#    print(solver)
#    sys.stdout.flush()
    solver.draw()
    plt.axis('equal')
    plt.show()
    
    # change circle radius
    solver.modify_set_constraint(constraints[2], 1.0)
    solver.update()
    solver.draw()
    plt.axis('equal')
    plt.show()
    
    # delete a constraint
#    solver.delete_constraint(constraints[12]) # f15: line length
#    solver.delete_constraint(constraints[9]) # f11: tangent line circle

    solver.delete_constraint(constraints[-1]) # TODO: why hang w/ -1,-2 (f19: set dy)
#    solver.delete_constraint(constraints[7]) # f9: set y dist to dy
    
#    solver.delete_constraint(constraints[10]) # f12: point on circle
    
    solver.reset()
    print(solver)
    sys.stdout.flush()

    # animate (and time)
    fig = plt.figure()
    MAX = 1.0
    N = 100
    def animate(f):
        fig.clear()
        t = timeit.default_timer()
        solver.modify_set_constraint(constraints[2], (MAX * (f + 1))/(N + 1))
        solver.update()
        t = timeit.default_timer() - t
        print(t)
        print(solver.is_satisfied())
        solver.draw()
        plt.axis('equal')
    
    anim = animation.FuncAnimation(fig, animate, xrange(N), repeat=True)
    plt.show()
    
    # delete the circle (c1)
    solver.delete_geometry(geometry[4])
    solver.update()
    solver.draw()
    plt.axis('equal')
    plt.show()
    
if __name__ == '__main__':
    main()