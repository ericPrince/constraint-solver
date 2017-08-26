import matplotlib.pyplot as plt # TODO: add/remove this for profiling

from equation_solving import Eqn, Var

#----------------------------------------------------------

class Geometry (object):
    def __init__(self, name):
        self.vars = []
        self.name = name

    def draw(self, ax=None):
        ax = ax or plt.gca()

    def delete(self):
        for var in self.vars:
            var.delete() # TODO: put delete method in var/eqn

class Point (Geometry):
    def __init__(self, name, x=0.0, y=0.0):
        self.x = Var(name + '.x', x)
        self.y = Var(name + '.y', y)
        self.vars = [self.x, self.y]
        self.name = name

    def draw(self, ax=None):
        ax = ax or plt.gca()
        plt.scatter(x=(self.x.val,), y=(self.y.val,)) # TODO: Point plot

# TODO: add Line (instead of / in addition to, line segment)

class Line_Segment (Geometry):
    def __init__(self, name, x1=0.0, y1=0.0, x2=0.0, y2=0.0):
        self.p1 = Point(name + '.p1', x1, y1)
        self.p2 = Point(name + '.p2', x2, y2)
        self.vars = [self.p1.x, self.p1.y, self.p2.x, self.p2.y]
        self.name = name

    def draw(self, ax=None):
        ax = ax or plt.gca()
        line = plt.Line2D(xdata=(self.p1.x.val, self.p2.x.val), ydata=(self.p1.y.val, self.p2.y.val))
        ax.add_artist(line)
        self.p1.draw(ax)
        self.p2.draw(ax)

class Radius (Geometry):
    def __init__(self, name, r=1.0):
        self.r = Var(name + '.r', r)
        self.vars = [self.r]

class Circle (Geometry):
    def __init__(self, name, cx=0.0, cy=0.0, cr=1.0):
        self.p = Point(name + '.p', cx, cy)
        self.r = Radius(name + '.r', cr)
        self.vars = [self.p.x, self.p.y, self.r.r]

    def draw(self, ax=None):
        ax = ax or plt.gca()
        circle = plt.Circle((self.p.x.val, self.p.y.val), self.r.r.val, fill=None)
        ax.add_artist(circle)
        self.p.draw(ax)

#----------------------------------------------------------

import constraints_unsigned as cstr

class Constraint (object):
    def __init__(self):
        self.equations = []

class SetVar (Constraint):
    def __init__(self, name, var, val):
        self.var = var
        self.val = val

        self.equations = [
            Eqn(name, lambda var: cstr.set_val([var], self.val), [var])
        ]

class HorzDist (Constraint):
    def __init__(self, name, p1, p2, d):
        self.p1 = p1
        self.p2 = p2
        self.d  = d

        self.equations = [
            Eqn(name, lambda x1,x2,d: cstr.horz_dist([x1,x2],d), [p1.x,p2.x,d])
        ]

class VertDist (Constraint):
    def __init__(self, name, p1, p2, d):
        self.p1 = p1
        self.p2 = p2
        self.d  = d

        self.equations = [
            Eqn(name, lambda y1,y2,d: cstr.vert_dist([y1,y2],d), [p1.y,p2.y,d])
        ]

# TODO: creating the constraint could/should add a/d as var!
#  - constraint could have a special var list that gets added when constraint added!!! yes
# TODO: could/should create constant class

class LineLength (Constraint):
    def __init__(self, name, L, d):
        self.L = L
        self.d = d

        self.equations = [
            Eqn(name, lambda Lx1,Ly1,Lx2,Ly2,d: cstr.line_length([Lx1,Ly1,Lx2,Ly2], d), [L.p1.x,L.p1.y,L.p2.x,L.p2.y,d]) 
        ]

class AnglePoint3 (Constraint):
    def __init__(self, name, p1, p2, p3, a):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.a = a

        self.equations = [
            Eqn(name, lambda x1,y1,x2,y2,x3,y3,a: cstr.angle_point3([x1,y1,x2,y2,x3,y3], a), [p1.x,p1.y,p2.x,p2.y,p3.x,p3.y,a])
        ]

class TangentLineCircle (Constraint):
    def __init__(self, name, L, C):
        self.L = L
        self.C = C

        self.equations = [
            Eqn(name, lambda Lx1,Ly1,Lx2,Ly2,cx,cy,cr : cstr.tangent_line_circle([Lx1,Ly1,Lx2,Ly2,cx,cy], cr), [L.p1.x,L.p1.y,L.p2.x,L.p2.y,C.p.x,C.p.y,C.r.r])
        ]

class PointOnCircle (Constraint):
    def __init__(self, name, p, C):
        self.p = p
        self.C = C

        self.equations = [
            Eqn(name, lambda x,y,cx,cy,cr: cstr.point_on_circle([x,y,cx,cy], cr), [p.x,p.y,C.p.x,C.p.y,C.r.r])
        ]

class GroundPoint (Constraint):
    pass

class CoincidentPoint2 (Constraint):
    def __init__(self, name, p1, p2):
        self.p1 = p1
        self.p2 = p2

        self.equations = [
            Eqn(name + '.x', lambda x1,x2: cstr.set_val([x1], x2), [p1.x, p2.x]),
            Eqn(name + '.y', lambda y1,y2: cstr.set_val([y1], y2), [p1.y, p2.y])
        ]

