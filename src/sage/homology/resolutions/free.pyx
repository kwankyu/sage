"""
Free resolutions

The :class:`FreeResolution` implements a finite free resolution, which is a
chain complex of free modules, terminating with a zero module at the end, whose
homology groups are all zero.

The class is intended to be subclassed for finite free resolutions in different
subject areas. Thus :meth:`_repr_module` may be overrided by a subclass. See
Examples below.

EXAMPLES::

    sage: from sage.homology.resolutions.free import FreeResolution
    sage: S.<x,y,z,w> = PolynomialRing(QQ)
    sage: M = S**1
    sage: N = M.submodule([vector([g]) for g in [y*w - z^2, -x*w + y*z, x*z - y^2]])
    sage: Q = M.quotient(N)
    sage: d0 = Q.coerce_map_from(M)
    sage: m1 = matrix(S, 1, [z^2 - y*w, y*z - x*w, y^2 - x*z])
    sage: m2 = matrix(S, 3, [-y, x, z, -y, -w, z])
    sage: r = FreeResolution([d0, m1, m2], name='S')
    sage: r
    S^1 <-- S^3 <-- S^2 <-- 0

::

    sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
    sage: S.<x,y,z,w> = PolynomialRing(QQ)
    sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
    sage: r = GradedFreeResolution_polynomial(I)
    sage: r
    S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0

AUTHORS:

- Kwankyu Lee (2022-05-13): initial implementation

"""

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
from sage.rings.ideal import Ideal_generic

from sage.structure.sage_object import SageObject


