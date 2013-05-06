"""Transformation Classes."""

import math

from core.geometry import Vector
from core.geometry import normalize, cross


class Matrix4x4(object):

    """Class describing a 4x4 transformation matrix."""

    def __init__(self,
                 t00=1.0, t01=0.0, t02=0.0, t03=0.0,
                 t10=0.0, t11=1.0, t12=0.0, t13=0.0,
                 t20=0.0, t21=0.0, t22=1.0, t23=0.0,
                 t30=0.0, t31=0.0, t32=0.0, t33=1.0,):
        """Default constructor for Matrix4x4."""
        self.m = [[t00, t01, t02, t03],
                  [t10, t11, t12, t13],
                  [t20, t21, t22, t23],
                  [t30, t31, t32, t33]]

    def __eq__(self, m2):
        """Overload the comparison operator."""
        for i in range(4):
            for j in range(4):
                if self.m[i][j] != m2.m[i][j]:
                    return False
        return True

    def __ne__(self, m2):
        """Overload the comparison operator."""
        for i in range(4):
            for j in range(4):
                if self.m[i][j] != m2.m[i][j]:
                    return True
        return False

    def __str__(self):
        """Return a string describing the matrix."""
        return "Matrix4x4 (%s)" % str(self.m)


def transpose(m):
    """Return the transpose of m."""
    return Matrix4x4(m.m[0][0], m.m[1][0], m.m[2][0], m.m[3][0],
                     m.m[0][1], m.m[1][1], m.m[2][1], m.m[3][1],
                     m.m[0][2], m.m[1][2], m.m[2][2], m.m[3][2],
                     m.m[0][3], m.m[1][3], m.m[2][3], m.m[3][3])

class Transform(object):

    """Class describing a 3D transformation."""

    def __init__(self, matrix=None, matrix_inverse=None):
        """Default constructor for Transform."""
        if matrix is None:
            self.m = Matrix4x4()
            self.m_inv = Matrix4x4()
        else:
            self.m = matrix
            if matrix_inverse is None:
                self.m_inv = inverse(self.m)
            else:
                self.m_inv = matrix_inverse
    
    def inverse(self):
        """Return the inverse of the transform."""
        return Transform(self.m_inv, self.m)
        
    def is_identity(self):
        """Return True if it is the identity transform."""
        return self.m == Matrix4x4()

    def has_scale(self):
        """Return True if the transform has a scaling term."""
        la2 = self(Vector(1, 0, 0)).length_squared()
        lb2 = self(Vector(0, 1, 0)).length_squared()
        lc2 = self(Vector(0, 0, 1)).length_squared()
        not_one = lambda x: x<0.999 or x>1.001
        return not_one(la2) or not_one(lb2) or not_one(lc2)
    
    def __eq__(self, t):
        """Overload the comparison operator."""
        return self.m == t.m and self.m_inv == t.m_inv
    
    def __ne__(self, t):
        """Overload the comparison operator."""
        return self.m != t.m or self.m_inv != t.m_inv
    
    def __str__(self):
        """Return a string describing the transform."""
        return "Transform (m='%s', m_inv='%s')" % (str(self.m), str(self.m_inv))


def translate(delta):
    """Construct a Transform representing the translation by delta."""
    m = Matrix4x4(1.0, 0.0, 0.0, delta.x,
                  0.0, 1.0, 0.0, delta.y,
                  0.0, 0.0, 1.0, delta.z,
                  0.0, 0.0, 0.0, 1.0)
    m_inv = Matrix4x4(1.0, 0.0, 0.0, -delta.x,
                      0.0, 1.0, 0.0, -delta.y,
                      0.0, 0.0, 1.0, -delta.z,
                      0.0, 0.0, 0.0, 1.0)
    return Transform(m, m_inv)


def scale(x, y, z):
    """Construct a Transform representing a scale by (x, y, z)."""
    m = Matrix4x4(  x, 0.0, 0.0, 0.0,
                  0.0,   y, 0.0, 0.0,
                  0.0, 0.0,   z, 0.0,
                  0.0, 0.0, 0.0, 1.0)
    m_inv = Matrix4x4( 1.0/x, 0.0,   0.0,   0.0,
                       0.0,   1.0/y, 0.0,   0.0,
                       0.0,   0.0,   1.0/z, 0.0,
                       0.0,   0.0,   0.0,   1.0)
    return Transform(m, m_inv)


