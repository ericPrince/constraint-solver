# import operator as op

import igraph
from matplotlib import cm


def create_solver_graph(gs, cmap=cm.rainbow):
    """
    Returns an igraph graph that represents a solved solver

    Vertices are colored based on which constrained set
    they belong to. Groups of variables/equations with
    the same color belong to the same equation set and
    will be solved together

    Parameters
    ----------
    gs
        Geom solver instance
    cmap
        Color map to use to color graph vertices
    """
    var_list = list(gs.vars)
    eqn_list = list(gs.eqns)

    # var_idx = dict(map(op.itemgetter(1, 0), enumerate(var_list)))
    # eqn_idx = dict(map(op.itemgetter(1, 0), enumerate(eqn_list, len(var_list))))
    var_idx = {var: i for i, var in enumerate(var_list)}
    eqn_idx = {eqn: i + len(var_list) for i, eqn in enumerate(eqn_list)}

    g = igraph.Graph(len(var_list) + len(eqn_list))

    for eqn in gs.eqns:
        g.add_edges((eqn_idx[eqn], var_idx[var]) for var in eqn.all_vars)

    g.vs["label"] = [var.name for var in var_list] + [eqn.name for eqn in eqn_list]

    g.vs["shape"] = ["circle"] * len(var_list) + ["square"] * len(eqn_list)

    # rectangle, circle, hidden, triangle_up, triangle_down, aliases...
    # X11 colors, hex string, tuple

    eqn_set_list = list(gs.eqn_sets)
    eqn_set_idx = {eqn_set: i for i, eqn_set in enumerate(eqn_set_list)}

    g.vs["color"] = [
        cmap(
            0.3
            if var.solved_by is None
            else float(eqn_set_idx[var.solved_by]) / len(eqn_set_list)
        )
        for var in var_list
    ] + [
        cmap(
            0.6
            if eqn.eqn_set is None
            else float(eqn_set_idx[eqn.eqn_set]) / len(eqn_set_list)
        )
        for eqn in eqn_list
    ]

    g.vs["edge_color"] = [
        "black" if var.is_constrained() else "gray" for var in var_list
    ] + ["black"] * len(eqn_list)

    g.vs["size"] = [50] * len(var_list) + [20] * len(eqn_list)

    # size, width

    return g