#----------------------------------------------------------

def main():
    import matplotlib.pyplot as plt
    import equation_solving as solver
    from math import pi

    r0 = 1.5
    d = 3.0
    a = pi/6.0
    d_x = 3.0 # TODO: these 2 should correspond to eqn/var (f8/f9)
    d_y = 1.0


    p0 = Point('p0', 0.0, 0.0)
    p1 = Point('p1', 1.0, 1.0)
    p2 = Point('p2', 2.0, 2.0)
    p3 = Point('p3', 3.0, 3.0)
    c1 = Circle('c1', 0.0, 0.0, 1.0)
    L1 = Line_Segment('L1', 1.0, 1.0, 3.0, 3.0)

    geometry = (p0, p1, p2, p3, c1, L1)
    

    d1 = Var('d1', 1.0)
    a1 = Var('a1', pi/4.0)
    dx = Var('dx', 2.0)
    dy = Var('dy', 1.0)

    variables = (d1, a1, dx, dy)
    

    f1  = SetVar('f1', p0.x, 0.0)
    f2  = SetVar('f2', p0.y, 0.0)
    f3  = SetVar('f3', c1.r.r, r0)
    f4  = SetVar('f4', d1, d)
    f5  = SetVar('f5', a1, a)
    f67 = CoincidentPoint2('f67', p0, c1.p)
    f8  = HorzDist('f8', p0, p1, dx)
    f9  = VertDist('f9', p0, p1, dy)
    f10 = AnglePoint3('f10', p1, p3, p2, a1)
    f11 = TangentLineCircle('f11', L1, c1)
    f12 = PointOnCircle('f12', p3, c1)
    f1314 = CoincidentPoint2('f1314', L1.p1, p3)
    f15 = LineLength('f15', L1, d1)
    f1617 = CoincidentPoint2('f1617', L1.p2, p2)
    f18 = SetVar('f18', dx, d_x)
    f19 = SetVar('f19', dy, d_y)

    constraints = (f1, f2, f3, f4, f5, f67, f8, f9, f10, f11, f12, f1314, f15, f1617, f18, f19)

    all_vars = set(variables)
    for g in geometry:
        all_vars |= set(g.vars)
    
    eqn_set = solver.EqnSet()
    
    for constraint in constraints:
        for eqn in constraint.equations:
            eqn_set.add(eqn)


    fig, ax = plt.subplots()
    
    for geom in geometry:
        geom.draw(ax)
    
    plt.axis('equal')
    plt.show()
    
    print(str(eqn_set))
    print('=====')
    print('')
    print('')

    solve_sets, uc_set = solver.split_equation_set(eqn_set)
    solver.solve_eqn_sets(solve_sets, all_vars)
    
#    solver.solve_eqn_sets({eqn_set}, all_vars)
    
    fig, ax = plt.subplots()
    
    for geom in geometry:
        geom.draw(ax)
    
    plt.axis('equal')
    plt.show()


def problem2():
    from math import pi

    r0 = 1.5
    d = 3.0
    a = pi/6.0
    d_x = 3.0 # TODO: these 2 should correspond to eqn/var (f8/f9)
    d_y = 1.0


    p0 = Point('p0', 0.0, 0.0)
    p1 = Point('p1', 1.0, 1.0)
    p2 = Point('p2', 2.0, 2.0)
    p3 = Point('p3', 3.0, 3.0)
    c1 = Circle('c1', 0.0, 0.0, 1.0)
    L1 = Line_Segment('L1', 1.0, 1.0, 3.0, 3.0)

    geometry = (p0, p1, p2, p3, c1, L1)
    

    d1 = Var('d1', 1.0)
    a1 = Var('a1', pi/4.0)
    dx = Var('dx', 2.0)
    dy = Var('dy', 1.0)

    variables = (d1, a1, dx, dy)
    

    f1  = SetVar('f1', p0.x, 0.0)
    f2  = SetVar('f2', p0.y, 0.0)
    f3  = SetVar('f3', c1.r.r, r0)
    f4  = SetVar('f4', d1, d)
    f5  = SetVar('f5', a1, a)
    f67 = CoincidentPoint2('f67', p0, c1.p)
    f8  = HorzDist('f8', p0, p1, dx)
    f9  = VertDist('f9', p0, p1, dy)
    f10 = AnglePoint3('f10', p1, p3, p2, a1)
    f11 = TangentLineCircle('f11', L1, c1)
    f12 = PointOnCircle('f12', p3, c1)
    f1314 = CoincidentPoint2('f1314', L1.p1, p3)
    f15 = LineLength('f15', L1, d1)
    f1617 = CoincidentPoint2('f1617', L1.p2, p2)
    f18 = SetVar('f18', dx, d_x)
    f19 = SetVar('f19', dy, d_y)

    constraints = (f1, f2, f3, f4, f5, f67, f8, f9, f10, f11, f12, f1314, f15, f1617, f18, f19)

    all_vars = set(variables)
    for g in geometry:
        all_vars |= set(g.vars)
    
    return geometry, variables, constraints, all_vars

if __name__ == '__main__':
    main()