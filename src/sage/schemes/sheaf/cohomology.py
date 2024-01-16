"""
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
    sage: sh = X.structure_sheaf().image_to_ambient_space()
"""

from sage.misc.flatten import flatten
from sage.combinat.integer_lists.invlex import IntegerListsLex
from sage.modules.free_module import VectorSpace

class Module:
    """
    Top cohomology module of the twisted structure sheaf of a projective space.
    """
    def __init__(self, S, shifts):
        self._graded_ring = S
        self._shifts = shifts

        n = S.ngens()

        basis = []
        summands_basis = []
        summands_index = []
        index = 0
        for m in self._shifts:
            # list of integer vectors whose entries are all negative integers and sum to -m
            l = [-vector(e) for e in IntegerListsLex(length=n, min_sum=m, max_sum=m, min_part=1)]
            basis += l
            summands_basis.append(l)
            summands_index.append(index)
            index += len(l)

        self._summands_basis = summands_basis
        self._summands_index = summands_index
        self._basis = basis
        self._vector_space = VectorSpace(S.base_ring(), len(self._basis))

    def __repr__(self):
        return 'H^r(O_{P_r}()'


class Complex:
    def __init__(self, resolution):
        self._resolution = resolution
        self._base_ring = resolution.target().base_ring()

    def __repr__(self):
        return 'Complex'

    def module(self, i):
        S = self._base_ring
        shifts = self._resolution.shifts(i)
        return Module(S, shifts)

    def differential(self, i):
        G1 = self.module(i)
        G0 = self.module(i - 1)




