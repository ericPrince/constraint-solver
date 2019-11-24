"""

constraints - definitions of common geometric constraints

TODO: add dependence on sign of parameter!!!!

"""

from __future__ import division

from math import hypot, atan2

# --------------------------------------------------------------------
# basic
# --------------------------------------------------------------------


def distance(x, d):
    (x1, y1, x2, y2) = x

    return hypot(x2 - x1, y2 - y1) - d


def set_val(x, v):
    return x[0] - v


def distance_1D(x, d):
    return abs(x[1] - x[0]) - d


def offset_line_point(x, d):
    (x1, y1, x2, y2, x3, y3) = x

    dL = hypot(x2 - x1, y2 - y1)

    # this should be signed for d?
    return (dL * (y3 - y1) + d * (x2 - x1)) * (x2 - x1) - (
        dL * (x3 - x1) - d * (y2 - y1)
    ) * (y2 - y1)


# def offset_line_point(x, d):
#    (x1, y1, x2, y2, x3, y3) = x # 3rd point is the point
#
#    dL = hypot(x2 - x1, y2 - y1)
#
#    # TODO: make this signed for d
#    return min(
#           ( dL * (y3 - y1) + d * (x2 - x1) ) * (x2 - x1)
#         - ( dL * (x3 - x1) - d * (y2 - y1) ) * (y2 - y1),
#
#           ( dL * (y3 - y1) - d * (x2 - x1) ) * (x2 - x1)
#         - ( dL * (x3 - x1) + d * (y2 - y1) ) * (y2 - y1) )

# TODO: make these signed?
def angle_point4(x, a):
    (x1, y1, x2, y2, x3, y3, x4, y4) = x

    return abs(atan2(x4 - x3, y4 - y3) - atan2(x2 - x1, y2 - y1)) - a


def angle_point3(x, a):
    (x1, y1, x2, y2, x3, y3) = x  # 2nd point is the base of the angle

    return abs(atan2(x3 - x2, y3 - y2) - atan2(x1 - x2, y1 - y2)) - a


def angle_point2(x, a):
    (x1, y1, x2, y2) = x

    # TODO: make this constraint signed?
    return abs(atan2(x1 - x2, y1 - y2)) - a


def point_on_line(x, p=None):
    (x1, y1, x2, y2, x3, y3) = x  # 3rd point is the point

    return (y3 - y1) * (x2 - x1) - (x3 - x1) * (y2 - y1)


# --------------------------------------------------------------------
# non-basic
# --------------------------------------------------------------------


def point_on_circle(x, r):
    return distance(x, r)


def tangent_line_circle(x, r):
    return offset_line_point(x, r)


def line_length(x, d):
    return distance(x, d)


# TODO: make this signed, but also cases for +- r1/r2
def tangent_circle_circle(x, r1, r2):
    return min(distance(x, r1 + r2), distance(x, r1 - r2))
