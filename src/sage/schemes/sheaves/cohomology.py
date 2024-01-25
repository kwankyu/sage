r"""
Cohomology of coherent sheaves

This module implements Maruyama's method for computing cohomology of coherent
sheaves on a projective space.

Let `M` be a graded module finitely generated over the homogeneous coordinate
ring `S` of the projective `r`-space over a field `k`. We aim for computing the
cohomology groups `H^q(\tilde M)` for the coherent sheaf `\tilde M`.

Let `S=k[x_0,x_2,\dots,x_r]`. Then `M` is a quotient of the free module
`\bigoplus_{i=1}^{t}S` by a submodule. Let

.. MATH::

    0\to\bigoplus_{j=1}^{t_{r+1}}S(-m^{(r+1)}_j)\overset{f_{r+1}}{\longrightarrow}\dots
    \overset{f_1}{\longrightarrow}\bigoplus_{j=1}^{t_0}S(-m^{(0)}_j)\overset{f_0}{\longrightarrow}M\to 0

be a minimal free resolution of `M`. Then it induces a complex of (top) cohomology groups

.. MATH::

    \bigoplus_{j=1}^{t_{i+1}}H^r(\OO_{\PP^r}(-m^{(i+1)}_j))\overset{H^r(f_{i+1})}{\longrightarrow}
    \bigoplus_{j=1}^{t_i}H^r(\OO_{\PP^r}(-m^{(i)}_j))\overset{H^r(f_{i})}{\longrightarrow}
    \bigoplus_{j=1}^{t_{i-1}}H^r(\OO_{\PP^r}(-m^{(i-1)}_j))

where `i` runs from `1` to `r`. Now it holds that

.. MATH::

    H^t(\tilde M)\cong \ker H^r(f_{r-t})/\im H^r(f_{r-t+1})

for `1\le t\le r - 1` and

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

in which the complex of (bottom) cohomology groups

.. MATH::

    \bigoplus_{j=1}^{t_{i+1}}H^0(\OO_{\PP^r}(-m^{(i+1)}_j))\overset{H^0(f_{i+1})}{\longrightarrow}
    \bigoplus_{j=1}^{t_i}H^0(\OO_{\PP^r}(-m^{(i)}_j))\overset{H^0(f_{i})}{\longrightarrow}
    \bigoplus_{j=1}^{t_{i-1}}H^0(\OO_{\PP^r}(-m^{(i-1)}_j))

where `i` runs from `1` to `r`, is used.

The implemented algorithm works for twisted coherent sheaf and accepts shifted
graded module `M(-n)` with shift `n`.

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


class CohomologyGroupBottom:
    r"""
    Bottom cohomology group of the twisted structure sheaf of a projective space.

    INPUT:

    - ``S`` -- a direct sum of copies of the coordinate ring of a projective space

    - ``shifts`` -- shifts of the component rings of ``S``

    This represents `\bigoplus_{j=1}^{t_i}H^0(\OO_{\PP^r}(-m^{(i)}_j))` for shifts `m^{(i)}_j`.

    EXAMPLES::

        sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
        sage: X = P2.subscheme([x^4 + y^4 + z^4])
        sage: c = X.structure_sheaf()._cohomology
        sage: c.cohomology_group_bottom(1)
        Bottom Cohomology Group of dimension 0
    """
    def __init__(self, S, shifts):
        """
        Initialize.
        """
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
        r"""
        Return the string representation.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: c = X.structure_sheaf()._cohomology
            sage: c.cohomology_group_bottom(0)
            Bottom Cohomology Group of dimension 1
        """
        return f'Bottom Cohomology Group of dimension {self.rank}'


class CohomologyGroupTop:
    r"""
    Top cohomology group of the twisted structure sheaf of a projective space.

    INPUT:

    - ``S`` -- a direct sum of copies of the coordinate ring of a projective space

    - ``shifts`` -- shifts of the component rings of ``S``

    This represents `\bigoplus_{j=1}^{t_i}H^r(\OO_{\PP^r}(-m^{(i)}_j))` for shifts `m^{(i)}_j`.

    EXAMPLES::

        sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
        sage: X = P2.subscheme([x^4 + y^4 + z^4])
        sage: c = X.structure_sheaf()._cohomology
        sage: c.cohomology_group_top(0)
        Top Cohomology Group of dimension 0
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
        r"""
        Return the string representation.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: c = X.structure_sheaf()._cohomology
            sage: c.cohomology_group_top(1)
            Top Cohomology Group of dimension 3
        """
        return f'Top Cohomology Group of dimension {self.rank}'