def rotate_x(angle):
    """Construct a Transform representing a rotation around x axis."""
    sin_t = math.sin(math.radians(angle))
    cos_t = math.cos(math.radians(angle))
    m = Matrix4x4(1.0, 0.0,      0.0, 0.0,
                  0.0, cos_t, -sin_t, 0.0,
                  0.0, sin_t,  cos_t, 0.0,
                  0.0, 0.0,      0.0, 1.0)
    return Transform(m, transpose(m))


def rotate_y(angle):
    """Construct a Transform representing a rotation around y axis."""
    sin_t = math.sin(math.radians(angle))
    cos_t = math.cos(math.radians(angle))
    m = Matrix4x4(cos_t,  0.0, sin_t, 0.0,
                  0.0,    1.0,   0.0, 0.0,
                  -sin_t, 0.0, cos_t, 0.0,
                  0.0,    0.0,   0.0, 1.0)
    return Transform(m, transpose(m))


def rotate_z(angle):
    """Construct a Transform representing a rotation around z axis."""
    sin_t = math.sin(math.radians(angle))
    cos_t = math.cos(math.radians(angle))
    m = Matrix4x4(cos_t, -sin_t, 0.0, 0.0,
                  sin_t,  cos_t, 0.0, 0.0,
                    0.0,    0.0, 1.0, 0.0,
                    0.0,    0.0, 0.0, 1.0)
    return Transform(m, transpose(m))


def rotate(angle, axis):
    """Construct a Transform representing a rotation around the specified axis."""
    a = normalize(axis)
    sin_t = math.sin(math.radians(angle))
    cos_t = math.cos(math.radians(angle))
    mat = Matrix4x4(a.x * a.x + (1.0 - a.x * a.x) * cos_t,
                    a.x * a.y * (1.0 - cos_t) - a.z * sin_t,
                    a.x * a.z * (1.0 - cos_t) + a.y * sin_t,
                    0.0,
                    a.x * a.y * (1.0 - cos_t) + a.z * sin_t,
                    a.y * a.y + (1.0 - a.y * a.y) * cos_t,
                    a.y * a.z * (1.0 - cos_t) - a.x * sin_t,
                    0.0,
                    a.x * a.z * (1.0 - cos_t) - a.y * sin_t,
                    a.y * a.z * (1.0 - cos_t) + a.x * sin_t,
                    a.z * a.z + (1.0 - a.z * a.z) * cos_t,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0)
    return Transform(mat, transpose(mat))


def look_at(pos, look, up):
    """Construct a Transform corresponding to a viewpoint in world space."""
    cam_to_world = Matrix4x4()
    
    # initialize fourth column of the viewing matrix
    cam_to_world.m[0][3] = pos.x
    cam_to_world.m[1][3] = pos.y
    cam_to_world.m[2][3] = pos.z
    cam_to_world.m[3][3] = 1.0

    # construct the base
    dir = normalize(look-pos)
    left = normalize(cross(normalize(up), dir))
    new_up = cross(dir, left)
    
    # fill the other columns
    cam_to_world.m[0][0] = left.x
    cam_to_world.m[1][0] = left.y
    cam_to_world.m[2][0] = left.z
    cam_to_world.m[3][0] = 0.0
    cam_to_world.m[0][1] = new_up.x
    cam_to_world.m[1][1] = new_up.y
    cam_to_world.m[2][1] = new_up.z
    cam_to_world.m[3][1] = 0.0
    cam_to_world.m[0][2] = dir.x
    cam_to_world.m[1][2] = dir.y
    cam_to_world.m[2][2] = dir.z
    cam_to_world.m[3][2] = 0.0

    return Transform(inverse(cam_to_world), cam_to_world)


def inverse(m):
    """Return the inverse of matrix m."""
    # dummy implementation for now
    return m

