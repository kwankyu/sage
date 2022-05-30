r"""
Graded free resolutions of modules

This module defines :class:`GradedFreeResolution` which computes a graded free
resolution of a homogeneous ideal `I` of a graded multivariate polynomial ring
`S`, or a homogeneous submodule of a graded free module `M` over `S`. The
output resolution is always minimal.

The degrees given to the variables of `S` are integers or integer vectors of
the same length. In the latter case, `S` is said to be multigraded, and the
resolution is a multigraded free resolution. The standard grading where all
variables have degree `1` is used if the degrees are not specified.

A summand of the graded free module `M` is a shifted (or twisted) module of
rank one over `S`, denoted `S(-d)` with shift `d`.

The computation of the resolution is done by the libSingular behind. Different
Singular algorithms can be chosen for best performance.

EXAMPLES::

    sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
    sage: S.<x,y,z,w> = PolynomialRing(QQ)
    sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
    sage: r = GradedFreeResolution_polynomial(I, algorithm='minimal')
    sage: r
    S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
    sage: GradedFreeResolution_polynomial(I, algorithm='shreyer')
    S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
    sage: GradedFreeResolution_polynomial(I, algorithm='standard')
    S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
    sage: GradedFreeResolution_polynomial(I, algorithm='heuristic')
    S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0

::

    sage: d = r.differential(2)
    sage: d
    Free module morphism defined as left-multiplication by the matrix
    [ y  x]
    [-z -y]
    [ w  z]
    Domain: Ambient free module of rank 2 over the integral domain Multivariate Polynomial Ring
    in x, y, z, w over Rational Field
    Codomain: Ambient free module of rank 3 over the integral domain Multivariate Polynomial Ring
    in x, y, z, w over Rational Field
    sage: d.image()
    Submodule of Ambient free module of rank 3 over the integral domain Multivariate Polynomial Ring
    in x, y, z, w over Rational Field
    Basis matrix:
    [ y -z  w]
    [ x -y  z]
    sage: m = d.image()
    sage: GradedFreeResolution_polynomial(m, shifts=(2,2,2))
    S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0

A reference for graded free resolutions with respect to multigrading is
[MilStu2005]_.

AUTHORS:

- Kwankyu Lee (2022-05): initial version

"""

# ****************************************************************************
#       Copyright (C) 2022 Kwankyu Lee <ekwankyu@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from sage.libs.singular.decl cimport *
from sage.libs.singular.decl cimport ring
from sage.libs.singular.function cimport Resolution, new_sage_polynomial, access_singular_ring
from sage.structure.sequence import Sequence, Sequence_generic
from sage.libs.singular.function import singular_function
from sage.matrix.constructor import matrix as _matrix
from sage.matrix.matrix_mpolynomial_dense import Matrix_mpolynomial_dense
from sage.modules.free_module_element import vector
from sage.modules.free_module import FreeModule_generic
from sage.rings.integer_ring import ZZ
from sage.rings.polynomial.laurent_polynomial_ring import LaurentPolynomialRing
from sage.rings.ideal import Ideal_generic

from .free import FreeResolution
from .free cimport singular_monomial_exponents


