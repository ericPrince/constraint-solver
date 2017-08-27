import igraph

from matplotlib import cm

def create_solver_graph(gs, cmap = cm.rainbow):
    var_list = list(gs.vars)
    eqn_list = list(gs.eqns)

    var_idx = {var: i                for i,var in enumerate(var_list)}
    eqn_idx = {eqn: i + len(gs.vars) for i,eqn in enumerate(eqn_list)}
    
    g = igraph.Graph(len(gs.vars) + len(gs.eqns))
    
    for eqn in gs.eqns:
        g.add_edges((eqn_idx[eqn], var_idx[var]) for var in eqn.all_vars)
    
    g.vs['label'] = ([var.name for var in var_list] 
                  +  [eqn.name for eqn in eqn_list])
    
    g.vs['shape'] = (['circle'] * len(var_list) 
                   + ['square'] * len(eqn_list))
    
    # rectangle, circle, hidden, triangle_up, triangle_down, aliases...
    # X11 colors, hex string, tuple
    
    eqn_set_list = list(gs.eqn_sets)
    eqn_set_idx = {eqn_set: i for i,eqn_set in enumerate(eqn_set_list)}
    
    # TODO: doesn't work if var.solved is None
    g.vs['color'] = ([cmap( float(eqn_set_idx[var.solved_by]) 
                              / len(eqn_set_list) )
                      for var in var_list] 
                  
                  +  [cmap( float(eqn_set_idx[eqn.eqn_set]) 
                              / len(eqn_set_list) )
                      for eqn in eqn_list])
    
#                  + ['white'] * len(eqn_list))
    
    g.vs['size'] = [50] * len(var_list) + [20] * len(eqn_list)
    
    # size, width    
    
    return g


def main():
    import matplotlib.pyplot as plt
    import geom_solver as gs
    
    import sys
    sys.path.append('./test')
    import sample_problems as samples
    
    geometry, variables, constraints, all_vars = samples.problem2()
    
    solver = gs.GeometrySolver()
    
    for g in geometry:
        solver.add_geometry(g)
    
    for v in variables:
        solver.add_variable(v)
    
    for c in constraints:
        solver.add_constraint(c)
    
    solver.update()
    
    igraph.plot(create_solver_graph(solver), bbox=(0,0,1000,1000))
#    igraph.plot(create_solver_graph(solver), 'C:/Users/Prince/Downloads/solver_graph.png', bbox=(0,0,1000,1000))
    
    
    solver.draw()
    plt.axis('equal')
    plt.show()

if __name__ == '__main__':
    main()