class MaruyamaComplex:
    r"""
    This class implements Maruyama's method to compute the cohomology group
    `H^q(\tilde M(n))` as a vector space over the base field `k` and
    `h^q(\tilde M(n))=\dim_kH^q(\tilde M(n))` where `n` denotes the twist.

    INPUT:

    - ``M`` -- a quotient of a free module over `S` by a submodule, where `S`
      is a multi-variate polynomial ring

    - ``twist`` -- (default: 0) an integer

    This class provides :meth:`H` and :meth:`h` as public interface, and all
    other methods are internal.

    EXAMPLES::

        sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
        sage: X = P2.subscheme([x^4 + y^4 + z^4])
        sage: sh = X.structure_sheaf(1)  # twisted sheaf
        sage: sh._cohomology
        Maruyama Complex defined by S(1) <-- S(-3) <-- 0
    """
    def __init__(self, M, twist=0):
        """
        Initialize.
        """
        shifts = [-twist for i in range(M.cover().degree())]
        self.resolution = M.relations().graded_free_resolution(shifts=shifts)
        self.base_ring = self.resolution.target().base_ring()
        self.coefficient_field = self.base_ring.base_ring()
        self.projective_space_dimension = self.base_ring.ngens() - 1

    def __repr__(self):
        """
        Return the string representation.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: X.structure_sheaf()._cohomology
            Maruyama Complex defined by S(0) <-- S(-4) <-- 0
        """
        return f'Maruyama Complex defined by {self.resolution}'

    def cohomology_group_bottom(self, i):
        r"""
        Return `i`-th bottom cohomology group `\bigoplus_{j=1}^{t_i}H^0(\OO_{\PP^r}(-m^{(i)}_j))`

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: c = X.structure_sheaf()._cohomology
            sage: c.cohomology_group_bottom(1)
            Bottom Cohomology Group of dimension 0
        """
        S = self.base_ring
        shifts = self.resolution.shifts(i)
        return CohomologyGroupBottom(S, shifts)

    def cohomology_group_top(self, i):
        r"""
        Return `i`-th top cohomology group `\bigoplus_{j=1}^{t_i}H^r(\OO_{\PP^r}(-m^{(i)}_j))`

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: c = X.structure_sheaf()._cohomology
            sage: c.cohomology_group_top(1)
            Top Cohomology Group of dimension 3
        """
        S = self.base_ring
        shifts = self.resolution.shifts(i)
        return CohomologyGroupTop(S, shifts)

    def differential_bottom(self, i):
        r"""
        Return `i`-th bottom differential map `H^0(f_i)`.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: c = X.structure_sheaf()._cohomology
            sage: c.differential_bottom(1)
            Vector space morphism represented as left-multiplication by the matrix:
            []
            Domain: Vector space of dimension 0 over Rational Field
            Codomain: Vector space of dimension 1 over Rational Field
        """
        H1 = self.cohomology_group_bottom(i)
        H0 = self.cohomology_group_bottom(i - 1)
        M = self.resolution.differential(i).matrix()
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

    def differential_top(self, i):
        r"""
        Return `i`-th top differential map `H^r(f_i)`.

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: c = X.structure_sheaf()._cohomology
            sage: c.differential_top(1)
            Vector space morphism represented as left-multiplication by the matrix:
            []
            Domain: Vector space of dimension 3 over Rational Field
            Codomain: Vector space of dimension 0 over Rational Field
        """
        H1 = self.cohomology_group_top(i)
        H0 = self.cohomology_group_top(i - 1)
        M = self.resolution.differential(i).matrix()
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
        r"""
        Return the `t`-th cohomology group `H^t(\tilde M)`.

        INPUT:

        - ``t`` -- non-negative integer

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: c = X.structure_sheaf()._cohomology
            sage: c.H(1)
            Vector space quotient V/W of dimension 3 over Rational Field where
            V: Vector space of degree 3 and dimension 3 over Rational Field
            Basis matrix:
            [1 0 0]
            [0 1 0]
            [0 0 1]
            W: Vector space of degree 3 and dimension 0 over Rational Field
            Basis matrix:
            []
        """
        r = self.projective_space_dimension
        if t == r:
            return self.cohomology_group_top(0).vector_space.quotient(self.differential_top(1).image())
        elif 1 <= t and t < r:
            return self.differential_top(r - t).kernel().quotient(self.differential_top(r - t + 1).image())
        elif t == 0:
            raise ValueError('not implemented')
        elif t > r:
            return VectorSpace(self.coefficient_field, 0)
        raise IndexError('index must be non-negative')

    def h(self, t):
        r"""
        Return the dimension `h^t(\tilde M)` of the `t`-th cohomology group `H^t(\tilde M)`.

        INPUT:

        - ``t`` -- non-negative integer

        EXAMPLES::

            sage: P2.<x,y,z> = ProjectiveSpace(QQ, 2)
            sage: X = P2.subscheme([x^4 + y^4 + z^4])
            sage: c = X.structure_sheaf()._cohomology
            sage: c.h(1)
            3
        """
        r = self.projective_space_dimension
        if t == r:
            return self.cohomology_group_top(0).rank - self.differential_top(1).rank()
        elif 1 <= t and t < r:
            return self.differential_top(r - t).kernel().dimension() - self.differential_top(r - t + 1).rank()
        elif t == 0:
            a = (self.cohomology_group_bottom(0).rank - self.cohomology_group_top(r + 1).rank
                 + self.cohomology_group_top(r).rank)
            b = self.differential_bottom(1).rank() + self.differential_top(r).rank()
            return a - b
        elif t > r:
            return 0
        raise IndexError('index must be non-negative')

