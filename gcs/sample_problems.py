from math import pi

from . import geom2d as g2d

#----------------------------------------------------------
# Sample Problem
#----------------------------------------------------------

def problem2():
    r0 = 1.5
    d = 3.0
    a = pi/6.0
    d_x = 3.0 # TODO: these 2 should correspond to eqn/var (f8/f9)
    d_y = 1.0


    p0 = g2d.Point('p0', 0.0, 0.0)
    p1 = g2d.Point('p1', 1.0, 1.0)
    p2 = g2d.Point('p2', 2.0, 2.0)
    p3 = g2d.Point('p3', 3.0, 3.0)
    c1 = g2d.Circle('c1', 0.0, 0.0, 1.0)
    L1 = g2d.Line_Segment('L1', 1.0, 1.0, 3.0, 3.0)

    geometry = (p0, p1, p2, p3, c1, L1)
    

    d1 = g2d.Var('d1', 1.0)
    a1 = g2d.Var('a1', pi/4.0)
    dx = g2d.Var('dx', 2.0)
    dy = g2d.Var('dy', 1.0)

    variables = (d1, a1, dx, dy)
    

    f1  = g2d.SetVar('f1', p0.x, 0.0)
    f2  = g2d.SetVar('f2', p0.y, 0.0)
    f3  = g2d.SetVar('f3', c1.r, r0)
    f4  = g2d.SetVar('f4', d1, d)
    f5  = g2d.SetVar('f5', a1, a)
    f67 = g2d.CoincidentPoint2('f67', p0, c1.p)
    f8  = g2d.HorzDist('f8', p0, p1, dx)
    f9  = g2d.VertDist('f9', p0, p1, dy)
    f10 = g2d.AnglePoint3('f10', p1, p3, p2, a1)
    f11 = g2d.TangentLineCircle('f11', L1, c1)
    f12 = g2d.PointOnCircle('f12', p3, c1)
    f1314 = g2d.CoincidentPoint2('f1314', L1.p1, p3)
    f15 = g2d.LineLength('f15', L1, d1)
    f1617 = g2d.CoincidentPoint2('f1617', L1.p2, p2)
    f18 = g2d.SetVar('f18', dx, d_x)
    f19 = g2d.SetVar('f19', dy, d_y)

    constraints = (f1, f2, f3, f4, f5, f67, f8, f9, f10, f11, f12, f1314, f15, f1617, f18, f19)

    all_vars = set(variables)
    for g in geometry:
        all_vars |= set(g.vars)
    
    return geometry, variables, constraints, all_vars