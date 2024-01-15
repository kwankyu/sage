r"""
Sheaf on subschemes of projective spaces


EXAMPLES::

We define the Fermat cubic surface in P^3::

    sage: P3 = ProjectiveSpace(QQ, 3, 'x')
    sage: P3.inject_variables()
    Defining x0, x1, x2, x3
    sage: X = P3.subscheme(x0^3+x1^3+x2^3+x3^3)
    sage: X
    Closed subscheme of Projective Space of dimension 3 over Rational Field defined by:
      x0^3 + x1^3 + x2^3 + x3^3

"""

from sage.structure.sage_object import SageObject

class Sheaf(SageObject):
    def __init__(self, X, module):
        self._base_scheme = X
        self._module = module

    def _repr_(self):
        return f'Sheaf on {self._base_scheme}'

    def base_scheme(self):
        return self._base_scheme

    def cohomology(self, r):
        pass

    def image_to_ambient_sapce(self):
        """
        Return the direct image of this sheaf to the ambient space.

        The image is with respect to the inclusion morphism from the base
        scheme into the projective Space.
        """
        X = self._base_scheme
        A = X.ambient_space()
        S = A.coordinate_ring()
        M = self._module.change_ring(S)
        return A.coherent_sheaf(M)

