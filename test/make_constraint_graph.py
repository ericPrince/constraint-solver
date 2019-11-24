import sys

import matplotlib.pyplot as plt
import igraph

import gcs.geom_solver as gs
import gcs.sample_problems as samples
from gcs.constraint_graph import create_solver_graph


def main():
    # -----------------------------------------------------
    # set up problem
    # -----------------------------------------------------

    geometry, variables, constraints, all_vars = samples.problem2()

    solver = gs.GCS()

    for g in geometry:
        solver.add_geometry(g)

    for v in variables:
        solver.add_variable(v)

    #    solver.update()

    for c in constraints:
        solver.add_constraint(c)

    # -----------------------------------------------------
    # show unsolved graph
    # -----------------------------------------------------

    solver.reset()
    igraph.plot(create_solver_graph(solver.solver), bbox=(0, 0, 1000, 1000))

    # -----------------------------------------------------
    # solve
    # -----------------------------------------------------

    solver.update()

    print(solver.is_satisfied())
    sys.stdout.flush()

    # -----------------------------------------------------
    # show solved graph and geometry
    # -----------------------------------------------------

    igraph.plot(create_solver_graph(solver.solver), bbox=(0, 0, 1000, 1000))

    # solver.draw()
    solver.plot()
    plt.axis("equal")
    plt.show()


if __name__ == "__main__":
    main()
