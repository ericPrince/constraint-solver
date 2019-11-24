"""
Use geom2d p
"""

import time

import sys
sys.path.append('..')

#import geom2d
import geom_solver as gs
import sample_problems as samples

sys.path.append(r'D:\Documents')
from ccad import display


def main():
    geometry, variables, constraints, all_vars = samples.problem2()

    solver = gs.GCS()

    for g in geometry:
        solver.add_geometry(g)

    for v in variables:
        solver.add_variable(v)

    for c in constraints:
        solver.add_constraint(c)

    v = display.view()
    display.start()

    solver.draw(v)
#    display.start()

#    time.sleep(1.0)

    # solved system
    solver.update()

    v.clear()
    solver.draw(v)

#    display.start()

if __name__ == '__main__':
    main()
