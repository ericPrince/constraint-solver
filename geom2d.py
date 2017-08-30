"""
geom2d: 2D geometry and constraints built from equation solving elements
"""

import matplotlib.pyplot as plt # TODO: add/remove this for profiling

from solve_elements import Eqn, Var

#----------------------------------------------------------
# Geometry
#----------------------------------------------------------

class Geometry (object):
    def __init__(self, name):
        self.vars = []
        self.name = name

    def draw(self, ax=None):
        ax = ax or plt.gca()

    def delete(self):
        for var in self.vars:
            var.delete()

class Point (Geometry):
    def __init__(self, name, x=0.0, y=0.0):
        self.x = Var(name + '.x', x)
        self.y = Var(name + '.y', y)
        self.vars = [self.x, self.y]
        self.name = name

    def draw(self, ax=None):
        ax = ax or plt.gca()
        plt.scatter(x=(self.x.val,), y=(self.y.val,))

# TODO: add Line (instead of / in addition to, line segment)

class Line_Segment (Geometry):
    def __init__(self, name, x1=0.0, y1=0.0, x2=0.0, y2=0.0):
        self.p1 = Point(name + '.p1', x1, y1)
        self.p2 = Point(name + '.p2', x2, y2)
        self.vars = [self.p1.x, self.p1.y, self.p2.x, self.p2.y]
        self.name = name

    def draw(self, ax=None):
        ax = ax or plt.gca()
        line = plt.Line2D(xdata=(self.p1.x.val, self.p2.x.val), 
                          ydata=(self.p1.y.val, self.p2.y.val))
        ax.add_artist(line)
        self.p1.draw(ax)
        self.p2.draw(ax)

class Circle (Geometry):
    def __init__(self, name, cx=0.0, cy=0.0, cr=1.0):
        self.p = Point(name + '.p', cx, cy)
        self.r = Var(name + '.r', cr)
        self.vars = [self.p.x, self.p.y, self.r]

    def draw(self, ax=None):
        ax = ax or plt.gca()
        circle = plt.Circle((self.p.x.val, self.p.y.val), 
                            self.r.val, 
                            fill=None)
        ax.add_artist(circle)
        self.p.draw(ax)

#----------------------------------------------------------
# Constraints
#----------------------------------------------------------

import constraints_unsigned as cstr
#import constraints_signed   as cstr

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
            Eqn(name, lambda x1,x2,d: cstr.distance_1D([x1,x2],d), [p1.x,p2.x,d])
        ]

class VertDist (Constraint):
    def __init__(self, name, p1, p2, d):
        self.p1 = p1
        self.p2 = p2
        self.d  = d

        self.equations = [
            Eqn(name, lambda y1,y2,d: cstr.distance_1D([y1,y2],d), [p1.y,p2.y,d])
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
            Eqn(name, lambda Lx1,Ly1,Lx2,Ly2,cx,cy,cr : cstr.tangent_line_circle([Lx1,Ly1,Lx2,Ly2,cx,cy], cr), [L.p1.x,L.p1.y,L.p2.x,L.p2.y,C.p.x,C.p.y,C.r])
        ]

class PointOnCircle (Constraint):
    def __init__(self, name, p, C):
        self.p = p
        self.C = C

        self.equations = [
            Eqn(name, lambda x,y,cx,cy,cr: cstr.point_on_circle([x,y,cx,cy], cr), [p.x,p.y,C.p.x,C.p.y,C.r])
        ]

class GroundPoint (Constraint):
    pass # TODO: make this, or no?

class CoincidentPoint2 (Constraint):
    def __init__(self, name, p1, p2):
        self.p1 = p1
        self.p2 = p2

        self.equations = [
            Eqn(name + '.x', lambda x1,x2: cstr.set_val([x1], x2), [p1.x, p2.x]),
            Eqn(name + '.y', lambda y1,y2: cstr.set_val([y1], y2), [p1.y, p2.y])
        ]
