# note: these functions are not used, see equation_solving instead

from blist import sortedlist

from .solve_elements import EqnSet


# original
def split_equation_set_v1(eqn_set):
    """Split an equation set up into smaller solvable equation sets"""

    # used for tiebreaker of priority key
    nEq = len(eqn_set.eqns)

    solve_sets = set()
    underconstrained_set = EqnSet()

    # keep track of what has been visited
    unique_eqn_combos = set()
    unsolved_eqns = set(eqn_set.eqns)

    # Initialize priority queue with the equations in the input set
    pq = [EqnSet().add(eqn) for eqn in eqn_set.eqns]
    pq.sort(key=lambda p: p.key(nEq))

    while pq:
        eqn_set = pq.pop()

        if eqn_set.is_solvable():
            # set this equation set as solved
            solve_sets.add(eqn_set)
            eqn_set.set_solved()
            unsolved_eqns.difference_update(eqn_set.eqns)

            # discard this equation set from all sets in the pq
            for p in pq:
                p.discard(eqn_set)

            # delete any empty eqn sets and re-sort the pq
            pq = filter(lambda p: not p.is_empty(), pq)
            pq.sort(key=lambda p: p.key(nEq))

            unique_eqn_combos = set(frozenset(eqs.eqns | eqs.vars) for eqs in pq)

        else:
            # add the frontier to the pq
            for eqs in eqn_set.frontier():
                eqn_combo = frozenset(eqs.eqns | eqs.vars)
                if eqn_combo not in unique_eqn_combos:
                    unique_eqn_combos.add(eqn_combo)
                    pq.add(eqs)

            pq.sort(key=lambda p: p.key(nEq))

    # create eqn set(s) of underconstrained systems
    underconstrained_set = EqnSet()
    for eqn in unsolved_eqns:
        underconstrained_set.add(eqn)

    underconstrained_set.set_solved()

    return solve_sets, underconstrained_set


# version that tries to solve many eqn sets at a time
def split_equation_set_v2(eqn_set):
    """Split an equation set up into smaller solvable equation sets"""

    # used for tiebreaker of priority key
    nEq = len(eqn_set.eqns)

    solve_sets = set()
    underconstrained_set = EqnSet()

    # keep track of what has been visited
    unique_eqn_combos = set()
    unsolved_eqns = set(eqn_set.eqns)

    # Initialize priority queue with the equations in the input set
    pq = [EqnSet().add(eqn) for eqn in eqn_set.eqns]
    pq.sort(key=lambda p: p.key(nEq))

    while pq:
        # try to solve as many eqn sets as possible
        eqn_set = None
        while pq and pq[-1].is_solvable():
            eqn_set = pq.pop()

            # set this equation set as solved
            solve_sets.add(eqn_set)
            eqn_set.set_solved()
            unsolved_eqns.difference_update(eqn_set.eqns)

            # discard this equation set from all sets in the pq
            for p in pq:
                p.discard(eqn_set)

        # then sort the pq if solves happened, otherwise add to the pq
        if eqn_set:
            # delete any empty eqn sets and re-sort the pq
            pq = filter(lambda p: not p.is_empty(), pq)
            pq.sort(key=lambda p: p.key(nEq))

            unique_eqn_combos = set(frozenset(eqs.eqns | eqs.vars) for eqs in pq)

        else:
            eqn_set = pq.pop()

            # add the frontier to the pq
            for eqs in eqn_set.frontier():
                eqn_combo = frozenset(eqs.eqns | eqs.vars)
                if eqn_combo not in unique_eqn_combos:
                    unique_eqn_combos.add(eqn_combo)
                    pq.add(eqs)

            pq.sort(key=lambda p: p.key(nEq))

    # create eqn set(s) of underconstrained systems
    underconstrained_set = EqnSet()
    for eqn in unsolved_eqns:
        underconstrained_set.add(eqn)

    underconstrained_set.set_solved()

    return solve_sets, underconstrained_set


# version using blist.sortedlist
def split_equation_set_v3(eqn_set):
    """Split an equation set up into smaller solvable equation sets"""

    # used for tiebreaker of priority key
    nEq = len(eqn_set.eqns)

    solve_sets = set()
    underconstrained_set = EqnSet()

    # keep track of what has been visited
    unique_eqn_combos = set()
    unsolved_eqns = set(eqn_set.eqns)

    # Initialize priority queue with the equations in the input set
    pq = sortedlist(
        [EqnSet().add(eqn) for eqn in eqn_set.eqns], key=lambda p: p.key(nEq)
    )

    while pq:
        eqn_set = pq.pop()

        if eqn_set.is_solvable():
            # set this equation set as solved
            solve_sets.add(eqn_set)
            eqn_set.set_solved()
            unsolved_eqns.difference_update(eqn_set.eqns)

            # discard this equation set from all sets in the pq
            for p in pq:
                p.discard(eqn_set)

            # delete any empty eqn sets and re-sort the pq
            pq = sortedlist(
                filter(lambda p: not p.is_empty(), pq), key=lambda p: p.key(nEq)
            )

            unique_eqn_combos = set(frozenset(eqs.eqns | eqs.vars) for eqs in pq)

        else:
            # add the frontier to the pq
            for eqs in eqn_set.frontier():
                eqn_combo = frozenset(eqs.eqns | eqs.vars)
                if eqn_combo not in unique_eqn_combos:
                    unique_eqn_combos.add(eqn_combo)
                    pq.add(eqs)

    # create eqn set(s) of underconstrained systems
    underconstrained_set = EqnSet()
    for eqn in unsolved_eqns:
        underconstrained_set.add(eqn)

    underconstrained_set.set_solved()

    return solve_sets, underconstrained_set


# use the blist version
split_equation_set = split_equation_set_v3
