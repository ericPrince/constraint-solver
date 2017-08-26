"""
Use geom2d p
"""

import sys
import timeit

import matplotlib.pyplot as plt
from matplotlib import animation

sys.path.append('..')

import geom2d
import geom_solver as gs
import sample_problems as samples

def main():
    geometry, variables, constraints, all_vars = samples.problem2()
    
    solver = gs.GeometrySolver()
    
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
#    cstr_del = constraints[10] # f12: point on circle
    
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