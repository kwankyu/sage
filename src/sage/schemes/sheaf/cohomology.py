
from sage.misc.flatten import flatten
from sage.combinat.integer_lists.invlex import IntegerListsLex


class Module:
    """
    Top cohomology module of the twisted structure sheaf of a projective space.
    """
    def __init__(self, S, m):
        self._graded_ring = S
        self._twist = m

        n = S.ngens()

        basis = []
        summands_basis = []
        for m in self._twist:
            # list of integer vectors whose entries are all negative integers and sum to -m
            l = [-vector(e) for e in IntegerListsLex(length=n, min_sum=m, max_sum=m, min_part=1)]
            basis += l
            summands_basis.append(l)

        self._summands_basis = summands_basis
        self._basis = basis
        self._vector_space = VectorSpace(S.base_ring(), len(self._basis))

    def _repr_(self):
        return 'H^r(O_{P_r}()'


class Complex:
    def __init__(self, resolution):
        self._resolution = resolution
        self._base_ring = resolution.target().base_ring()

    def module(self, i):
        S = self._base_ring
        m = self._resolution.shifts(i)
        return Module(self_base_ring, m)



