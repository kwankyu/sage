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
    r"""
    Coherent sheaf on a projective scheme.

    INPUT:

    - ``scheme`` -- the base scheme on which the sheaf is defined

    - ``module`` -- a free module or its quotient by a submodule

    - ``twist`` -- (default: 0) an integer

    This class constructs the coherent sheaf `\tilde M(n)` if `M` is the
    ``module`` and `n` is the ``twist``.
    """
    def __init__(self, scheme, module, twist=0):
        """
        Initialize ``self``.
        """
        try:
            if module.is_ambient():
                module = module.quotient(module.zero_submodule())
        except AttributeError:
            pass

        assert module.cover() == module.free_cover()

        self._base_scheme = scheme
        self._module = module
        self._twist = twist

    @cached_property
    def _cohomology(self):
        """
        Return an object that computes the cohomology.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme(x^4 + y^4 + z^4)
            sage: sheaf = X.structure_sheaf()
            sage: c = sheaf._cohomology
            sage: c.H(1).dimension()
            3
            sage: c.h(1)
            3
        """
        raise NotImplementedError('_cohomology is not implemented')

    def _repr_(self):
        sheaf = 'Twisted Sheaf' if self._twist else 'Sheaf'
        return f'{sheaf} on {self._base_scheme}'

    def base_scheme(self):
        """
        Return the base scheme on which this sheaf is defined.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme(x^4 + y^4 + z^4)
            sage: s = X.structure_sheaf()
            sage: s.base_scheme()
            Closed subscheme of Projective Space of dimension 2 over Rational Field defined by:
              x^4 + y^4 + z^4
        """
        return self._base_scheme

    def defining_twist(self):
        """
        Return the integer by which the module defining this coherent sheaf is
        twisted.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme(x^4 + y^4 + z^4)
            sage: s = X.structure_sheaf(3)
            sage: s.defining_twist()
            3
        """
        return self._twist

    def defining_module(self):
        """
        Return the module defining this coherent sheaf.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme(x^4 + y^4 + z^4)
            sage: X.structure_sheaf()
            Sheaf on Closed subscheme of Projective Space of dimension 2 over
            Rational Field defined by: x^4 + y^4 + z^4
        """
        return self._module

    def cohomology_group(self, r=0):
        """
        Return the `r`-th cohomology as a vector space.

        INPUT:

        - ``r`` -- (default: 0) a non-negative integer

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme(x^4 + y^4 + z^4)
            sage: s = X.structure_sheaf()
            sage: s.cohomology_group(1).dimension()
            3
        """
        return self._cohomology.H(r)

    def cohomology(self, r=0):
        """
        Return the dimension of the `r`-th cohomology as a vector space.

        INPUT:

        - ``r`` -- (default: 0) a non-negative integer

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme(x^4 + y^4 + z^4)
            sage: sheaf = X.structure_sheaf()
            sage: s.cohomology(0)
            1
            sage: s.cohomology(1)
            3
            sage: s.cohomology(2)
            0
        """
        return self._cohomology.h(r)


