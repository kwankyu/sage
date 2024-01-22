"""
Cohomology of coherent sheaves

EXAMPLES:

We define the Fermat cubic surface in `P^3`::

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

    sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
    sage: X = P2.subscheme([x^4 + y^4 + z^4])
    sage: sh = X.structure_sheaf().image_to_ambient_space()
"""

from sage.misc.flatten import flatten
from sage.combinat.integer_lists.invlex import IntegerListsLex
from sage.modules.free_module import VectorSpace
from sage.modules.free_module_element import vector


class HomologySpaceBottom:
    """
    Top cohomology module of the twisted structure sheaf of a projective space.
    """
    def __init__(self, S, shifts):
        self.graded_ring = S
        self.shifts = shifts

        n = S.ngens()

        basis = []
        summands_basis = []
        summands_index = []
        rank = 0
        for m in self.shifts:
            # list of integer vectors whose entries are all non-negative integers and sum to -m
            l = [vector(e) for e in IntegerListsLex(length=n, min_sum=-m, max_sum=-m)]
            basis += l
            summands_basis.append(l)
            summands_index.append(rank)
            rank += len(l)

        self.summands_basis = summands_basis
        self.summands_index = summands_index
        self.basis = basis
        self.vector_space = VectorSpace(S.base_ring(), rank)
        self.rank = rank

    def __repr__(self):
        return 'H^r(O_{P_r}()'

class HomologySpaceTop:
    """
    Top cohomology module of the twisted structure sheaf of a projective space.
    """
    def __init__(self, S, shifts):
        self.graded_ring = S
        self.shifts = shifts

        n = S.ngens()

        basis = []
        summands_basis = []
        summands_index = []
        rank = 0
        for m in self.shifts:
            # list of integer vectors whose entries are all negative integers and sum to -m
            l = [-vector(e) for e in IntegerListsLex(length=n, min_sum=m, max_sum=m, min_part=1)]
            basis += l
            summands_basis.append(l)
            summands_index.append(rank)
            rank += len(l)

        self.summands_basis = summands_basis
        self.summands_index = summands_index
        self.basis = basis
        self.vector_space = VectorSpace(S.base_ring(), rank)
        self.rank = rank

    def __repr__(self):
        return 'H^r(O_{P_r}()'


class Complex:
    def __init__(self, M, twist=0):
        shifts = [-twist for i in range(M.cover().degree())]
        self.resolution = M.relations().graded_free_resolution(shifts=shifts)
        self.base_ring = self.resolution.target().base_ring()
        self.coefficient_field = self.base_ring.base_ring()
        self.projective_space_dimension = self.base_ring.ngens() - 1

    def __repr__(self):
        return 'Complex'

    def homology_space_bottom(self, i):
        S = self.base_ring
        shifts = self.resolution.shifts(i)
        return HomologySpaceBottom(S, shifts)

    def homology_space_top(self, i):
        S = self.base_ring
        shifts = self.resolution.shifts(i)
        return HomologySpaceTop(S, shifts)

    def differential_bottom(self, t):
        """
        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: sh = X.structure_sheaf().image_to_ambient_space()
            sage: c = sh.cohomology()
        """
        H1 = self.homology_space_bottom(t)
        H0 = self.homology_space_bottom(t - 1)
        M = self.resolution.differential(t).matrix()
        K = self.coefficient_field
        zero = K.zero()

        assert M.ncols() == len(H1.summands_basis)
        assert M.nrows() == len(H0.summands_basis)

        A = []
        for i in range(M.ncols()):
            basis = H1.summands_basis[i]
            for v in basis:
                image = [zero for e in range(H0.rank)]
                for j in range(M.nrows()):
                    f = M[i,j]
                    basis = H0.summands_basis[j]
                    for c, m in zip(f.coefficients(), f.exponents()):
                        u = v + vector(m)
                        assert(sum(u) == -H0.shifts[j])
                        if any(e < 0 for e in u):
                            continue
                        k = H0.summands_index[j] + basis.index(u)
                        image[k] += c
                A.append(vector(K, image))

        return H1.vector_space.hom(A, codomain=H0.vector_space, side='right')

    def differential_top(self, t):
        """
        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: sh = X.structure_sheaf().image_to_ambient_space()
            sage: c = sh.cohomology()
        """
        H1 = self.homology_space_top(t)
        H0 = self.homology_space_top(t - 1)
        M = self.resolution.differential(t).matrix()
        K = self.coefficient_field
        zero = K.zero()

        assert M.ncols() == len(H1.summands_basis)
        assert M.nrows() == len(H0.summands_basis)

        A = []
        for i in range(M.ncols()):
            basis = H1.summands_basis[i]
            for v in basis:
                image = [zero for e in range(H0.rank)]
                for j in range(M.nrows()):
                    f = M[i,j]
                    basis = H0.summands_basis[j]
                    for c, m in zip(f.coefficients(), f.exponents()):
                        u = v + vector(m)
                        assert(sum(u) == -H0.shifts[j])
                        if any(e >= 0 for e in u):
                            continue
                        k = H0.summands_index[j] + basis.index(u)
                        image[k] += c
                A.append(vector(K, image))

        return H1.vector_space.hom(A, codomain=H0.vector_space, side='right')

    def H(self, t):
        r = self.projective_space_dimension
        if t == r:
            return self.homology_space_top(0).vector_space.quotient(self.differential_top(1).image())
        if 1 <= t and t < r:
            return self.differential_top(r - t).kernel().quotient(self.differential_top(r - t + 1).image())
        if t == 0:
            raise ValueError('not implemented')

    def h(self, t):
        r = self.projective_space_dimension
        if t == 0:
            a = self.homology_space_bottom(0).rank + self.homology_space_top(r).rank - self.homology_space_top(r + 1).rank
            b = self.differential_bottom(1).rank() + self.differential_top(r).rank()
            return a - b
        return self.H(t).dimension()

