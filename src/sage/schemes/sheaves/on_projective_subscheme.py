r"""
Coherent sheaves on projective subschemes

EXAMPLES::

    sage: P3.<x,y,z,w> = ProjectiveSpace(QQ, 3)
    sage: X = P3.subscheme([y*w - z^2, -x*w + y*z, x*z - y^2])
    sage: X
    Closed subscheme of Projective Space of dimension 3 over Rational Field defined by:
      -z^2 + y*w,
      y*z - x*w,
      -y^2 + x*z

"""

from sage.schemes.sheaves.sheaf import Sheaf as _

class Sheaf(_):

    def __init__(self, scheme, module, twist=0):
        super().__init__(scheme, module, twist)
        self._cohomology = self.image_to_ambient_space()._cohomology

    def image_to_ambient_space(self):
        """
        Return the direct image of this sheaf to the ambient space.

        The image is with respect to the inclusion morphism from the base
        scheme into the projective Space.
        """
        X = self._base_scheme
        A = X.ambient_space()
        S = A.coordinate_ring()
        M = self._module.change_ring(S)
        return A.coherent_sheaf(M, twist=self._twist)

