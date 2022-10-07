## -*- encoding: utf-8 -*-
"""
This file (./integration_doctest.sage) was *autogenerated* from ./integration.tex,
with sagetex.sty version 2011/05/27 v2.3.1.
It contains the contents of all the sageexample environments from this file.
You should be able to doctest this file with:
sage -t ./integration_doctest.sage
It is always safe to delete this file; it is not used in typesetting your
document.

Sage example in ./integration.tex, line 73::

  sage: x = var('x'); f(x) = exp(-x^2) * log(x)
  sage: result = integrate(f, x, 1, 3)
  ...
  sage: N(result)  # abs tol 1e-14
  0.03586029499126769

Sage example in ./integration.tex, line 78::

  sage: plot(f, 1, 3, fill='axis')
  Graphics object consisting of 2 graphics primitives

Sage example in ./integration.tex, line 104::

  sage: N(integrate(sin(x^2)/(x^2), x, 1, infinity))  # abs tol 2e-15
  0.285736646322853 - 6.93889390390723e-18*I

Sage example in ./integration.tex, line 108::

  sage: plot(sin(x^2)/(x^2), x, 1, 10, fill='axis')
  Graphics object consisting of 2 graphics primitives

Sage example in ./integration.tex, line 162::

  sage: fp = plot(f, 1, 3, color='red')
  sage: n = 4
  sage: interp_points = [(1+2*u/(n-1), N(f(1+2*u/(n-1))))
  ....:                  for u in range(n)]
  sage: A = PolynomialRing(RR, 'x')
  sage: pp = plot(A.lagrange_polynomial(interp_points), 1, 3, fill='axis')
  sage: fp+pp
  Graphics object consisting of 3 graphics primitives

Sage example in ./integration.tex, line 522::

  sage: N(integrate(cos(log(cos(x))), x, 0, pi/4))  # rel tol 2e-12
  0.7766520331543109

Sage example in ./integration.tex, line 536::

  sage: integrate(log(1+x)*x, x, 0, 1)
  1/4
  sage: N(integrate(log(1+x)*x, x, 0, 1))
  0.250000000000000

Sage example in ./integration.tex, line 562::

  sage: numerical_integral(cos(log(cos(x))), 0, pi/4)  # rel tol 2e-11
  (0.7766520331543109, 8.622569693298564e-15)

Sage example in ./integration.tex, line 600::

  sage: numerical_integral(exp(-x^100), 0, 1.1)
  (0.99432585119150..., 4.0775730...e-09)
  sage: numerical_integral(exp(-x^100), 0, 1.1, algorithm='qng') # abs tol 2e-12
  (0.9943275385765319, 0.016840666914705607)

Sage example in ./integration.tex, line 612::

  sage: integrate(cos(log(cos(x))), x, 0, pi/4)
  integrate(cos(log(cos(x))), x, 0, 1/4*pi)

Sage example in ./integration.tex, line 622::

  sage: N(integrate(cos(log(cos(x))), x, 0, pi/4), digits=60) # abs tol 2e-12
  0.7766520331543109

Sage example in ./integration.tex, line 628::

  sage: N(integrate(sin(x)*exp(cos(x)), x, 0, pi), digits=60)
  2.35040238728760291376476370119120163031143596266819174045913

Sage example in ./integration.tex, line 644::

  sage: sage.calculus.calculus.nintegral(sin(sin(x)), x, 0, 1)
  (0.430606103120690..., 4.78068810228705...e-15, 21, 0)

Sage example in ./integration.tex, line 654::

  sage: g = sin(sin(x))
  sage: g.nintegral(x, 0, 1)
  (0.430606103120690..., 4.78068810228705...e-15, 21, 0)

Ensure consistent results on 32-bit and 64-bit systems by using the same
precision::

  sage: _ = gp.default('realprecision', 38)

Sage example in ./integration.tex, line 703::

  sage: gp('intnum(x=17, 20, exp(-x^2)*log(x))')
  2.5657285005610514829173563961304785900 E-127

Sage example in ./integration.tex, line 717::

  sage: gp('intnum(x=0, 1, sin(sin(x)))')
  0.43060610312069060491237735524846578643
  sage: old_prec = gp.set_precision(50)
  sage: gp('intnum(x=0, 1, sin(sin(x)))')
  0.43060610312069060491237735524846578643360804182200

Sage example in ./integration.tex, line 746::

  sage: p = gp.set_precision(old_prec) # we reset the default precision
  sage: gp('intnum(x=0, 1, x^(-99/100))')  # rel tol 1e-9
  73.629142577870966597465391764897770039

Sage example in ./integration.tex, line 754::

  sage: gp('intnum(x=[0, -99/100], 1, x^(-99/100))')
  100.00000000000000000000000000000000000

Sage example in ./integration.tex, line 766::

  sage: gp('intnum(x=[0, -1/42], 1, x^(-99/100))')  # rel tol 1e-9
  74.472749314025559405335761513474670714

Sage example in ./integration.tex, line 785::

  sage: import mpmath
  sage: mpmath.mp.prec = 53
  sage: mpmath.quad(lambda x: mpmath.sin(mpmath.sin(x)), [0, 1])
  mpf('0.43060610312069059')

Sage example in ./integration.tex, line 795::

  sage: a = RDF(pi); b = mpmath.mpf(a); b
  mpf('3.1415926535897931')
  sage: c = RDF(b); c
  3.141592653589793

Sage example in ./integration.tex, line 824::

  sage: mpmath.mp.prec = 113
  sage: mpmath.quad(lambda x: mpmath.sin(mpmath.sin(x)), [0, 1])
  mpf('0.430606103120690604912377355248465809')

Sage example in ./integration.tex, line 846::

  sage: f(x) = sin(sin(x))
  sage: mpmath.quad(f, [0, 1])
  Traceback (most recent call last):
  ...
  TypeError: no canonical coercion from <class 'sage.libs.mpmath.ext_main.mpf'> to ...

Sage example in ./integration.tex, line 866::

  sage: g(x) = max_symbolic(sin(x), cos(x))
  sage: mpmath.mp.prec = 100
  sage: mpmath.quadts(lambda x: g(N(x, 100)), [0, 1])
  mpf('0.873912416263035435957979086252')

Sage example in ./integration.tex, line 878::

  sage: mpmath.mp.prec = 170
  sage: mpmath.quadts(lambda x: g(N(x, 190)), [0, 1])
  mpf('0.87391090757400975205393005981962476344054148354188794')
  sage: N(sqrt(2) - cos(1), 100)
  0.87391125650495533140075211677

Sage example in ./integration.tex, line 892::

  sage: mpmath.quadts(lambda x: g(N(x, 170)), [0, mpmath.pi / 4, 1])
  mpf('0.87391125650495533140075211676672147483736145475902551')

Sage example in ./integration.tex, line 979::

  sage: y = var('y'); integrate(exp(y*sin(x)), (x, 0, sqrt(y)))  # long time
  integrate(e^(y*sin(x)), x, 0, sqrt(y))

Sage example in ./integration.tex, line 990::

  sage: f = lambda y: numerical_integral(lambda x: exp(y*sin(x)),  \
                                         0, sqrt(y))[0]
  sage: f(0.0), f(0.5), f(1.0) # abs tol 2e-15
  (0.0, 0.8414895067661431, 1.6318696084180513)

Sage example in ./integration.tex, line 998::

  sage: numerical_integral(f, 0, 1) # abs tol 2e-16
  (0.8606791942204567, 6.301207560882073e-07)

Sage example in ./integration.tex, line 1008::

  sage: f = lambda y: sage.calculus.calculus.nintegral(exp(y*sin(x)), \
                                                       x, 0, sqrt(y))[0]
  sage: numerical_integral(f, 0, 1) # abs tol 2e-16
  (0.8606791942204567, 6.301207560882096e-07)

Sage example in ./integration.tex, line 1016::

  sage: f = lambda y: RDF(mpmath.quad(lambda x: mpmath.exp(y*mpmath.sin(x)), \
                                      [0, sqrt(y)]))
  sage: numerical_integral(f, 0, 1) # abs tol 2e-16
  (0.8606791942204567, 6.301207561187562e-07)

Sage example in ./integration.tex, line 1027::

  sage: mpmath.mp.dps = 60
  sage: f = lambda x, y: mpmath.exp(y*mpmath.sin(x))
  sage: mpmath.quad(f, [0,1], [0,1])
  mpf('1.28392205755238471754385917646324675741664250325189751108716305')

Sage example in ./integration.tex, line 1044::

  sage: def evalI(n):
  ....:   f = lambda y: numerical_integral(lambda x: exp(y*sin(x)),
  ....:               0, sqrt(y), algorithm='qng', max_points=n)[0]
  ....:   return numerical_integral(f, 0, 1, algorithm='qng', max_points=n)
  sage: evalI(100) # abs tol 2e-12
  (0.8606792028826138, 5.553962923506737e-07)

Sage example in ./integration.tex, line 1228::

  sage: T = ode_solver()

Sage example in ./integration.tex, line 1244::

  sage: def f_1(t,y,params): return [y[1],params[0]*(1-y[0]^2)*y[1]-y[0]]
  sage: T.function = f_1

Sage example in ./integration.tex, line 1266::

  sage: def j_1(t,y,params):
  ....:     return [[0, 1],
  ....:             [-2*params[0]*y[0]*y[1]-1, params[0]*(1-y[0]^2)],
  ....:             [0,0]]
  sage: T.jacobian = j_1

Sage example in ./integration.tex, line 1279::

  sage: T.algorithm = "rk8pd"
  sage: T.ode_solve(y_0=[1,0], t_span=[0,100], params=[10],
  ....:             num_points=1000)
  sage: f = T.interpolate_solution()

Sage example in ./integration.tex, line 1302::

  sage: plot(f, 0, 100)
  Graphics object consisting of 1 graphics primitive

Sage example in ./integration.tex, line 1363::

  sage: t, y = var('t, y')
  sage: desolve_rk4(t*y*(2-y), y, ics=[0,1], end_points=[0, 1], step=0.5)
  [[0, 1], [0.5, 1.12419127424558], [1.0, 1.461590162288825]]

Sage example in ./integration.tex, line 1399::

  sage: import mpmath
  sage: mpmath.mp.prec = 53
  sage: sol = mpmath.odefun(lambda t, y: y, 0, 1)
  sage: sol(1)
  mpf('2.7182818284590451')
  sage: mpmath.mp.prec = 100
  sage: sol(1)
  mpf('2.7182818284590452353602874802307')
  sage: N(exp(1), 100)
  2.7182818284590452353602874714

Sage example in ./integration.tex, line 1436::

  sage: mpmath.mp.prec = 53
  sage: f = mpmath.odefun(lambda t, y: [-y[1], y[0]], 0, [1, 0])
  sage: f(3)
  [mpf('-0.98999249660044542'), mpf('0.14112000805986721')]
  sage: (cos(3.), sin(3.))
  (-0.989992496600445, 0.141120008059867)

Sage example in ./integration.tex, line 1497::

  sage: mpmath.mp.prec = 10
  sage: sol = mpmath.odefun(lambda t, y: y, 0, 1)
  sage: sol(1)
  mpf('2.7148')
  sage: mpmath.mp.prec = 100
  sage: sol(1)
  mpf('2.7135204235459511323824699502438')

"""
