from __future__ import print_function

import scipy.optimize as opt

def solve_numeric(eqn_set, ftol=1.0e-10):
    '''
    Solve an equation set numerically

    Parameters
    ----------
    eqn_set: EqnSet
        the equation set to solve

    Returns
    -------
    success: bool
        true if the equation set was solved (and its variables were updated)
    '''

    eqn_list = list(eqn_set.eqns)
    var_list = list(eqn_set.vars)

    if len(var_list) == 0:
        [print(eqn) for eqn in eqn_list]
        # TODO: decide its ok to be over-constrained but consistent
        #   no bc what if same eqn twice, then any solution is possible
        #   depending on order equations are given in!
        for eqn in eqn_list:
            if abs(eqn()) > ftol:
                return False
        return True

    V0 = [var.val for var in var_list]

    def F(V):
        for var,val in zip(var_list, V):
            var.val = val

        # TODO: added ability to solve underconstrained systems
        return [eqn() for eqn in eqn_list] + [0.0]*(len(var_list) - len(eqn_list))

    # solve methods: hybr, lm, (krylov used to work)
    sol = opt.root(F, V0, args=(), method='lm')
    VF = sol.x

    return all(abs(f) < ftol for f in F(VF))

#    if sol.success:
#        F(VF) # set values of variables
#    else:
#        print (sol)
#
#    return sol.success