class GradedFreeResolution_polynomial(FreeResolution):
    """
    Graded free resolutions of ideals of multi-variate polynomial rings.

    INPUT:

    - ``ideal`` -- a homogeneous ideal of a multivariate polynomial ring `S`, or
      a homogeneous submodule of a free module `M` of rank `n` over `S`

    - ``degree`` -- a list of integers or integer vectors giving degrees of
      variables of `S`; this is a list of 1s by default

    - ``shifts`` -- a list of integers or integer vectors giving shifts of
      degrees of `n` summands of the free module `M`; this is a list of zero
      degrees of length `n` by default

    - ``algorithm`` -- Singular algorithm to compute a resolution of ``ideal``

    If ``ideal`` is an ideal of `S`, then `M = S`, a free module of rank `1`
    over `S`.

    OUTPUT: a graded minimal free resolution of ``ideal``

    The available algorithms and the corresponding Singular commands are shown
    below:

        ============= ============================
        algorithm     Singular commands
        ============= ============================
        ``minimal``   ``mres(ideal)``
        ``shreyer``   ``minres(sres(std(ideal)))``
        ``standard``  ``minres(nres(std(ideal)))``
        ``heuristic`` ``minres(res(std(ideal)))``
        ============= ============================

    EXAMPLES::

        sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
        sage: S.<x,y,z,w> = PolynomialRing(QQ)
        sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
        sage: r = GradedFreeResolution_polynomial(I)
        sage: r
        S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
        sage: len(r)
        2
    """
    def __init__(self, ideal, degrees=None, shifts=None, name='S', algorithm='shreyer'):
        """
        Initialize.

        TESTS::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: TestSuite(r).run(skip=['_test_pickling'])
        """
        cdef int i, j, k, ncols, nrows
        cdef list res_betti, prev_grade, grade

        if isinstance(ideal, Ideal_generic):
            S = ideal.ring()
            m = ideal
            M = S**1
            N = M.submodule([vector([g]) for g in ideal.gens()])
            rank = 1
        elif isinstance(ideal, FreeModule_generic):
            S = ideal.base_ring()
            m = ideal.matrix().transpose()
            M = ideal.ambient_module()
            N = ideal
            rank = m.nrows()
        elif isinstance(ideal, Matrix_mpolynomial_dense):
            S = ideal.base_ring()
            m = ideal.transpose()
            N = ideal.row_space()
            M = N.ambient_module()
            rank = ideal.ncols()
        else:
            raise TypeError('no ideal, module, or matrix')

        Q = M.quotient(N)
        d0 = Q.coerce_map_from(M)
        nvars = S.ngens()

        if degrees is None:
            degrees = nvars*[1]  # standard grading

        if len(degrees) != nvars:
            raise ValueError('the length of degrees does not match the number of generators')

        if degrees[0] in ZZ:
            zero_deg = 0
            multigrade = False
        else:   # degrees are integer vectors
            zero_deg = degrees[0].parent().zero()
            multigrade = True

        # This ensures the first component of the Singular resolution to be a
        # module, like the later components. This is important when the
        # components are converted to Sage modules.
        module = singular_function("module")
        mod = module(m)

        if shifts is None:
            shifts = rank*[zero_deg]

        if algorithm == 'minimal':
            mres = singular_function('mres')  # syzygy method
            r = mres(mod, 0)
        elif algorithm == 'shreyer':
            std = singular_function('std')
            sres = singular_function('sres')  # Shreyer method
            minres = singular_function('minres')
            r = minres(sres(std(mod), 0))
        elif algorithm == 'standard':
            nres = singular_function('nres')  # standard basis method
            minres = singular_function('minres')
            r = minres(nres(mod, 0))
        elif algorithm == 'heuristic':
            std = singular_function('std')
            res = singular_function('res')    # heuristic method
            minres = singular_function('minres')
            r = minres(res(std(mod), 0))

        res_mats, res_degs = to_sage_resolution_graded(r, degrees)

        # compute graded Betti numbers
        res_betti = []
        prev_grade = list(shifts)
        for k in range(len(res_degs)):
            grade = []
            degs = res_degs[k]
            ncols = len(degs)
            for j in range(ncols):
                col = degs[j]
                nrows = len(col)
                # should be enough to compute the graded Betti number
                # from any one entry of the column vector
                for i in range(nrows):
                    d = col[i]
                    if d is not None:
                        e = prev_grade[i]
                        grade.append(d + e)
                        break
            res_betti.append(grade)
            prev_grade = grade

        super().__init__([d0] + res_mats, name=name)

        self._base = (M, shifts)
        self._zero_deg = zero_deg
        self._degrees = degrees
        self._res_betti = res_betti
        self._multigrade = multigrade
        self._name = name

    def _repr_module(self, i):
        """
        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r._repr_module(0)
            'S(0)'
            sage: r._repr_module(1)
            'S(-2)⊕S(-2)⊕S(-2)'
            sage: r._repr_module(2)
            'S(-3)⊕S(-3)'
            sage: r._repr_module(3)
            '0'
        """
        if i > len(self):
            m = '0'
        else:
            if i == 0:
                S, shifts = self._base
            else:
                shifts = self._res_betti[i - 1]

            if len(shifts) > 0:
                for j in range(len(shifts)):
                    shift = shifts[j]
                    if j == 0:
                        m = f'{self._name}' + \
                            (f'(-{shift})' if shift != self._zero_deg else '(0)')
                    else:
                        m += f'\u2295{self._name}' + \
                             (f'(-{shift})' if shift != self._zero_deg else '(0)')
            else:
                m = '0'
        return m

    def shifts(self, i):
        """
        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r.shifts(0)
            [0]
            sage: r.shifts(1)
            [2, 2, 2]
            sage: r.shifts(2)
            [3, 3]
            sage: r.shifts(3)
            []
        """
        if i < 0:
            raise IndexError('invalid index')
        elif i == 0:
            _, shifts = self._base
        elif i > len(self):
            shifts = []
        else:
            shifts = self._res_betti[i - 1]

        return shifts

    def betti(self, i, a=None):
        """
        Return the `i`-th Betti number in degree `a`.

        INPUT:

        - ``i`` -- nonnegative integer

        - ``a`` -- a degree; if ``None``, return Betti numbers in all degrees

        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r.betti(0)
            {0: 1}
            sage: r.betti(1)
            {2: 3}
            sage: r.betti(2)
            {3: 2}
            sage: r.betti(1, 0)
            0
            sage: r.betti(1, 1)
            0
            sage: r.betti(1, 2)
            3
        """
        shifts = self.shifts(i)

        if a is None:
            degrees = shifts
        else:
            degrees = [a]

        betti = {}
        for s in degrees:
            betti[s] = len([d for d in shifts if d == s])

        if a is None:
            return betti
        else:
            return betti[a] if a in betti else 0

    def K_polynomial(self):
        """
        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r.K_polynomial()
            2*t^3 - 3*t^2 + 1
        """
        if self._multigrade:
            n = self._degrees[0].degree()
        else:
            n = 1

        L = LaurentPolynomialRing(ZZ, 't', n)

        Kpoly = 1
        sign = -1
        for j in range(len(self)):
            for v in self._res_betti[j]:
                if self._multigrade:
                    Kpoly += sign * L.monomial(*list(v))
                else:
                    Kpoly += sign * L.monomial(v)
            sign = -sign

        return Kpoly