class FreeResolution(SageObject):
    """
    Base class of free resolutions.

    EXAMPLES::

        sage: from sage.homology.resolutions.free import FreeResolution
        sage: S.<x,y,z,w> = PolynomialRing(QQ)
        sage: M = S**1
        sage: N = M.submodule([vector([g]) for g in [y*w - z^2, -x*w + y*z, x*z - y^2]])
        sage: Q = M.quotient(N)
        sage: d0 = Q.coerce_map_from(M)
        sage: m1 = matrix(S, 1, [z^2 - y*w, y*z - x*w, y^2 - x*z])
        sage: m2 = matrix(S, 3, [-y, x, z, -y, -w, z])
        sage: r = FreeResolution([d0, m1, m2], name='S')
        sage: r
        S^1 <-- S^3 <-- S^2 <-- 0
    """
    def __init__(self, maps, name='F'):
        """
        Initialize.

        TESTS::

            sage: from sage.homology.resolutions.free import FreeResolution
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: M = S**1
            sage: N = M.submodule([vector([g]) for g in [y*w - z^2, -x*w + y*z, x*z - y^2]])
            sage: Q = M.quotient(N)
            sage: d0 = Q.coerce_map_from(M)
            sage: m1 = matrix(S, 1, [z^2 - y*w, y*z - x*w, y^2 - x*z])
            sage: m2 = matrix(S, 3, [-y, x, z, -y, -w, z])
            sage: r = FreeResolution([d0, m1, m2], name='S')
            sage: TestSuite(r).run(skip=['_test_pickling'])
        """
        self.__base_ring = maps[0].base_ring()
        self.__maps = maps
        self.__name = name
        self.__length = len(maps) - 1

    def __repr__(self):
        """
        Return the string form of this resolution.

        INPUT:

        - ``i`` -- a positive integer

        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r
            S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
        """
        s = self._repr_module(0)
        for i in range(1, self.__length + 1):
            s += ' <-- ' + self._repr_module(i)
        s += ' <-- 0'
        return s

    def _repr_module(self, i):
        """
        Return the string form of the `i`-th free module.

        INPUT:

        - ``i`` -- a positive integer

        EXAMPLES::

            sage: from sage.homology.resolutions.free import FreeResolution
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: M = S**1
            sage: N = M.submodule([vector([g]) for g in [y*w - z^2, -x*w + y*z, x*z - y^2]])
            sage: Q = M.quotient(N)
            sage: d0 = Q.coerce_map_from(M)
            sage: m1 = matrix(S, 1, [z^2 - y*w, y*z - x*w, y^2 - x*z])
            sage: m2 = matrix(S, 3, [-y, x, z, -y, -w, z])
            sage: r = FreeResolution([d0, m1, m2], name='S')
            sage: r
            S^1 <-- S^3 <-- S^2 <-- 0
        """
        if i == 0:
            r = self.__maps[0].domain().rank()
            s = f'{self.__name}^{r}'
            return s
        elif i > self.__length:
            s = '0'
        else:
            r = self.__maps[i].ncols()
            if r > 0:
                s = f'{self.__name}^{r}'
            else:
                s = '0'
        return s

    def __len__(self):
        """
        Return the length of this resolution.

        The length of a free resolution is the index of the last nonzero free module.

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
        return self.__length

    def __getitem__(self, i):
        """
        Return the `i`-th free module of this resolution.

        INPUT:

        - ``i`` -- a positive integer

        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r
            S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
            sage: r.target()
            Quotient module by Submodule of Ambient free module of rank 1 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            Basis matrix:
            [-z^2 + y*w]
            [ y*z - x*w]
            [-y^2 + x*z]
       """
        if i < 0:
            raise IndexError('invalid index')
        elif i > self.__length:
            F = (self.__base_ring)**0
        elif i == self.__length:
            F = (self.__base_ring)**(self.__maps[i].ncols())
        else:
            F = (self.__base_ring)**(self.__maps[i + 1].nrows())
        return F

    def target(self):
        """
        Return the codomain of the initial differential map.

        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r
            S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
            sage: r.target()
            Quotient module by Submodule of Ambient free module of rank 1 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            Basis matrix:
            [-z^2 + y*w]
            [ y*z - x*w]
            [-y^2 + x*z]
       """
        return self.__maps[0].codomain()

    def differential(self, i):
        """
        Return the matrix representing the `i`-th differential map.

        INPUT:

        - ``i`` -- a positive integer

        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r
            S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
            sage: r.differential(3)
            Free module morphism defined by the matrix
            []
            Domain: Ambient free module of rank 0 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            Codomain: Ambient free module of rank 2 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            sage: r.differential(2)
            Free module morphism defined as left-multiplication by the matrix
            [-y  x]
            [ z -y]
            [-w  z]
            Domain: Ambient free module of rank 2 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            Codomain: Ambient free module of rank 3 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            sage: r.differential(1)
            Free module morphism defined as left-multiplication by the matrix
            [z^2 - y*w y*z - x*w y^2 - x*z]
            Domain: Ambient free module of rank 3 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            Codomain: Ambient free module of rank 1 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
        """
        if i < 0:
            raise IndexError('invalid index')
        elif i == 0:
            m = self.__maps[0]
        elif i == self.__length + 1:
            s = (self.__base_ring)**0
            t = (self.__base_ring)**(self.__maps[i - 1].ncols())
            m = s.hom(0, t)
        elif i > self.__length + 1:
            s = (self.__base_ring)**0
            t = (self.__base_ring)**0
            m = s.hom(0, t)
        else:
            s = (self.__base_ring)**(self.__maps[i].ncols())
            t = (self.__base_ring)**(self.__maps[i].nrows())
            m = s.hom(self.__maps[i], t, side='right')
        return m

    d = differential

    def matrix(self, i):
        """
        Return the matrix representing the `i`-th differential map.

        INPUT:

        - ``i`` -- a positive integer

        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: r
            S(0) <-- S(-2)⊕S(-2)⊕S(-2) <-- S(-3)⊕S(-3) <-- 0
            sage: r.matrix(3)
            []
            sage: r.matrix(2)
            [-y  x]
            [ z -y]
            [-w  z]
            sage: r.matrix(1)
            [z^2 - y*w y*z - x*w y^2 - x*z]
        """
        if i <= 0:
            raise IndexError(f'invalid index')
        elif i <= self.__length:
            return self.__maps[i]
        else:
            return self.differential(i).matrix()

    def chain_complex(self):
        """
        Return this resolution as a chain complex.

        A chain complex in Sage has its own useful methods.

        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution_polynomial
            sage: S.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution_polynomial(I)
            sage: unicode_art(r.chain_complex())
                                                           ⎛-y  x⎞
                                                           ⎜ z -y⎟
                       (z^2 - y*w y*z - x*w y^2 - x*z)     ⎝-w  z⎠
             0 <── C_0 <────────────────────────────── C_1 <────── C_2 <── 0
        """
        from sage.homology.chain_complex import ChainComplex
        mats = {}
        for i in range(self.__length, 0, -1):
            mats[i] = self.matrix(i)
        return ChainComplex(mats, degree_of_differential=-1)


class FreeResolution_polynomial(FreeResolution):
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

        sage: from sage.homology.resolutions.free import FreeResolution_polynomial
        sage: P.<x,y,z,w> = PolynomialRing(QQ)
        sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
        sage: r = FreeResolution_polynomial(I)
        sage: r
        S^1 <-- S^3 <-- S^2 <-- 0
        sage: len(r)
        2

    ::

        sage: FreeResolution_polynomial(I, algorithm='shreyer')
        S^1 <-- S^3 <-- S^2 <-- 0
        sage: FreeResolution_polynomial(I, algorithm='standard')
        S^1 <-- S^3 <-- S^2 <-- 0
        sage: FreeResolution_polynomial(I, algorithm='heuristic')
        S^1 <-- S^3 <-- S^2 <-- 0
        sage: FreeResolution_polynomial(I, algorithm='minimal')
        S^1 <-- S^3 <-- S^2 <-- 0
    """
    def __init__(self, ideal, name='S', algorithm='shreyer'):
        """
        Initialize.

        TESTS::

            sage: from sage.homology.resolutions.free import FreeResolution_polynomial
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = FreeResolution_polynomial(I)
            sage: TestSuite(r).run(skip=['_test_pickling'])
        """
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

        # This ensures the first component of the Singular resolution to be a
        # module, like the later components. This is important when the
        # components are converted to Sage modules.
        module = singular_function("module")
        mod = module(m)

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

        res_mats = to_sage_resolution(r)

        super().__init__([d0] + res_mats, name=name)

        self._base = M
        self._name = name


cdef to_sage_resolution(Resolution res):
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

                if zero_mat:
                    zero_mat = first == NULL

                mat[i - 1, j] = new_sage_polynomial(sage_ring, first)

        # Singular sometimes leaves zero matrix in the resolution. We can stop
        # when one is seen.
        if zero_mat:
            break

        res_mats.append(mat)

    return res_mats


cdef singular_monomial_exponents(poly *p, ring *r):
    """
    Return the list of exponents of monomial ``p``.
    """
    cdef int v
    cdef list ml = list()

    for v in range(1, r.N + 1):
        ml.append(p_GetExp(p, v, r))
    return ml

