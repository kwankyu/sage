r"""
Sheaf on projective space


EXAMPLES::

We define the Fermat cubic surface in P^3::

    sage: P3 = ProjectiveSpace(QQ, 3, 'x')
    sage: P3.inject_variables()
    Defining x0, x1, x2, x3
    sage: X = P3.subscheme(x0^3+x1^3+x2^3+x3^3)
    sage: X
    Closed subscheme of Projective Space of dimension 3 over Rational Field defined by:
      x0^3 + x1^3 + x2^3 + x3^3

    sage: P3.<x,y,z,w> = ProjectiveSpace(QQ, 3)
    sage: X = P3.subscheme([y*w - z^2, -x*w + y*z, x*z - y^2])
    sage: X
    Closed subscheme of Projective Space of dimension 3 over Rational Field defined by:
      -z^2 + y*w,
      y*z - x*w,
      -y^2 + x*z

"""

from sage.structure.sage_object import SageObject

class Sheaf(SageObject):

    def __init__(self, base, module):
        self._base = base
        self._module = module

    def _repr_(self):
        return f'Sheaf on {self._base}'

    def base_scheme(self):
        return self._base

    def cohomology(self, r=0):
        """
        EXAMPLES::

            sage: P3 = ProjectiveSpace(QQ, 3, 'x')
            sage: P3.inject_variables()
            sage: X = P3.subscheme(x0^3+x1^3+x2^3+x3^3)
            sage: sheaf = X.structure_sheaf().image_to_ambient_sapce()
            sage: sheaf.cohomology()
        """
        from sage.schemes.sheaf.cohomology import Complex
        M = self._module
        I = M.relations()
        c = Complex(I.graded_free_resolution())
        return c


