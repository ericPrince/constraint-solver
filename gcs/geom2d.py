"""
geom2d: 2D geometry and constraints built from equation solving elements
"""

import matplotlib.pyplot as plt  # TODO: add/remove this for profiling

from .solve_elements import Eqn, Var
from . import constraints_unsigned as cstr

# form . import constraints_signed   as cstr

try:
    from ccad import model
except ImportError:
    pass

# ----------------------------------------------------------
# Geometry
# ----------------------------------------------------------


class Geometry(object):
    def __init__(self, name):
        self.vars = []
        self.name = name

    def plot(self, ax=None):
        ax = ax or plt.gca()

    def draw(self, view):
        pass

    def delete(self):
        for var in self.vars:
            var.delete()


class Point(Geometry):
    def __init__(self, name, x=0.0, y=0.0):
        self.x = Var(name + ".x", x)
        self.y = Var(name + ".y", y)
        self.vars = [self.x, self.y]
        self.name = name

    def plot(self, ax=None):
        ax = ax or plt.gca()
        plt.scatter(x=(self.x.val,), y=(self.y.val,))

    def draw(self, view):
        self.geom = model.vertex([self.x.val, self.y.val, 0])
        view.display(self.geom)


# TODO: add Line (instead of / in addition to, line segment)


class Line_Segment(Geometry):
    def __init__(self, name, x1=0.0, y1=0.0, x2=0.0, y2=0.0):
        self.p1 = Point(name + ".p1", x1, y1)
        self.p2 = Point(name + ".p2", x2, y2)
        self.vars = [self.p1.x, self.p1.y, self.p2.x, self.p2.y]
        self.name = name

    def plot(self, ax=None):
        ax = ax or plt.gca()
        line = plt.Line2D(
            xdata=(self.p1.x.val, self.p2.x.val), ydata=(self.p1.y.val, self.p2.y.val)
        )
        ax.add_artist(line)
        self.p1.plot(ax)
        self.p2.plot(ax)

    def draw(self, view):
        self.geom = model.segment(
            [self.p1.x.val, self.p1.y.val, 0], [self.p2.x.val, self.p2.y.val, 0]
        )
        view.display(self.geom)


class Circle(Geometry):
    def __init__(self, name, cx=0.0, cy=0.0, cr=1.0):
        self.p = Point(name + ".p", cx, cy)
        self.r = Var(name + ".r", cr)
        self.vars = [self.p.x, self.p.y, self.r]

    def plot(self, ax=None):
        ax = ax or plt.gca()
        circle = plt.Circle((self.p.x.val, self.p.y.val), self.r.val, fill=None)
        ax.add_artist(circle)
        self.p.plot(ax)

    def draw(self, view):
        self.geom = model.circle(self.r.val)
        self.geom.translate([self.p.x.val, self.p.y.val, 0])
        view.display(self.geom)


# ----------------------------------------------------------
# Constraints
# ----------------------------------------------------------


class Constraint(object):
    def __init__(self):
        self.equations = []


class SetVar(Constraint):
    def __init__(self, name, var, val):
        self.var = var
        self.val = val

        self.equations = [Eqn(name, lambda var: cstr.set_val([var], self.val), [var])]


class HorzDist(Constraint):
    def __init__(self, name, p1, p2, d):
        self.p1 = p1
        self.p2 = p2
        self.d = d

        self.equations = [
            Eqn(name, lambda x1, x2, d: cstr.distance_1D([x1, x2], d), [p1.x, p2.x, d])
        ]


class VertDist(Constraint):
    def __init__(self, name, p1, p2, d):
        self.p1 = p1
        self.p2 = p2
        self.d = d

        self.equations = [
            Eqn(name, lambda y1, y2, d: cstr.distance_1D([y1, y2], d), [p1.y, p2.y, d])
        ]


class LineLength(Constraint):
    def __init__(self, name, L, d):
        self.L = L
        self.d = d

        self.equations = [
            Eqn(
                name,
                lambda Lx1, Ly1, Lx2, Ly2, d: cstr.line_length([Lx1, Ly1, Lx2, Ly2], d),
                [L.p1.x, L.p1.y, L.p2.x, L.p2.y, d],
            )
        ]


class AnglePoint3(Constraint):
    def __init__(self, name, p1, p2, p3, a):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.a = a

        self.equations = [
            Eqn(
                name,
                lambda x1, y1, x2, y2, x3, y3, a: cstr.angle_point3(
                    [x1, y1, x2, y2, x3, y3], a
                ),
                [p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, a],
            )
        ]


class TangentLineCircle(Constraint):
    def __init__(self, name, L, C):
        self.L = L
        self.C = C

        self.equations = [
            Eqn(
                name,
                lambda Lx1, Ly1, Lx2, Ly2, cx, cy, cr: cstr.tangent_line_circle(
                    [Lx1, Ly1, Lx2, Ly2, cx, cy], cr
                ),
                [L.p1.x, L.p1.y, L.p2.x, L.p2.y, C.p.x, C.p.y, C.r],
            )
        ]


class PointOnCircle(Constraint):
    def __init__(self, name, p, C):
        self.p = p
        self.C = C

        self.equations = [
            Eqn(
                name,
                lambda x, y, cx, cy, cr: cstr.point_on_circle([x, y, cx, cy], cr),
                [p.x, p.y, C.p.x, C.p.y, C.r],
            )
        ]


class GroundPoint(Constraint):
    # note: untested
    def __init__(self, name, p):
        self.p = p
        self.gx = p.x.val
        self.gy = p.y.val

        self.equations = [
            Eqn(name, lambda x: x - self.gx, [p.x]),
            Eqn(name, lambda y: y - self.gy, [p.y]),
        ]


class CoincidentPoint2(Constraint):
    def __init__(self, name, p1, p2):
        self.p1 = p1
        self.p2 = p2

        self.equations = [
            Eqn(name + ".x", lambda x1, x2: cstr.set_val([x1], x2), [p1.x, p2.x]),
            Eqn(name + ".y", lambda y1, y2: cstr.set_val([y1], y2), [p1.y, p2.y]),
        ]
