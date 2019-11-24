from .equation_solving import split_equation_set, solve_eqn_set
from .system_solver    import Solver


class GCS (object):
    """Geometric constraint solver (GCS)"""

    __slots__ = (
        'geometry',    # set of geometry elements in the system
        'constraints', # set of constraints in the system
        'solver',      # underlying Solver object
    )

    def __init__(self,
                 split_func = split_equation_set,
                 solve_func = solve_eqn_set,
                 solve_tol  = 1.0e-6):

        self.geometry    = set()
        self.constraints = set()

        self.solver = Solver(split_func,
                             solve_func,
                             solve_tol)

    #--------------------------------------------

    def add_geometry(self, geom):
        """Add a new geometry element"""
        self.geometry.add(geom)
        self.solver.add_variables(geom.vars)

    def delete_geometry(self, geom):
        """Delete a geometry element"""
        self.geometry.discard(geom)
        for var in geom.vars:
            self.solver.delete_variable(var)

    #--------------------------------------------

    def add_variable(self, var):
        self.solver.add_variable(var)

    def modify_variable(self, var, val):
        self.solver.modify_variable(var, val)

    def delete_variable(self, var):
        self.solver.delete_variable(var)

    #--------------------------------------------

    def add_constraint(self, cstr):
        """Add a new constraint to the system"""
        self.constraints.add(cstr)
        self.solver.add_equations(cstr.equations)

    def modify_set_constraint(self, cstr, val):
        """Modify the value of a "set" constraint"""
        # TODO: replace "set" constraints with "constant" constraints
        cstr.val = val
        self.solver.modify_variable(cstr.var, val)

    def delete_constraint(self, cstr):
        """Delete a constraint and its equations"""
        self.constraints.discard(cstr)
        self.solver.delete_equations(cstr.equations)

    #--------------------------------------------

    def is_satisfied(self):
        return self.solver.is_satisfied()

    def is_constrained(self):
        return self.solver.is_constrained()

    #--------------------------------------------

    def update(self):
        self.solver.update()

    def reset(self):
        self.solver.reset()

    #--------------------------------------------

    def plot(self, ax=None):
        """Plot all geometry"""
        for g in self.geometry:
            g.plot(ax)

    def draw(self, view):
        for g in self.geometry:
            g.draw(view)
