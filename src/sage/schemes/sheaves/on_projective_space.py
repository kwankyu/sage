r"""
Coherent sheaves on projective spaces

EXAMPLES:

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

    sage: P3 = ProjectiveSpace(QQ, 3, 'x')
    sage: P3.inject_variables()
    sage: X = P3.subscheme(x0^3+x1^3+x2^3+x3^3)
    sage: sheaf = X.structure_sheaf().image_to_ambient_sapce()
    sage: sheaf.cohomology()
"""

from functools import cached_property
from sage.schemes.sheaves.sheaf import Sheaf as _

class Sheaf(_):

    @cached_property
    def _cohomology(self):
        from sage.schemes.sheaves.cohomology import MaruyamaComplex
        return MaruyamaComplex(self._module, twist=self._twist)




