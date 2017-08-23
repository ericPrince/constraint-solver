'''

constraints - definitions of common geometric constraints

TODO: keep abs() or should sign of parameters matter?

'''

from __future__ import division, print_function

from math import hypot, atan2, pi

#--------------------------------------------------------------------
# basic

def distance(x, d):
    (x1, y1, x2, y2) = x

    return hypot(x2 - x1, y2 - y1) - d

def horz_dist(x, dx):
    return abs(x[1] - x[0]) - dx

def vert_dist(x, dy):
    return abs(x[1] - x[0]) - dy

# def offset_line_point(x, d):
#     # 3rd point is the point
#     # TODO: be careful about sign of d!!

#     (x1, y1, x2, y2, x3, y3) = x

#     dL = hypot(x2 - x1, y2 - y1)

#     # note: swapped d portion to be perp of line
#     return ( dL * (y3 - y1) + d * (x2 - x1) ) * (x2 - x1) \
#          - ( dL * (x3 - x1) - d * (y2 - y1) ) * (y2 - y1)

def offset_line_point(x, d):
    # 3rd point is the point
    # TODO: be careful about sign of d!!

    (x1, y1, x2, y2, x3, y3) = x

    dL = hypot(x2 - x1, y2 - y1)

    # note: swapped d portion to be perp of line
    return min(
           ( dL * (y3 - y1) + d * (x2 - x1) ) * (x2 - x1)
         - ( dL * (x3 - x1) - d * (y2 - y1) ) * (y2 - y1), 

           ( dL * (y3 - y1) - d * (x2 - x1) ) * (x2 - x1)
         - ( dL * (x3 - x1) + d * (y2 - y1) ) * (y2 - y1)
    )

def angle_point4(x, a):
    (x1, y1, x2, y2, x3, y3, x4, y4) = x

    return abs( atan2(x4 - x3, y4 - y3) - atan2(x2 - x1, y2 - y1) ) - a

def angle_point3(x, a):
    # 2nd point is the base of the angle

    (x1, y1, x2, y2, x3, y3) = x

    return abs( atan2(x3 - x2, y3 - y2) - atan2(x1 - x2, y1 - y2) ) - a

def angle_point2(x, a):
    (x1, y1, x2, y2) = x

    return abs( atan2(x1 - x2, y1 - y2) ) - a

def point_on_line(x, p=None):
    # 3rd point is the point

    (x1, y1, x2, y2, x3, y3) = x

    return (y3 - y1) * (x2 - x1) \
         - (x3 - x1) * (y2 - y1)


#--------------------------------------------------------------------
# non-basic

def point_on_circle(x, r):
    return distance(x, r)

def tangent_line_circle(x, r):
    # 3rd point is circle center

    return offset_line_point(x, r)

def set_val(x, v):
    return x[0] - v

def line_length(x, d):
    return distance(x, d)

#--------------------------------------------------------------------
#--------------------------------------------------------------------

def main():
#    import numpy as np
    import scipy.optimize as opt
    import matplotlib.pyplot as plt
    
    # x_list = np.zeros(4)
    # y_list = np.zeros(4)
    # r_list = np.zeros(1)

    def apply_constraints(X):
        (x0, x1, x2, x3, x4, 
         y0, y1, y2, y3, y4, 
         r0)                 = X

        Y = (
            set_val((x4,), 0), 
            set_val((y4,), 0), 
            horz_dist((x0, x4), 0),
            vert_dist((y0, y4), 0), 
            horz_dist((x1, x4), 3), 
            vert_dist((y1, y4), 1), 
            angle_point3((x1, y1, x3, y3, x2, y2), pi/6), 
            set_val((r0,), 1.5), 
            tangent_line_circle((x3, y3, x2, y2, x0, y0), r0), 
            point_on_circle((x3, y3, x0, y0), r0), 
            line_length((x3, y3, x2, y2), 5)
        )

        return Y

    # WOW: initial condition is SO important for convergence!!
    # X0 = np.zeros(11)
    # X0 = (
    #     0, 3.5, 5, 1, 0, 
    #     0, 0.6, 5, 1, 0, 
    #     1.5
    # )
    X0 = (
        0, 3.5, 5, 0, 0, 
        0, 0.6, 2, 2, 0, 
        1.5
    )

    sol = opt.root(apply_constraints, X0, args=(), method='hybr')

    XF = sol.x

    (x0, x1, x2, x3, x4, 
     y0, y1, y2, y3, y4, 
     r0)                 = XF

    print(XF)
    # print(sol)

    plt.figure()

    plt.scatter(x=(x0, x1, x2, x3, x4), y=(y0, y1, y2, y3, y4))
    L1 = plt.Line2D(xdata=(x3, x2), ydata=(y3, y2))
    C1 = plt.Circle((x0, y0), r0, fill=None)

    plt.gca().add_artist(L1)
    plt.gca().add_artist(C1)

    plt.axis('equal')

    plt.show()


if __name__ == '__main__':
    main()