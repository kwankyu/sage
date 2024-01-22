r"""
Coherent sheaves

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

AUTHORS:

- Kwankyu Lee (2024-01-22): initial version

"""

from functools import cached_property
from sage.structure.sage_object import SageObject

class Sheaf(SageObject):

    def __init__(self, scheme, module, twist=0):
        try:
            if module.is_ambient():
                module = module.quotient(module.zero_submodule())
        except AttributeError:
            pass

        self._base_scheme = scheme
        self._module = module
        self._twist = twist

    @cached_property
    def _cohomology(self):
         raise NotImplementedError('_cohomology is not implemented')

    def _repr_(self):
        if self._twist != 0:
            obj = 'Twisted Sheaf'
        else:
            obj = 'Sheaf'
        return f'{obj} on {self._base_scheme}'

    def base_scheme(self):
        return self._base_scheme

    def twist(self):
        return self._twist

    def defining_module(self):
        return self._module

    def cohomology(self, r=0):
        """
        EXAMPLES::

            sage: P3 = ProjectiveSpace(QQ, 3, 'x')
            sage: P3.inject_variables()
            sage: X = P3.subscheme(x0^3+x1^3+x2^3+x3^3)
            sage: sheaf = X.structure_sheaf().image_to_ambient_space()
            sage: sheaf.cohomology()
        """
        return self._cohomology.h(r)

