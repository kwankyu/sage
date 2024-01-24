r"""
Cohomology of coherent sheaves

This modules implements Maruyama's method for computing cohomology of coherent
sheaves on a projective space.

Let `M` be a module finitely generated over the coordinate ring `S` of the
projective `r`-space over a field `k`. Let `S=k[x_0,x_2,\dots,x_r]`. Then `M`
is a quotient of the free module `\bigoplus_{i=1}^{t}S` by a submodule. Let

.. MATH::

    0\to\bigoplus_{j=1}^{t_{r+1}}S(-m^{(r+1)}_j)\overset{f_{r+1}}{\longrightarrow}\dots
    \overset{f_1}{\longrightarrow}\bigoplus_{j=1}^{t_0}S(-m^{(0)}_j)\overset{f_0}{\longrightarrow}M\to 0

be a minimal free resolution of `M`. Then it induces a complex of (top) homology groups

.. MATH::

    \bigoplus_{j=1}^{t_{i+1}}H^r(\OO_{\PP^r}(-m^{(i+1)}_j))\overset{H^r(f_{i+1})}{\longrightarrow}
    \bigoplus_{j=1}^{t_i}H^r(\OO_{\PP^r}(-m^{(i)}_j))\overset{H^r(f_{i})}{\longrightarrow}
    \bigoplus_{j=1}^{t_{i-1}}H^r(\OO_{\PP^r}(-m^{(i-1)}_j))

where `i` runs from `1` to `r`. Now it holds that

.. MATH::

    H^q(\tilde M)\cong \ker H^r(f_{r-q})/\im H^r(f_{r-q+1})

for `1\le q\le r - 1` and

.. MATH::

    H^r(\tilde M)\cong \bigoplus_{j=1}^{t_0}H^r(\OO_{\PP^r}(-m^{(0)}_j))/\im H^r(f_1)

and `\dim H^0(\tilde M)` can be computed by the formula

.. MATH::

    \begin{split}
    &\dim \bigoplus_{j=1}^{t_{0}}H^0(\OO_{\PP^r}(-m^{(0)}_j))
    -\dim \bigoplus_{j=1}^{t_{r+1}}H^r(\OO_{\PP^r}(-m^{(r+1)}_j))
    +\dim \bigoplus_{j=1}^{t_{r}}H^r(\OO_{\PP^r}(-m^{(r)}_j)) \\
    &\quad -\rank H^0(f_1)-\rank H^r(f_r)
    \end{split}

in which the complex of (bottom) homology groups

.. MATH::

    \bigoplus_{j=1}^{t_{i+1}}H^0(\OO_{\PP^r}(-m^{(i+1)}_j))\overset{H^0(f_{i+1})}{\longrightarrow}
    \bigoplus_{j=1}^{t_i}H^0(\OO_{\PP^r}(-m^{(i)}_j))\overset{H^0(f_{i})}{\longrightarrow}
    \bigoplus_{j=1}^{t_{i-1}}H^0(\OO_{\PP^r}(-m^{(i-1)}_j))

is used.

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


class HomologyGroupBottom:
    """
    Top cohomology group of the twisted structure sheaf of a projective space.
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


class HomologyGroupTop:
    """
    Top cohomology group of the twisted structure sheaf of a projective space.
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


class MaruyamaComplex:
    def __init__(self, M, twist=0):
        shifts = [-twist for i in range(M.cover().degree())]
        self.resolution = M.relations().graded_free_resolution(shifts=shifts)
        self.base_ring = self.resolution.target().base_ring()
        self.coefficient_field = self.base_ring.base_ring()
        self.projective_space_dimension = self.base_ring.ngens() - 1

    def __repr__(self):
        return 'Maruyama Complex'

    def homology_group_bottom(self, i):
        S = self.base_ring
        shifts = self.resolution.shifts(i)
        return HomologyGroupBottom(S, shifts)

    def homology_group_top(self, i):
        S = self.base_ring
        shifts = self.resolution.shifts(i)
        return HomologyGroupTop(S, shifts)

    def differential_bottom(self, t):
        """
        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: sh = X.structure_sheaf().image_to_ambient_space()
            sage: c = sh.cohomology()
        """
        H1 = self.homology_group_bottom(t)
        H0 = self.homology_group_bottom(t - 1)
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
        H1 = self.homology_group_top(t)
        H0 = self.homology_group_top(t - 1)
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
            return self.homology_group_top(0).vector_space.quotient(self.differential_top(1).image())
        if 1 <= t and t < r:
            return self.differential_top(r - t).kernel().quotient(self.differential_top(r - t + 1).image())
        if t == 0:
            raise ValueError('not implemented')

    def h(self, t):
        r = self.projective_space_dimension
        if t == 0:
            a = self.homology_group_bottom(0).rank - self.homology_group_top(r + 1).rank + self.homology_group_top(r).rank
            b = self.differential_bottom(1).rank() + self.differential_top(r).rank()
            return a - b
        return self.H(t).dimension()

