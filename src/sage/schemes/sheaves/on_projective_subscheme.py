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

from functools import cached_property
from sage.modules.free_module import FreeModule
from sage.schemes.sheaves.sheaf import Sheaf as _

class Sheaf(_):

    @cached_property
    def _cohomology(self):
        return self.image_to_ambient_space()._cohomology

    def image_to_ambient_space(self):
        """
        Return the direct image of this sheaf to the ambient space.

        The image is with respect to the inclusion morphism from the base
        scheme into the projective Space.

        INPUT:

        - ``twist`` -- (default: `0`) an integer

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme(x^4 + y^4 + z^4)
            sage: X.structure_sheaf()
            Sheaf on Closed subscheme of Projective Space of dimension 3 over
            Rational Field defined by: x0^3 + x1^3 + x2^3 + x3^3
        """
        X = self._base_scheme
        A = X.ambient_space()
        S = A.coordinate_ring()

        d = self._module.degree()
        M = FreeModule(S, d)
        I = X.defining_polynomials()
        J = self._module.relations().gens()
        G = [f * M.gen(i) for i in range(d) for f in I] + [v.change_ring(S) for v in J]
        N = M.submodule(G)
        return A.coherent_sheaf(M.quotient(N), twist=self._twist)