cdef to_sage_resolution_graded(Resolution res, degrees):
    """
    Pull from Singular resolution ``res`` the data to construct Sage
    resolution.

    INPUT:

    - ``res`` -- Singular resolution

    - ``degrees`` -- list of integers or integer vectors

    The procedure is destructive, and ``res`` is not usable afterward.
    """
    cdef ring *singular_ring
    cdef syStrategy singular_res
    cdef poly *p
    cdef poly *p_iter
    cdef poly *first
    cdef poly *previous
    cdef poly *acc
    cdef resolvente mods
    cdef ideal *mod
    cdef int i, j, k, idx, rank, nrows, ncols
    cdef int ngens = len(degrees)
    cdef bint zero_mat

    singular_res = res._resolution[0]
    sage_ring = res.base_ring
    singular_ring = access_singular_ring(res.base_ring)

    if singular_res.minres != NULL:
        mods = singular_res.minres
    elif singular_res.fullres != NULL:
        mods = singular_res.fullres
    else:
        raise ValueError('Singular resolution is not usable')

    res_mats = []
    res_degs = []

    # length is the length of fullres. The length of minres
    # can be shorter. Hence we avoid SEGFAULT by stopping
    # at NULL pointer.
    for idx in range(singular_res.length):
        mod = <ideal *> mods[idx]
        if mod == NULL:
            break
        rank = mod.rank
        free_module = sage_ring ** rank

        nrows = rank
        ncols = mod.ncols # IDELEMS(mod)

        mat = _matrix(sage_ring, nrows, ncols)
        matdegs = []
        zero_mat = True
        for j in range(ncols):
            p = <poly *> mod.m[j]
            degs = []
            # code below copied and modified from to_sage_vector_destructive
            # in sage.libs.singular.function.Converter
            for i in range(1, rank + 1):
                previous = NULL
                acc = NULL
                first = NULL
                p_iter = p
                while p_iter != NULL:
                    if p_GetComp(p_iter, singular_ring) == i:
                        p_SetComp(p_iter, 0, singular_ring)
                        p_Setm(p_iter, singular_ring)
                        if acc == NULL:
                            first = p_iter
                        else:
                            acc.next = p_iter
                        acc = p_iter
                        if p_iter == p:
                            p = pNext(p_iter)
                        if previous != NULL:
                            previous.next = pNext(p_iter)
                        p_iter = pNext(p_iter)
                        acc.next = NULL
                    else:
                        previous = p_iter
                        p_iter = pNext(p_iter)

                # degree of a homogeneous polynomial can be computed from the
                # first monomial
                if first != NULL:
                    exps = singular_monomial_exponents(first, singular_ring)
                    deg = 0
                    for k in range(ngens):
                        deg += exps[k] * degrees[k]
                    degs.append(deg)
                else:
                    degs.append(None)

                mat[i - 1, j] = new_sage_polynomial(sage_ring, first)

            matdegs.append(degs)

            if zero_mat:
                zero_mat = all(d is None for d in degs)

        # Singular sometimes leaves zero matrix in the resolution. We can stop
        # when one is seen.
        if zero_mat:
            break

        res_mats.append(mat)
        res_degs.append(matdegs)

    return res_mats, res_degs


