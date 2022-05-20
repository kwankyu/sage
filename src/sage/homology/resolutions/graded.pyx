"""
Graded free resolutions

This module defines :class:`GradedFreeResolution` which computes a graded free
resolution of a homogeneous ideal `I` of a graded multi-variate polynomial ring
`S`. The output resolution is always minimal.

The degrees given to the variables of `S` are integers or integer vectors of
the same length. In the latter case, the resolution is also called multigraded
free resolution. The standard grading where all variables have degree `1` is
used if the degrees are not specified.

The computation of the resolution is done by the libSingular behind. Different
Singular algorithms can be chosen for best performance.

EXAMPLES::

    sage: from sage.homology.resolutions.graded import GradedFreeResolution
    sage: P.<x,y,z,w> = PolynomialRing(QQ)
    sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
    sage: r = GradedFreeResolution(I, algorithm='minimal')
"""

from sage.libs.singular.decl cimport *
from sage.libs.singular.decl cimport ring
from sage.libs.singular.function cimport Resolution, new_sage_polynomial, access_singular_ring
from sage.structure.sequence import Sequence, Sequence_generic
from sage.libs.singular.function import singular_function
from sage.matrix.constructor import matrix as Matrix
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ
from sage.rings.polynomial.laurent_polynomial_ring import LaurentPolynomialRing

from .free import FreeResolution


class GradedFreeResolution(FreeResolution):
    """
    Graded free resolutions of ideals of multi-variate polynomial rings.

    INPUT:

    - ``ideal`` -- a homogeneous ideal of a multi-variate polynomial ring

    - ``degree`` -- list of integers or integer vectors

    - ``algorithm`` -- Singular algorithm to compute a resolution of ``ideal``

    OUTPUT: a graded minimal free resolution of the ideal

    The ``degrees`` specify degrees of the variables of the multi-variate
    polynomial ring `S` of which ``ideal`` is a homogeneous ideal.

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

        sage: from sage.homology.resolutions.graded import GradedFreeResolution
        sage: S.<x,y,z,w> = PolynomialRing(QQ)
        sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
        sage: r = GradedFreeResolution(I)
        sage: r
        S(-(3))⊕S(-(3)) <-- S(-(2))⊕S(-(2))⊕S(-(2)) <-- S(-(3))⊕S(-(3)) <-- 0
        sage: len(r)
        2
    """
    def __init__(self, ideal, degrees=None, name='S', algorithm='shreyer'):
        cdef int i, j, k, ncols, nrows
        cdef list res_betti, prev_grade, grade

        from sage.rings.ideal import Ideal_generic

        if isinstance(ideal, Ideal_generic):
            S = ideal.ring()
        else:
            S = ideal.base_ring()

        ng = S.ngens()

        if degrees is None:
            degrees = ng*[1]  # standard grading

        if len(degrees) != ng:
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
        if isinstance(ideal, Ideal_generic):
            module = singular_function("module")
            mod = module(ideal)
        else:
            module = singular_function("module")
            mod = module(ideal)

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

        res_mats, res_degs = to_sage_resolution(r, degrees)

        # compute graded Betti numbers
        res_betti = []
        prev_grade = [zero_deg]
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

        if isinstance(ideal, Ideal_generic):
            M = S.quotient(ideal)
            d0 = M.coerce_map_from(S)
            super().__init__([d0] + res_mats, name=name)
        else:
            super().__init__(res_mats, name=name)

        self.base = (S, zero_deg)
        self.ideal = ideal
        self.degrees = degrees
        self.length = len(res_mats)
        self.res_mats = res_mats
        self.res_degs = res_degs
        self.res_betti = res_betti
        self.multigrade = multigrade

    def _repr_module(self, i):
        """
        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
            sage: r._repr_module(0)
            'S(-(3))⊕S(-(3))'
            sage: r._repr_module(1)
            'S(-(2))⊕S(-(2))⊕S(-(2))'
            sage: r._repr_module(2)
            'S(-(3))⊕S(-(3))'
            sage: r._repr_module(3)
            '0'
        """
        if i == 0:
            S, shift = self.base
            m = f'{self._name}(-{shift})'
        elif i > self.length:
            m = '0'
        else:
            shifts = self.res_betti[i - 1]
            if len(shifts) > 0:
                for j in range(len(shifts)):
                    shift = shifts[j]
                    if j == 0:
                        m = f'{self._name}(-{shift})'
                    else:
                        m += f'\u2295{self._name}(-{shift})'
            else:
                m = '0'
        return m

    def shifts(self, i):
        """
        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
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
            _, zero_deg = self.base
            shifts = [zero_deg]
        elif i > self.length:
            shifts = []
        else:
            shifts = self.res_betti[i - 1]

        return shifts

    def K_polynomial(self):
        """
        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
            sage: r.K_polynomial()
            2*t^3 - 3*t^2 + 1
        """
        if self.multigrade:
            n = self.degrees[0].degree()
        else:
            n = 1

        L = LaurentPolynomialRing(ZZ, 't', n)

        Kpoly = 1
        sign = -1
        for j in range(self.length):
            for v in self.res_betti[j]:
                if self.multigrade:
                    Kpoly += sign * L.monomial(*list(v))
                else:
                    Kpoly += sign * L.monomial(v)
            sign = -sign

        return Kpoly


cdef to_sage_resolution(Resolution res, degrees):
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

        mat = Matrix(sage_ring, nrows, ncols)
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


cdef singular_monomial_exponents(poly *p, ring *r):
    """
    Return the list of exponents of monomial ``p``.
    """
    cdef int v
    cdef list ml = list()

    for v in range(1, r.N + 1):
        ml.append(p_GetExp(p, v, r))
    return ml
