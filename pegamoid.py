#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function
from builtins import bytes, dict, int, range, super

__name__ = 'Pegamoid'
__author__ = u'Ignacio Fdez. Galván'
__copyright__ = u'Copyright © 2018–2019'
__license__ = 'GPL v3.0'
__version__ = '2.2.1'

import sys
try:
  from qtpy.QtCore import Qt, QObject, QThread, QEvent
  from qtpy.QtWidgets import *
  from qtpy.QtGui import QPixmap, QIcon, QKeySequence, QColor, QPalette
  import qtpy
  v = qtpy.PYQT_VERSION
  if (v is None):
    v = qtpy.PYSIDE_VERSION
  QtVersion = '{0} {1} (Qt {2})'.format(qtpy.API_NAME, v, qtpy.QT_VERSION)
except:
  try:
    from PyQt5.QtCore import Qt, QObject, QThread, QEvent, PYQT_VERSION_STR, QT_VERSION_STR
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QColor, QPalette
    QtVersion = 'PyQt5 {0} (Qt {1})'.format(PYQT_VERSION_STR, QT_VERSION_STR)
  except ImportError:
    from PyQt4.QtCore import Qt, QObject, QThread, QEvent, PYQT_VERSION_STR, QT_VERSION_STR
    from PyQt4.QtGui import *
    QtVersion = 'PyQt4 {0} (Qt {1})'.format(PYQT_VERSION_STR, QT_VERSION_STR)
import vtk.qt
try:
  vtk.qt.QVTKRWIBase = "QGLWidget"
  from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
  QtVersion += ' with QtOpenGL'
except ImportError:
  vtk.qt.QVTKRWIBase = "QWidget"
  from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from vtk.util import numpy_support

import h5py
import numpy as np
from fractions import Fraction

import os
import os.path
import codecs
import re
import struct
import traceback
import time
from copy import deepcopy
from socket import gethostname
from datetime import datetime
from tempfile import mkdtemp
from shutil import rmtree
from functools import partial
from collections import OrderedDict
try:
  from itertools import zip_longest
except ImportError:
  from itertools import izip_longest as zip_longest
try:
  from ttfquery._scriptregistry import registry
except ImportError:
  pass

icondata = codecs.decode(b'''
iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABGdBTUEAALGPC/xhBQAAAAFzUkdC
AK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAAZiS0dE
AP8A/wD/oL2nkwAAAAlwSFlzAAAASAAAAEgARslrPgAAC31JREFUaN7tmWusXNdVx/9r7X0ec+bM
nTv36Vdsx4kNseu0xE1CadqGggCpEhKilaBSJb4UCZSvVAjxiCpRUD/QSAUVgYQKAhpRJPhQ5QsK
tCqRiJs4IbUdP5N7k2vfx9w775kzZ5+91+LDdRGIYDtc+gD5L62zpTl7pP2bNXvttdYG7ume7un/
tOjdfuGL+uuYwyzODl7B0A0pqABQCARBA8pQwrPHMPQwxBA+AGEqYCZAFRIA9UriFH4k8F0hvyVw
1wOGLzgdfbMUignq9H8HYOajCTQgy05HJ+uPxJocM+N4ny1qec1lplbFFHsDEwCVoEEqVOpQaemn
KIdTBYHEEkhBAAhCjApGHKxOkMhY0zCURtXzc35blv22NKXUrwG4ufmHozsC2DtNkIlCA97jd+Rz
1Va4whldAIdVCZN21XD9elQvMspcjLiKOQl1kBBIJFKVnGFZYYwlBjODDUAWqnFQSb34vJSyOZHJ
wtAP9036xf3l2/54tS5vUoSbd+OBOwJwSpBSj8CgASBRRV2D1qE6YmaXUKIZZZRSyjFib8kGAyME
Us6MKgS3Fs8EMgAihcYePnHq4qlOY1a2Xiuq2LkwkCp09XByv8Ghp2ew9vTg9uu73cv4PoP4sAFZ
OswpeUqo5BiOY/IUUYjYSoRILeyu0e5oYDQiqwaAAYNA+h0DSAEo6a6nCBQIFFjZg1HBoALh0OaX
xub2q7sLAIoI238xIYqwnxNynJCjhCpKyHPMYsiqhVFDBgZGDQyYDAwZEBiMGAwLBkGh2N2WqrsP
FQCiQADgFfBQVERUQbGUPmhrqnv8C5EB7BzHZGmBUnIUw3FCnhMEGxmxsMpkwGBl4t0RrAklEsFK
0FI9GB7KgJJCVHdjkShUBSIKEVEJguBVEVS00qBNEOoIGO1tDxjANCiGQcYxKk4oUIzACUnEkUYU
g8FKYCWQGjZqiPXq9OpyZrIHm9xcyihzMcUrlVbXAkIQiKqqBgQJGiRoCAE+BA1evQT1EK1QU685
BJt78wAT1MISIyZLgSwFikk4YokpRowIBgYEwDBrvzO059sXPtw4lP1obvOGpYgN2RqDagI577R6
FtCuh1evXj28VPBSoQqVVCJOVZ2qlhqrQ6q85yiku2cFgcC7AZAiqDEGESKKKEJEFkyMahzo7D+8
+pPmITmzFM1fz6mxU6esiilORHVfBX+qxPRTTt2fJZSU34Go1KlTpz54lRIkpZJM1Uihhva6iVUA
9QhQeAAEBpEhMDNZsmxh2cJSVq/pua9cPDrpTT8UN6NLM3bm9ZSSaxb2moG5Ysj8KxO/WGq5sFlu
nlGFeng4ODjsIgQn0KmyFmqkUJZCRQrdowcCIBNxGlBAkILAxGBDxhhYNrBkyFJEEXobg/eaEzSZ
WWisNanZjSgaKdR79UagLqiPCpm2up3+D8+kg5fjlkGlFUqdogwlpBAjEzVholEYqcpYpmDaowec
wrfFaaVdqTSGIALBMhljYYwlYyyskb5asbqYHop6rXS2TJFWBtYTKAikcijdUIejbtnpDN+YzA7W
R3UwKEC41JJ84U0YaRRGEoe+pmEgLvR1FAayNwCZAstP5UEdVmSiiXrEUIoYFBkykYWNLKxNksQY
w6WxnOYmz2IkCQFRgBgPb6da2h3d4fZqJy3OV5ERKwFiAjx78TZMNAp9SUJXMr8jue9I162H/p4B
qs2A8TkHmeiFMFArhdY1aA1AyuDUkEks2ThJE9tqzr5RbvjWxE8WlHQWoDwg1AudZl3tZBuDzZnB
S8X9YYW2Fk41Sxdc5NRF3vlYxpqFvuZVW2bcjTDrt+T60i/Xi9DXvQEAgO8IfE9e8zvS9TsyH8ba
9MHXBVInUJ1hMplKfubJ06uyRpP1tc3DQwwWnJYtr75ZatnsSne2e3VwpHgtLLf2Nc+Fuo8mOknH
fpxW/ZD7jjSrdphzN8Ji+aavuZvhhc0vjlBcrPYOEHqKT157+KZvh+fLN/1ytREWp+OyNdHJjFPX
DPCzQaR58PSyObb/yNmdV4f7N4qN/QWK+RJlq8Bktj/uL47OuVM1Si+d/tUH1gfj4cwgDOvTnput
NsKCWwvLbiUcnF72R8sV/3q54s+69XAriuNOZ+0d0umR4tKzbfi+vkXAhzim/ZSjlEYIHDMbGMtE
VoLG9/3QgcHGt9tZx3UOZwfSqYK4i262dm7zweo86g//wvF/wgGxvdDPx8Nx0234pWpNDpar4ej0
sj9eXPaJ35Cnuc7XZXB3BY25m0kyVtQeiobuZnhLCv0oBIsSiZTpVKvEcaCQBPgkcEiXDy/2tq52
5oc8aDWsT7e32nOdb7l9Rx87eK72fuu23fbMcDBqlevVsnsrHCrf9Eenl6sT00u+VW3I78tIn9Py
7hZ/1wDqAb8tOPR7zbXe30+vhZ48Hvp6zJehNtVpPLHjZGKLbEpFw9eqPM8SLL+y+ZEn7PSJR5C/
xzfo5vixqNMZdxZG7fG+6Yo/XF719xcX/fHi29WJ4nXvq3X5XOjLV8H/nrZ+F2piBvIPJCiv+8PR
Ev+iXTJPxPu4aZeNRAtc2hnjbd34eF2aJzbdqZOPpC6PsujlN/qDlxJcrcZiQkfialsivyVabYVu
1ZazoStflUIvfU+K+v+U69Vo3szwEa7Tfk5plhJkiMjMAY88tN98at9RM/UTra29HVZfvRm+UDnt
6lTHMtFeGOuWTHQDigHwbn7zd1lS3jZVKnRbirD9Hz984oMJfKWHGgYPxBP9SDnScRjIHw1fq750
8oTFxZXw/W2r3ElzvzODZ0rCZyEfa0n8Y82ji752cv7Pi/7ojc/87DP4KfrxH1yA4383DxmpjRb5
g3bJPNk63No4yAeWGtLIUyR/WUd2fopSn1n4yg8GwCe3fhrgGjpyg85vXjANzQ4Z4p+hiB7nGk0j
ExUNbqSLZvFgi+dsSslzBHpuS9qbYxkp3yryCRCBSolSrvpVzamGVw+u/c8BTq8toZCCDtiDScZZ
M0HcMmRmGTxDQEOBXKF1haZBJRGEKIjUVOUYMc8ZsDdixZKlmCNOOE0yruUJkoxA7QLTG2MZlRWq
SjTsFvRQB1BJoMIQjwxs38BsM5kbBKzlnHfaph2ef+w8Nq5svDPAxzYeRUyxaYetMwR+NOPseErJ
gRhx08DUGBQRseFbvYfdYg0gIjYwZGFhyKoBE+82VIhodwZUabczoXTLdtsruwUfAUQKZYWwQhkg
YlAAMBXVrZf+9MLXX/iN175gGlSEob5zFJrneRjwPsflUxOd7CcQq4KVlCKKQk55yLmBGqVkYZXA
nkAlgPEtmwAoADgCVUQkBGIDNgyTMLhmyNQNTMPA5EycESghENMuAIIGLlGaQid2ooX16nPnXHPn
ci9Chr+y82Y1DP07A8xyEwwzX8LF4zAZe/Woc10WeUnmeS7UqDYxZNoEWgPobQA3CbRNwIDABYOr
mGLfpKacit+rP5L8BLarK3jR/TO1ZZsqVAbQiMA1AjcMeMGADzGZoww6RuD9RNQAYASBSy2jAYbJ
xnCTi6LsRkcptymjXPlvzoEaZbAw9ZzySa51t2SX/ZJZGqWUvk2gixX8lVLL9YEMxznn+gf/+CeY
fPzuzoxbJgCqW57aAbDyx73PvlRqSU2aySxFBw3MSUP8PoP4gZjiRo7ctmZa2636N//mBjYHt93E
v7nzaUQUf3ggg48HDb2E4wsKvFJqufrM/F+Xn9h6En+7/I3vWq//851fw/uSh7HuN9KY4mOG+AMM
fj+De1D63Z9rfGIULy2iast/BfitzqcxVYc6ZY/3pLd/qtMXezrYTJHIl5ee+55fXHy5/3k4OM4p
vy8ie8TA/IsC7ucbv/LOqYRC8bI7h0fjM69MtPgWAHl26fnv283LLzU/AwDy252nVhWyeive3buS
uqd7uqd7uqf/X/o3WcSqZKuF0icAAAAASUVORK5CYII=
''', 'base64')

boxicondata = codecs.decode(b'''
iVBORw0KGgoAAAANSUhEUgAAAEAAAAApCAQAAAAvm+fHAAAABGdBTUEAALGPC/xhBQAAAAFzUkdC
AK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAAJiS0dE
AP+Hj8y/AAAACXBIWXMAAC38AAAt/AGuw+yYAAAGBklEQVRYw7XYe2zW1RkH8A+XchEITO5Mpitg
AkPlIsMtUJ2XlEF0QwkXCTjcFi6C2cAlyhwiGl0QMTqUWtkUzDBKQCbCRAdxdIEIyE1BjDC0JTIu
HQVboLT07A9ef/29Lb++Bd3z/nd+53nO857v+Z7n+R4uxrJ08mOTLLJdqUIvG+VKjf2fraE2fmC4
WZbZpViFEP1O22uJe/XS/NtetoGWuhvid161xeHYshVKBcFRxaoEwTn/sdZMg12uwTdfupF+pnhR
gYPORMueU2K3N80xXL6gwkR9/cZKhVFyJ33oOXd+U1gGOxjb5DJ7rfGU8QboIAtt/EuwxxWgie7G
yLdLWcrjrP1eN9l1Wlza1r8QWz444DED0hAe6pRgXo1z0sEt5njfsRQsVY5ab7abtdfwYhLItl+w
z4YYwoetM8tN2mmgoUWC4wZd0LulPqZY5t/ORju4U55RumlSvwQmqVJlqub6mWa5zyOES+3wvKkK
BavrPPVZrnKXBbb5Kjq4X3jT/fprVffyLbwrOKB7FCrbSC/YkTr5wTlVgjf00TIjmG3leNh7DjuX
guW/CjwhV6ckWHKcELxY43MD7dzkEesciRAutsHjbtMxI8LN9fYrf/WZ8uj22OMvxrm6NizPCMrk
JoRqaqIKwfGInqd8bJGxemiakdxdDDXXlsi30kF56ZO+Z6+gQJvETV0gOGG02z1rq5NRqCJvmW6g
1omeLWS71QxvR2AGwYn0aRNUCmbUwZB9gnVaoYHvGOQh7zgUIXzcJnMN00WjlEczXd1oijwFitKu
tfNwrE7H6m1BkZ51MiSYmjbWTE8TLLE3Cn/GXkv80j3me9d+palzE1Qptc9a84yzUlBmVDzUDYoF
r0TZZ2JITYSHmWuT49HtcS76v2cU2WChyXJ01Qyd7RJs1D4e5I+C0+5I/P85SgT5dZ761gaabrXT
gkqHbbbYDLm6aZFWpsaqEDwYd+3iI8EH2iYGny8oM6Qel9n1jgrW6K31BdNtaoXgS9fEB+9WIZiZ
GLRrBobE7feCs8Ykfu/viGCprHhOywWHXJvolIkh1dbWZsEunRNnPCood1ftnF6L51TjNluVgSHV
9jOnBU8mfu9gm+BDHeKDswXlRiQ6nWfI4kSGVFtjiwXFbkicMUK5YHbtnLal55RmT2ZgSLX1clCw
KrFaZnlNcES/2jk9mhi0c0aGVNsDgkq/SPx+rUOC5fHakWWp4Ij+iU6ZGFJt59u1T3RNnDFTUOHu
+NA1vqyZU1pL3tvfBUddX48EhigTzK+DIR/UZsiDggpja9SubnLNsMRmh1UKTltjhoFa19F4N5Qv
KDE4ccYdtRnS3kbBTp1TtSvHZAttqFG7vq53JTZ5yjDfvSAfejggWJvYDTfySm2GjFYmWGm8p62t
Vbv2W+tp97jX4rR696lXL6CHpgmqTEz8/z0V1WbIakFQXqt25cVqV7yj2Rird4e84yGDUnqolfWC
fb6fmMAMQaUJ6YMnYv1JqVWmu0V2jdqVXu9+aLq3FKmM9NBWz7rdaCcFf0r0bKPgQgzJczAKVW6r
uYbGOhqJ3WEPY73kY6eifStJCbZmCT65F2ZIE1cb5892R6HKfWapX+vtsoy6uaPbPO6fMT10xDqP
+Il2NXbia4bkJIXqJNcTCtL00HsedqO2GRVvS328IaiKTlKpHRYaKTsqb90zMCRlrfR3vxW+iPTQ
V7ZZYISrEislXGa1oNB9Ftge9b0VPrfCNP00N1WVKpPqJ8+ayDZKnp1RqLMOWOY+fRP00CDHBS9p
mBIxs/wjpoeKbbBPsE/2xb2MtHez2dY7GiF8zPvmuFWHGq3WPEGZn6Z1EAM85kCa0n7+0p4vWrjO
JK/bH1O8H8k3RveUtLrCnqhdy9LRAOPNs8an0ZtBEBxMUNT1tMauNNxzMT1UodDf/FZfk1QI8t1p
jpV2K6lxrRXIM0W/erQz9Xi+uNxgM62N6aFix1InP/6OdNgWSzwgV3ctv42Xo5o9Yi8TLPGJ07FN
rnDMTsv8wc/10ubiXkYuFZaRXlao1HaLTPQjneqkay37H9gL/mliu8SBAAAAAElFTkSuQmCC
''', 'base64')

# For CIELab <-> RGB conversion: http://colorizer.org/
background_color = {
  'F': (0.449, 0.448, 0.646), # CIELab(50,12,-27)
  'I': (0.711, 0.704, 0.918), # CIELab(75,12,-27)   Hue ~ 240
  '1': (0.605, 0.759, 0.682), # CIELab(75,-17,5.5)  Hue ~ 150
  '2': (0.569, 0.775, 0.569), # CIELab(75,-27.5,21) Hue ~ 120
  '3': (0.654, 0.757, 0.548), # CIELab(75,-18.5,24) Hue ~  90
  'S': (0.883, 0.673, 0.670), # CIELab(75,19.5,8)   Hue ~   0
  'D': (0.609, 0.417, 0.416), # CIELab(50,19.5,8)
  '?': (0.466, 0.466, 0.466)  # CIELab(50,0,0)
}

angstrom = 0.52917721067

#===============================================================================
# Class for orbitals defined in term of basis functions, which can be computed
# at arbitrary points in space.
# The basis functions and orbitals can be read from HDF5 and Molden formats.
# Orbital coefficients can be read from InpOrb format if an HDF5 file has been
# read before.

class Orbitals(object):

  def __init__(self, orbfile, ftype):
    self.inporb = None
    self.file = orbfile
    self.type = ftype
    self.eps = np.finfo(np.float).eps
    self.wf = 'SCF'
    if (self.type == 'hdf5'):
      self.read_h5_basis()
      self.read_h5_MO()
      self.inporb = 'gen'
      self.h5file = self.file
    elif (self.type == 'molden'):
      self.read_molden_basis()
      self.read_molden_MO()

  # Read basis set from an HDF5 file
  def read_h5_basis(self):
    with h5py.File(self.file, 'r') as f:
      sym = f.attrs['NSYM']
      self.N_bas = f.attrs['NBAS']
      self.irrep = [i.decode('ascii').strip() for i in f.attrs['IRREP_LABELS']]
      # First read the centers and their properties
      if (sym > 1):
        labels = f['DESYM_CENTER_LABELS'][:]
        charges = f['DESYM_CENTER_CHARGES'][:]
        coords = f['DESYM_CENTER_COORDINATES'][:]
        self.mat = np.reshape(f['DESYM_MATRIX'][:], (sum(self.N_bas), sum(self.N_bas))).T
      else:
        labels = f['CENTER_LABELS'][:]
        charges = f['CENTER_CHARGES'][:]
        coords = f['CENTER_COORDINATES'][:]
      self.centers = [{'name':str(l.decode('ascii')).strip(), 'Z':int(q), 'xyz':x} for l,q,x in zip(labels, charges, coords)]
      self.geomcenter = (np.amin(coords, axis=0) + np.amax(coords, axis=0))/2
      # Then read the primitives and assign them to the centers
      prims = f['PRIMITIVES'][:]    # (exponent, coefficient)
      prids = f['PRIMITIVE_IDS'][:] # (center, l, shell)
      # The basis_id contains negative l if the shell is Cartesian
      if (sym > 1):
        basis_function_ids = 'DESYM_BASIS_FUNCTION_IDS'
      else:
        basis_function_ids = 'BASIS_FUNCTION_IDS'
      bf_id = np.rec.fromrecords(np.insert(f[basis_function_ids][:], 4, -1, axis=1), names='c, s, l, m, tl') # (center, shell, l, m, true-l)
      bf_cart = set([(b['c'], b['l'], b['s']) for b in bf_id if (b['l'] < 0)])
      # Add contaminants, which are found as lower l basis functions after higher l ones
      # The "tl" field means the "l" from which exponents and coefficients are to be taken, or "true l"
      ii = [sum(self.N_bas[:i]) for i in range(len(self.N_bas))]
      if (sym > 1):
        sbf_id = np.rec.fromrecords(np.insert(f['BASIS_FUNCTION_IDS'][:], 4, -1, axis=1), names='c, s, l, m, tl')
      else:
        sbf_id = bf_id
      for i,nb in zip(ii, self.N_bas):
        prev = {'c': -1, 'l': -1, 's': -1, 'tl': 0, 'm': None}
        for b in sbf_id[i:i+nb]:
          if (b['c']==prev['c'] and abs(b['l']) < abs(prev['tl'])):
            b['tl'] = prev['tl']
          else:
            b['tl'] = b['l']
          prev = {n: b[n] for n in b.dtype.names}
      if (sym > 1):
        for i,b in enumerate(self.mat.T):
          bb = np.array(sbf_id[i])
          nz = np.nonzero(b)[0]
          assert (np.all(bf_id[nz][['l','s','m']] == bb[['l','s','m']]))
          for j in nz:
            bf_id[j]['tl'] = bb['tl']
      # Workaround for bug in HDF5 files where p-type contaminants did all have m=0
      p_shells, p0_counts = np.unique([np.array(b)[['c','s','tl']] for b in bf_id if ((b['l']==1) and (b['m']==0))], return_counts=True)
      if (np.any(p0_counts > 1)):
        if (sym > 1):
          # can't fix it with symmetry
          error = 'Bad m for p contaminants. The file could have been created by a buggy or unsupported OpenMolcas version'
          raise Exception(error)
        else:
          m = -1
          for i in np.where(bf_id['l']==1)[0]:
            bi = list(p_shells).index(bf_id[i][['c','s','tl']])
            if (p0_counts[bi] > 1):
              bf_id[i]['m'] = m
              m += 1
              if (m > 1):
                m = -1
      # Count the number of m per basis to make sure it matches with the expected type
      counts = {}
      for b in bf_id:
        key = (b['c'], b['l'], b['s'], b['tl'])
        counts[key] = counts.get(key, 0)+1
      for f,n in counts.items():
        l = f[1]
        if (((l >= 0) and (n != 2*l+1)) or ((l < 0) and (n != (-l+1)*(-l+2)/2))):
          error = 'Inconsistent basis function IDs. The file could have been created by a buggy or unsupported OpenMolcas version'
          raise Exception(error)
      # Maximum angular momentum in the whole basis set,
      maxl = max([p[1] for p in prids])
      for i,c in enumerate(self.centers):
        c['basis'] = []
        c['cart'] = {}
        for l in range(maxl+1):
          ll = []
          # number of shells for this l and center
          maxshell = max([0] + [p[2] for p in prids if ((p[0] == i+1) and (p[1] == l))])
          for s in range(maxshell):
            # find out if this is a Cartesian shell (if the l is negative)
            # note that Cartesian shells never have (nor are) contaminants,
            # and since contaminants come after regular shells,
            # it should be safe to save just l and s
            if ((i+1, -l, s+1) in bf_cart):
              c['cart'][(l, s)] = True
            # get exponents and coefficients
            ll.append([0, [pp.tolist() for p,pp in zip(prids, prims) if ((p[0] == i+1) and (p[1] == l) and (p[2] == s+1))]])
          c['basis'].append(ll)
        # Add contaminant shells, that is, additional shells for lower l, with exponents and coefficients
        # from a higher l, and with some power of r**2
        for l in range(maxl-1):
          # find basis functions for this center and l, where l != tl
          cont = [(b['l'],b['tl'],b['s']) for b in bf_id[np.logical_and(bf_id['c']==i+1, bf_id['l']==l)] if (b['l'] != b['tl'])]
          # get a sorted unique set
          cont = sorted(set(cont))
          # copy the exponents and coefficients from the higher l and set the power of r**2
          for j in cont:
            new = deepcopy(c['basis'][j[1]][j[2]-1])
            new[0] = (j[1]-j[0])//2
            c['basis'][l].append(new)
      # At this point each center[i]['basis'] is a list of maxl items, one for each value of l,
      # each item is a list of shells,
      # each item is [power of r**2, primitives],
      # each "primitives" is a list of [exponent, coefficient]
      # Now get the indices for sorting all the basis functions (2l+1 or (l+1)(l+2)/2 for each shell)
      # by center, l, m, "true l", shell
      # To get the correct sorting for Cartesian shells, invert l
      for b in bf_id:
        if (b['l'] < 0):
          b['l'] *= -1
      self.bf_sort = np.argsort(bf_id, order=('c', 'l', 'm', 'tl', 's'))
      # And sph_c can be computed
      self.set_sph_c(maxl)
    # Reading the basis set invalidates the orbitals, if any
    self.MO = None
    self.MO_a = None
    self.MO_b = None

  # Read molecular orbitals from an HDF5 file
  def read_h5_MO(self):
    with h5py.File(self.file, 'r') as f:
      # Read the orbital properties
      if ('MO_ENERGIES' in f):
        mo_en = f['MO_ENERGIES'][:]
        mo_oc = f['MO_OCCUPATIONS'][:]
        mo_cf = f['MO_VECTORS'][:]
        if ('MO_TYPEINDICES' in f):
          mo_ti = f['MO_TYPEINDICES'][:]
        else:
          mo_ti = [b'?' for i in mo_oc]
      else:
        mo_en = []
        mo_oc = []
        mo_cf = []
        mo_ti = []
      if ('MO_ALPHA_ENERGIES' in f):
        mo_en_a = f['MO_ALPHA_ENERGIES'][:]
        mo_oc_a = f['MO_ALPHA_OCCUPATIONS'][:]
        mo_cf_a = f['MO_ALPHA_VECTORS'][:]
        if ('MO_ALPHA_TYPEINDICES' in f):
          mo_ti_a = f['MO_ALPHA_TYPEINDICES'][:]
        else:
          mo_ti_a = [b'?' for i in mo_oc_a]
      else:
        mo_en_a = []
        mo_oc_a = []
        mo_cf_a = []
        mo_ti_a = []
      if ('MO_BETA_ENERGIES' in f):
        mo_en_b = f['MO_BETA_ENERGIES'][:]
        mo_oc_b = f['MO_BETA_OCCUPATIONS'][:]
        mo_cf_b = f['MO_BETA_VECTORS'][:]
        if ('MO_BETA_TYPEINDICES' in f):
          mo_ti_b = f['MO_BETA_TYPEINDICES'][:]
        else:
          mo_ti_b = [b'?' for i in mo_oc_b]
      else:
        mo_en_b = []
        mo_oc_b = []
        mo_cf_b = []
        mo_ti_b = []
      mo_ti = [str(i.decode('ascii')) for i in mo_ti]
      mo_ti_a = [str(i.decode('ascii')) for i in mo_ti_a]
      mo_ti_b = [str(i.decode('ascii')) for i in mo_ti_b]
      self.MO = [{'ene':e, 'occup':o, 'type':t} for e,o,t in zip(mo_en, mo_oc, mo_ti)]
      self.MO_a = [{'ene':e, 'occup':o, 'type':t} for e,o,t in zip(mo_en_a, mo_oc_a, mo_ti_a)]
      self.MO_b = [{'ene':e, 'occup':o, 'type':t} for e,o,t in zip(mo_en_b, mo_oc_b, mo_ti_b)]
      # Read the coefficients
      ii = [sum(self.N_bas[:i]) for i in range(len(self.N_bas))]
      j = 0
      for i,b,s in zip(ii, self.N_bas, self.irrep):
        for orb,orb_a,orb_b in zip_longest(self.MO[i:i+b], self.MO_a[i:i+b], self.MO_b[i:i+b]):
          if (orb):
            orb['sym'] = s
            orb['coeff'] = np.zeros(sum(self.N_bas))
            orb['coeff'][i:i+b] = mo_cf[j:j+b]
          if (orb_a):
            orb_a['sym'] = s
            orb_a['coeff'] = np.zeros(sum(self.N_bas))
            orb_a['coeff'][i:i+b] = mo_cf_a[j:j+b]
          if (orb_b):
            orb_b['sym'] = s
            orb_b['coeff'] = np.zeros(sum(self.N_bas))
            orb_b['coeff'][i:i+b] = mo_cf_b[j:j+b]
          j += b
      # Desymmetrize the MOs
      if (len(self.N_bas) > 1):
        for orb in self.MO + self.MO_a + self.MO_b:
          orb['coeff'] = np.dot(self.mat, orb['coeff'])
      self.roots = ['Average']
      self.dm = [np.diag([o['occup'] for o in self.MO if (o['type'] in ['1', '2', '3'])])]
      self.sdm = None
      self.tdm = None
      self.H_eff = None
      mod = None
      if ('MOLCAS_MODULE' in f.attrs):
        mod = f.attrs['MOLCAS_MODULE'].decode('ascii')
      if (mod == 'CASPT2'):
        self.wf = 'PT2'
        self.roots[0] = 'Reference'
        # For CASPT2 the density matrices are symmetry-blocked, and for all orbitals (not F or D),
        # here we convert them to square, with full size
        self.dm = np.array([np.diag([o['occup'] for o in self.MO if (o['type'] not in ['F', 'D'])])])
        if ('DENSITY_MATRIX' in f):
          rootids = f.attrs['STATE_ROOTID'][:]
          for root in range(len(rootids)):
            self.dm = np.concatenate((self.dm, [np.zeros_like(self.dm[0])]))
            nMO = [(sum(self.N_bas[:i]), sum(self.N_bas[:i+1])) for i in range(len(self.N_bas))]
            j = 0
            k = 0
            for i,nbas in zip(nMO, self.N_bas):
              n = len([o for o in self.MO[i[0]:i[1]] if (o['type'] not in ['F', 'D'])])
              j1 = int(n*(n+1)/2)
              dm = np.zeros((n, n))
              dm[np.tril_indices(n, 0)] = f['DENSITY_MATRIX'][root,j:j+j1]
              dm = dm + np.tril(dm, -1).T
              self.dm[-1][k:k+n,k:k+n] = dm
              j += j1
              k += n
          # For MS-CASPT2, the densities are SS, but the energies are MS,
          # so take the energies from the effective Hamiltonian matrix instead
          if ('H_EFF' in f):
            self.H_eff = f['H_EFF'][:]
            self.roots.extend(['{0}: {1:.6f}'.format(i, e) for i,e in zip(rootids, np.diag(self.H_eff))])
            self.msroots = ['Reference']
            self.msroots.extend(['{0}: {1:.6f}'.format(i+1, e) for i,e in enumerate(f['STATE_PT2_ENERGIES'])])
          else:
            self.roots.extend(['{0}: {1:.6f}'.format(i, e) for i,e in zip(rootids, f['STATE_PT2_ENERGIES'])])
      else:
        if ('DENSITY_MATRIX' in f):
          self.dm = np.concatenate((self.dm, f['DENSITY_MATRIX'][:]))
          rootids = [i+1 for i in range(f.attrs['NROOTS'])]
          self.roots.extend(['{0}: {1:.6f}'.format(i, e) for i,e in zip(rootids, f['ROOT_ENERGIES'])])
        if ('SPINDENSITY_MATRIX' in f):
          sdm = f['SPINDENSITY_MATRIX'][:]
          if (not np.allclose(sdm, np.zeros_like(sdm))):
            sdm = np.insert(sdm, 0, np.mean(sdm, axis=0), axis=0)
            self.sdm = sdm
        if ('TRANSITION_DENSITY_MATRIX' in f):
          tdm = f['TRANSITION_DENSITY_MATRIX'][:]
          if (not np.allclose(tdm, np.zeros_like(tdm))):
            self.tdm = tdm
      # Read the optional notes
      if ('Pegamoid_notes' in f):
        self.notes = f['Pegamoid_notes'][:]

  # Read basis set from a Molden file
  def read_molden_basis(self):
    with open(self.file, 'r') as f:
      # Molden supports up to g functions, and by default all are Cartesian
      ang_labels = 'spdfg'
      cart = [False, True, True, True, True]
      # Specify the order of the Cartesian components according to the convention (see ang)
      order = []
      order.append([0])
      order.append([-1, 0, 1])
      order.append([-2, 1, 3, -1, 0, 2])
      order.append([-3, 3, 6, 0, -2, -1, 2, 5, 4, 1])
      order.append([-4, 6, 10, -3, -2, 2, 7, 5, 9, -1, 1, 8, 0, 3, 4])
      maxl = 0
      done = True
      if (re.search(r'\[MOLDEN FORMAT\]', f.readline(), re.IGNORECASE)):
        done = False
      line = ' '
      while ((not done) and (line != '')):
        line = f.readline()
        # Read the geometry
        if re.search(r'\[N_ATOMS\]', line, re.IGNORECASE):
          num = int(f.readline())
        elif re.search(r'\[ATOMS\]', line, re.IGNORECASE):
          unit = 1
          if (re.search(r'Angs', line, re.IGNORECASE)):
            unit = 1/0.52917721092
          self.centers = []
          for i in range(num):
            l, _, q, x, y, z = f.readline().split()
            self.centers.append({'name':l, 'Z':int(q), 'xyz':np.array([float(x), float(y), float(z)])*unit})
          self.geomcenter = (np.amin([c['xyz'] for c in self.centers], axis=0) + np.amax([c['xyz'] for c in self.centers], axis=0))/2
        # Read tags for spherical shells
        elif re.search(r'\[5D\]', line, re.IGNORECASE):
          cart[2] = False
          cart[3] = False
        elif re.search(r'\[5D7F\]', line, re.IGNORECASE):
          cart[2] = False
          cart[3] = False
        elif re.search(r'\[5D10F\]', line, re.IGNORECASE):
          cart[2] = False
          cart[3] = True
        elif re.search(r'\[7F\]', line, re.IGNORECASE):
          cart[3] = False
        elif re.search(r'\[9G\]', line, re.IGNORECASE):
          cart[4] = False
        # Read basis functions: a series of blank-separated blocks
        # starting with center number and followed by all the shells,
        # each is the angular momentum letter and number of primitives,
        # plus this number of exponents and coefficients.
        elif re.search(r'\[GTO\]', line, re.IGNORECASE):
          bf_id = []
          while (True):
            save = f.tell()
            # First find out if this is another center, or the basis set
            # specification has finished
            try:
              n = int(f.readline())
            except:
              f.seek(save)
              break
            self.centers[n-1]['cart'] = []
            basis = {}
            # Read the shells for this center
            while (True):
              try:
                l, nprim = f.readline().split()
                nprim = int(nprim)
                # The special label "sp" has the same exponent
                # but different coefficients for s and p functions
                if (l.lower() == 'sp'):
                  if (0 not in basis):
                    basis[0] = []
                  basis[0].append([0, []])
                  if (1 not in basis):
                    basis[1] = []
                  basis[1].append([0, []])
                  for i in range(nprim):
                    e, c1, c2 = (float(i) for i in f.readline().split())
                    basis[0][-1][1].append([e, c1])
                    basis[1][-1][1].append([e, c2])
                  bf_id.append([n, len(basis[0]), 0, 0])
                  if (cart[0]):
                    self.centers[n-1]['cart'].append((0, len(basis[0])-1))
                  if (cart[1]):
                    self.centers[n-1]['cart'].append((1, len(basis[1])-1))
                  for i in order[1]:
                    bf_id.append([n, len(basis[1]), -1, i])
                else:
                  l = ang_labels.index(l.lower())
                  if (l not in basis):
                    basis[l] = []
                  basis[l].append([0, []])
                  # Read exponents and coefficients
                  for i in range(nprim):
                    e, c = (float(i) for i in f.readline().split())
                    basis[l][-1][1].append([e, c])
                  # Set up the basis_id
                  if (cart[l]):
                    self.centers[n-1]['cart'].append((l, len(basis[l])-1))
                    for i in order[l]:
                      bf_id.append([n, len(basis[l]), -l, i])
                  else:
                    for i in range(l+1):
                      bf_id.append([n, len(basis[l]), l, i])
                      if (i > 0):
                        bf_id.append([n, len(basis[l]), l, -i])
              except:
                break
            nl = max(basis.keys())
            maxl = max(maxl, nl)
            self.centers[n-1]['basis'] = [[] for i in range(nl+1)]
            for i in basis.keys():
              self.centers[n-1]['basis'][i] = basis[i][:]
          # At this point each center[i]['basis'] is a list of maxl items, one for each value of l,
          # each item is a list of shells,
          # each item is [power of r**2, primitives],
          # each "primitives" is a list of [exponent, coefficient]
        elif re.search(r'\[MO\]', line, re.IGNORECASE):
          done = True
      # Now get the normalization factors and invert l for Cartesian shells
      # The factor is 1/sqrt(N(lx)*N(ly)*N(lz)), where N(x) is the double factorial of 2*x-1
      # N(0)=1, N(1)=1, N(2)=1*3, N(3)=1*3*5, ...
      self.fact = np.full(len(bf_id), 1.0)
      bf_id = np.rec.fromrecords(bf_id, names='c, s, l, m')
      for i,b in enumerate(bf_id):
        if (b['l'] < 0):
          b['l'] *= -1
          ly = int(np.floor((np.sqrt(8*(b['m']+b['l'])+1)-1)/2))
          lz = b['m']+b['l']-ly*(ly+1)//2
          lx = b['l']-ly
          ly -= lz
          lx = self._binom(2*lx, lx)*np.math.factorial(lx)//2**lx
          ly = self._binom(2*ly, ly)*np.math.factorial(ly)//2**ly
          lz = self._binom(2*lz, lz)*np.math.factorial(lz)//2**lz
          self.fact[i] = 1.0/np.sqrt(float(lx*ly*lz))
      # And get the indices for sorting the basis functions by center, l, m, shell
      self.bf_sort = np.argsort(bf_id, order=('c', 'l', 'm', 's'))
      self.head = f.tell()
      self.N_bas = [len(bf_id)]
      self.set_sph_c(maxl)
    # Reading the basis set invalidates the orbitals, if any
    self.MO = None
    self.MO_a = None
    self.MO_b = None

  # Read molecular orbitals from a Molden file
  def read_molden_MO(self):
    self.MO = []
    self.MO_a = []
    self.MO_b = []
    # Each orbital is a header with properties and a list of coefficients
    with open(self.file, 'r') as f:
      f.seek(self.head)
      while (True):
        try:
          sym = re.sub(r'^\d*', '', f.readline().split()[1])
          ene = float(f.readline().split()[1])
          spn = 'b' if (f.readline().split()[1] == 'Beta') else 'a'
          occ = float(f.readline().split()[1])
          cff = np.zeros(sum(self.N_bas))
          for i in range(sum(self.N_bas)):
            n, c = f.readline().split()
            cff[int(n)-1] = float(c)
          # Save the orbital as alpha or beta
          if (spn == 'b'):
            self.MO_b.append({'ene':ene, 'occup':occ, 'sym':sym, 'type':'?', 'coeff':self.fact*cff})
          else:
            self.MO_a.append({'ene':ene, 'occup':occ, 'sym':sym, 'type':'?', 'coeff':self.fact*cff})
        except:
          break
    # Build the list of irreps from the orbitals
    self.irrep = []
    for o in self.MO_a + self.MO_b:
      if (o['sym'] not in self.irrep):
        self.irrep.append(o['sym'])
    if (not self.MO_b):
      self.MO = deepcopy(self.MO_a)
      self.MO_a = []

  # Read molecular orbitals from an InpOrb file
  def read_inporb_MO(self, infile):
    if (self.type != 'hdf5'):
      return 'Current file is not HDF5'
    self.file = infile
    self.inporb = 0
    fortrannums = re.compile(r'-?\d*\.\d*[EeDd][+-]\d*(?!\.)')
    sections = {}
    with open(infile, 'r') as f:
      line = f.readline()
      # First read the header section (which must be the first) and
      # make sure the number of basis functions matches the current values
      while ((not line.startswith('#INFO')) and (line != '')):
        line = f.readline()
      sections['INFO'] = True
      line = f.readline()
      uhf, nsym, _ = (int(i) for i in f.readline().split())
      N_bas = np.array([int(i) for i in f.readline().split()])
      nMO = np.array([int(i) for i in f.readline().split()])
      if (not np.array_equal(N_bas, self.N_bas)):
        return 'Incompatible InpOrb data'
      # Decide whether or not beta orbitals will be read
      if (uhf):
        self.MO_b = deepcopy(self.MO)
      else:
        self.MO_a = []
        self.MO_b = []
      ii = [sum(self.N_bas[:i]) for i in range(len(self.N_bas))]
      # Read until EOF
      while (line != ''):
        # Find next section
        while ((not line.startswith('#')) and (line != '')):
          line = f.readline()
        # Read orbital coefficients, only the non-zero (by symmetry)
        # coefficients are written in the file
        if (line.startswith('#ORB')):
          sections['ORB'] = True
          line = '\n'
          j = 0
          for i,b,s in zip(ii, self.N_bas, self.irrep):
            for orb in self.MO[i:i+b]:
              orb['sym'] = s
              orb['coeff'] = np.zeros(sum(self.N_bas))
              cff = []
              f.readline()
              while (len(cff) < b):
                line = f.readline()
                if (re.search(r'\.[^ ]*\.', line)):
                  cff.extend(fortrannums.findall(line))
                else:
                  cff.extend(line.split())
              orb['coeff'][i:i+b] = [float(c) for c in cff]
              j += b
        elif (line.startswith('#UORB')):
          sections['UORB'] = True
          line = '\n'
          if (uhf):
            j = 0
            for i,b,s in zip(ii, self.N_bas, self.irrep):
              for orb in self.MO_b[i:i+b]:
                orb['sym'] = s
                orb['coeff'] = np.zeros(sum(self.N_bas))
                cff = []
                f.readline()
                while (len(cff) < b):
                  line = f.readline()
                  if (re.search(r'\.[^ ]*\.', line)):
                    cff.extend(fortrannums.findall(line))
                  else:
                    cff.extend(line.split())
                orb['coeff'][i:i+b] = [float(c) for c in cff]
                j += b
        # Read the occupations
        elif (line.startswith('#OCC')):
          sections['OCC'] = True
          line = '\n'
          f.readline()
          occ = []
          for i,b in zip(ii, self.N_bas):
            while (len(occ) < i+b):
              line = f.readline()
              if (re.search(r'\.[^ ]*\.', line)):
                occ.extend(fortrannums.findall(line))
              else:
                occ.extend(line.split())
        elif (line.startswith('#UOCC')):
          sections['UOCC'] = True
          line = '\n'
          if (uhf):
            f.readline()
            for i,b in zip(ii, self.N_bas):
              while (len(occ) < len(self.MO)+i+b):
                line = f.readline()
                if (re.search(r'\.[^ ]*\.', line)):
                  occ.extend(fortrannums.findall(line))
                else:
                  occ.extend(line.split())
        # Read the energies
        elif (line.startswith('#ONE')):
          sections['ONE'] = True
          line = '\n'
          f.readline()
          ene = []
          for i,b in zip(ii, self.N_bas):
            while (len(ene) < i+b):
              line = f.readline()
              if (re.search(r'\.[^ ]*\.', line)):
                ene.extend(fortrannums.findall(line))
              else:
                ene.extend(line.split())
        elif (line.startswith('#UONE')):
          sections['UONE'] = True
          line = '\n'
          if (uhf):
            f.readline()
            for i,b in zip(ii, self.N_bas):
              while (len(ene) < len(self.MO)+i+b):
                line = f.readline()
                if (re.search(r'\.[^ ]*\.', line)):
                  ene.extend(fortrannums.findall(line))
                else:
                  ene.extend(line.split())
        # Read the orbital types (same for alpha and beta)
        elif (line.startswith('#INDEX')):
          sections['INDEX'] = True
          line = '\n'
          idx = ''
          for i,b in zip(ii, self.N_bas):
            line = f.readline()
            while (len(idx) < i+b):
              idx += f.readline().split()[1]
          for i,o in enumerate(self.MO):
            o['type'] = idx[i].upper()
            o.pop('newtype', None)
          for i,o in enumerate(self.MO_b):
            o['type'] = idx[i].upper()
            o.pop('newtype', None)
        elif (line.startswith('#')):
          line = '\n'
      # Desymmetrize the orbital coefficients
      if (sections.get('ORB')):
        if (uhf and (not sections.get('UORB'))):
          return 'No UORB section'
        if (len(self.N_bas) > 1):
          for orb in self.MO + self.MO_b:
            orb['coeff'] = np.dot(self.mat, orb['coeff'])
      else:
        return 'No ORB section'
      # Assign occupations
      if (sections.get('OCC')):
        if (uhf and (not sections.get('UOCC'))):
          return 'No UOCC section'
        for i,o in enumerate(self.MO + self.MO_b):
          o['occup'] = float(occ[i])
      else:
        for o in self.MO + self.MO_b:
          o['occup'] = 0.0
      # Assign energies
      if (sections.get('ONE')):
        if (uhf and (not sections.get('UONE'))):
          return 'No UONE section'
        for i,o in enumerate(self.MO + self.MO_b):
          o['ene'] = float(ene[i])
      else:
        for o in self.MO + self.MO_b:
          o['ene'] = 0.0
    # Clear types
    if (not sections.get('INDEX')):
      for o in self.MO + self.MO_b:
        o['type'] = '?'
        o.pop('newtype', None)
    for o in self.MO + self.MO_b:
      o.pop('root_coeff', None)
      o.pop('root_coeffl', None)
      o.pop('root_coeffr', None)
      o.pop('root_occup', None)
      o.pop('root_type', None)
      o.pop('root_ene', None)

    if (self.MO_b):
      self.MO_a = deepcopy(self.MO)
      self.MO = []
    self.roots = ['InpOrb']
    self.dm = [np.diag([o['occup'] for o in self.MO if (o['type'] in ['1', '2', '3'])])]
    self.sdm = None
    self.tdm = None
    self.H_eff = None

    return True

  # Set the Cartesian coefficients for spherical harmonics
  def set_sph_c(self, maxl):
    # Get the coefficients for each value of l,m
    self.sph_c = []
    for l in range(maxl+1):
      s = {}
      for m in range(-l, l+1):
        s[m] = []
        # Go through all possible lx+ly+lz=l
        for lx in range(l+1):
          for ly in range(l-lx+1):
            lz = l - lx - ly
            # Get the coefficient (c_sph returns the square as a fraction with the sign)
            c = float(self._c_sph(l, m, lx, ly, lz))
            c = np.sign(c)*np.sqrt(abs(c))
            if (c != 0):
              s[m].append([c, [lx, ly, lz]])
      self.sph_c.append(s)
    # Now sph_c is a list of items for each l,
    # each item is a dict for each m,
    # each item is a list for each non-zero contribution,
    # each item is a list of coefficient and [lx, ly, lz] (x**lx * y**ly * z**lz)

  # Compute the angular component with quantum numbers l,m in an x,y,z grid
  # If cart=True, this is for a Cartesian shell
  def ang(self, x, y, z, l, m, cart=False):
    if (cart):
      # For Cartesian shells, m does not actually contain m, but:
      # m = T(ly+lz)-(lx+ly), where T(n) = n*(n+1)/2 is the nth triangular number
      ly = int(np.floor((np.sqrt(8*(m+l)+1)-1)/2))
      lz = m+l-ly*(ly+1)//2
      lx = l-ly
      ly -= lz
      assert (lx >= 0) and (ly >= 0) and (lz >= 0)
      c = np.sqrt(2**l)
      ang = c * x**lx * y**ly * z**lz
    else:
      ang = 0
      # Once sph_c has been computed, this is trivial
      for c in self.sph_c[l][m]:
        ang += c[0] * (x**c[1][0] * y**c[1][1] * z**c[1][2])
    return ang

  # Compute the radial component, with quantum number l, given the values of r**2 (as r2),
  # for a list of primitive Gaussians (exponents and coefficients, as ec)
  # and an optional power of r**2 (for contaminants)
  def rad(self, r2, l, ec, p=0, cache=None):
    rad = 0
    # For contaminants, the radial part is multiplied by r**(2*p)
    # and the normalization must be corrected, noting that the
    # angular part already includes a factor r**l
    if (p > 0):
      m = Fraction(2*l+1, 2*l+4*p+1)
      for i in range(2*l+1, 2*l+4*p, 2):
        m /= i
      m = np.sqrt(float(m))
      prad = np.power(r2, p)
    for e,c in ec:
      if (c != 0.0):
        if ((cache is None) or ((e,p) not in cache)):
          N = np.power((2*e)**(3+2*l)/np.pi**3, 0.25)
          if (p > 0):
            N *= m*np.power(4*e, p)
            cch = N * np.exp(-e*r2)*prad
          else:
            cch = N * np.exp(-e*r2)
          if (cache is not None):
            cache[(e,p)] = np.copy(cch)
        else:
          cch = cache[(e,p)]
        rad += c*cch
    return rad

  # Compute an atomic orbital as product of angular and radial components
  def ao(self, x, y, z, ec, l, m, p=0):
    ang = self.ang(x, y, z, l, m)
    r2 = x**2+y**2+z**2
    rad = self.rad(r2, l, ec, p)
    return ang*rad

  # Compute a molecular orbital, as linear combination of atomic orbitals
  # at different centers. It can use a cache of atomic orbitals to avoid
  # recomputing them. "spin" specifies if the coefficients will be taken
  # from self.MO (alpha) or self.MO_b (beta)
  def mo(self, n, x, y, z, spin='n', cache=None, callback=None, interrupt=False):
    mo = np.zeros_like(x)
    # Reorder MO coefficients
    if (spin == 'b'):
      MO = self.MO_b[n]
    elif (spin == 'a'):
      MO = self.MO_a[n]
    else:
      MO = self.MO[n]
    if ('root_coeff' in MO):
      MO = MO['root_coeff'][self.bf_sort]
    else:
      MO = MO['coeff'][self.bf_sort]

    if (callback is None):
      actions = [True]
    else:
      num = 0
      total = 0
      actions = [False, True]

    npoints = x.size
    if (cache is not None):
      chunk_size = cache.shape[1]
    use_cache = (cache is not None) and (chunk_size >= npoints)

    for compute in actions:
      f = 0
      # For each center, the relative x,y,z and r**2 are different
      for c in self.centers:
        x0, y0, z0 = [None]*3
        r2 = None
        # For each center, l and shell we have different radial parts
        for l,ll in enumerate(c['basis']):
          # Since all shells are computed for each m value, but the radial
          # part does not depend on m, we will save the radial part for
          # each shell to reuse it. This is a dict and not a list because
          # some shells could be skipped altogether
          rad_l = {}
          prim_cache = {}
          # For each center, l and m we have different angular parts
          # (the range includes both spherical and Cartesian indices)
          #for m in range(-l, l*(l+1)+1):
          for m in range(-l, l*(l+1)//2+1):
            ao_ang = None
            cart = None
            # Now each shell is an atomic orbital (basis function)
            for s,p in enumerate(ll):
              if (interrupt):
                return mo
              # Skip when out of range for spherical shells
              # Also invalidate the angular part if for some reason
              # there is a mixture of types among shells
              if ((l, s) in c['cart']):
                if (cart is False):
                  ang = None
                cart = True
              else:
                if (cart is True):
                  ang = None
                cart = False
                if (m > l):
                  continue
              # Only compute if above threshold
              if (abs(MO[f]) > self.eps):
                if (compute):
                  if callback is not None:
                    num += 1
                    callback('Computing: {0}/{1} ...'.format(num, total))
                  # The AO contribution is either in the cache
                  # or we compute it now
                  if (not use_cache or np.isnan(cache[f,0])):
                    # Compute relative coordinates if not done yet
                    if (x0 is None):
                      x0, y0, z0 = [x, y, z] - c['xyz'][:, np.newaxis]
                      r2 = x0**2 + y0**2 + z0**2
                    # Compute angular part if not done yet
                    if (ao_ang is None):
                      ao_ang = self.ang(x0, y0, z0, l, m, cart=cart)
                    # Compute radial part if not done yet
                    if (s not in rad_l):
                      rad_l[s] = self.rad(r2, l, p[1], p[0], cache=prim_cache)
                    cch = ao_ang*rad_l[s]
                    # Save in the cache if enabled
                    if (use_cache):
                      cache[f][0:cch.size] = np.copy(cch)
                  elif (use_cache):
                    cch = cache[f][0:x.size]
                  # Add the AO contribution to the MO
                  mo += MO[f]*cch
                else:
                  total += 1
              f += 1
    if (use_cache):
      cache.flush()
    return mo

  # Compute electron density as sum of square of (natural) orbitals times occupation.
  # It can use a cache for MO evaluation and a mask to select only some orbitals.
  def dens(self, x, y, z, cache=None, mask=None, spin=False, callback=None, interrupt=False):
    dens = np.zeros_like(x)
    if (self.MO_b):
      MO_list = [j for i in zip_longest(self.MO_a, self.MO_b) for j in i]
    else:
      MO_list = self.MO
    # If there is a callback function, we take two passes,
    # one to count the orbitals and another to actually compute them
    if (callback is None):
      actions = [True]
    else:
      total = 0
      actions = [False, True]

    npoints = x.size
    if (cache is not None):
      chunk_size = cache.shape[1]
    else:
      chunk_size = npoints
    chunk_list = list(range(0, npoints, chunk_size))

    for compute in actions:
      if (compute):
        do_list = chunk_list
      else:
        do_list = [0]
      for chunk,start in enumerate(do_list):
        if ((cache is not None) and (len(do_list) > 1)):
          cache[:,0] = np.nan
        x_ = x[start:start+chunk_size]
        y_ = y[start:start+chunk_size]
        z_ = z[start:start+chunk_size]
        num = 0
        j = 0
        for i,orb in enumerate(MO_list):
          if (interrupt):
            return dens
          if (orb is None):
            continue
          f = 1.0
          if (MO_list is self.MO):
            # Natural orbitals
            ii = i
            s = 'n'
          else:
            # Add alternated alpha and beta orbitals
            ii = i//2
            if (i%2 == 0):
              s = 'a'
            else:
              s = 'b'
              if (spin):
                f = -1.0
          if ((mask is None) or mask[j]):
            occup = f*orb.get('root_occup', orb['occup'])
            if (abs(occup) > self.eps):
              if (compute):
                if callback is not None:
                  num += 1
                  if (len(do_list) > 1):
                    callback('Computing: {0}/{1} (chunk {2}/{3}) ...'.format(num, total, chunk+1, len(do_list)))
                  else:
                    callback('Computing: {0}/{1} ...'.format(num, total))
                dens[start:start+chunk_size] += occup*self.mo(ii, x_, y_, z_, s, cache, interrupt=interrupt)**2
              else:
                total += 1
          j += 1
    return dens

  # Compute the Laplacian of a field by central finite differences
  def laplacian(self, box, field):
    n = field.shape
    box[:,0] /= n[0]-1
    box[:,1] /= n[1]-1
    box[:,2] /= n[2]-1
    g = np.linalg.inv(np.dot(box.T, box))
    data = -2*field*(sum(np.diag(g)))
    for i in range(n[0]):
      if ((i == 0) or (i == n[0]-1)):
        data[i,:,:] = None
      else:
        data[i,:,:] += (field[i-1,:,:]+field[i+1,:,:])*g[0,0]
        if (abs(g[0,1]) > 0):
          for j in range(1, n[1]-1):
            data[i,j,:] += (field[i-1,j-1,:]+field[i+1,j+1,:]-field[i-1,j+1,:]-field[i+1,j-1,:])*g[0,1]/2
        if (abs(g[0,2]) > 0):
          for k in range(1, n[2]-1):
            data[i,:,k] += (field[i-1,:,k-1]+field[i+1,:,k+1]-field[i-1,:,k+1]-field[i+1,:,k-1])*g[0,2]/2
    for j in range(n[1]):
      if ((j == 0) or (j == n[1]-1)):
        data[:,j,:] = None
      else:
        data[:,j,:] += (field[:,j-1,:]+field[:,j+1,:])*g[1,1]
        if (abs(g[1,2]) > 0):
          for k in range(1, n[2]-1):
            data[:,j,k] += (field[:,j-1,k-1]+field[:,j+1,k+1]-field[:,j-1,k+1]-field[:,j+1,k-1])*g[1,2]/2
    for k in range(n[2]):
      if ((k == 0) or (k == n[2]-1)):
        data[:,:,k] = None
      else:
        data[:,:,k] += (field[:,:,k-1]+field[:,:,k+1])*g[2,2]
    return data

  # Returns binomial coefficient as a fraction
  # Easy overflow for large arguments, but we are interested in relatively small arguments
  def _binom(self, n, k):
    mk = max(k,n-k)
    try:
      binom = Fraction(np.math.factorial(n), np.math.factorial(mk))
      binom *= Fraction(1, np.math.factorial(n-mk))
      assert (binom.denominator == 1)
    except ValueError:
      binom = Fraction(0, 1)
    return binom

  # Computes the coefficient for x^lx * y^ly * z^lz in the expansion of
  # the real solid harmonic S(l,±m) = C * r^l*(Y(l,m)±Y(l,-m))
  # Since the coefficients are square roots of rational numbers, this
  # returns the square of the coefficient as a fraction, with its sign
  #
  # See:
  # Transformation between Cartesian and pure spherical harmonic Gaussians
  # doi: 10.1002/qua.560540202
  # (note that there appears to be a error in v(4,0), the coefficient 1/4
  #  should probably be 3/4*sqrt(3/35) )
  def _c_sph(self, l, m, lx, ly, lz):
    assert (lx + ly + lz == l) and (lx >= 0) and (ly >= 0) and (lz >= 0)
    am = abs(m)
    assert (am <= l)
    j = lx + ly - am
    if (j % 2 == 0):
      j = j//2
    else:
      return Fraction(0, 1)
    c = 0
    for i in range((l-am)//2+1):
      c += self._binom(l, i) * self._binom(i, j) * Fraction(np.math.factorial(2*l-2*i), np.math.factorial(l-am-2*i)) * (-1)**i
    if (c == 0):
      return Fraction(0, 1)
    c_sph = c
    c = 0
    for k in range(j+1):
      c += self._binom(j, k) * self._binom(am, lx-2*k) * 1j**(am-lx+2*k)
    if (m >= 0):
      c = int(np.real(c))
    else:
      c = int(np.imag(c))
    if (c == 0):
      return Fraction(0, 1)
    c_sph *= c
    if (c_sph < 0):
      c_sph *= -c_sph
    else:
      c_sph *= c_sph
    if (m == 0):
      lm = 1
    else:
      lm = 2
    c = Fraction(np.math.factorial(l-am), np.math.factorial(l+am))
    c *= Fraction(lm, np.math.factorial(l))
    c *= Fraction(1, np.math.factorial(2*l))
    c_sph *= c
    return c_sph

  # Writes a new HDF5 file
  def write_hdf5(self, filename):
    with h5py.File(self.h5file, 'r') as fi, h5py.File(filename, 'w') as fo:
      fo.attrs['Pegamoid_version'] = '{0} {1}'.format(__name__, __version__)
      # Copy some data from the original file
      for a in ['NSYM', 'NBAS', 'NPRIM', 'IRREP_LABELS', 'NATOMS_ALL', 'NATOMS_UNIQUE']:
        if (a in fi.attrs):
          fo.attrs[a] = fi.attrs[a]
      for d in ['CENTER_LABELS', 'CENTER_CHARGES', 'CENTER_COORDINATES', 'BASIS_FUNCTION_IDS',
                'DESYM_CENTER_LABELS', 'DESYM_CENTER_CHARGES', 'DESYM_CENTER_COORDINATES', 'DESYM_BASIS_FUNCTION_IDS', 'DESYM_MATRIX',
                'PRIMITIVES', 'PRIMITIVE_IDS']:
        if (d in fi):
          fi.copy(d, fo)
      if (len(self.N_bas) > 1):
        sym = np.linalg.inv(self.mat)
      else:
        sym = np.eye(sum(self.N_bas))
      # Write orbital data from current orbitals
      # (could be loaded from InpOrb, selected from a root and/or have modified types)
      uhf = len(self.MO_b) > 0
      nMO = [(sum(self.N_bas[:i]), sum(self.N_bas[:i+1])) for i in range(len(self.N_bas))]
      if (uhf):
        cff = []
        for i,j in nMO:
          for k in range(i,j):
            cff.extend(np.dot(sym, self.MO_a[k].get('root_coeff', self.MO_a[k]['coeff']))[i:j])
        fo.create_dataset('MO_ALPHA_VECTORS', data=cff)
        cff = []
        for i,j in nMO:
          for k in range(i,j):
            cff.extend(np.dot(sym, self.MO_b[k].get('root_coeff', self.MO_b[k]['coeff']))[i:j])
        fo.create_dataset('MO_BETA_VECTORS', data=cff)
        fo.create_dataset('MO_ALPHA_OCCUPATIONS', data=[o['occup'] for o in self.MO_a])
        fo.create_dataset('MO_BETA_OCCUPATIONS', data=[o['occup'] for o in self.MO_b])
        fo.create_dataset('MO_ALPHA_ENERGIES', data=[o['ene'] for o in self.MO_a])
        fo.create_dataset('MO_BETA_ENERGIES', data=[o['ene'] for o in self.MO_b])
        tp = [o.get('newtype', o['type']) for o in self.MO_a]
        for i,o in enumerate(self.MO_a):
          if (tp[i] == '?'):
            tp[i] = 'I' if (o['occup'] > 0.5) else 'S'
        fo.create_dataset('MO_ALPHA_TYPEINDICES', data=np.string_(tp))
        tp = [o.get('newtype', o['type'])for o in self.MO_b]
        for i,o in enumerate(self.MO_b):
          if (tp[i] == '?'):
            tp[i] = 'I' if (o['occup'] > 0.5) else 'S'
        fo.create_dataset('MO_BETA_TYPEINDICES', data=np.string_(tp))
      else:
        cff = []
        for i,j in nMO:
          for k in range(i,j):
            cff.extend(np.dot(sym, self.MO[k].get('root_coeff', self.MO[k]['coeff']))[i:j])
        fo.create_dataset('MO_VECTORS', data=cff)
        fo.create_dataset('MO_OCCUPATIONS', data=[o.get('root_occup', o['occup']) for o in self.MO])
        fo.create_dataset('MO_ENERGIES', data=[o.get('root_ene', o['ene']) for o in self.MO])
        tp = [o.get('newtype', o['type']) for o in self.MO]
        for i,o in enumerate(self.MO):
          if (tp[i] == '?'):
            tp[i] = 'I' if (o.get('root_occup', o['occup']) > 1.0) else 'S'
        fo.create_dataset('MO_TYPEINDICES', data=np.string_(tp))
      if (self.notes is not None):
        fo.create_dataset('Pegamoid_notes', data=np.string_(self.notes))

  # Creates an InpOrb file from scratch
  def create_inporb(self, filename, MO=None):
    nMO = OrderedDict()
    for i,n in zip(self.irrep, self.N_bas):
      nMO[i] = n
    uhf = (len(self.MO_b) > 0) and (MO is not self.MO)
    if (uhf):
      alphaMO = self.MO_a
      index, error = create_index(alphaMO, self.MO_b, nMO)
    else:
      alphaMO = self.MO
      index, error = create_index(alphaMO, [], nMO)
    if (index is None):
      if (error is not None):
        raise Exception(error)
      return
    if (len(self.N_bas) > 1):
      sym = np.linalg.inv(self.mat)
    else:
      sym = np.eye(sum(self.N_bas))
    nMO = [(sum(self.N_bas[:i]), sum(self.N_bas[:i+1])) for i in range(len(self.N_bas))]
    with open(filename, 'w') as f:
      f.write('#INPORB 2.2\n')
      f.write('#INFO\n')
      f.write('* File generated by {0} from {1}\n'.format(__name__, self.file))
      f.write(wrap_list([int(uhf), len(self.N_bas), 0], 3, '{:8d}')[0])
      f.write('\n')
      f.write(wrap_list(self.N_bas, 8, '{:8d}')[0])
      f.write('\n')
      f.write(wrap_list(self.N_bas, 8, '{:8d}')[0])
      f.write('\n')
      f.write('*BC:HOST {0} PID {1} DATE {2}\n'.format(gethostname(), os.getpid(), datetime.now().ctime()))
      f.write('#ORB\n')
      for s,(i,j) in enumerate(nMO):
        for k in range(i,j):
          f.write('* ORBITAL{0:5d}{1:5d}\n'.format(s+1, k-i+1))
          cff = alphaMO[k].get('root_coeff', alphaMO[k]['coeff'])
          cff = np.dot(sym, cff)
          cff = wrap_list(cff[i:j], 5, '{:21.14E}', sep=' ')
          f.write(' ' + '\n '.join(cff) + '\n')
      if (uhf):
        f.write('#UORB\n')
        for s,(i,j) in enumerate(nMO):
          for k in range(i,j):
            f.write('* ORBITAL{0:5d}{1:5d}\n'.format(s+1, k-i+1))
            cff = self.MO_b[k].get('root_coeff', self.MO_b[k]['coeff'])
            cff = np.dot(sym, cff)
            cff = wrap_list(cff[i:j], 5, '{:21.14E}', sep=' ')
            f.write(' ' + '\n '.join(cff) + '\n')
      f.write('#OCC\n')
      f.write('* OCCUPATION NUMBERS\n')
      for i,j in nMO:
        occ = wrap_list([o.get('root_occup', o['occup']) for o in alphaMO[i:j]], 5, '{:21.14E}', sep=' ')
        f.write(' ' + '\n '.join(occ) + '\n')
      if (uhf):
        f.write('#UOCC\n')
        f.write('* Beta OCCUPATION NUMBERS\n')
        for i,j in nMO:
          occ = wrap_list([o.get('root_occup', o['occup']) for o in self.MO_b[i:j]], 5, '{:21.14E}', sep=' ')
          f.write(' ' + '\n '.join(occ) + '\n')
      f.write('#ONE\n')
      f.write('* ONE ELECTRON ENERGIES\n')
      for i,j in nMO:
        ene = wrap_list([o.get('root_ene', o['ene']) for o in alphaMO[i:j]], 10, '{:11.4E}', sep=' ')
        f.write(' ' + '\n '.join(ene) + '\n')
      if (uhf):
        f.write('#UONE\n')
        f.write('* Beta ONE ELECTRON ENERGIES\n')
        for i,j in nMO:
          ene = wrap_list([o.get('root_ene', o['ene']) for o in self.MO_b[i:j]], 10, '{:11.4E}', sep=' ')
          f.write(' ' + '\n '.join(ene) + '\n')
      f.write('#INDEX\n')
      f.write('\n'.join(index))
      f.write('\n')

#===============================================================================
# Class for orbitals (or any other function) defined as values in a predefined
# grid.
# The orbitals and grid definition can be read from Cube, Grid and Luscus format
# (currently only ASCII/formatted for the former two).
# The orbital data is read on demand.

class Grid(object):

  def __init__(self, gridfile, ftype):
    self.inporb = None
    self.transform = np.eye(4)
    self.file = gridfile
    self.type = ftype
    self.wf = None
    if (ftype == 'cube'):
      self.read_cube_header()
    elif (ftype == 'luscus'):
      self.read_luscus_header()
    elif (ftype == 'grid'):
      self.read_grid_header()

  # Read grid header from a Cube format
  def read_cube_header(self):
    self.irrep = ['z']
    with open(self.file, 'rb') as f:
      f.readline()
      # Read title and grid origin
      title = str(f.readline().decode('ascii')).strip()
      n, x, y, z = f.readline().split()
      num = int(n)
      translate = np.array([float(x), float(y), float(z)])
      # Read grid sizes and transformation matrix
      n, x, y, z = f.readline().split()
      ngridx = int(n)
      self.transform[0,0] = float(x)
      self.transform[1,0] = float(y)
      self.transform[2,0] = float(z)
      self.transform[0,3] = translate[0]
      n, x, y, z = f.readline().split()
      ngridy = int(n)
      self.transform[0,1] = float(x)
      self.transform[1,1] = float(y)
      self.transform[2,1] = float(z)
      self.transform[1,3] = translate[1]
      n, x, y, z = f.readline().split()
      ngridz= int(n)
      self.transform[0,2] = float(x)
      self.transform[1,2] = float(y)
      self.transform[2,2] = float(z)
      self.transform[2,3] = translate[2]
      # Read geometry
      self.centers = []
      for i in range(abs(num)):
        q, _, x, y, z = str(f.readline().decode('ascii')).split()
        self.centers.append({'name':'{0}'.format(i), 'Z':int(q), 'xyz':np.array([float(x), float(y), float(z)])})
      self.geomcenter = (np.amin([c['xyz'] for c in self.centers], axis=0) + np.amax([c['xyz'] for c in self.centers], axis=0))/2
      # Compute full volume size
      self.ngrid = [ngridx, ngridy, ngridz]
      self.orig = np.array([0.0, 0.0, 0.0])
      self.end = np.array([float(ngridx-1), float(ngridy-1), float(ngridz-1)])
      # If the number of atoms is negative, there are several orbitals in the file, read their numbers
      if (num < 0):
        data = str(f.readline().decode('ascii')).split()
        self.nMO = int(data[0])
        data = data[1:]
        self.MO = []
        while (len(data) < self.nMO):
          data.extend(str(f.readline().decode('ascii')).split())
        self.MO = [{'label':'{0}: {1}'.format(i, title), 'ene':0.0, 'occup':0.0, 'type':'?', 'sym':'z'} for i in data]
      else:
        self.nMO = 1
        self.MO = [{'label':title, 'ene':0.0, 'occup':0.0, 'type':'?', 'sym':'z'}]
      self.MO_a = []
      self.MO_b = []
      # Number of lines occupied by each "record" (ngridz * nMO)
      self.lrec = int(np.ceil(float(self.nMO)*self.ngrid[2]/6))
      # Save the position after the header
      self.head = f.tell()

  # Read grid header from a Grid format
  def read_grid_header(self):
    with open(self.file, 'rb') as f:
      f.readline()
      f.readline()
      # Read the geometry
      num = int(f.readline().split()[1])
      self.centers = []
      for i in range(num):
        l, x, y, z = str(f.readline().decode('ascii')).split()
        self.centers.append({'name':l, 'Z':name_to_Z(l), 'xyz':np.array([float(x), float(y), float(z)])})
      self.geomcenter = (np.amin([c['xyz'] for c in self.centers], axis=0) + np.amax([c['xyz'] for c in self.centers], axis=0))/2
      # Read number of orbitals and block size
      f.readline()
      f.readline()
      self.nMO = int(f.readline().split()[1])
      f.readline()
      self.bsize = int(f.readline().split()[1])
      f.readline()
      f.readline()
      f.readline()
      f.readline()
      f.readline()
      # Read grid definition and transform matrix
      self.ngrid = [int(i)+1 for i in f.readline().split()[1:]]
      translate = np.array([float(i) for i in f.readline().split()[1:]])
      x, y, z = (float(i) for i in f.readline().split()[1:])
      self.transform[0,0] = float(x)
      self.transform[1,0] = float(y)
      self.transform[2,0] = float(z)
      self.transform[0,3] = translate[0]
      x, y, z = (float(i) for i in f.readline().split()[1:])
      self.transform[0,1] = float(x)
      self.transform[1,1] = float(y)
      self.transform[2,1] = float(z)
      self.transform[1,3] = translate[1]
      x, y, z = (float(i) for i in f.readline().split()[1:])
      self.transform[0,2] = float(x)
      self.transform[1,2] = float(y)
      self.transform[2,2] = float(z)
      self.transform[2,3] = translate[2]
      self.orig = np.array([0.0, 0.0, 0.0])
      self.end = np.array([1.0, 1.0, 1.0])
      # Read and parse orbital names
      self.MO = []
      self.MO_a = []
      self.MO_b = []
      self.irrep = []
      for i in range(self.nMO):
        name = str(f.readline().decode('ascii'))
        match = re.match(r'\s*GridName=\s+(\d+)\s+(\d+)\s+(.+)\s+\((.+)\)\s+(\w)s*', name)
        if (match):
          self.MO.append({'ene':float(match.group(3)), 'occup':float(match.group(4)), 'type':match.group(5).upper(), 'sym':match.group(1), 'num':int(match.group(2)), 'idx':i})
          if (self.MO[-1]['sym'] not in self.irrep):
            self.irrep.append(self.MO[-1]['sym'])
        else:
          name = ' '.join(name.split()[1:])
          self.MO.append({'label':name, 'ene':0.0, 'occup':0.0, 'type':'?', 'sym':'z', 'num':0, 'idx':i})
          if ('z' not in self.irrep):
            self.irrep.append('z')
      # Sort the orbitals by symmetry and number
      self.MO.sort(key=lambda x: (x['sym'], x['num']))
      # Save the position after the header
      self.head = f.tell()
      # Find inporb location
      loc = f.tell()
      line = f.readline()
      while (line != b''):
        loc = f.tell()
        line = f.readline()
        if (line.startswith(b'#INPORB')):
          self.inporb = loc
          break

  # Read grid header from a Luscus format
  def read_luscus_header(self):
    self.irrep = ['z']
    with open(self.file, 'rb') as f:
      # Read the geometry
      num = int(f.readline())
      f.readline()
      atom = []
      self.centers = []
      for i in range(num):
        l, x, y, z = str(f.readline().decode('ascii')).split()
        self.centers.append({'name':l, 'Z':name_to_Z(l), 'xyz':np.array([float(x), float(y), float(z)])/angstrom})
      self.geomcenter = (np.amin([c['xyz'] for c in self.centers], axis=0) + np.amax([c['xyz'] for c in self.centers], axis=0))/2
      # Read number of orbitals and block size
      f.readline()
      data = f.readline().split()
      self.nMO = int(data[3])
      self.bsize = int(data[7])
      f.readline()
      # Read grid definition and transform matrix
      self.ngrid = [int(i) for i in f.readline().split()[1:]]
      translate = np.array([float(i) for i in f.readline().split()[1:]])
      x, y, z = (float(i) for i in f.readline().split()[1:])
      self.transform[0,0] = float(x)
      self.transform[1,0] = float(y)
      self.transform[2,0] = float(z)
      self.transform[0,3] = translate[0]
      x, y, z = (float(i) for i in f.readline().split()[1:])
      self.transform[0,1] = float(x)
      self.transform[1,1] = float(y)
      self.transform[2,1] = float(z)
      self.transform[1,3] = translate[1]
      x, y, z = (float(i) for i in f.readline().split()[1:])
      self.transform[0,2] = float(x)
      self.transform[1,2] = float(y)
      self.transform[2,2] = float(z)
      self.transform[2,3] = translate[2]
      self.orig = np.array([0.0, 0.0, 0.0])
      self.end = np.array([1.0, 1.0, 1.0])
      self.orboff = int(f.readline().split()[2])
      # Read and parse orbital names
      self.MO = []
      self.MO_a = []
      self.MO_b = []
      self.irrep = []
      for i in range(self.nMO):
        name = str(f.readline().decode('ascii'))
        match = re.match(r'\s*GridName=\s*(.+)\s*sym=\s*(\d+)\s*index=\s*(\d+)\s*Energ=\s*(.+)\s*occ=\s*(.+)\s*type=\s*(\w)\s*', name)
        if (match):
          self.MO.append({'ene':float(match.group(4)), 'occup':float(match.group(5)), 'type':match.group(6).upper(), 'sym':match.group(2), 'num':int(match.group(3)), 'idx':i})
          if (self.MO[-1]['sym'] not in self.irrep):
            self.irrep.append(self.MO[-1]['sym'])
        else:
          name = ' '.join(name.split()[1:])
          self.MO.append({'label':name, 'ene':0.0, 'occup':0.0, 'type':'?', 'sym':'z', 'num':0, 'idx':i})
          if ('z' not in self.irrep):
            self.irrep.append('z')
      # Sort the orbitals by symmetry and number
      self.MO.sort(key=lambda x: (x['sym'], x['num']))
      f.readline()
      # Save the position after the header
      self.head = f.tell()
      # Find inporb location
      loc = f.tell()
      line = f.readline()
      while (line != ''):
        loc = f.tell()
        line = f.readline().decode('ascii', errors='replace')
        if (line.startswith('#INPORB')):
          self.inporb = loc
          break

  # Read and return precomputed MO values
  def mo(self, n, x, y, z, spin=None, cache=None, callback=None, interrupt=False):
    if (self.type == 'cube'):
      # In Cube format, the nesting is x:y:z:MO, with
      # wrapped lines and forced newlines every lrec values
      vol = np.empty(tuple(self.ngrid))
      with open(self.file, 'rb') as f:
        f.seek(self.head)
        for i in range(self.ngrid[0]):
          for j in range(self.ngrid[1]):
            data = b''
            for k in range(self.lrec):
              if (interrupt):
                return vol
              data += f.readline()
            vol[i,j,:] = [float(k) for k in data.split()[n::self.nMO]]
    elif (self.type == 'grid'):
      # In Grid format, the nesting is MO:x:y:z, but divided in
      # blocks of length bsize
      data = []
      norb = self.MO[n]['idx']
      with open(self.file, 'rb') as f:
        f.seek(self.head)
        num = np.prod(self.ngrid)
        while (len(data) < num):
          lb = min(self.bsize, num-len(data))
          for o in range(self.nMO):
            f.readline()
            for i in range(lb):
              if (interrupt):
                vol = np.resize(data, num)
                return np.reshape(vol, tuple(self.ngrid))
              if (o == norb):
                data.append(float(f.readline()))
              else:
                f.readline()
      vol = np.reshape(data, tuple(self.ngrid))
    elif (self.type == 'luscus'):
      # In Luscus format, the nesting is MO:x:y:z, but divided in
      # blocks of length bsize, and in binary format
      data = []
      norb = self.MO[n]['idx']
      with open(self.file, 'rb') as f:
        f.seek(self.head)
        num = np.prod(self.ngrid)
        while (len(data) < num):
          if (interrupt):
            vol = np.resize(data, num)
            return np.reshape(vol, tuple(self.ngrid))
          lb = min(self.bsize, num-len(data))
          lbb = lb*struct.calcsize('d')
          f.seek(norb*lbb, 1)
          data.extend(list(struct.unpack(lb*'d', f.read(lbb))))
          f.seek((self.nMO-norb-1)*lbb, 1)
      vol = np.reshape(data, tuple(self.ngrid))
    return vol

#===============================================================================

# Create an index section from alpha and beta orbitals
def create_index(MO, MO_b, nMO, old=None):
  index = []
  error = None
  orbs = list(zip_longest(MO, MO_b))
  for si,s in enumerate(nMO):
    index.append('* 1234567890')
    if (old is not None):
      types = old[si]
    else:
      types = ''
    # Try to merge different alpha and beta types
    for oa,ob in orbs:
      if (oa['sym'] != s):
        continue
      tpa = oa.get('newtype', oa['type']).lower()
      if (ob is None):
        tp = tpa
      else:
        tpb = ob.get('newtype', ob['type']).lower()
        if (tpb == tpa):
          tp = tpa
        elif (tpa+tpb in ['is', 'si']):
          tp = '2'
        else:
          error = 'Alpha and beta types differ'
          return (None, error)
      if (tp == '?'):
        o = oa['occup']
        try:
          o += ob['occup']
        except TypeError:
          pass
        tp = 'i' if (o > 1.0) else 's'
      if ('num' in oa):
        l = list(types)
        l[oa['num']-1] = tp
        types = ''.join(l)
      else:
        types += tp
    for j,l in enumerate(wrap_list(types, 10, '{}')):
      index.append('{0} {1}'.format(str(j)[-1], l))
  return (index, error)

#===============================================================================

# Return atomic number from atomic name
def name_to_Z(name):
  symbol = [                                              'X',
    'H',  'HE', 'LI', 'BE', 'B',  'C',  'N',  'O',  'F',  'NE',
    'NA', 'MG', 'AL', 'SI', 'P',  'S',  'CL', 'AR', 'K',  'CA',
    'SC', 'TI', 'V',  'CR', 'MN', 'FE', 'CO', 'NI', 'CU', 'ZN',
    'GA', 'GE', 'AS', 'SE', 'BR', 'KR', 'RB', 'SR', 'Y',  'ZR',
    'NB', 'MO', 'TC', 'RU', 'RH', 'PD', 'AG', 'CD', 'IN', 'SN',
    'SB', 'TE', 'I',  'XE', 'CS', 'BA', 'LA', 'CE', 'PR', 'ND',
    'PM', 'SM', 'EU', 'GD', 'TB', 'DY', 'HO', 'ER', 'TM', 'YB',
    'LU', 'HF', 'TA', 'W',  'RE', 'OS', 'IR', 'PT', 'AU', 'HG',
    'TL', 'PB', 'BI', 'PO', 'AT', 'RN', 'FR', 'RA', 'AC', 'TH',
    'PA', 'U',  'NP', 'PU', 'AM', 'CM', 'BK', 'CF', 'ES', 'FM',
    'MD', 'NO', 'LR', 'RF', 'DB', 'SG', 'BH', 'HS', 'MT', 'DS',
    'RG', 'CN', 'NH', 'FL', 'MC', 'LV', 'TS', 'OG'
  ]
  s = '{0:2.2}'.format(name.upper())
  if (s[1] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    s = s[0]
  try:
    return symbol.index(s)
  except:
    return 0

#===============================================================================

# Return a list, each element containing at most n items each with format f
def wrap_list(data, n, f, sep=''):
  text = []
  ini = 0
  while ini < len(data):
    end = min(ini+n, len(data))
    fmt = sep.join([f]*(end-ini))
    text.append(fmt.format(*data[ini:end]))
    ini = end
  return text

#===============================================================================

# Convert a "human-readable" file size into a number of bytes
def parse_size(size):
  units = { 'KB': 10**3,  'MB': 10**6,  'GB': 10**9,  'TB': 10**12,
           'KIB': 2**10, 'MIB': 2**20, 'GIB': 2**30, 'TIB': 2**40}
  factor = 1
  try:
    size_ = size.upper()
    for i in units:
      if i in size_:
        factor *= units[i]
        size_ = size_.replace(i, '')
    size_.replace('B', '')
    num = float(size_)
    if (num >= 0):
      return int(factor*num)
    else:
      raise
  except:
    return None

#===============================================================================

def group_widgets(*args):
  layout = QHBoxLayout()
  layout.setContentsMargins(0, 0, 0, 0)
  for w in args:
    layout.addWidget(w)
  group = QFrame()
  group.setLayout(layout)
  return group

def get_input_type(mapper, algtype):
  obj = mapper
  while (not isinstance(obj, algtype)):
    obj = obj.GetInputAlgorithm()
  return obj

class Initializer(QThread):
  def run(self):
    self.parent().vtkWidget.Initialize()

class Worker(QThread):
  def __init__(self, *args, **kwargs):
    self.disable_list = kwargs.pop('disable_list', [])
    super().__init__(*args, **kwargs)
    self.qApp = QApplication.instance()
    self.selected = None
    self.started.connect(self.disable_widgets)
    self.finished.connect(self.restore_widgets)
  def disable_widgets(self):
    self.selected = self.qApp.focusWidget()
    self.status = [i.isEnabled() for i in self.disable_list]
    for i in self.disable_list:
      i.setEnabled(False)
  def restore_widgets(self):
    for i,s in zip(self.disable_list, self.status):
      i.setEnabled(s)
    if ((self.qApp.focusWidget() is None) and (self.selected is not None)):
      self.selected.setFocus(Qt.OtherFocusReason)

class FileRead(Worker):
  def __init__(self, *args, **kwargs):
    self.filename = kwargs.pop('filename', None)
    self.ftype = kwargs.pop('ftype', None)
    super().__init__(*args, **kwargs)
    self.orbitals = None
    self.error = None
  def run(self):
    if ((self.filename is None) or (self.ftype is None)):
      return
    if (self.ftype in ['hdf5', 'molden']):
      try:
        self.orbitals = Orbitals(self.filename, self.ftype)
      except Exception as e:
        self.error = 'Error processing {0} file {1}:\n{2}'.format(self.ftype, self.filename, e)
        traceback.print_exc()
    elif (self.ftype in ['inporb']):
      self.error = self.parent().orbitals.read_inporb_MO(self.filename)
      if (self.error == True):
        self.error = None
        self.orbitals = self.parent().orbitals
    elif (self.ftype in ['grid', 'luscus', 'cube']):
      try:
        self.orbitals = Grid(self.filename, self.ftype)
      except Exception as e:
        self.error = 'Error processing {0} file {1}:\n{2}'.format(self.ftype, self.filename, e)
        traceback.print_exc()

class ComputeVolume(Worker):
  def __init__(self, *args, **kwargs):
    self.cache = kwargs.pop('cache', None)
    self.dens_type = kwargs.pop('dens_type', [])
    super().__init__(*args, **kwargs)
    self.data = None
  def run(self):
    if (self.parent() is None):
      return
    print_func = self.parent().setStatus
    orb = self.parent().orbital
    x, y, z = numpy_support.vtk_to_numpy(self.parent().xyz.GetOutput().GetPoints().GetData()).T
    if (self.parent().MO is self.parent().orbitals.MO_b):
      spin = 'b'
    elif (self.parent().MO is self.parent().orbitals.MO_a):
      spin = 'a'
    else:
      spin = 'n'
    mask = [o['density'] for o in self.parent().notes]
    if ('a' in self.dens_type):
      l = 0
      if (self.parent().orbitals.MO_b):
        alphaMO = self.parent().orbitals.MO_a
      else:
        alphaMO = self.parent().orbitals.MO
      for o in [j for i in zip_longest(alphaMO, self.parent().orbitals.MO_b) for j in i]:
        if (o is None):
          continue
        try:
          if (o['root_occup'] < 0):
            mask[l] = False
        except TypeError:
          pass
        l += 1
    if ('d' in self.dens_type):
      l = 0
      if (self.parent().orbitals.MO_b):
        alphaMO = self.parent().orbitals.MO_a
      else:
        alphaMO = self.parent().orbitals.MO
      for o in [j for i in zip_longest(alphaMO, self.parent().orbitals.MO_b) for j in i]:
        if (o is None):
          continue
        try:
          if (o['root_occup'] > 0):
            mask[l] = False
        except TypeError:
          pass
        l += 1
    if ((orb == 0) or (orb <= -3)):
      self.data = self.parent().orbitals.dens(x, y, z, self.cache, mask=mask, callback=print_func, interrupt=self.parent().interrupt)
      if ('h' in self.dens_type):
        self.data *= -1
    elif (orb == -1):
      self.data = self.parent().orbitals.dens(x, y, z, self.cache, mask=mask, spin=True, callback=print_func, interrupt=self.parent().interrupt)
    elif (orb == -2):
      ngrid = self.parent().xyz.GetInput().GetDimensions()
      data = self.parent().orbitals.dens(x, y, z, self.cache, mask=mask, callback=print_func, interrupt=self.parent().interrupt).reshape(ngrid[::-1])
      # Get the actual lengths of the possibly transformed axes
      c0 = np.array([x[0], y[0], z[0]])
      n = ngrid[0]-1
      c1 = np.array([x[n], y[n], z[n]])-c0
      n = ngrid[0]*(ngrid[1]-1)
      c2 = np.array([x[n], y[n], z[n]])-c0
      n = ngrid[0]*ngrid[1]*(ngrid[2]-1)
      c3 = np.array([x[n], y[n], z[n]])-c0
      matrix = np.vstack((c3[::-1], c2[::-1], c1[::-1])).T
      data = self.parent().orbitals.laplacian(matrix, data).T
      self.data = data
    else:
      self.data = self.parent().orbitals.mo(orb-1, x, y, z, spin, self.cache, callback=print_func, interrupt=self.parent().interrupt)

class ScrollMessageBox(QDialog):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.setWindowTitle('Keyboard shortcuts')
    self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    self.setSizeGripEnabled(True)
    scroll = QTextEdit()
    scroll.setReadOnly(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.viewport().setAutoFillBackground(False)
    scroll.setMinimumWidth(400)
    scroll.setHtml('''
                   <p>In the render window:<br>
                   &nbsp;&nbsp;<b>Left button</b>: Rotate<br>
                   &nbsp;&nbsp;<b>Right button</b>, <b>Ctrl+Shift+Left button</b>, <b>Wheel</b>: Zoom<br>
                   &nbsp;&nbsp;<b>Middle button</b>, <b>Shift+Left button</b>: Translate<br>
                   &nbsp;&nbsp;<b>Ctrl+Left button</b>: Rotate in the screen plane</p>
                   <p><b>P</b>: Toggle orthographic projection</p>
                   <p><b>R</b>: Fit the view to the scene</p>
                   <p><b>Shift+R</b>: Reset camera to default position</p>
                   <p><b>{0}</b>: Load file</p>
                   <p><b>Ctrl+H</b>: Save HDF5 file</p>
                   <p><b>Ctrl+I</b>: Save InpOrb file</p>
                   <p><b>Ctrl+C</b>: Save cube file</p>
                   <p><b>Ctrl+P</b>: Save PNG image</p>
                   <p><b>{1}</b>: Clear orbitals</p>
                   <p><b>{2}</b>: Quit</p>
                   <p><b>{3}</b>: Show this window</p>
                   <p><b>PgUp</b>/<b>PgDown</b>: Switch to previous/next orbital</p>
                   <p><b>Alt+PgUp</b>/<b>Alt+PgDown</b>: Switch to previous/next density type</p>
                   <p><b>Shift+PgUp</b>/<b>Shift+PgDown</b>: Switch to previous/next root</p>
                   <p><b>Ctrl+PgUp</b>/<b>Ctrl+PgDown</b>: Switch to previous/next irrep</p>
                   <p><b>A</b>/<b>B</b>: Switch to alpha/beta or electron/spin orbitals</p>
                   <p><b>Ctrl+L</b>: Show/hide full list of orbitals</p>
                   <p><b>F</b>: Change orbital type to frozen</p>
                   <p><b>I</b>: Change orbital type to inactive</p>
                   <p><b>1</b>: Change orbital type to RAS1 (active)</p>
                   <p><b>2</b>: Change orbital type to RAS2 (active)</p>
                   <p><b>3</b>: Change orbital type to RAS3 (active)</p>
                   <p><b>S</b>: Change orbital type to secondary</p>
                   <p><b>D</b>: Change orbital type to deleted</p>
                   <p><b>0</b>: Restore initial orbital type</p>
                   <p><b>+</b>/<b>-</b>, <b>Shift++</b>/<b>Shift+-</b>: Increase/decrease isosurface value in smaller or larger steps</p>
                   <p><b>Alt+V</b>: Set focus to isosurface value</p>
                   <p><b>O</b>/<b>T</b>, <b>Shift+O</b>/<b>Shift+T</b>: Increase/decrease opacity in smaller or larger steps</p>
                   <p><b>Alt+O</b>: Set focus to opacity</p>
                   <p><b>Ctrl+S</b>: Toggle isosurface display</p>
                   <p><b>Ctrl+Shift+PgUp</b>/<b>Ctrl+Shift+PgDown</b>: Cycle through the different sign displays</p>
                   <p><b>Ctrl+N</b>: Toggle nodal surface display</p>
                   <p><b>Ctrl+A</b>: Cycle through molecule representations</p>
                   <p><b>Ctrl+M</b>: Toggle name labels display</p>
                   <p><b>Ctrl+B</b>: Toggle grid box display</p>
                   <p><b>Alt+B</b>: Set focus to box size</p>
                   <p><b>Ctrl+T</b>: Show/hide grid box transform editor</p>
                   <p><b>Alt+G</b>: Set focus to grid points</p>
                   <p><b>Ctrl+G</b>: Toggle gradient lines display</p>
                   <p><b>Ctrl+Shift+G</b>: Show/hide gradient lines options</p>
                   <p><b>Alt+L</b>: Set focus to line density</p>
                   <p><b>Alt+S</b>: Set focus to start radius</p>
                   <p><b>Alt+M</b>: Set focus to max. steps</p>
                   <p><b>Ctrl+Shift+D</b>: Set gradient lines direction to down</p>
                   <p><b>Ctrl+Shift+B</b>: Set gradient lines direction to both (up and down)</p>
                   <p><b>Ctrl+Shift+U</b>: Set gradient lines direction to up</p>
                   <p><b>X</b>: Show/hide texture and color settings</p>
                   '''.format(
                       QKeySequence(QKeySequence.Open).toString(),
                       QKeySequence(QKeySequence.Close).toString(),
                       QKeySequence(QKeySequence.Quit).toString(),
                       QKeySequence(QKeySequence.HelpContents).toString()
                       ))
    vbox = QVBoxLayout()
    bbox = QDialogButtonBox(QDialogButtonBox.Ok)
    vbox.addWidget(scroll)
    vbox.addWidget(bbox)
    self.setLayout(vbox)
    bbox.accepted.connect(self.accept)

class TakeScreenshot(QDialog):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.setWindowTitle('Save PNG image')
    self.setSizeGripEnabled(True)
    self.fileLabel = QLabel('&Filename:')
    self.fileBox = QLineEdit()
    self.fileBox.setMinimumWidth(200)
    self.fileLabel.setBuddy(self.fileBox)
    self.fileButton = QPushButton('...')
    self.transparentBox = QCheckBox('&Transparent background:')
    self.transparentBox.setLayoutDirection(Qt.RightToLeft)
    self.transparentBox.setChecked(True)
    self.panelBox = QCheckBox('Show text &panel:')
    self.panelBox.setLayoutDirection(Qt.RightToLeft)
    self.saveButton = QPushButton('&Save')
    hbox1 = QHBoxLayout()
    hbox1.addWidget(self.fileLabel)
    hbox1.addWidget(self.fileBox)
    hbox1.addWidget(self.fileButton)
    hbox2 = QHBoxLayout()
    hbox2.addWidget(self.transparentBox)
    hbox2.addStretch(1)
    hbox3 = QHBoxLayout()
    hbox3.addWidget(self.panelBox)
    hbox3.addStretch(1)
    hbox4 = QHBoxLayout()
    hbox4.addStretch(1)
    hbox4.addWidget(self.saveButton)
    vbox = QVBoxLayout()
    vbox.addLayout(hbox1)
    vbox.addLayout(hbox2)
    vbox.addLayout(hbox3)
    vbox.addStretch(1)
    vbox.addLayout(hbox4)
    self.setLayout(vbox)
    self.fileButton.clicked.connect(self.select_file)
    self.saveButton.clicked.connect(self.save_screenshot)
    self.fileBox.setToolTip('Filename for the saved image')
    self.fileBox.setWhatsThis('Type the filename for the saved image, or select it using the button to the right. The file. The file will be overwritten.')
    self.fileButton.setToolTip('Select saved file')
    self.fileButton.setWhatsThis('Select the file to save the image in, or type the filename in the box to the left. The file. The file will be overwritten.')
    self.transparentBox.setToolTip('Make the background transparent, or show its current color')
    self.transparentBox.setWhatsThis('If checked, the saved image will have transparent background.')
    self.panelBox.setToolTip('Show or hide the text panel')
    self.panelBox.setWhatsThis('If checked, the text panel with orbital information will be included in the saved image.')
    self.saveButton.setToolTip('Save the image file')
    self.saveButton.setWhatsThis('Write the image to the specified file. The file will be overwritten.')

  def select_file(self):
    result = QFileDialog.getSaveFileName(self, 'Save image')
    if (not result):
      return
    try:
      filename, _ = result
    except ValueError:
      filename = result
    self.fileBox.setText(filename)

  def save_screenshot(self):
    filename = str(self.fileBox.text())
    if (filename == ''):
      self.parent().show_error('Filename not specified')
      return

    ren = self.parent().ren
    renwin = self.parent().vtkWidget.GetRenderWindow()
    renwin.SetAlphaBitPlanes(1)

    panel_changed = False
    if (not self.panelBox.isChecked()):
      if (self.parent().panel is not None):
        self.parent().panel.VisibilityOff()
        panel_changed = True

    wti = vtk.vtkWindowToImageFilter()
    wti.SetInput(renwin)
    wti.SetInputBufferTypeToRGBA()
    wti.ReadFrontBufferOff()
    w = vtk.vtkPNGWriter()
    w.SetFileName(filename)
    w.SetCompressionLevel(9)
    if (self.transparentBox.isChecked()):
      # Use the workaround of black and white backgrounds
      c = ren.GetBackground()
      ren.SetBackground(0,0,0)
      wti.Update()
      black = vtk.vtkImageData()
      black.ShallowCopy(wti.GetOutput())
      ren.SetBackground(1,1,1)
      wti = vtk.vtkWindowToImageFilter()
      wti.SetInput(renwin)
      wti.SetInputBufferTypeToRGBA()
      wti.ReadFrontBufferOff()
      wti.Update()
      white = vtk.vtkImageData()
      white.ShallowCopy(wti.GetOutput())
      ren.SetBackground(c)
      self.parent().vtk_update()
      trans = self.set_transparency(white, black)
      w.SetInputData(trans)
    else:
      wti.Update()
      w.SetInputData(wti.GetOutput())
    if (panel_changed):
      self.parent().panel.VisibilityOn()
      self.parent().vtk_update()
    w.Write()

  # Getting an image with transparent background does not work within Qt, so we
  # have to use a trick similar to that used in ParaView: get images with black
  # and white backgrounds and figure out the transparency from their difference
  def set_transparency(self, white_background, black_background):
    wdata = numpy_support.vtk_to_numpy(white_background.GetPointData().GetScalars()).astype(float)
    bdata = numpy_support.vtk_to_numpy(black_background.GetPointData().GetScalars()).astype(float)
    output = deepcopy(bdata)
    alpha = 255 - (wdata[:,0:3].max(1) - bdata[:,0:3].max(1))
    mask = alpha > 0
    output[:,0:3] *= 255/np.where(mask[:,np.newaxis], alpha[:,np.newaxis], 255)
    output[:,3] = alpha
    oi = vtk.vtkImageData()
    oi.CopyStructure(black_background)
    oi.GetPointData().SetScalars(numpy_support.numpy_to_vtk(output, 1, vtk.VTK_UNSIGNED_CHAR))
    return oi

class SimpleVTK(QVTKRenderWindowInteractor):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
  def keyPressEvent(self, event):
    pass
  def keyReleaseEvent(self, event):
    pass

# A menu with tooltips
class MenuTT(QMenu):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
  def event(self, e):
    if ((e.type() == QEvent.ToolTip) and (self.activeAction() != 0)):
      try:
        QToolTip.showText(e.globalPos(), self.activeAction().toolTip())
      except AttributeError:
        pass
    elif (e.type() != QEvent.Timer):
      QToolTip.hideText()
    return super().event(e)

# A fake mutable boolean type, to pass as reference
class MutableBool(object):
  def __init__(self):
    self.value = False
  def put(self, value):
    self.value = value
  def __bool__(self):
    return self.value
  __nonzero__ = __bool__

class MainWindow(QMainWindow):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._ready = False
    self.init_UI()
    self.init_properties()
    self.init_VTK()

    screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
    self.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.size(), QApplication.desktop().availableGeometry(screen)))

    self.vtkWidget.setFocus()
    self.show()
    self.vtk_update()

  # Clean up when exiting
  def __del__(self):
    self.deltmp()
  def closeEvent(self, event):
    try:
      self.message.close()
    except:
      pass
    self.deltmp()
    event.accept()

  def init_properties(self):
    self._filename = None
    self._orbitals = None
    self._MO = None
    self._orbital = None
    self._notes = None
    self._xyz = None
    self._surface_actor = None
    self._nodes_actor = None
    self._mol_actor = None
    self._names_actor = None
    self._box_actor = None
    self._axes_actor = None
    self._gradient_actor = None
    self._panel_actor = None
    self._dens = None
    self._root = None
    self._irrep = None
    self._irreplist = None
    self._spin = None
    self._spinlist = None
    self._haveBasis = None
    self._haveInpOrb = None
    self._isovalue = None
    self._opacity = None
    self._boxSize = None
    self._transform = None
    self._gridPoints = None
    self._lineDensity = None
    self._startRadius = None
    self._maxSteps = None

    self._fileReadThread = None
    self._computeVolumeThread = None
    self._newgrid = True
    self._tainted = True
    self._minval = 1e-10
    self._maxval = 0.1
    self._tmpdir = mkdtemp()
    self._cache_file = None
    self._timestamp = time.time()

    self.orbitals = None
    self.orbital = None
    self.MO = None
    self.notes = None
    self.surface = None
    self.nodes = None
    self.mol = None
    self.names = None
    self.box = None
    self.axes = None
    self.gradient = None
    self.haveBasis = False
    self.haveInpOrb = False
    self.transform = np.eye(4).flatten().tolist()
    self.gridPoints = 30
    self.lineDensity = 10
    self.startRadius = 1.5
    self.maxSteps = 50

    self.isovalueBox.setText('0.05')
    self.isovalueBox.editingFinished.emit()
    self.opacityBox.setText('1.0')
    self.opacityBox.editingFinished.emit()

    self.type_setEnabled(False)
    self.surfaceBox.setChecked(True)
    self.surfaceBox.setEnabled(False)
    self.nodesBox.setChecked(False)
    self.nodesBox.setEnabled(False)
    self.namesBox.setChecked(False)
    self.boxBox.setChecked(False)
    self.bothButton.setChecked(True)

    self.interrupt = MutableBool()
    self.scratchsize = {'max':parse_size(os.environ.get('PEGAMOID_MAXSCRATCH')), 'rec':None}
    if (self.scratchsize['max'] is None):
      self.scratchsize['max'] = parse_size('1GiB')

  def init_UI(self):
    self.icon = QPixmap()
    self.icon.loadFromData(icondata)
    self.icon = QIcon(self.icon)
    self.qApp = QApplication.instance()
    self.qApp.setWindowIcon(self.icon)

    self.setWindowTitle('Pegamoid')
    self.setWindowIcon(self.icon)
    self.setWindowFlags(self.windowFlags() | Qt.WindowContextHelpButtonHint)

    self.mainMenu = self.menuBar()
    self.fileMenu = MenuTT('&File')
    self.mainMenu.addMenu(self.fileMenu)
    self.loadAction = self.fileMenu.addAction('&Load file...')
    self.fileMenu.addSeparator()
    self.saveMenu = MenuTT('&Save')
    self.fileMenu.addMenu(self.saveMenu)
    self.saveHDF5Action = self.saveMenu.addAction('Save &HDF5...')
    self.saveInpOrbAction = self.saveMenu.addAction('Save &InpOrb...')
    self.saveCubeAction = self.saveMenu.addAction('Save &cube...')
    self.saveMenu.addSeparator()
    self.screenshotAction = self.saveMenu.addAction('Save &PNG image...')
    self.fileMenu.addSeparator()
    self.scratchAction = self.fileMenu.addAction('Use scratch')
    self.scratchAction.setCheckable(True)
    self.scratchAction.setChecked(True)
    self.fileMenu.addSeparator()
    self.clearAction = self.fileMenu.addAction('&Clear')
    self.quitAction = self.fileMenu.addAction('&Quit')
    self.viewMenu = MenuTT('Vie&w')
    self.mainMenu.addMenu(self.viewMenu)
    self.orthographicAction = self.viewMenu.addAction('&Orthographic')
    self.orthographicAction.setCheckable(True)
    self.fitViewAction = self.viewMenu.addAction('&Fit view')
    self.resetCameraAction = self.viewMenu.addAction('&Reset camera')
    self.helpMenu = MenuTT('&Help')
    self.mainMenu.addMenu(self.helpMenu)
    self.keysAction = self.helpMenu.addAction('&Keys')
    self.aboutAction = self.helpMenu.addAction('&About')

    # widgets
    self.fileLabel = QLabel('File:')
    self.filenameLabel = QLabel('')
    self.fileButton = QPushButton('Load file...')
    self.densityTypeLabel = QLabel('Density:')
    self.densityTypeButton = QComboBox()
    self.rootLabel = QLabel('Root:')
    self.rootButton = QComboBox()
    self.irrepLabel = QLabel('Irrep:')
    self.irrepButton = QComboBox()
    self.orbitalLabel = QLabel('Orbital:')
    self.orbitalButton = QComboBox()
    self.spinButton = QComboBox()
    self.listButton = QPushButton('List')
    self.typeLabel = QLabel('Type:')
    self.typeButtonGroup = QButtonGroup()
    activeFrame = QFrame()
    self.frozenButton = QRadioButton('F')
    self.inactiveButton = QRadioButton('I')
    self.RAS1Button = QRadioButton('1')
    self.RAS2Button = QRadioButton('2')
    self.RAS3Button = QRadioButton('3')
    self.secondaryButton = QRadioButton('S')
    self.deletedButton = QRadioButton('D')
    self.resetButton = QPushButton('Reset')
    self.isovalueLabel = QLabel('&Value:')
    self.isovalueSlider = QSlider(Qt.Horizontal)
    self.isovalueBox = QLineEdit()
    self.isovalueLabel.setBuddy(self.isovalueBox)
    self.opacityLabel = QLabel('&Opacity:')
    self.opacitySlider = QSlider(Qt.Horizontal)
    self.opacityBox = QLineEdit()
    self.opacityLabel.setBuddy(self.opacityBox)
    self.textureButton = QPushButton('Te&xture')
    self.surfaceBox = QCheckBox('Surface:')
    self.signButton = QComboBox()
    self.nodesBox = QCheckBox('Nodes:')
    self.moleculeLabel = QLabel('Molecule:')
    self.moleculeButton = QComboBox()
    self.namesBox = QCheckBox('Names:')
    self.boxBox = QCheckBox('Box:')
    self.boxSizeLabel = QLabel('&Box size:')
    self.boxSizeBox = QLineEdit()
    self.boxSizeLabel.setBuddy(self.boxSizeBox)
    self.transformButton = QPushButton()
    self.gridPointsLabel = QLabel('&Grid points:')
    self.gridPointsBox = QLineEdit()
    self.gridPointsLabel.setBuddy(self.gridPointsBox)
    self.gradientBox = QCheckBox('Gradient:')
    self.showGradientButton = QToolButton()
    self.gradientGroup = QFrame()
    self.lineDensityLabel = QLabel('&Line density:')
    self.lineDensityBox = QLineEdit()
    self.lineDensityLabel.setBuddy(self.lineDensityBox)
    self.startRadiusLabel = QLabel('&Start radius:')
    self.startRadiusBox = QLineEdit()
    self.startRadiusLabel.setBuddy(self.startRadiusBox)
    self.maxStepsLabel = QLabel('&Max. steps:')
    self.maxStepsBox = QLineEdit()
    self.maxStepsLabel.setBuddy(self.maxStepsBox)
    self.directionButtonGroup = QButtonGroup()
    self.upButton = QRadioButton('Up')
    self.bothButton = QRadioButton('Both')
    self.downButton = QRadioButton('Down')
    self.cancelButton = QPushButton('Cancel')
    self.statusLabel = QLabel()

    self.boxicon = QPixmap()
    self.boxicon.loadFromData(boxicondata)
    self.boxicon = QIcon(self.boxicon)
    self.transformButton.setIcon(self.boxicon)

    self.frame = QFrame()

    # display properties
    self.mainMenu.setNativeMenuBar(False)
    self.frame.setFrameStyle(QFrame.Shape(QFrame.Panel | QFrame.Sunken))
    self.filenameLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.listButton.setCheckable(True)
    self.orbitalButton.setSizeAdjustPolicy(QComboBox.AdjustToContents)
    activeFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
    self.frozenButton.setLayoutDirection(Qt.RightToLeft)
    self.inactiveButton.setLayoutDirection(Qt.RightToLeft)
    self.RAS1Button.setLayoutDirection(Qt.RightToLeft)
    self.RAS2Button.setLayoutDirection(Qt.RightToLeft)
    self.RAS3Button.setLayoutDirection(Qt.RightToLeft)
    self.secondaryButton.setLayoutDirection(Qt.RightToLeft)
    self.deletedButton.setLayoutDirection(Qt.RightToLeft)
    self.isovalueBox.setFixedWidth(80)
    self.opacityBox.setFixedWidth(60)
    self.textureButton.setCheckable(True)
    self.surfaceBox.setLayoutDirection(Qt.RightToLeft)
    self.signButton.addItem(u'+', [True, False])
    self.signButton.addItem(u'−', [False, True])
    self.signButton.addItem(u'+ & −', [True, True])
    self.signButton.setCurrentIndex(2)
    self.nodesBox.setLayoutDirection(Qt.RightToLeft)
    self.moleculeButton.addItems([u'Balls&Sticks', u'Nuclei', u'None'])
    self.moleculeButton.setCurrentIndex(0)
    self.namesBox.setLayoutDirection(Qt.RightToLeft)
    self.boxBox.setLayoutDirection(Qt.RightToLeft)
    self.boxSizeBox.setFixedWidth(120)
    self.transformButton.setCheckable(True)
    self.gridPointsBox.setFixedWidth(50)
    self.gradientBox.setLayoutDirection(Qt.RightToLeft)
    self.gradientGroup.hide()
    self.showGradientButton.setArrowType(Qt.RightArrow)
    self.showGradientButton.setAutoRaise(True)
    self.lineDensityBox.setFixedWidth(50)
    self.startRadiusBox.setFixedWidth(50)
    self.maxStepsBox.setFixedWidth(50)
    self.downButton.setLayoutDirection(Qt.RightToLeft)
    self.bothButton.setLayoutDirection(Qt.RightToLeft)
    self.upButton.setLayoutDirection(Qt.RightToLeft)
    self.cancelButton.setEnabled(False)
    self.cancelButton.hide()

    # tooltips
    self.loadAction.setToolTip('Load a file in any supported format')
    self.saveHDF5Action.setToolTip('Save current orbitals in HDF5 format')
    self.saveInpOrbAction.setToolTip('Save current orbitals in InpOrb format')
    self.saveCubeAction.setToolTip('Save current volume in cube format')
    self.screenshotAction.setToolTip('Save the current view as an image')
    self.scratchAction.setToolTip('Use a scratch file for caching basis functions (faster, but uses disk space)')
    self.clearAction.setToolTip('Clear the currently loaded file')
    self.quitAction.setToolTip('Quit {}'.format(__name__))
    self.orthographicAction.setToolTip('Toggle the use of an orthographic projection (perspective if disabled)')
    self.fitViewAction.setToolTip('Fit the currently displayed objects in the view')
    self.resetCameraAction.setToolTip('Reset the camera to the default view')
    self.keysAction.setToolTip('Show list of hotkeys')
    self.aboutAction.setToolTip('Show information about {} and environment'.format(__name__))
    self.filenameLabel.setToolTip('Currently loaded filename')
    self.fileButton.setToolTip('Load a file in any supported format')
    self.densityTypeButton.setToolTip('Select type of density for natural orbitals')
    self.densityTypeButton.setWhatsThis('Select the type of density to compute natural orbitals for, out of those available.<br>Keys: <b>Alt+PgUp</b>, <b>Alt+PgDown</b>')
    self.rootButton.setToolTip('Select root for natural active orbitals')
    self.rootButton.setWhatsThis('Select a root to compute the natural active orbitals for, if the file contains root-specific density matrices.<br>Keys: <b>Shift+PgUp</b>, <b>Shift+PgDown</b>')
    self.irrepButton.setToolTip('Select irrep for the orbital list')
    self.irrepButton.setWhatsThis('This list shows the irreps available in the file, by name or number. Selecting one irrep restricts the orbitals available in the button on the right to the selected irrep. Select "All" for no restriction.<br>Keys: <b>Ctrl+PgUp</b>, <b>Ctrl+PgDown</b>')
    self.orbitalButton.setToolTip('Select orbital to display')
    self.orbitalButton.setWhatsThis('This shows all the orbitals available in the file, belonging to the selected irrep and spin if applicable. If no irrep is selected ("All") and if the file is not a precomputed grid, the electron density, the spin density and the Laplacian of the electron density may also be available. Selecting an orbital displays it in the 3D view above.<br>Keys: <b>PgUp</b>, <b>PgDown</b>')
    self.spinButton.setToolTip('Select spin for the orbital list')
    self.spinButton.setWhatsThis('Select alpha or beta orbitals. This list is only visible if the file contains spin-orbitals.<br>Keys: <b>A</b>, <b>B</b>')
    self.listButton.setToolTip('Show/hide full list of orbitals')
    self.listButton.setWhatsThis('Open or close a window showing the list of all orbitals (no restrictions), where custom notes can be added.<br>Key: <b>Shift+L</b>')
    activeFrame.setWhatsThis('RAS1, RAS2 and RAS3 orbitals count as "active"')
    self.frozenButton.setToolTip('Set orbital as frozen')
    self.frozenButton.setWhatsThis('Set the type of the current orbital to "Frozen". This type will be saved in HDF5 or InpOrb files.<br>Key: <b>F</b>')
    self.inactiveButton.setToolTip('Set orbital as inactive')
    self.inactiveButton.setWhatsThis('Set the type of the current orbital to "Inactive". This type will be saved in HDF5 or InpOrb files.<br>Key: <b>I</b>')
    self.RAS1Button.setToolTip('Set orbital as RAS1 (active)')
    self.RAS1Button.setWhatsThis('Set the type of the current orbital to "RAS1" (active). This type will be saved in HDF5 or InpOrb files.<br>Key: <b>1</b>')
    self.RAS2Button.setToolTip('Set orbital as RAS2 (active)')
    self.RAS2Button.setWhatsThis('Set the type of the current orbital to "RAS2" (active). This type will be saved in HDF5 or InpOrb files.<br>Key: <b>2</b>')
    self.RAS3Button.setToolTip('Set orbital as RAS3 (active)')
    self.RAS3Button.setWhatsThis('Set the type of the current orbital to "RAS3" (active). This type will be saved in HDF5 or InpOrb files.<br>Key: <b>3</b>')
    self.secondaryButton.setToolTip('Set orbital as secondary')
    self.secondaryButton.setWhatsThis('Set the type of the current orbital to "Secondary". This type will be saved in HDF5 or InpOrb files.<br>Key: <b>S</b>')
    self.deletedButton.setToolTip('Set orbital as deleted')
    self.deletedButton.setWhatsThis('Set the type of the current orbital to "Deleted". This type will be saved in HDF5 or InpOrb files.<br>Key: <b>D</b>')
    self.resetButton.setToolTip('Reset orbital to its initial type')
    self.resetButton.setWhatsThis('Discard changes to the current orbital type and restore the type (if any) specified in the file.<br>Key: <b>0</b> (zero)')
    self.isovalueSlider.setToolTip('Set value for the isosurfaces (inverse log scale)')
    self.isovalueSlider.setWhatsThis('Change the value for which the isosurfaces are computed. The scale of the slider is inverse logarithmic, moving it to the right makes the value smaller and the surfaces typically "larger". Both positive and negative surfaces are controlled with the slider. To show the isosurface for a value of 0 enable "Nodes" below.<br>Keys: <b>(Shift+)+</b>, <b>(Shift+)-</b>')
    self.isovalueBox.setToolTip('Set value for the isosurfaces')
    self.isovalueBox.setWhatsThis('Value for which the isosurfaces are computed. Lower values make the surfaces typically "larger". Both positive and negative surfaces are affected by this value. To show the isosurface for a value of 0 enable "Nodes" below.')
    self.opacitySlider.setToolTip('Set opacity of the isosurfaces')
    self.opacitySlider.setWhatsThis('Change the opacity of the isosurfaces. Lower opacity makes the surface more transparent.<br>Keys: <b>(Shift+)O</b> (oh), <b>(Shift+)T</b>')
    self.opacityBox.setToolTip('Set opacity of the isosurfaces')
    self.opacityBox.setWhatsThis('Opacity of the isosurfaces. Lower opacity makes the surface more transparent.')
    self.textureButton.setToolTip('Show/hide the texture settings for the isosurfaces')
    self.textureButton.setWhatsThis('Open or close a window where isosurface colors and texture/shading settings can be changed.<br>Key: <b>X</b>')
    self.surfaceBox.setToolTip('Show/hide the isosurfaces')
    self.surfaceBox.setWhatsThis('If checked, the isosurfaces of the current orbital or density are displayed.<br>Key: <b>Ctrl+S</b>')
    self.signButton.setToolTip('Set which parts of the isosurfaces are displayed')
    self.signButton.setWhatsThis('Controls whether the positive, negative or both parts of the isosurface are displayed.<br>Key: <b>Ctrl+Shift+PgUp</b>, <b>Ctrl+Shift+PgDown</b></b>')
    self.nodesBox.setToolTip('Show/hide the nodal surfaces')
    self.nodesBox.setWhatsThis('If checked, the nodal surfaces (value=0) of the current orbital or density are displayed.<br>Key: <b>Ctrl+N</b>')
    self.moleculeButton.setToolTip('Set molecule representation')
    self.moleculeButton.setWhatsThis('Select the type of representation used for the molecule: balls and sticks, smaller nuclei, or none.<br>Key: <b>Ctrl+A</b>')
    self.namesBox.setToolTip('Show/hide the atom names')
    self.namesBox.setWhatsThis('If checked, text labels with the available names are shown at the nucleus or center positions.<br>Key: <b>Ctrl+M</b>')
    self.boxBox.setToolTip('Show/hide the grid box')
    self.boxBox.setWhatsThis('If checked, the outline of the current grid box is displayed.<br>Key: <b>Ctrl+B</b>')
    self.boxSizeBox.setToolTip('Set the box size in x, y, z (in bohr)')
    self.boxSizeBox.setWhatsThis('Dimension of the grid box along the x, y and z axes, in bohr. Values can be separated by commas or spaces. Only available if the file is not a precomputed grid.')
    self.transformButton.setToolTip('Show/hide the transformation matrix for the box')
    self.transformButton.setWhatsThis('Open or close a window where a translation and transformation matrix can be specified for the grid box.<br>Key: <b>Ctrl+T</b>')
    self.gridPointsBox.setToolTip('Set the number of grid points in the largest dimension')
    self.gridPointsBox.setWhatsThis('Number of grid points along the largest dimension, the number in the other dimensions is adjusted to keep the grid approximately cubic. Only available if the file is not a precomputed grid.')
    self.gradientBox.setToolTip('Show/hide the gradient stream lines (slow)')
    self.gradientBox.setWhatsThis('If checked, stream lines representing the gradient field of the current orbital or density are displayed. Note that this may be slow.<br>Key: <b>Ctrl+G</b>')
    self.showGradientButton.setToolTip('Show/hide advanced options for gradient lines')
    self.showGradientButton.setWhatsThis('Show or hide additional options for the representation of the gradient stream lines.<br>Key: <b>Ctrl+Shift+G</b>')
    self.lineDensityBox.setToolTip('Set the density of gradient lines')
    self.lineDensityBox.setWhatsThis('Controls the number of lines generated. The number of starting points is the square of this number for each nucleus or center.')
    self.startRadiusBox.setToolTip('Set the starting radius for the gradient lines')
    self.startRadiusBox.setWhatsThis('The lines start on a sphere of this radius (in bohr) around each nucleus or center.')
    self.maxStepsBox.setToolTip('Set the maximum number of steps for the gradient lines')
    self.maxStepsBox.setWhatsThis('Maximum number of steps in the integration of the gradient stream lines. Reduce to speed up.')
    self.downButton.setToolTip('Show only lines towards lower values')
    self.downButton.setWhatsThis('Integrate the gradient stream lines only towards lower values from the starting points (outwards for the electron density).<br>Key: <b>Ctrl+Shift+D</b>')
    self.bothButton.setToolTip('Show lines in both directions')
    self.downButton.setWhatsThis('Integrate the gradient stream lines in both directions.<br>Key: <b>Ctrl+Shift+B</b>')
    self.upButton.setToolTip('Show only lines towards higher values')
    self.upButton.setWhatsThis('Integrate the gradient stream lines only towards higher values from the starting points (inwards for the electron density).<br>Key: <b>Ctrl+Shift+U</b>')
    self.cancelButton.setToolTip('Interrupt current calculation')
    self.cancelButton.setWhatsThis('Interrupt the current calculation as soon as possible, the display window will show the partial result in pink.<br>Key: <b>Esc</b>')

    # value properties
    self.isovalueSlider.setRange(0, 1000)
    self.opacitySlider.setRange(0, 100)
    self.typeButtonGroup.addButton(self.frozenButton, 1)
    self.typeButtonGroup.addButton(self.inactiveButton, 2)
    self.typeButtonGroup.addButton(self.RAS1Button, 3)
    self.typeButtonGroup.addButton(self.RAS2Button, 4)
    self.typeButtonGroup.addButton(self.RAS3Button, 5)
    self.typeButtonGroup.addButton(self.secondaryButton, 6)
    self.typeButtonGroup.addButton(self.deletedButton, 7)
    self.directionButtonGroup.addButton(self.downButton, vtk.vtkStreamTracer.BACKWARD)
    self.directionButtonGroup.addButton(self.bothButton, vtk.vtkStreamTracer.BOTH)
    self.directionButtonGroup.addButton(self.upButton, vtk.vtkStreamTracer.FORWARD)

    # layout
    hbox1 = QHBoxLayout()
    hbox1.addWidget(self.fileButton)
    hbox1.addWidget(self.fileLabel)
    hbox1.addWidget(self.filenameLabel, stretch=1)

    hbox2 = QHBoxLayout()
    self.densityTypeGroup = group_widgets(self.densityTypeLabel, self.densityTypeButton)
    hbox2.addWidget(self.densityTypeGroup)
    hbox2.addStretch(1)

    hbox3 = QHBoxLayout()
    hbox3.setSpacing(10)
    self.rootGroup = group_widgets(self.rootLabel, self.rootButton)
    hbox3.addWidget(self.rootGroup)
    self.irrepGroup = group_widgets(self.irrepLabel, self.irrepButton)
    hbox3.addWidget(self.irrepGroup)
    self.orbitalGroup = group_widgets(self.orbitalLabel, self.orbitalButton, self.spinButton)
    hbox3.addWidget(self.orbitalGroup)
    hbox3.addSpacing(10)
    hbox3.addWidget(self.listButton)
    hbox3.addStretch(1)

    hbox4 = QHBoxLayout()
    hbox4.addWidget(self.typeLabel)
    hbox4.addSpacing(10)
    activeLayout = QHBoxLayout()
    activeLayout.addWidget(group_widgets(self.RAS1Button, self.RAS2Button, self.RAS3Button))
    activeFrame.setLayout(activeLayout)
    self.typeGroup = group_widgets(self.frozenButton, self.inactiveButton, activeFrame, self.secondaryButton, self.deletedButton)
    hbox4.addWidget(self.typeGroup)
    hbox4.addSpacing(10)
    hbox4.addWidget(self.resetButton)
    hbox4.addStretch(1)
    self.moleculeGroup = group_widgets(self.moleculeLabel, self.moleculeButton)
    hbox4.addWidget(self.moleculeGroup)
    hbox4.addWidget(self.namesBox)

    hbox5 = QHBoxLayout()
    hbox5.setSpacing(10)
    self.isovalueGroup = group_widgets(self.isovalueLabel, self.isovalueSlider, self.isovalueBox)
    hbox5.addWidget(self.isovalueGroup, stretch=2)
    self.opacityGroup = group_widgets(self.opacityLabel, self.opacitySlider, self.opacityBox)
    hbox5.addWidget(self.opacityGroup, stretch=1)
    hbox5.addWidget(self.textureButton)

    hbox6 = QHBoxLayout()
    hbox6.setSpacing(10)
    hbox6.addWidget(self.surfaceBox)
    hbox6.addWidget(self.signButton)
    hbox6.addWidget(self.nodesBox)
    hbox6.addWidget(self.boxBox)
    self.boxSizeGroup = group_widgets(self.boxSizeLabel, self.boxSizeBox)
    hbox6.addWidget(self.boxSizeGroup)
    hbox6.addWidget(self.transformButton)
    self.gridPointsGroup = group_widgets(self.gridPointsLabel, self.gridPointsBox)
    hbox6.addWidget(self.gridPointsGroup)
    hbox6.addStretch(1)

    hbox7 = QHBoxLayout()
    hbox7.addWidget(self.gradientBox)
    gradientLayout = QHBoxLayout()
    gradientLayout.setContentsMargins(0, 0, 0, 0)
    self.lineDensityGroup = group_widgets(self.lineDensityLabel, self.lineDensityBox)
    gradientLayout.addWidget(self.lineDensityGroup)
    self.startRadiusGroup = group_widgets(self.startRadiusLabel, self.startRadiusBox)
    gradientLayout.addWidget(self.startRadiusGroup)
    self.maxStepsGroup = group_widgets(self.maxStepsLabel, self.maxStepsBox)
    gradientLayout.addWidget(self.maxStepsGroup)
    gradientLayout.addWidget(self.downButton)
    gradientLayout.addWidget(self.bothButton)
    gradientLayout.addWidget(self.upButton)
    self.gradientGroup.setLayout(gradientLayout)
    hbox7.addWidget(self.gradientGroup)
    hbox7.addWidget(self.showGradientButton)
    hbox7.addStretch(1)

    line = QFrame()
    line.setFrameShape(QFrame.Shape(QFrame.HLine | QFrame.Sunken))

    vbox = QVBoxLayout()
    vbox.setSpacing(10)
    vbox.addWidget(self.frame, stretch=1)
    vbox.addLayout(hbox1)
    vbox.addWidget(line)
    vbox.addLayout(hbox2)
    vbox.addLayout(hbox3)
    vbox.addLayout(hbox4)
    vbox.addLayout(hbox5)
    vbox.addLayout(hbox6)
    vbox.addLayout(hbox7)

    _widget = QWidget()
    _widget.setLayout(vbox)

    self.listDock = ListDock(self)
    self.listDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    self.addDockWidget(Qt.RightDockWidgetArea, self.listDock)
    self.listDock.hide()
    self.listDock.setWhatsThis('This is a detachable window that shows all orbitals in the file. For each orbital you can add a custom note and specify whether it should be included in the electron and spin density. This information is not saved.<br>Key: <b>Ctrl+L</b>')

    self.transformDock = TransformDock(self)
    self.transformDock.setFloating(True)
    self.transformDock.hide()
    self.transformDock.setWhatsThis('This is a detachable window that allows setting a transformation (rotation, scaling, shearing, translation) for the grid box. This is only possible if the current file is not a precomputed grid. The transformation affects the display and any grid saved in the cube format.')

    self.textureDock = TextureDock(self)
    self.textureDock.setFloating(True)
    self.textureDock.hide()
    self.textureDock.setWhatsThis('This is a detachable window that allows modifying the color and texture/shading properties for the isosurfaces.')

    self.screenshot = None
    self.keymess = None

    self.setCentralWidget(_widget)
    self.statusBar().addWidget(self.statusLabel)
    self.statusBar().addPermanentWidget(self.cancelButton)
    self.statusBar().setStyleSheet('QStatusBar::item{border:0};')
    self.statusLabel.setText('Ready.')
    self.resize(800, 800)

    # shortcuts
    self.loadAction.setShortcut(QKeySequence(QKeySequence.Open)) # Ctrl+O
    self.saveHDF5Action.setShortcut('Ctrl+H')
    self.saveInpOrbAction.setShortcut('Ctrl+I')
    self.saveCubeAction.setShortcut('Ctrl+C')
    self.screenshotAction.setShortcut('Ctrl+P')
    self.clearAction.setShortcut(QKeySequence(QKeySequence.Close)) # Ctrl+W
    self.quitAction.setShortcut(QKeySequence(QKeySequence.Quit)) # Ctrl+Q
    self.keysAction.setShortcut(QKeySequence(QKeySequence.HelpContents)) # F1
    self.orthographicAction.setShortcut(QKeySequence('P'))
    self.fitViewAction.setShortcut(QKeySequence('R'))
    self.resetCameraAction.setShortcut(QKeySequence('Shift+R'))
    self.listButton.setShortcut('Ctrl+L')
    self.prevDensShortcut = QShortcut(QKeySequence('Alt+PgUp'), self)
    self.prevDensShortcut.activated.connect(self.prev_dens)
    self.nextDensShortcut = QShortcut(QKeySequence('Alt+PgDown'), self)
    self.nextDensShortcut.activated.connect(self.next_dens)
    self.prevRootShortcut = QShortcut(QKeySequence('Shift+PgUp'), self)
    self.prevRootShortcut.activated.connect(self.prev_root)
    self.nextRootShortcut = QShortcut(QKeySequence('Shift+PgDown'), self)
    self.nextRootShortcut.activated.connect(self.next_root)
    self.nextMoleculeShortcut = QShortcut(QKeySequence('Ctrl+A'), self)
    self.nextMoleculeShortcut.activated.connect(self.next_molecule)
    self.prevIrrepShortcut = QShortcut(QKeySequence('Ctrl+PgUp'), self)
    self.prevIrrepShortcut.activated.connect(self.prev_irrep)
    self.nextIrrepShortcut = QShortcut(QKeySequence('Ctrl+PgDown'), self)
    self.nextIrrepShortcut.activated.connect(self.next_irrep)
    self.prevOrbitalShortcut = QShortcut(QKeySequence('PgUp'), self)
    self.prevOrbitalShortcut.activated.connect(self.prev_orbital)
    self.nextOrbitalShortcut = QShortcut(QKeySequence('PgDown'), self)
    self.nextOrbitalShortcut.activated.connect(self.next_orbital)
    self.alphaShortcut = QShortcut(QKeySequence('A'), self)
    self.alphaShortcut.activated.connect(self.select_alpha)
    self.betaShortcut = QShortcut(QKeySequence('B'), self)
    self.betaShortcut.activated.connect(self.select_beta)
    self.frozenButton.setShortcut('F')
    self.inactiveButton.setShortcut('I')
    self.RAS1Button.setShortcut('1')
    self.RAS2Button.setShortcut('2')
    self.RAS3Button.setShortcut('3')
    self.secondaryButton.setShortcut('S')
    self.deletedButton.setShortcut('D')
    self.resetButton.setShortcut('0')
    self.increaseIsovalueShortcut = QShortcut(QKeySequence('+'), self)
    self.increaseIsovalueShortcut.activated.connect(self.increase_isovalue)
    self.decreaseIsovalueShortcut = QShortcut(QKeySequence('-'), self)
    self.decreaseIsovalueShortcut.activated.connect(self.decrease_isovalue)
    self.increaseMoreIsovalueShortcut = QShortcut(QKeySequence('Shift++'), self)
    self.increaseMoreIsovalueShortcut.activated.connect(partial(self.increase_isovalue, True))
    self.decreaseMoreIsovalueShortcut = QShortcut(QKeySequence('Shift+-'), self)
    self.decreaseMoreIsovalueShortcut.activated.connect(partial(self.decrease_isovalue, True))
    self.increaseOpacityShortcut = QShortcut(QKeySequence('O'), self)
    self.increaseOpacityShortcut.activated.connect(self.increase_opacity)
    self.decreaseOpacityShortcut = QShortcut(QKeySequence('T'), self)
    self.decreaseOpacityShortcut.activated.connect(self.decrease_opacity)
    self.increaseMoreOpacityShortcut = QShortcut(QKeySequence('Shift+O'), self)
    self.increaseMoreOpacityShortcut.activated.connect(partial(self.increase_opacity, True))
    self.decreaseMoreOpacityShortcut = QShortcut(QKeySequence('Shift+T'), self)
    self.decreaseMoreOpacityShortcut.activated.connect(partial(self.decrease_opacity, True))
    self.textureButton.setShortcut('X')
    self.surfaceBox.setShortcut('Ctrl+S')
    self.prevSignShortcut = QShortcut(QKeySequence('Ctrl+Shift+PgUp'), self)
    self.prevSignShortcut.activated.connect(self.prev_sign)
    self.nextSignShortcut = QShortcut(QKeySequence('Ctrl+Shift+PgDown'), self)
    self.nextSignShortcut.activated.connect(self.next_sign)
    self.nodesBox.setShortcut('Ctrl+N')
    self.namesBox.setShortcut('Ctrl+M')
    self.boxBox.setShortcut('Ctrl+B')
    self.transformButton.setShortcut('Ctrl+T')
    self.gradientBox.setShortcut('Ctrl+G')
    self.showGradientButton.setShortcut('Ctrl+Shift+G')
    self.downButton.setShortcut('Ctrl+Shift+D')
    self.bothButton.setShortcut('Ctrl+Shift+B')
    self.upButton.setShortcut('Ctrl+Shift+U')
    self.cancelButton.setShortcut('Esc')

    # signals
    self.qApp.aboutToQuit.connect(self.deltmp)
    self.loadAction.triggered.connect(self.load_file)
    self.saveHDF5Action.triggered.connect(self.write_hdf5)
    self.saveInpOrbAction.triggered.connect(self.write_inporb)
    self.saveCubeAction.triggered.connect(self.write_cube)
    self.screenshotAction.triggered.connect(self.show_screenshot)
    self.clearAction.triggered.connect(self.clear)
    self.scratchAction.triggered.connect(self.toggle_cache)
    self.quitAction.triggered.connect(self.close)
    self.keysAction.triggered.connect(self.show_keys)
    self.aboutAction.triggered.connect(self.show_about)
    self.orthographicAction.triggered.connect(self.orthographic)
    self.fitViewAction.triggered.connect(self.reset_camera)
    self.resetCameraAction.triggered.connect(partial(self.reset_camera, True))
    self.fileButton.clicked.connect(self.load_file)
    self.densityTypeButton.currentIndexChanged.connect(self.densityTypeButton_changed)
    self.rootButton.currentIndexChanged.connect(self.rootButton_changed)
    self.irrepButton.currentIndexChanged.connect(self.irrepButton_changed)
    self.orbitalButton.currentIndexChanged.connect(self.orbitalButton_changed)
    self.spinButton.currentIndexChanged.connect(self.spinButton_changed)
    self.listButton.clicked.connect(self.show_list)
    self.typeButtonGroup.buttonClicked.connect(self.typeButtonGroup_changed)
    self.resetButton.clicked.connect(self.reset_type)
    self.isovalueSlider.valueChanged.connect(self.isovalueSlider_changed)
    self.isovalueBox.editingFinished.connect(self.isovalueBox_changed)
    self.opacitySlider.valueChanged.connect(self.opacitySlider_changed)
    self.opacityBox.editingFinished.connect(self.opacityBox_changed)
    self.textureButton.clicked.connect(self.show_texture)
    self.surfaceBox.stateChanged.connect(self.toggle_surface)
    self.signButton.currentIndexChanged.connect(self.sign_changed)
    self.nodesBox.stateChanged.connect(self.toggle_nodes)
    self.moleculeButton.currentIndexChanged.connect(self.molecule_changed)
    self.namesBox.stateChanged.connect(self.toggle_names)
    self.boxBox.stateChanged.connect(self.toggle_box)
    self.boxSizeBox.editingFinished.connect(self.boxSizeBox_changed)
    self.transformButton.clicked.connect(self.edit_transform)
    self.gridPointsBox.editingFinished.connect(self.gridPointsBox_changed)
    self.gradientBox.stateChanged.connect(self.toggle_gradient)
    self.showGradientButton.clicked.connect(self.toggle_gradient_options)
    self.lineDensityBox.editingFinished.connect(self.lineDensityBox_changed)
    self.startRadiusBox.editingFinished.connect(self.startRadiusBox_changed)
    self.maxStepsBox.editingFinished.connect(self.maxStepsBox_changed)
    self.directionButtonGroup.buttonClicked.connect(self.directionButtonGroup_changed)
    self.cancelButton.clicked.connect(self.cancel)

  def init_VTK(self):
    framelayout = QVBoxLayout()
    try:
      self.vtkWidget = SimpleVTK(self.frame, stereo=1)
    except:
      self.vtkWidget = SimpleVTK(self.frame, Qt.WindowFlags(), stereo=1)
    self.vtkWidget.setWhatsThis('Render window where the orbitals are displayed. Click and drag with the primary (left) mouse button to rotate; use the secondary (right) button, the wheel, or Ctrl+Shift+primary to zoom; the tertiary (middle) button or Shift+primary to translate; Ctrl+primary to rotate in the screen plane.')
    framelayout.addWidget(self.vtkWidget)
    framelayout.setContentsMargins(0, 0, 0, 0)
    self.frame.setLayout(framelayout)

    self.ren = vtk.vtkRenderer()
    self.ren.UseDepthPeelingOn()
    self.ren.SetMaximumNumberOfPeels(20)
    self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
    self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
    self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    #self.iren.Initialize()
    t = Initializer(self)
    t.wait()

    self.lut = vtk.vtkLookupTable()
    self.lut.SetNumberOfTableValues(3)
    self.lut.SetTableValue(0, *self.textureDock.negcolor)
    self.lut.SetTableValue(1, *self.textureDock.zerocolor)
    self.lut.SetTableValue(2, *self.textureDock.poscolor)
    self.lut.SetTableRange(-np.finfo(np.float).eps, np.finfo(np.float).eps)
    self.lut.SetNanColor(1, 1, 1, 1)

    # lighting
    light1 = vtk.vtkLight()
    light1.SetColor(1.0, 1.0, 1.0)
    light2 = vtk.vtkLight()
    light1.DeepCopy(light2)
    light3 = vtk.vtkLight()
    light1.DeepCopy(light3)
    light1.SetIntensity(1.0)
    light1.SetPosition(self.light_pos(45, 45))
    light1.SetLightTypeToCameraLight()
    light2.SetIntensity(0.6)
    light2.SetPosition(self.light_pos(-30, -60))
    light2.SetLightTypeToCameraLight()
    light3.SetIntensity(0.5)
    light3.SetPosition(self.light_pos(-30, 60))
    light3.SetLightTypeToCameraLight()
    self.ren.AutomaticLightCreationOff()
    self.ren.RemoveAllLights()
    self.ren.AddLight(light1)
    self.ren.AddLight(light2)
    self.ren.AddLight(light3)

    self.ren.SetBackground(*background_color['?'])

    # fonts
    try:
      self.sansFont = registry.fontFile('Droid Sans')
    except (NameError, KeyError):
      self.sansFont = None
    try:
      self.sansBoldFont = registry.fontFile('Droid Sans Bold')
    except (NameError, KeyError):
      self.sansBoldFont = None
    try:
      self.monoFont = registry.fontFile('Droid Sans Mono')
    except (NameError, KeyError):
      self.monoFont = None

    self.ready = True

  def deltmp(self):
    try:
      if (self._cache_file is not None):
        del self._cache_file
      rmtree(self._tmpdir)
    except:
      pass

  #========= properties

  @property
  def ready(self):
    return self._ready

  @ready.setter
  def ready(self, value):
    self._ready = value

  @property
  def filename(self):
    return self._filename

  @filename.setter
  def filename(self, value):
    old = self._filename
    self._filename = value
    self._filename_changed(value, old)

  def _filename_changed(self, new, old):
    if (new is None):
      self.filenameLabel.setText('')
      return
    ftype = self.detect_format(new)
    if (ftype is None):
      error = 'File {0} not found'.format(new)
      self.show_error(error)
      return
    elif (ftype == 'unknown'):
      error = 'Format of {0} not recognized'.format(new)
      self.show_error(error)
      return
    elif (ftype in ['inporb']):
      try:
        assert (self.orbitals.type == 'hdf5')
      except (AssertionError, AttributeError):
        error = 'The InpOrb format does not contain basis set information, it must be loaded after an HDF5 file (*.h5)'
        self.show_error(error)
        return
    self.setStatus('Reading...')
    if (self._fileReadThread is not None):
      self._fileReadThread.wait()
    self._fileReadThread = FileRead(self, filename=new, ftype=ftype)
    self._fileReadThread.disable_list = [self.loadAction, self.saveMenu, self.clearAction, self.fileButton]
    self._fileReadThread.finished.connect(self.file_read)
    self._fileReadThread.start()

  @property
  def isGrid(self):
    return isinstance(self.orbitals, Grid)

  @property
  def orbitals(self):
    return self._orbitals

  @orbitals.setter
  def orbitals(self, value):
    self._orbitals = value
    self._orbitals_changed(value)

  def _orbitals_changed(self, new):
    enabled = new is not None
    self.orbitalGroup.setEnabled(enabled)
    self.saveHDF5Action.setEnabled(enabled and (new.type == 'hdf5'))
    self.MO = None
    self.xyz = None
    try:
      roots = new.roots
    except AttributeError:
      roots = ['Average']
    self.rootButton.clear()
    for i,r in enumerate(roots):
      self.rootButton.addItem(r)
    densities = ['State']
    try:
      if (self.orbitals.sdm.shape):
        densities.append('Spin')
    except:
      pass
    if (len(roots) > 2):
      densities.append('Difference')
      if (self.orbitals.tdm is not None):
        densities.append('Transition')
    if ((len(roots) > 2) or (enabled and (new.wf == 'PT2'))):
      self.rootGroup.setEnabled(True)
      self.rootGroup.show()
    else:
      self.rootGroup.setEnabled(False)
      self.rootGroup.hide()
    self.densityTypeButton.clear()
    for d in densities:
      self.densityTypeButton.addItem(d)
    if (len(densities) > 1):
      self.densityTypeGroup.setEnabled(True)
      self.densityTypeGroup.show()
    else:
      self.densityTypeGroup.setEnabled(False)
      self.densityTypeGroup.hide()
    if (not enabled):
      self.orbital = None
      self.haveBasis = False
      self.haveInpOrb = False
      self.irreplist = []
      self.spinlist = ['']
      self.type_setEnabled(False)
      self.set_typeButtonGroup()
      return
    self.haveBasis = isinstance(new, Orbitals)
    self.haveInpOrb = new.inporb is not None
    # Select initial orbital
    self.initial_orbital()
    # Generate list of irreps
    irreplist = []
    for o in new.MO + new.MO_a + new.MO_b:
      s = o['sym']
      if (s not in irreplist):
        irreplist.append(s)
    if ('z' in irreplist):
      irreplist.remove('z')
    self.irreplist = irreplist
    # Generate list of spins
    spinlist = []
    if (len(new.MO_a) > 0):
      spinlist.append('alpha')
    if (len(new.MO_b) > 0):
      spinlist.append('beta')
    if ((len(new.MO) > 0) and spinlist):
      spinlist.insert(0, u'—')
    if (not spinlist):
      spinlist = ['']
    self.spinlist = spinlist
    # Create the list of orbitals for notes
    self.build_notes()
    self.ready = False
    # Create molecule (nuclei)
    self.new_mol()
    # Create the box
    self.surface = None
    self.nodes = None
    self.gradient = None
    self.new_box()
    self.toggle_names()
    if (self.box is not None):
      v = self.box.GetVisibility()
      self.box.VisibilityOn()
      self.reset_camera(new.type != 'inporb')
      self.box.SetVisibility(v)
    else:
      self.reset_camera(new.type != 'inporb')
    self.ready = True
    self.vtk_update()

  @property
  def orbital(self):
    return self._orbital

  @orbital.setter
  def orbital(self, value):
    old = self._orbital
    self._orbital = value
    self._orbital_changed(value, old)

  def _orbital_changed(self, new, old):
    if (new == old):
      if ((new is not None) and (not self._tainted)):
        return
    self.signButton.setEnabled(new != 0)
    self.build_surface()

  @property
  def MO(self):
    return self._MO

  @MO.setter
  def MO(self, value):
    self._MO = value
    if ((self.orbital is not None) and (self.orbital > 0)):
      self._tainted = True
    if (self.rootButton.count() > 1):
      self.root = self.root
    self.populate_orbitals()
    self._tainted = False

  @property
  def notes(self):
    return self._notes

  @notes.setter
  def notes(self, value):
    self._notes = value
    self._notes_changed(value)

  def _notes_changed(self, new):
    enabled = new is not None
    self.listDock.set_list()

  @property
  def xyz(self):
    return self._xyz

  @xyz.setter
  def xyz(self, value):
    self._xyz = value
    self._newgrid = True

  @property
  def surface(self):
    return self._surface_actor

  @surface.setter
  def surface(self, value):
    if (self._surface_actor is not None):
      self.ren.RemoveActor(self._surface_actor)
    self._surface_actor = value
    if (self._surface_actor is not None):
      self.ren.AddActor(self._surface_actor)
    self._surface_changed(value)

  def _surface_changed(self, new):
    enabled = new is not None
    self.isovalueGroup.setEnabled(enabled)
    self.opacityGroup.setEnabled(enabled)
    self.surfaceBox.setEnabled(enabled)
    self.signButton.setEnabled(enabled)
    self.saveCubeAction.setEnabled(enabled)

  @property
  def nodes(self):
    return self._nodes_actor

  @nodes.setter
  def nodes(self, value):
    if (self._nodes_actor is not None):
      self.ren.RemoveActor(self._nodes_actor)
    self._nodes_actor = value
    if (self._nodes_actor is not None):
      self.ren.AddActor(self._nodes_actor)
    self._nodes_changed(value)

  def _nodes_changed(self, new):
    enabled = new is not None
    self.nodesBox.setEnabled(enabled)

  @property
  def mol(self):
    return self._mol_actor

  @mol.setter
  def mol(self, value):
    if (self._mol_actor is not None):
      self.ren.RemoveActor(self._mol_actor)
    self._mol_actor = value
    if (self._mol_actor is not None):
      self.ren.AddActor(self._mol_actor)
    self._mol_changed(value)

  def _mol_changed(self, new):
    enabled = new is not None
    self.moleculeGroup.setEnabled(enabled)

  @property
  def names(self):
    return self._names_actor

  @names.setter
  def names(self, value):
    if (self._names_actor is not None):
      self.ren.RemoveActor(self._names_actor)
    self._names_actor = value
    if (self._names_actor is not None):
      self.ren.AddActor(self._names_actor)
    self._names_changed(value)

  def _names_changed(self, new):
    enabled = new is not None
    self.namesBox.setEnabled(enabled)

  @property
  def box(self):
    return self._box_actor

  @box.setter
  def box(self, value):
    if (self._box_actor is not None):
      self.ren.RemoveActor(self._box_actor)
    self._box_actor = value
    if (self._box_actor is not None):
      self.ren.AddActor(self._box_actor)
    self._box_changed(value)

  def _box_changed(self, new):
    enabled = new is not None
    self.boxBox.setEnabled(enabled)

  @property
  def axes(self):
    return self._axes_actor

  @axes.setter
  def axes(self, value):
    if (self._axes_actor is not None):
      self.ren.RemoveActor(self._axes_actor)
    self._axes_actor = value
    if (self._axes_actor is not None):
      self.ren.AddActor(self._axes_actor)

  @property
  def gradient(self):
    return self._gradient_actor

  @gradient.setter
  def gradient(self, value):
    if (self._gradient_actor is not None):
      self.ren.RemoveActor(self._gradient_actor)
    self._gradient_actor = value
    if (self._gradient_actor is not None):
      self.ren.AddActor(self._gradient_actor)
    self._gradient_changed(value)

  def _gradient_changed(self, new):
    enabled = new is not None
    self.gradientBox.setEnabled(enabled)
    if (not enabled):
      self.gradientBox.setChecked(False)

  @property
  def panel(self):
    return self._panel_actor

  @panel.setter
  def panel(self, value):
    if (self._panel_actor is not None):
      self.ren.RemoveActor2D(self._panel_actor)
    self._panel_actor = value
    if (self._panel_actor is not None):
      self.ren.AddActor2D(self._panel_actor)
    self._panel_changed(value)

  def _panel_changed(self, new):
    enabled = new is not None

  @property
  def haveBasis(self):
    return self._haveBasis

  @haveBasis.setter
  def haveBasis(self, value):
    self._haveBasis = value
    self.boxSizeGroup.setEnabled(value)
    self.transformDock.set_enabled(value)
    self.gridPointsGroup.setEnabled(value)
    if (self.orbitals is None):
      self.gridPointsGroup.setEnabled(True)

  @property
  def haveInpOrb(self):
    return self._haveInpOrb

  @haveInpOrb.setter
  def haveInpOrb(self, value):
    self._haveInpOrb = value
    self.saveInpOrbAction.setEnabled(value)

  @property
  def dens(self):
    return self._dens

  @dens.setter
  def dens(self, value):
    old = self._dens
    self._dens = value
    self._dens_changed(value, old)

  def _dens_changed(self, new, old):
    try:
      roots = self.orbitals.roots
    except AttributeError:
      roots = ['Average']
    if (new in ['State', 'Spin']):
      items = roots
    elif (new in ['Difference', 'Transition']):
      rootids = []
      for r in roots:
        i = r.find(':')
        if (i > 0):
          rootids.append(r[0:i])
      items = []
      for i,r1 in enumerate(rootids):
        for r2 in rootids[i+1:]:
          items.append(u'{0} → {1}'.format(r1, r2))
    if (new != old):
      self._tainted = True
    old_root = self.rootButton.currentText()
    self.rootButton.blockSignals(True)
    self.rootButton.clear()
    for r in items:
      self.rootButton.addItem(r)
    index = self.rootButton.findText(old_root)
    if (index >= 0):
      self.rootButton.setCurrentIndex(index)
    self.rootButton.blockSignals(False)
    self.root = self.rootButton.currentIndex()

  @property
  def root(self):
    return self._root

  @root.setter
  def root(self, value):
    old = self._root
    self._root = value
    self._root_changed(value, old)

  def _root_changed(self, new, old):
    if (self.MO is None):
      return
    if (self.dens == 'State'):
      dm = self.orbitals.dm[new]
    elif (self.dens == 'Spin'):
      dm = self.orbitals.sdm[new]
    elif (self.dens == 'Difference'):
      n = len(self.orbitals.roots)-1
      r1 = int((2*n-1-np.sqrt((2*n-1)**2-8*new))/2)
      r2 = new+1+int((r1**2-(2*n-3)*r1)/2)
      dm = self.orbitals.dm[r2+1]-self.orbitals.dm[r1+1]
    elif (self.dens == 'Transition'):
      n = len(self.orbitals.roots)-1
      r1 = int((2*n-1-np.sqrt((2*n-1)**2-8*new))/2)
      r2 = new+1+int((r1**2-(2*n-3)*r1)/2)
      dm = self.orbitals.tdm[r2*(r2-1)//2+r1]
    if (self.orbitals.wf == 'PT2'):
      fix_frozen = True
      tp_act = set([o['type'] for o in self.MO])
      tp_act -= set(['F', 'D'])
      act = [o for o in self.MO if (o['type'] in tp_act)]
    else:
      fix_frozen = False
      tp_act = ['1', '2', '3']
      act = [o for o in self.MO if (o['type'] in tp_act)]
    if (len(act) != dm.shape[0]):
      self.show_error('Wrong density matrix size.')
      return
    if (self.dens == 'State'):
      if (np.allclose(dm, np.diag(np.diag(dm)), atol=1e-20)):
        for o in self.MO:
          o.pop('root_occup', None)
          o.pop('root_ene', None)
        for o,n in zip(act, np.diag(dm)):
          if (n != o['occup']):
            o['root_occup'] = n
          o.pop('root_coeff', None)
          o.pop('root_coeffl', None)
          o.pop('root_coeffr', None)
          o.pop('root_type', None)
      else:
        for s in set([o['sym'] for o in act]):
          symidx = [i for i,o in enumerate(act) if (o['sym'] == s)]
          symdm = dm[np.ix_(symidx,symidx)]
          symact = [act[i] for i in symidx]
          occ, vec = np.linalg.eigh(symdm)
          freevec = [1 for i in symidx]
          idx = [-1 for i in symidx]
          for i in range(len(symidx)):
            idx[i] = np.argmax(abs(vec[i,:]*freevec))
            if (vec[i,idx[i]] < 0.0):
              vec[:,idx[i]] *= -1
            freevec[idx[i]] = 0
          occ = occ[idx]
          vec = vec[:,idx]
          # Check contributions for each orbital, if there are significant
          # contributions from several types, mark this type as '?'
          mix = []
          for i in range(vec.shape[1]):
            types = []
            for a in tp_act:
              if (sum([j**2 for n,j in enumerate(vec[:,i]) if (symact[n]['type']==a)]) > 1.0-1e-4):
                types.append(a)
            mix.append(types[0] if (len(types) == 1) else '?')
          new_MO = np.dot(vec.T, [o['coeff'] for o in symact])
          for o,n,c,t in zip(symact, occ, new_MO, mix):
            o['root_occup'] = n
            o['root_coeff'] = c
            o['root_type'] = t
            o['root_ene'] = 0.0
      if (fix_frozen):
        for o in self.MO:
          if (o['type'] == 'F'):
            o['root_occup'] = 2.0
    elif (self.dens in ['Spin', 'Difference']):
      for o in self.MO:
        o['root_occup'] = 0.0
        o['root_ene'] = 0.0
      for s in set([o['sym'] for o in act]):
        symidx = [i for i,o in enumerate(act) if (o['sym'] == s)]
        symdm = dm[np.ix_(symidx,symidx)]
        symact = [act[i] for i in symidx]
        occ, vec = np.linalg.eigh(symdm)
        mix = []
        for i in range(vec.shape[1]):
          types = []
          for a in tp_act:
            if (sum([j**2 for n,j in enumerate(vec[:,i]) if (symact[n]['type']==a)]) > 1.0-1e-6):
              types.append(a)
          mix.append(types[0] if (len(types) == 1) else '?')
        new_MO = np.dot(vec.T, [o['coeff'] for o in symact])
        for o,n,c,t in zip(symact, occ, new_MO, mix):
          o['root_occup'] = n
          o['root_coeff'] = c
          o['root_type'] = t
    elif (self.dens == 'Transition'):
      for o in self.MO:
        o['root_occup'] = 0.0
        o['root_ene'] = 0.0
      for s in set([o['sym'] for o in act]):
        symidx = [i for i,o in enumerate(act) if (o['sym'] == s)]
        symdm = dm[np.ix_(symidx,symidx)]
        symact = [act[i] for i in symidx]
        vecl, occ, vecr = np.linalg.svd(symdm)
        vecr = vecr.T
        mix = []
        for i in range(vecl.shape[1]):
          types = []
          for a in tp_act:
            if (sum([j**2 for n,j in enumerate(vecl[:,i]) if (symact[n]['type']==a)]) > 1.0-1e-6):
              types.append(a)
            if (sum([j**2 for n,j in enumerate(vecr[:,i]) if (symact[n]['type']==a)]) > 1.0-1e-6):
              if (a not in types):
                types.append(a)
          mix.append(types[0] if (len(types) == 1) else '?')
        new_MOl = np.dot(vecl.T, [o['coeff'] for o in symact])
        new_MOr = np.dot(vecr.T, [o['coeff'] for o in symact])
        for o,n,cl,cr,t in zip(symact, occ, new_MOl, new_MOr, mix):
          o['root_occup'] = n**2/2
          o['root_coeffl'] = cl
          o['root_coeffr'] = cr
          if (self.spin == 'hole'):
            o['root_coeff'] = cl
          elif (self.spin == 'particle'):
            o['root_coeff'] = cr
          o['root_type'] = t
    if (self.dens == 'Transition'):
      spinlist = ['hole', 'particle']
    else:
      try:
        spinlist = []
        if (len(new.MO_a) > 0):
          spinlist.append('alpha')
        if (len(new.MO_b) > 0):
          spinlist.append('beta')
        if ((len(new.MO) > 0) and spinlist):
          spinlist.insert(0, '—')
        if (not spinlist):
          spinlist = ['']
      except:
        spinlist = ['']
    if (set(spinlist) != set(self.spinlist)):
      self.spinlist = spinlist
    if ((self.orbital <= 0) or (self.MO[self.orbital-1]['type'] in tp_act)):
      self._tainted = True
    self.populate_orbitals()
    self._tainted = False

  @property
  def irrep(self):
    return self._irrep

  @irrep.setter
  def irrep(self, value):
    old = self._irrep
    self._irrep = value
    if (value != old):
      self.populate_orbitals()

  @property
  def irreplist(self):
    return self._irreplist

  @irreplist.setter
  def irreplist(self, value):
    self._irreplist = value
    self.irrepButton.clear()
    self.irrepButton.addItem('All')
    enabled = len(value) > 1
    if (enabled):
      for i in value:
        self.irrepButton.addItem(i)
    self.irrepGroup.setEnabled(enabled)

  @property
  def nosym(self):
    return len(self.irreplist) <= 1

  @property
  def spin(self):
    return self._spin

  @spin.setter
  def spin(self, value):
    self._spin = value
    self._spin_changed(value)

  def _spin_changed(self, new):
    if (self.orbitals is None):
      return
    if (new == 'hole'):
      for o in self.MO:
        if ('root_coeffl' in o):
          o['root_coeff'] = o['root_coeffl']
    if (new == 'particle'):
      for o in self.MO:
        if ('root_coeffr' in o):
          o['root_coeff'] = o['root_coeffr']
    if (new == 'alpha'):
      self.MO = self.orbitals.MO_a
    elif (new == 'beta'):
      self.MO = self.orbitals.MO_b
    else:
      self.MO = self.orbitals.MO

  @property
  def spinlist(self):
    return self._spinlist

  @spinlist.setter
  def spinlist(self, value):
    self._spinlist = value
    self.spinButton.clear()
    for i in value:
      self.spinButton.addItem(i)
    enabled = len(value) > 1
    self.spinButton.setEnabled(enabled)
    if (len(value) > 1):
      self.spinButton.show()
    else:
      self.spinButton.hide()

  @property
  def isovalue(self):
    return self._isovalue

  @isovalue.setter
  def isovalue(self, value):
    old = self._isovalue
    self._isovalue = value
    self._isovalue_changed(value, old)

  def _isovalue_changed(self, new, old):
    logrange = np.log(self._maxval/self._minval)
    reldist = np.log(new/self._minval)/logrange
    slider_value = round(self.isovalueSlider.maximum() - reldist * (self.isovalueSlider.maximum() + self.isovalueSlider.minimum()))
    self.isovalueSlider.blockSignals(True)
    self.isovalueSlider.setValue(slider_value)
    self.isovalueSlider.blockSignals(False)
    if (self.surface is not None):
      contour = get_input_type(self.surface.GetMapper(), vtk.vtkContourFilter)
      if (self.orbital == 0):
        val = [True, False]
      else:
        try:
          val = [i.toBool() for i in self.signButton.currentData().toList()]
        except AttributeError:
          try:
            val = [i.toBool() for i in self.signButton.itemData(self.signButton.currentIndex()).toList()]
          except AttributeError:
            val = self.signButton.itemData(self.signButton.currentIndex())
      contour.SetNumberOfContours(np.count_nonzero(val))
      i = 0
      if (val[0]):
        contour.SetValue(i, new)
        i += 1
      if (val[1]):
        contour.SetValue(i, -new)
      self.vtk_update()

  @property
  def opacity(self):
    return self._opacity

  @opacity.setter
  def opacity(self, value):
    old = self._opacity
    self._opacity = value
    self._opacity_changed(value, old)

  def _opacity_changed(self, new, old):
    if (new == old):
      return
    slider_value = round(self.opacitySlider.minimum() + new * (self.opacitySlider.maximum() + self.opacitySlider.minimum()))
    self.opacitySlider.blockSignals(True)
    self.opacitySlider.setValue(slider_value)
    self.opacitySlider.blockSignals(False)
    if (self.surface is None):
      return
    self.surface.GetProperty().SetOpacity(new)
    self.vtk_update()

  @property
  def boxSize(self):
    return self._boxSize

  @boxSize.setter
  def boxSize(self, value):
    old = self._boxSize
    self._boxSize = value
    self._boxSize_changed(value, old)

  def _boxSize_changed(self, new, old):
    if (new == old):
      return
    self.boxSizeBox.setText('def')
    self.boxSizeBox.editingFinished.emit()
    if (self.boxSize is not None):
      self.build_grid()

  @property
  def transform(self):
    return self._transform

  @transform.setter
  def transform(self, value):
    old = self._transform
    self._transform = value
    self._transform_changed(value, old)

  def _transform_changed(self, new, old):
    if (new == old):
      return
    self.transformDock.set_boxes(new)
    if (self.transform is not None):
      self.build_grid()

  @property
  def gridPoints(self):
    return self._gridPoints

  @gridPoints.setter
  def gridPoints(self, value):
    old = self._gridPoints
    self._gridPoints = value
    self._gridPoints_changed(value, old)

  def _gridPoints_changed(self, new, old):
    if ((new == old) or (new is None)):
      return
    self.gridPointsBox.setText('def')
    self.gridPointsBox.editingFinished.emit()
    self.build_grid()

  @property
  def lineDensity(self):
    return self._lineDensity

  @lineDensity.setter
  def lineDensity(self, value):
    old = self._lineDensity
    self._lineDensity = value
    self._lineDensity_changed(value, old)

  def _lineDensity_changed(self, new, old):
    if ((new == old) or (new is None)):
      return
    self.lineDensityBox.setText('def')
    self.lineDensityBox.editingFinished.emit()
    self.set_gradient_source()

  @property
  def startRadius(self):
    return self._startRadius

  @startRadius.setter
  def startRadius(self, value):
    old = self._startRadius
    self._startRadius = value
    self._startRadius_changed(value, old)

  def _startRadius_changed(self, new, old):
    if ((new == old) or (new is None)):
      return
    self.startRadiusBox.setText('def')
    self.startRadiusBox.editingFinished.emit()
    self.set_gradient_source()

  @property
  def maxSteps(self):
    return self._maxSteps

  @maxSteps.setter
  def maxSteps(self, value):
    old = self._maxSteps
    self._maxSteps = value
    self._maxSteps_changed(value, old)

  def _maxSteps_changed(self, new, old):
    if ((new == old) or (new is None)):
      return
    self.maxStepsBox.setText('def')
    self.maxStepsBox.editingFinished.emit()
    self.set_gradient_source()

  #=========

  def light_pos(self, elevation, azimuth):
    e = np.deg2rad(elevation)
    a = np.deg2rad(azimuth)
    return [np.cos(e)*np.sin(a), np.sin(e), np.cos(e)*np.cos(a)]

  def clear(self):
    self.filename = None
    self.orbitals = None
    self.MO = None
    self.notes = None
    self.surface = None
    self.nodes = None
    self.mol = None
    self.names = None
    self.box = None
    self.axes = None
    self.gradient = None
    self.panel = None
    self.ren.SetBackground(*background_color['?'])
    self.vtk_update()

  def load_file(self):
    result = QFileDialog.getOpenFileName(self, 'Load file')
    try:
      filename, _ = result
    except ValueError:
      filename = result
    if (filename):
      self.filename = str(filename)

  # Detect the format of an input file
  def detect_format(self, infile):
    if (not os.path.isfile(infile)):
      return None
    try:
      with h5py.File(infile, 'r') as f:
        return 'hdf5'
    except (OSError, IOError):
      with open(infile, 'rb') as f:
        line = f.readline().decode('ascii', errors='replace')
        if (re.search(r'\[MOLDEN FORMAT\]', line, re.IGNORECASE)):
          return 'molden'
        elif (line.startswith('#INPORB')):
          return 'inporb'
        else:
          try:
            N = int(line)
            line = f.readline()
            for i in range(N):
              line = f.readline().decode('ascii', errors='replace')
            line = f.readline().decode('ascii', errors='replace')
            assert (line.strip() == '<GRID>')
            return 'luscus'
          except:
            f.seek(0)
            line = f.readline()
            line = f.readline()
            line = f.readline().decode('ascii', errors='replace')
            if (line.startswith('Natom=')):
              return 'grid'
            else:
              try:
                data = line.split()
                N = int(data[0])
                o = (float(i) for i in data[1:])
                return 'cube'
              except:
                pass
    return 'unknown'

  def setStatus(self, text, force=False):
    # Try to to change status too fast, it may cause crashes
    t = time.time()
    if (t - self._timestamp >= 0.05):
      self.statusLabel.setText(text)
      self._timestamp = time.time()
    elif (force):
      time.sleep(0.05)
      self.statusLabel.setText(text)
      self._timestamp = time.time()

  def file_read(self):
    self.setStatus('Ready.', force=True)
    if (self._fileReadThread.error is None):
      self.filenameLabel.setText(self.filename)
    else:
      self.show_error(self._fileReadThread.error)
      return
    self._fileReadThread.quit()
    self._fileReadThread.wait()
    self.orbitals = self._fileReadThread.orbitals

  # Return a string with orbital information for the drop-down list
  def orb_to_list(self, n, orb):
    if ('label' in orb):
      return '{0}'.format(orb['label'])
    else:
      num = orb.get('num', n)
      # Build irrep and local numbering
      if (self.nosym):
        numsym = ''
      else:
        if (self.irrep == 'All'):
          numsym = ' [{0}]'.format(orb['sym'])
        else:
          m = [o['sym'] for o in self.MO[:n]].count(orb['sym'])
          numsym = ' [{0}, {1}]'.format(orb['sym'], m)
      # Add new type if it has been modified
      tp = orb.get('root_type', orb['type'])
      if (('newtype' in orb) and (orb['newtype'] != tp)):
        tp += u'→' + orb['newtype']
      return u'{0}{1}: {2:.4f} ({3:.4f}) {4}'.format(num, numsym, orb.get('root_ene', orb['ene']), orb.get('root_occup', orb['occup']), tp)

  def populate_orbitals(self):
    prev = self.orbital
    self.orbitalButton.blockSignals(True)
    self.orbitalButton.clear()
    if (self.MO is None):
      return
    if (self.irrep == 'All'):
      orblist = {i+1:self.orb_to_list(i+1, o) for i,o in enumerate(self.MO)}
      if ((not self.isGrid) and any([(o.get('root_occup', o['occup']) != 0.0) for o in self.MO])):
        is_it_spin = (self.dens == 'State') and any([(o.get('root_occup', o['occup']) < -1e-4) for o in self.MO])
        if (self.dens == 'State'):
          if (not is_it_spin):
            orblist[0] = 'Density'
            orblist[-2] = 'Laplacian (numerical)'
          if (is_it_spin or ('beta' in self.spinlist)):
            orblist[-1] = 'Spin density'
        elif (self.dens == 'Spin'):
          orblist[-3] = 'Spin density'
        elif (self.dens == 'Difference'):
          orblist[-3] = 'Difference density'
          orblist[-4] = 'Attachment density'
          orblist[-5] = 'Detachment density'
        elif (self.dens == 'Transition'):
          if (self.spin == 'hole'):
            orblist[-3] = 'Hole density'
          elif (self.spin == 'particle'):
            orblist[-3] = 'Particle density'
    else:
      orblist = {i+1:self.orb_to_list(i+1, o) for i,o in enumerate(self.MO) if (o['sym'] == self.irrep)}
    for k in sorted(orblist.keys()):
      self.orbitalButton.addItem(orblist[k], k)
    new = self.orbitalButton.findData(prev)
    if ((new < 0) and (prev < 0)):
      new = self.orbitalButton.findData(0)
    if (new < 0):
      new = self.orbitalButton.findData(-3)
    if (new < 0):
      new = 0
    self.orbitalButton.setCurrentIndex(new)
    self.orbitalButton.blockSignals(False)
    self.orbitalButton.currentIndexChanged.emit(new)

  def build_notes(self):
    notes = []
    if (self.orbitals.MO_b):
      alphaMO = self.orbitals.MO_a
    else:
      alphaMO = self.orbitals.MO
    for i,orb in enumerate([j for i in zip_longest(alphaMO, self.orbitals.MO_b) for j in i]):
      if (orb is None):
        continue
      note = {}
      if ('label' in orb):
        note['name'] = orb['label']
      else:
        if (i%2 == 0):
          num = '{0}'.format(i//2+1)
        else:
          num = '{0}b'.format(i//2+1)
        if (self.nosym):
          note['name'] = '#{0} {1:.4f} {2}'.format(num, orb['ene'], orb['type'])
        else:
          note['name'] = '#{0} [{1}] {2:.4f} {3}'.format(num, orb['sym'], orb['ene'], orb['type'])
      note['occup'] = orb['occup']
      # This could be nice, but it's not so good when changing states or density types
      #note['density'] = orb['occup'] != 0
      note['density'] = True
      note['note'] = ''
      notes.append(note)
    for i,note in enumerate(notes):
      try:
        note['note'] = self.orbitals.notes[i]
      except:
        pass
    self.notes = notes

  def initial_orbital(self):
    if (len(self.orbitals.MO_b) > 0):
      maxocc = 1.0
    else:
      maxocc = 2.0
    minene = -np.inf
    orb = -10
    if (self.MO is None):
      MO = self.orbitals.MO if (self.orbitals.MO) else self.orbitals.MO_a
    else:
      MO = self.MO
    for i,o in enumerate(MO):
      if ((o['occup'] >= maxocc/2) and (o['ene'] >= minene)):
        orb = i+1
        minene = o['ene']
    if (orb < 0):
      orb = 1
    self.orbital = orb

  def new_mol(self):
    # Assign nuclear radii
    r = np.array([c['Z'] for c in self.orbitals.centers])
    try:
      r = np.cbrt(r)
    except AttributeError:
      r = np.power(r, 1.0/3)
    r[r<0.5] = 0.5
    # Create VTK objects
    pt = vtk.vtkPeriodicTable()
    vtkr = numpy_support.numpy_to_vtk(0.1*r, 1, vtk.VTK_DOUBLE)
    vtkr.SetName('radii')
    vtkl = vtk.vtkStringArray()
    for c in self.orbitals.centers:
      vtkl.InsertNextValue(c['name'])
    vtkl.SetName('labels')
    pts = vtk.vtkPoints()
    for c in self.orbitals.centers:
      pts.InsertNextPoint(*c['xyz'])
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.GetPointData().AddArray(vtkl)
    # Add actor for molecule
    mol = vtk.vtkMolecule()
    # Change coordinates in angstrom for setting bonds
    for i,c in enumerate(self.orbitals.centers):
      xyz = c['xyz']*angstrom
      mol.AppendAtom(c['Z'], *xyz)
    bp = vtk.vtkSimpleBondPerceiver()
    bp.SetInputData(mol)
    bp.Update()
    molb = vtk.vtkMolecule()
    molb.DeepCopy(bp.GetOutput())
    # Change coordinates back to bohr
    for i in range(molb.GetNumberOfAtoms()):
      xyz = np.array(molb.GetAtomPosition(i))/angstrom
      molb.SetAtomPosition(i, *xyz)
    # Remove (hide) bonds with ghost atoms
    for i in range(molb.GetNumberOfBonds()):
      Z1 = molb.GetBond(i).GetBeginAtom().GetAtomicNumber()
      Z2 = molb.GetBond(i).GetEndAtom().GetAtomicNumber()
      if ((Z1 < 1) or (Z2 < 1)):
        molb.SetBondOrder(i, 0)
    molb.GetVertexData().AddArray(vtkr)
    mm = vtk.vtkMoleculeMapper()
    mm.SetInputData(molb)
    mm.SetRenderAtoms(True)
    mm.SetAtomicRadiusScaleFactor(0.3)
    mm.SetBondRadius(0.075)
    if (True):
      mm.SetAtomicRadiusTypeToVDWRadius()
      mm.SetRenderBonds(True)
    else:
      mm.SetAtomicRadiusTypeToCustomArrayRadius()
      mm.SetRenderBonds(False)
    self.mol = vtk.vtkActor()
    self.mol.SetMapper(mm)
    self.set_representation(self.moleculeButton.currentIndex())
    # Add actor for names
    l = vtk.vtkLabeledDataMapper()
    try:
      l.SetInputData(pd)
    except AttributeError:
      l.SetInput(pd)
    l.SetLabelModeToLabelFieldData()
    l.SetFieldDataName('labels')
    l.GetLabelTextProperty().SetColor(0, 0, 0)
    if (self.sansBoldFont is not None):
      l.GetLabelTextProperty().SetFontFamily(vtk.VTK_FONT_FILE)
      l.GetLabelTextProperty().SetFontFile(self.sansBoldFont)
    else:
      l.GetLabelTextProperty().ItalicOff()
      l.GetLabelTextProperty().BoldOn()
    l.GetLabelTextProperty().ShadowOn()
    l.GetLabelTextProperty().SetJustificationToCentered()
    l.GetLabelTextProperty().SetVerticalJustificationToCentered()
    self.names = vtk.vtkActor2D()
    self.names.SetMapper(l)

  def new_box(self):
    # Center molecule and compute max/min extent (with clearance)
    clearance = 4.0
    xyz = np.array([c['xyz'] for c in self.orbitals.centers])
    extent = np.array([np.amin(xyz, axis=0), np.amax(xyz, axis=0)])
    self.boxSize = None
    self.boxSize = np.ceil(extent[1]-extent[0]+2*clearance).tolist()

  def build_grid(self):
    if (self.isGrid):
      # For precomputed grids, just take the defined grid
      lims = np.array([self.orbitals.orig, self.orbitals.end])
      ngrid = self.orbitals.ngrid
      boxSize = lims[1,:]-lims[0,:]
      matrix = self.orbitals.transform.flatten()
      # Fill up the box size and transformation boxes with the values that would reproduce this grid
      # Since the number of grid points is controlled by a single parameter,
      # we have to scale the axes according to the number of grid divisions
      # and modify the transformation accordingly; out of the infinite
      # possible scalings, we chose the one that will make the determinant
      # of the transformation equal to 1.
      t = vtk.vtkTransform()
      t.SetMatrix(matrix)
      ng = [n-1 for n in ngrid]
      f = np.cbrt(abs(t.GetMatrix().Determinant())*np.prod(boxSize)/np.prod(ng))
      bSize = [np.round(f*n, decimals=2) for n in ng]
      m = np.copy(matrix).reshape(4, 4)
      m[0:3,0] *= boxSize[0]/bSize[0]
      m[0:3,1] *= boxSize[1]/bSize[1]
      m[0:3,2] *= boxSize[2]/bSize[2]
      midpoint = 0.5*(lims[0,:]+lims[1,:])
      m[0:3,3] = t.TransformPoint(midpoint)-self.orbitals.geomcenter
      self.transformDock.set_boxes(np.round(m.flatten(), decimals=6))
      self.boxSizeBox.blockSignals(True)
      self.boxSizeBox.setText('{0}, {1}, {2}'.format(*bSize))
      self.boxSizeBox.blockSignals(False)
    else:
      if (self.boxSize is None):
        return
      boxSize = self.boxSize
      lims = np.array([[-0.5*x for x in self.boxSize], [0.5*x for x in self.boxSize]])
      # Get the actual number of points according to the maximum set on the UI
      dim = [abs(x-y) for x,y in zip(lims[1], lims[0])]
      size = max(dim)/(self.gridPoints-1)
      if (size == 0.0):
        size = 1.0
      ngrid = [min(int(np.ceil(x/size))+1,self.gridPoints) for x in dim]
      matrix = self.transform[:]
      matrix[3]  += self.orbitals.geomcenter[0]
      matrix[7]  += self.orbitals.geomcenter[1]
      matrix[11] += self.orbitals.geomcenter[2]
      self.transformDock.set_boxes()
    self.gridPointsBox.blockSignals(True)
    self.gridPointsBox.setText('{0}'.format(np.max(ngrid)))
    self.gridPointsBox.blockSignals(False)
    self.update_cache(ngrid)
    grid = vtk.vtkImageData()
    grid.SetOrigin(lims[0,:])
    grid.SetSpacing([b/(n-1) for b,n in zip(boxSize, ngrid)])
    grid.SetDimensions(ngrid)
    transform = vtk.vtkTransform()
    transform.SetMatrix(matrix)
    self.xyz = vtk.vtkTransformFilter()
    self.xyz.SetTransform(transform)
    try:
      self.xyz.SetInputData(grid)
    except AttributeError:
      self.xyz.SetInput(grid)
    self.xyz.Update()
    o = vtk.vtkStructuredGridOutlineFilter()
    o.SetInputConnection(self.xyz.GetOutputPort())
    m = vtk.vtkPolyDataMapper()
    m.SetInputConnection(o.GetOutputPort())
    self.box = vtk.vtkActor()
    self.box.SetMapper(m)
    self.box.GetProperty().SetColor(1, 1, 1)
    self.box.GetProperty().SetOpacity(0.5)
    self.build_axes()
    self.toggle_box()
    self.build_surface()

  def build_axes(self):
    bounds = self.box.GetBounds()
    grid = self.xyz.GetOutput()
    ngrid = grid.GetDimensions()
    o = np.zeros(3)
    ox = np.zeros(3)
    oy = np.zeros(3)
    oz = np.zeros(3)
    grid.GetPoint(0, 0, 0, o)
    grid.GetPoint(ngrid[0]-1, 0, 0, ox)
    grid.GetPoint(0, ngrid[1]-1, 0, oy)
    grid.GetPoint(0, 0, ngrid[2]-1, oz)
    nx = (ox-o)/(ngrid[0]-1)
    ny = (oy-o)/(ngrid[1]-1)
    nz = (oz-o)/(ngrid[2]-1)
    axisX = vtk.vtkAxisActor()
    axisX.SetAxisBaseForX(nx)
    axisX.SetAxisBaseForY(ny)
    axisX.SetAxisBaseForZ(nz)
    axisX.GetAxisMainLineProperty().SetOpacity(0)
    axisX.SetMajorTickSize(0.5)
    axisX.MinorTicksVisibleOff()
    axisX.SetBounds(bounds)
    axisX.SetPoint1(o)
    axisX.SetPoint2(ox)
    axisX.SetAxisTypeToX()
    axisX.GetAxisMajorTicksProperty().SetColor(1, 0.8, 0.8)
    axisX.SetRange(0, ngrid[0]-1)
    axisY = vtk.vtkAxisActor()
    axisY.SetAxisBaseForX(nx)
    axisY.SetAxisBaseForY(ny)
    axisY.SetAxisBaseForZ(nz)
    axisY.GetAxisMainLineProperty().SetOpacity(0)
    axisY.SetMajorTickSize(0.5)
    axisY.MinorTicksVisibleOff()
    axisY.SetBounds(bounds)
    axisY.SetPoint1(o)
    axisY.SetPoint2(oy)
    axisY.SetAxisTypeToY()
    axisY.GetAxisMajorTicksProperty().SetColor(0.8, 1, 0.8)
    axisY.SetRange(0, ngrid[1]-1)
    axisZ = vtk.vtkAxisActor()
    axisZ.SetAxisBaseForX(nx)
    axisZ.SetAxisBaseForY(ny)
    axisZ.SetAxisBaseForZ(nz)
    axisZ.GetAxisMainLineProperty().SetOpacity(0)
    axisZ.SetMajorTickSize(0.5)
    axisZ.MinorTicksVisibleOff()
    axisZ.SetBounds(bounds)
    axisZ.SetPoint1(o)
    axisZ.SetPoint2(oz)
    axisZ.SetAxisTypeToZ()
    axisZ.GetAxisMajorTicksProperty().SetColor(0.8, 0.8, 1)
    axisZ.SetRange(0, ngrid[2]-1)
    self.axes = vtk.vtkAssembly()
    self.axes.AddPart(axisX)
    self.axes.AddPart(axisY)
    self.axes.AddPart(axisZ)

  def update_cache(self, ngrid):
    self.scratchsize['rec'] = None
    if (self.orbitals is None):
      return
    if (self._cache_file is not None):
      del self._cache_file
    if (not self.scratchAction.isChecked()):
      return
    if (self.isGrid):
      self._cache_file = None
    else:
      nbas = sum(self.orbitals.N_bas)
      npoints = np.prod(ngrid)
      size = nbas*npoints
      mintype = 'float32'
      self.scratchsize['rec'] = size*np.dtype(mintype).itemsize
      # Select a type such that everything fits
      for i in ['float64', mintype]:
        if (size*np.dtype(i).itemsize <= self.scratchsize['max']):
          dtype = i
          break
      else:
        # If not possible, find out maximum size
        dtype = mintype
        npoints = self.scratchsize['max']//(nbas*np.dtype(dtype).itemsize)
        self._cache_file = None
        if (npoints < 100):
          return
      self._cache_file = np.memmap(os.path.join(self._tmpdir, '{0}.cache'.format(__name__.lower())), dtype=dtype, mode='w+', shape=(sum(self.orbitals.N_bas), npoints))
      self._cache_file[:,0] = np.nan

  def toggle_cache(self, enabled):
    if (enabled):
      try:
        ngrid = self.xyz.GetInput().GetDimensions()
        self.update_cache(ngrid)
      except:
        raise
    else:
      if (self._cache_file is not None):
        fname = self._cache_file.filename
        del self._cache_file
        self._cache_file = None

  def build_surface(self):
    if (self.xyz is None):
      return
    if (self.isGrid):
      self.setStatus('Reading...')
    else:
      self.setStatus('Computing...')
    self.cancelButton.setEnabled(True)
    self.cancelButton.show()
    if (self._computeVolumeThread is not None):
      self._computeVolumeThread.wait()
    dens_type = []
    dt = self.orbitalButton.currentText()
    if (dt == 'Hole density'):
      dens_type.append('h')
    if (dt == 'Particle density'):
      dens_type.append('p')
    if (dt == 'Attachment density'):
      dens_type.append('a')
    if (dt == 'Detachment density'):
      dens_type.append('d')
    self._computeVolumeThread = ComputeVolume(self, cache=self._cache_file, dens_type=dens_type)
    self._computeVolumeThread.disable_list = [self.scratchAction, self.densityTypeGroup, self.rootGroup, self.irrepGroup, self.orbitalGroup, self.boxSizeGroup, self.gridPointsGroup, self.gradientBox, self.gradientGroup, self.transformDock]
    self._computeVolumeThread.finished.connect(self.volume_computed)
    self._computeVolumeThread.start()

  def volume_computed(self):
    self.cancelButton.setEnabled(False)
    self.cancelButton.hide()
    points = self.xyz.GetInput()
    try:
      vtkmo = numpy_support.numpy_to_vtk(self._computeVolumeThread.data.flatten('F'), 1, vtk.VTK_DOUBLE)
    except AttributeError:
      if (type(self._computeVolumeThread.data) is str):
        self.show_error(self._computeVolumeThread.data)
      vtkmo = numpy_support.numpy_to_vtk(1e-6*(np.random.rand(points.GetNumberOfPoints())-0.5), 1, vtk.VTK_DOUBLE)
    vtkmo.SetName('Values')
    self._computeVolumeThread.quit()
    self._computeVolumeThread.wait()
    points.GetPointData().SetScalars(vtkmo)
    if (self._newgrid):
      self.ready = False
      self._newgrid = False
      transform = self.xyz.GetTransform()
      t = vtk.vtkTransformFilter()
      t.SetTransform(transform)
      try:
        t.SetInputData(points)
      except AttributeError:
        t.SetInput(points)
      # Create the isosurface
      c = vtk.vtkContourFilter()
      c.SetInputConnection(t.GetOutputPort())
      # split positive and negative parts to get good normals
      pos = vtk.vtkClipPolyData()
      pos.SetInputConnection(c.GetOutputPort())
      neg = vtk.vtkClipPolyData()
      neg.InsideOutOn()
      neg.SetInputConnection(c.GetOutputPort())
      rvneg = vtk.vtkReverseSense()
      rvneg.SetInputConnection(neg.GetOutputPort())
      rvneg.ReverseCellsOn()
      rvneg.ReverseNormalsOn()
      tot = vtk.vtkAppendPolyData()
      tot.AddInputConnection(pos.GetOutputPort())
      tot.AddInputConnection(rvneg.GetOutputPort())
      rv = vtk.vtkReverseSense()
      rv.SetInputConnection(tot.GetOutputPort())
      rv.SetReverseCells(transform.GetMatrix().Determinant() < 0)
      m = vtk.vtkPolyDataMapper()
      m.SetInputConnection(rv.GetOutputPort())
      m.UseLookupTableScalarRangeOn()
      m.SetLookupTable(self.lut)
      self.surface = vtk.vtkActor()
      self.surface.SetMapper(m)
      self.surface.GetProperty().SetColor(self.textureDock.zerocolor)
      self.surface.GetProperty().SetOpacity(self.opacity)
      self.surface.GetProperty().SetAmbient(self.textureDock.ambient)
      self.surface.GetProperty().SetDiffuse(self.textureDock.diffuse)
      self.surface.GetProperty().SetSpecular(self.textureDock.specular)
      self.surface.GetProperty().SetSpecularPower(self.textureDock.power)
      self.surface.GetProperty().SetSpecularColor(self.textureDock.specularcolor)
      self.surface.GetProperty().SetInterpolation(self.textureDock.interpolation)
      self.surface.GetProperty().SetRepresentation(self.textureDock.representation)
      self.surface.GetProperty().SetLineWidth(self.textureDock.size)
      self.surface.GetProperty().SetPointSize(self.textureDock.size)
      # Create the nodal surface
      cn = vtk.vtkContourFilter()
      cn.SetInputConnection(t.GetOutputPort())
      cn.SetNumberOfContours(1)
      cn.SetValue(0, 0.0)
      rvn = vtk.vtkReverseSense()
      rvn.SetInputConnection(cn.GetOutputPort())
      rvn.SetReverseCells(transform.GetMatrix().Determinant() < 0)
      mn = vtk.vtkPolyDataMapper()
      mn.SetInputConnection(rvn.GetOutputPort())
      mn.ScalarVisibilityOff()
      self.nodes = vtk.vtkActor()
      self.nodes.SetMapper(mn)
      self.nodes.GetProperty().SetColor(1, 1, 1)
      self.nodes.GetProperty().SetOpacity(0.5)
      # Streamlines
      g = vtk.vtkGradientFilter()
      g.SetInputConnection(self.xyz.GetOutputPort())
      a = vtk.vtkAssignAttribute()
      a.SetInputConnection(g.GetOutputPort())
      a.Assign('Gradients', 'VECTORS', 'POINT_DATA')
      b = vtk.vtkArrayCalculator()
      b.SetInputConnection(a.GetOutputPort())
      b.AddScalarArrayName('Values')
      b.SetFunction('abs(Values)')
      b.SetResultArrayName('Values')
      sl = vtk.vtkStreamTracer()
      sl.SetInputConnection(b.GetOutputPort())
      sl.SetIntegratorTypeToRungeKutta45()
      sl.SetInitialIntegrationStep(0.1)
      sl.SetMinimumIntegrationStep(1e-6) # make it small enough to be able to converge to converge (see below)
      sl.SetTerminalSpeed(1e-8)          # affects tails, but also convergence to stationary points
      sl.SetMaximumNumberOfSteps(100)
      sl.SetMaximumPropagation(100)
      sl.SetIntegrationDirection(self.directionButtonGroup.checkedId())
      sl.SetComputeVorticity(False)
      lut = vtk.vtkLookupTable()
      lut.SetAlphaRange(0.2, 0.8)
      lut.SetHueRange(0.75, 0)
      lut.SetScaleToLog10()
      lut.Build()
      sss = vtk.vtkSphereSource()
      slm = vtk.vtkPolyDataMapper()
      slm.SetInputConnection(sl.GetOutputPort())
      slm.InterpolateScalarsBeforeMappingOn()
      slm.SetLookupTable(lut)
      slm.SetScalarRange(1e-5, 2)
      self.gradient = vtk.vtkActor()
      self.gradient.SetMapper(slm)
      self.gradient.GetProperty().SetOpacity(0.1)
      self.gradient.GetProperty().SetLineWidth(3)
    if (self.orbital == -2):
      # Remove outer points from Laplacian
      e = vtk.vtkExtractVOI()
      try:
        e.SetInputData(points)
      except AttributeError:
        e.SetInput(points)
      subgrid = list(points.GetExtent())
      subgrid[0] += 1
      subgrid[2] += 1
      subgrid[4] += 1
      subgrid[1] -= 1
      subgrid[3] -= 1
      subgrid[5] -= 1
      e.SetVOI(subgrid)
      c = get_input_type(self.surface.GetMapper(), vtk.vtkContourFilter)
      c.SetInputConnection(e.GetOutputPort())
      cn = get_input_type(self.nodes.GetMapper(), vtk.vtkContourFilter)
      cn.SetInputConnection(e.GetOutputPort())
    else:
      c = get_input_type(self.surface.GetMapper(), vtk.vtkContourFilter)
      e = c.GetInputAlgorithm()
      if (isinstance(e, vtk.vtkExtractVOI)):
        try:
          c.SetInputData(e.GetInput())
        except AttributeError:
          c.SetInput(e.GetInput())
        cn = get_input_type(self.nodes.GetMapper(), vtk.vtkContourFilter)
        try:
          cn.SetInputData(e.GetInput())
        except AttributeError:
          cn.SetInput(e.GetInput())
    self.set_gradient_source()
    b = get_input_type(self.gradient.GetMapper(), vtk.vtkArrayCalculator)
    b.Update()
    self.gradient.GetMapper().SetScalarRange(b.GetOutput().GetScalarRange())
    # If interrupted the surface is probably incomplete
    if (self.interrupt):
      self.surface.GetMapper().SetScalarVisibility(False)
      self.surface.GetProperty().SetColor(1.0, 0.8, 1.0)
    else:
      self.surface.GetMapper().SetScalarVisibility(self.orbital != 0)
    self.update_range()
    self.toggle_surface()
    self.toggle_nodes()
    self.toggle_gradient()
    self.ready = True
    enabled = (self.orbital is not None) and (self.orbital > 0)
    self.type_setEnabled(enabled)
    self.set_typeButtonGroup()
    self.set_panel()
    if (self.interrupt):
      self.interrupt.put(False)
      self.setStatus('Interrupted.', force=True)
    else:
      self.setStatus('Ready.', force=True)

  def set_gradient_source(self):
    if (self.gradient is None):
      return
    seeds = vtk.vtkAppendPolyData()
    for i in self.orbitals.centers:
      s = vtk.vtkSphereSource()
      s.SetCenter(i['xyz'])
      s.SetThetaResolution(self.lineDensity)
      s.SetPhiResolution(self.lineDensity)
      s.SetRadius(self.startRadius)
      seeds.AddInputConnection(s.GetOutputPort())
    sl = get_input_type(self.gradient.GetMapper(), vtk.vtkStreamTracer)
    sl.SetSourceConnection(seeds.GetOutputPort())
    sl.SetMaximumNumberOfSteps(self.maxSteps)
    self.vtk_update()

  def update_range(self):
    minval, maxval = self.xyz.GetInput().GetScalarRange()
    if (maxval*minval < 0):
      maxval = max(abs(minval), abs(maxval))
      minval = 0.0
    else:
      minval, maxval = (min(abs(minval), abs(maxval)), max(abs(minval), abs(maxval)))
    if (maxval == 0):
      maxval = 1.0
    if (minval < 100):
      maxval = min(maxval, 100)
    if (maxval == minval):
      maxval *= 1.1
    if (minval == 0):
      minval = np.nanmin(abs(numpy_support.vtk_to_numpy(self.xyz.GetInput().GetPointData().GetScalars())))
      minval = max(minval, 1e-6*maxval)
    self._minval, self._maxval = (minval, maxval)
    self.isovalue = self.isovalue

  def densityTypeButton_changed(self, value):
    if (value >= 0):
      self.dens = self.densityTypeButton.currentText()

  def rootButton_changed(self, value):
    if (value >= 0):
      self.root = self.rootButton.currentIndex()

  def irrepButton_changed(self, value):
    if (value >= 0):
      self.irrep = self.irrepButton.currentText()

  def orbitalButton_changed(self, value):
    if (value < 0):
      return
    try:
      self.orbital = self.orbitalButton.currentData()
    except AttributeError:
      index = self.orbitalButton.currentIndex()
      if (index < 0):
        self.orbital = None
      else:
        try:
          self.orbital, _ = self.orbitalButton.itemData(index).toInt()
        except AttributeError:
          self.orbital = self.orbitalButton.itemData(index)

  def spinButton_changed(self, value):
    if (value >= 0):
      self.spin = self.spinButton.currentText()

  def isovalueSlider_changed(self, value):
    logrange = np.log(self._maxval/self._minval)
    reldist = (value - self.isovalueSlider.minimum())/(self.isovalueSlider.maximum() - self.isovalueSlider.minimum())
    new = self._maxval * np.exp(-reldist*logrange)
    self.isovalueBox.setText('{:.4g}'.format(new))
    self.isovalue = new

  def isovalueBox_changed(self):
    try:
      value = float(self.isovalueBox.text())
      assert 0.0 < value
      self.isovalue = value
    except:
      self.isovalueBox.setText('{:.4g}'.format(self.isovalue))

  def opacitySlider_changed(self, value):
    new = (value - self.opacitySlider.minimum())/(self.opacitySlider.maximum() - self.opacitySlider.minimum())
    self.opacityBox.setText('{:.2f}'.format(new))
    self.opacity = new

  def opacityBox_changed(self):
    try:
      value = float(self.opacityBox.text())
      assert 0.0 <= value <= 1.0
      self.opacity = value
    except:
      self.opacityBox.setText('{:.2f}'.format(self.opacity))

  def show_list(self):
    if (self.listButton.isChecked()):
      self.listDock.show()
    else:
      self.listDock.hide()

  def show_texture(self):
    if (self.textureButton.isChecked()):
      self.textureDock.set_pos()
      self.textureDock.show()
    else:
      self.textureDock.hide()

  def toggle_surface(self):
    if (self.surface is None):
      return
    if (self.surfaceBox.isChecked()):
      self.surface.VisibilityOn()
    else:
      self.surface.VisibilityOff()
    self.vtk_update()

  def sign_changed(self):
    self.isovalue += 0

  def toggle_nodes(self):
    if (self.nodes is None):
      return
    if (self.nodesBox.isChecked()):
      self.nodes.VisibilityOn()
    else:
      self.nodes.VisibilityOff()
    self.vtk_update()

  def molecule_changed(self, new):
    if (self.mol is None):
      return
    self.set_representation(new)
    self.vtk_update()

  def set_representation(self, rep):
    if (rep == 2):
      self.mol.VisibilityOff()
    else:
      self.mol.VisibilityOn()
      mm = self.mol.GetMapper()
      if (rep == 0):
        mm.SetAtomicRadiusTypeToVDWRadius()
        mm.SetRenderBonds(True)
      elif (rep == 1):
        mm.SetAtomicRadiusTypeToCustomArrayRadius()
        mm.SetRenderBonds(False)

  def toggle_names(self):
    if (self.names is None):
      return
    if (self.namesBox.isChecked()):
      self.names.VisibilityOn()
    else:
      self.names.VisibilityOff()
    self.vtk_update()

  def toggle_box(self):
    if (self.box is None):
      return
    if (self.boxBox.isChecked()):
      self.box.VisibilityOn()
      if (self.axes is not None):
        self.axes.VisibilityOn()
    else:
      self.box.VisibilityOff()
      if (self.axes is not None):
        self.axes.VisibilityOff()
    self.vtk_update()

  def toggle_gradient(self):
    if (self.gradient is None):
      return
    if (self.gradientBox.isChecked()):
      self.gradient.VisibilityOn()
    else:
      self.gradient.VisibilityOff()
    self.vtk_update()

  def reset_type(self):
    orb = self.MO[self.orbital-1]
    orb.pop('newtype', None)
    self.set_typeButtonGroup()

  def type_setEnabled(self, enabled):
    self.typeLabel.setEnabled(enabled)
    self.typeGroup.setEnabled(enabled)
    self.resetButton.setEnabled(enabled)

  def typeButtonGroup_changed(self):
    try:
      tp = str(self.typeButtonGroup.checkedButton().text())
    except AttributeError:
      tp = '?'
    tp = tp.replace('&', '')
    if ((self.orbital is None) or (self.MO is None)):
      return
    if (self.orbital > 0):
      orb = self.MO[self.orbital-1]
      item = self.orbitalButton.findData(self.orbital)
      old = orb.get('root_type', orb['type'])
      if (tp == old):
        orb.pop('newtype', None)
      else:
        orb['newtype'] = tp
      self.orbitalButton.setItemText(item, self.orb_to_list(self.orbital, orb))
    self.ren.SetBackground(*background_color[tp])
    self.vtk_update()
    self.set_panel()

  def set_typeButtonGroup(self):
    init = self.typeButtonGroup.checkedId()
    if ((self.orbital is None) or (self.MO is None)):
      tp = '?'
    else:
      if (self.orbital < 1):
        tp = ''
      else:
        orb = self.MO[self.orbital-1]
        try:
          tp = orb.get('newtype', orb.get('root_type', orb['type']))
        except:
          tp = ''
    if (tp == 'F'):
      self.frozenButton.setChecked(True)
    elif (tp == 'I'):
      self.inactiveButton.setChecked(True)
    elif (tp == '1'):
      self.RAS1Button.setChecked(True)
    elif (tp == '2'):
      self.RAS2Button.setChecked(True)
    elif (tp == '3'):
      self.RAS3Button.setChecked(True)
    elif (tp == 'S'):
      self.secondaryButton.setChecked(True)
    elif (tp == 'D'):
      self.deletedButton.setChecked(True)
    else:
      self.typeButtonGroup.setExclusive(False)
      for b in self.typeButtonGroup.buttons():
        b.setChecked(False)
      self.typeButtonGroup.setExclusive(True)
    if (self.typeButtonGroup.checkedId() != init):
      self.typeButtonGroup_changed()

  def set_panel(self):
    # Update the description text
    if (self.orbital > 0):
      tp = self.MO[self.orbital-1]['type']
    elif (self.orbital < 1):
      tp = '2'
    else:
      tp = '?'
    text = ''
    try:
      modified = not np.allclose(self.MO[self.orbital-1]['coeff'], self.MO[self.orbital-1].get('root_coeff', self.MO[self.orbital-1]['coeff']))
    except KeyError:
      modified = False
    if (self.rootGroup.isEnabled()):
      if ((not modified) and (self.orbital > 0)):
        if (self.orbitals.wf == 'PT2'):
          text = 'Reference\n'
        else:
          text = 'State average\n'
      elif (self.dens in ['State', 'Spin']):
        if (self.orbitals.wf == 'PT2'):
          if (self.root == 0):
            text = 'Reference\n'
          else:
            text = 'State {0}\n'.format(self.rootButton.currentText().split(':')[0])
        else:
          if (self.root == 0):
            text = 'State average\n'
          else:
            text = 'Root {0}\n'.format(self.rootButton.currentText().split(':')[0])
      elif (self.dens == 'Difference'):
        text = 'Difference from root {0} to {1}\n'.format(*self.rootButton.currentText().split(u' → '))
      elif (self.dens == 'Transition'):
        text = 'Transition ({0}) from root {1} to {2}\n'.format(self.spin, *self.rootButton.currentText().split(u' → '))
    try:
      sd = ''
      if (self.dens == 'Spin'):
        sd = 'Spin density'
      elif (self.dens == 'Difference'):
        sd = 'Difference density'
      elif (self.dens == 'Transition'):
        if (self.spin == 'hole'):
          sd = 'Hole density'
        if (self.spin == 'particle'):
          sd = 'Particle density'
      text += {0:'Density', -1:'Spin density', -2:'Laplacian (numerical)', -3:sd, -4:'Attachment density', -5:'Detachment density'}[self.orbital]
    except KeyError:
      orb = self.MO[self.orbital-1]
      tp = orb.get('newtype', orb.get('root_type', orb['type']))
      if ('label' in orb):
        text += orb['label']
      else:
        if (self.nosym):
          sym = ''
        else:
          m = [o['sym'] for o in self.MO[:self.orbital]].count(orb['sym'])
          sym = ' [{0}, {1}]'.format(orb['sym'], m)
        text += '#{0}{1}   E: {2:.6f}   occ: {3:.4f}   {4}'.format(self.orbital, sym, orb.get('root_ene', orb['ene']), orb.get('root_occup', orb['occup']), tp)
    # Update the counts
    irrep = [i for i in self.orbitals.irrep if (i != 'z')]
    nsym = len(irrep)
    types = {k:[0]*nsym for k in ['F', 'I', '1', '2', '3', 'S', 'D']}
    for o in self.MO:
      try:
        sym = irrep.index(o['sym'])
        tp = o.get('newtype', o['type'])
        if (tp in types):
          types[tp][sym] += 1
      except:
        pass
    text += '\n' + '   '.join(['{0}: {1}'.format(i, ','.join(map(str, types[i]))) for i in ['F', 'I', '1', '2', '3', 'S', 'D'] if (sum(types[i]) > 0)])
    if (self.panel is None):
      self.panel = vtk.vtkTextActor()
      if (self.monoFont is not None):
        self.panel.GetTextProperty().SetFontFamily(vtk.VTK_FONT_FILE)
        self.panel.GetTextProperty().SetFontFile('/usr/share/fonts/truetype/droid/DroidSansMono.ttf')
      self.panel.GetTextProperty().SetFontSize(12)
      self.panel.GetTextProperty().SetLineSpacing(1.2)
      self.panel.GetTextProperty().SetBackgroundOpacity(0.1)
      self.panel.SetPosition(5, 5)
      self.panel.SetWidth(300)
      self.panel.SetHeight(300)
    self.panel.SetInput(text)
    self.vtk_update()

  def boxSizeBox_changed(self):
    try:
      value = [float(i) for i in re.split(r'[ ,]*', str(self.boxSizeBox.text()).strip())]
      assert (len(value) == 3) and all([i > 0 for i in value])
      self.boxSize = value
      self.boxSizeBox.blockSignals(True)
      self.boxSizeBox.setText('{0}, {1}, {2}'.format(*self.boxSize))
      self.boxSizeBox.blockSignals(False)
    except Exception as e:
      self.boxSizeBox.blockSignals(True)
      if (self.boxSize is None):
        self.boxSizeBox.setText('')
      else:
        self.boxSizeBox.setText('{0}, {1}, {2}'.format(*self.boxSize))
      self.boxSizeBox.blockSignals(False)

  def edit_transform(self):
    if (self.transformButton.isChecked()):
      self.transformDock.set_pos()
      self.transformDock.show()
    else:
      self.transformDock.hide()

  def gridPointsBox_changed(self):
    try:
      value = int(self.gridPointsBox.text())
      assert 2 <= value <= 200
      self.gridPoints = value
    except:
      self.gridPointsBox.blockSignals(True)
      if (self.gridPoints is None):
        self.gridPointsBox.setText('')
      else:
        self.gridPointsBox.setText('{0}'.format(self.gridPoints))
      self.gridPointsBox.blockSignals(False)

  def toggle_gradient_options(self):
    if (self.gradientGroup.isVisible()):
       self.gradientGroup.hide()
       self.showGradientButton.setArrowType(Qt.RightArrow)
    else:
       self.gradientGroup.show()
       self.showGradientButton.setArrowType(Qt.LeftArrow)

  def lineDensityBox_changed(self):
    try:
      value = int(self.lineDensityBox.text())
      assert 2 <= value <= 50
      self.lineDensity = value
    except:
      self.lineDensityBox.blockSignals(True)
      if (self.lineDensity is None):
        self.lineDensityBox.setText('')
      else:
        self.lineDensityBox.setText('{0}'.format(self.lineDensity))
      self.lineDensityBox.blockSignals(False)

  def startRadiusBox_changed(self):
    try:
      value = float(self.startRadiusBox.text())
      assert 0 <= value
      self.startRadius = value
    except:
      self.startRadiusBox.blockSignals(True)
      if (self.startRadius is None):
        self.startRadiusBox.setText('')
      else:
        self.startRadiusBox.setText('{0}'.format(self.startRadius))
      self.startRadiusBox.blockSignals(False)

  def maxStepsBox_changed(self):
    try:
      value = int(self.maxStepsBox.text())
      assert 0 <= value
      self.maxSteps = value
    except:
      self.maxStepsBox.blockSignals(True)
      if (self.maxSteps is None):
        self.maxStepsBox.setText('')
      else:
        self.maxStepsBox.setText('{0}'.format(self.maxSteps))
      self.maxStepsBox.blockSignals(False)

  def directionButtonGroup_changed(self):
    sl = get_input_type(self.gradient.GetMapper(), vtk.vtkStreamTracer)
    sl.SetIntegrationDirection(self.directionButtonGroup.checkedId())
    self.vtk_update()

  def cancel(self):
    if (self._computeVolumeThread.isRunning()):
      self.interrupt.put(True)

  def write_hdf5(self, *args):
    if (self.orbitals.type != 'hdf5'):
      return
    result = QFileDialog.getSaveFileName(self, 'Save HDF5')
    if (not result):
      return
    try:
      filename, _ = result
    except ValueError:
      filename = result
    notes = [n['note'] for n in self.notes]
    if (any(notes)):
      self.orbitals.notes = notes
    else:
      self.orbitals.notes = None
    try:
      self.orbitals.write_hdf5(str(filename))
    except Exception as e:
      error = 'Error writing hdf5 file {0}:\n{1}'.format(filename, e)
      traceback.print_exc()
      self.show_error(error)

  def write_inporb(self, *args):
    if (not self.haveInpOrb):
      return
    result = QFileDialog.getSaveFileName(self, 'Save InpOrb')
    if (not result):
      return
    try:
      filename, _ = result
    except ValueError:
      filename = result
    try:
      if (self.orbitals.inporb == 'gen'):
        self.orbitals.create_inporb(filename, self.MO)
      else:
        self.patch_inporb(filename)
    except Exception as e:
      error = 'Error writing inporb file {0}:\n{1}'.format(filename, e)
      traceback.print_exc()
      self.show_error(error)

  def write_cube(self, *args):
    if (self.surface is None):
      return
    result = QFileDialog.getSaveFileName(self, 'Save cube')
    if (not result):
      return
    try:
      filename, _ = result
    except ValueError:
      filename = result
    try:
      data = self.xyz.GetInput()
      ngrid = data.GetDimensions()
      grid = data.GetSpacing()
      orig = list(data.GetOrigin())
      transform = self.xyz.GetTransform().GetMatrix()
      try:
        note = ' {0}'.format(self.notes[self.orbital-1]['note'])
      except:
        note = ''
      with open(filename, 'w') as f:
        f.write('File generated by {0} from {1}\n'.format(__name__, self.filename))
        f.write('{0} {1}\n'.format(self.orbitalButton.currentText(), note))
        orig.append(1.0)
        transform.MultiplyPoint(orig, orig)
        f.write('{0:5d} {1:11.6f} {2:11.6f} {3:11.6f}\n'.format(len(self.orbitals.centers), *orig))
        for i in range(3):
          axis = [0, 0, 0, 0]
          axis[i] = grid[i]
          axis = transform.MultiplyPoint(axis)
          f.write('{0:5d} {1:11.6f} {2:11.6f} {3:11.6f}\n'.format(ngrid[i], *axis))
        for c in self.orbitals.centers:
          f.write('{0:5d} {0:11.6f} {1:11.6f} {2:11.6f} {3:11.6f}\n'.format(c['Z'], *c['xyz']))
        vol = numpy_support.vtk_to_numpy(data.GetPointData().GetScalars()).reshape(ngrid[::-1]).T
        for x in vol:
          for y in x:
            f.write('\n'.join(wrap_list(y, 6, '{:13.5E}')))
            f.write('\n')
    except Exception as e:
      error = 'Error writing cube file {0}:\n{1}'.format(filename, e)
      traceback.print_exc()
      self.show_error(error)

  # Copy an InpOrb file, changing header and index section
  def patch_inporb(self, outfile):
    with open(self.orbitals.file, 'r') as f:
      f.seek(self.orbitals.inporb)
      with open(outfile, 'w') as fo:
        line = f.readline()
        while (line != ''):
          fo.write(line)
          line = f.readline()
          # In the header, modify only the title, but read numbers of orbitals
          if (line.startswith('#INFO')):
            fo.write(line)
            line = f.readline()
            fo.write('* File generated by {0} from {1}\n'.format(__name__, self.filename))
            line = f.readline()
            fo.write(line)
            line = f.readline()
            fo.write(line)
            line = f.readline()
            fo.write(line)
            line = f.readline()
            fo.write(line)
            line = f.readline()
          # Read the existing index section
          if (line.startswith('#INDEX')):
            fo.write(line)
            index = []
            line = f.readline().split()
            while (line[0][0] not in ['#', '<']):
              if (line[0] == '*'):
                index.append('')
              else:
                index[-1] += line[1]
              line = f.readline().split()
            nMO = OrderedDict()
            for i,l in enumerate(index):
              nMO['{0}'.format(i+1)] = len(l)
            break
        if (self.orbitals.MO_b):
          alphaMO = self.orbitals.MO_a
        else:
          alphaMO = self.orbitals.MO
        index, error = create_index(alphaMO, self.orbitals.MO_b, nMO, old=index)
        if (index is None):
          if (error is not None):
            self.show_error(error)
            return
        # Write the new index section
        fo.write('\n'.join(index))
        fo.write('\n')

  def prev_dens(self):
    if (not self.densityTypeButton.isEnabled()):
      return
    self.densityTypeButton.setEnabled(False)
    index = self.densityTypeButton.currentIndex()
    if (index > 0):
      self.densityTypeButton.setCurrentIndex(index-1)
    self.densityTypeButton.setEnabled(True)

  def next_dens(self):
    if (not self.densityTypeButton.isEnabled()):
      return
    self.densityTypeButton.setEnabled(False)
    index = self.densityTypeButton.currentIndex()
    if (index < self.densityTypeButton.count()-1):
      self.densityTypeButton.setCurrentIndex(index+1)
    self.densityTypeButton.setEnabled(True)

  def prev_root(self):
    if (not self.rootButton.isEnabled()):
      return
    self.rootButton.setEnabled(False)
    index = self.rootButton.currentIndex()
    if (index > 0):
      self.rootButton.setCurrentIndex(index-1)
    self.rootButton.setEnabled(True)

  def next_root(self):
    if (not self.rootButton.isEnabled()):
      return
    self.rootButton.setEnabled(False)
    index = self.rootButton.currentIndex()
    if (index < self.rootButton.count()-1):
      self.rootButton.setCurrentIndex(index+1)
    self.rootButton.setEnabled(True)

  def prev_irrep(self):
    if (not self.irrepButton.isEnabled()):
      return
    self.irrepButton.setEnabled(False)
    index = self.irrepButton.currentIndex()
    if (index > 0):
      self.irrepButton.setCurrentIndex(index-1)
    self.irrepButton.setEnabled(True)

  def next_irrep(self):
    if (not self.irrepButton.isEnabled()):
      return
    self.irrepButton.setEnabled(False)
    index = self.irrepButton.currentIndex()
    if (index < self.irrepButton.count()-1):
      self.irrepButton.setCurrentIndex(index+1)
    self.irrepButton.setEnabled(True)

  def prev_orbital(self):
    if (not self.orbitalButton.isEnabled()):
      return
    self.orbitalButton.setEnabled(False)
    index = self.orbitalButton.currentIndex()
    if (index > 0):
      self.orbitalButton.setCurrentIndex(index-1)
    self.orbitalButton.setEnabled(True)

  def next_orbital(self):
    if (not self.orbitalButton.isEnabled()):
      return
    self.orbitalButton.setEnabled(False)
    index = self.orbitalButton.currentIndex()
    if (index < self.orbitalButton.count()-1):
      self.orbitalButton.setCurrentIndex(index+1)
    self.orbitalButton.setEnabled(True)

  def select_alpha(self):
    if (not self.spinButton.isEnabled()):
      return
    index = self.spinButton.findText('alpha')
    if (index < 0):
      index = self.spinButton.findText('hole')
    if (index >= 0):
      self.spinButton.setCurrentIndex(index)

  def select_beta(self):
    if (not self.spinButton.isEnabled()):
      return
    index = self.spinButton.findText('beta')
    if (index < 0):
      index = self.spinButton.findText('particle')
    if (index >= 0):
      self.spinButton.setCurrentIndex(index)

  def increase_isovalue(self, more=False):
    if (not self.isovalueSlider.isEnabled()):
      return
    value = self.isovalueSlider.value()
    if (more):
      step = self.isovalueSlider.pageStep()
    else:
      step = self.isovalueSlider.singleStep()
    self.isovalueSlider.setValue(value-step)

  def decrease_isovalue(self, more=False):
    if (not self.isovalueSlider.isEnabled()):
      return
    value = self.isovalueSlider.value()
    if (more):
      step = self.isovalueSlider.pageStep()
    else:
      step = self.isovalueSlider.singleStep()
    self.isovalueSlider.setValue(value+step)

  def increase_opacity(self, more=False):
    if (not self.opacitySlider.isEnabled()):
      return
    value = self.opacitySlider.value()
    if (more):
      step = self.opacitySlider.pageStep()
    else:
      step = self.opacitySlider.singleStep()
    self.opacitySlider.setValue(value+step)

  def decrease_opacity(self, more=False):
    if (not self.opacitySlider.isEnabled()):
      return
    value = self.opacitySlider.value()
    if (more):
      step = self.opacitySlider.pageStep()
    else:
      step = self.opacitySlider.singleStep()
    self.opacitySlider.setValue(value-step)

  def prev_sign(self):
    if (not self.signButton.isEnabled()):
      return
    index = self.signButton.currentIndex()
    index = (index-1) % self.signButton.count()
    self.signButton.setCurrentIndex(index)

  def next_sign(self):
    if (not self.signButton.isEnabled()):
      return
    index = self.signButton.currentIndex()
    index = (index+1) % self.signButton.count()
    self.signButton.setCurrentIndex(index)

  def prev_molecule(self):
    if (not self.moleculeButton.isEnabled()):
      return
    index = self.moleculeButton.currentIndex()
    index = (index-1) % self.moleculeButton.count()
    self.moleculeButton.setCurrentIndex(index)

  def next_molecule(self):
    if (not self.moleculeButton.isEnabled()):
      return
    index = self.moleculeButton.currentIndex()
    index = (index+1) % self.moleculeButton.count()
    self.moleculeButton.setCurrentIndex(index)

  def show_keys(self):
    if (self.keymess is None):
      self.keymess = ScrollMessageBox(self)
    self.keymess.show()
    self.keymess.activateWindow()

  def show_about(self):
    python_version = sys.version
    vtk_version = vtk.vtkVersion.GetVTKVersion()
    if (self._cache_file is None):
      s_act = 0
    else:
      s_act = self._cache_file.nbytes / 2**20
    s_max = 0
    if (self.scratchsize['max'] is not None):
      s_max = self.scratchsize['max'] / 2**20
    s_rec = 0
    if (self.scratchsize['rec'] is not None):
      s_rec = np.ceil(self.scratchsize['rec'] / 2**20)
    scratchstring = 'max: {0:.2f}, used: {1:.2f}, rec: {2:.0f}, in MiB'.format(s_max, s_act, s_rec)
    QMessageBox.about(self, 'About {0}'.format(__name__),
                      u'''<h2>{0} v{1}</h2>
                      <p>An orbital viewer ideal for OpenMolcas.<br>
                      {2}, {3}</p>
                      <p>{0} can open files in <i>HDF5</i>, <i>Molden</i>, <i>Luscus</i>, <i>grid</i> (ascii) and <i>cube</i> (formatted) formats;
                      after loading an HDF5 file, it can also read files in <i>InpOrb</i> format.<br>
                      It can modify orbital types and save the result in <i>HDF5</i> and <i>InpOrb</i> formats, or save the volume data in <i>cube</i> format.</p>
                      <p><b>python</b>: {4}<br>
                      <b>Qt API</b>: {5}<br>
                      <b>VTK</b>: {6}</p>
                      <p>Scratch space: {7}<br>({8})</p>
                      '''.format(__name__, __version__, __copyright__, __author__, python_version, QtVersion, vtk_version, self._tmpdir, scratchstring)
                      )

  def show_screenshot(self):
    if (self.screenshot is None):
      self.screenshot = TakeScreenshot(self)
    self.screenshot.show()
    self.screenshot.activateWindow()

  def show_error(self, error):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(error)
    msg.setWindowTitle('Error')
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()
    del msg

  def set_scale(self):
    camera = self.ren.GetActiveCamera()
    if (camera.GetParallelProjection()):
      self._prevscale = camera.GetParallelScale()
    else:
      self._prevscale = camera.GetDistance()

  def orthographic(self):
    camera = self.ren.GetActiveCamera()
    # Set the orthographic or perspective projection, trying to keep the same scale factor
    if (self.orthographicAction.isChecked()):
      # Zooming in perspective projection changes distance
      scale = camera.GetDistance()/self._prevscale * camera.GetParallelScale()
      camera.SetParallelScale(scale)
      camera.ParallelProjectionOn()
    else:
      # Zooming in orthographic projection changes parallel scale
      factor = self._prevscale/camera.GetParallelScale()
      camera.Dolly(factor)
      camera.ParallelProjectionOff()
    self.set_scale()
    self.vtk_update()

  def reset_camera(self, restore=False):
    if (restore):
      self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
      self.ren.GetActiveCamera().SetPosition(0, 0, 10)
      self.ren.GetActiveCamera().SetViewUp(0, 1, 0)
    self.ren.ResetCamera()
    self.set_scale()
    self.vtk_update()

  def vtk_update(self):
    if (self.ready):
      self.ren.ResetCameraClippingRange()
      self.vtkWidget.GetRenderWindow().Render()

class ListDock(QDockWidget):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.init_UI()

  def init_UI(self):
    self.setWindowTitle('List')
    self.ready = True
    self.modified = False
    self.orbLabels = []
    self.orbCheckBoxes = []
    self.orbNotes = []
    self.allButton = QPushButton('All')
    self.activeButton = QPushButton('Active')
    self.noneButton = QPushButton('None')

    self.allButton.setToolTip('Include all occupied orbitals in the densities')
    self.allButton.setWhatsThis('Select all occupied orbitals when computing the electron and spin density.')
    self.activeButton.setToolTip('Include only active orbitals in the densities')
    self.activeButton.setWhatsThis('Select only occupied active orbitals when computing the electron and spin density.')
    self.noneButton.setToolTip('Exclude all orbitals from the densities')
    self.noneButton.setWhatsThis('Deselect all orbitals for computing the electron and spin density.')

    self.grid = QGridLayout()
    head1 = QLabel('Orbital')
    head1.setAlignment(Qt.AlignCenter)
    head2 = QLabel('Density')
    head2.setAlignment(Qt.AlignCenter)
    head3 = QLabel('Notes')
    head3.setAlignment(Qt.AlignCenter)
    self.grid.addWidget(head1, 0, 0)
    self.grid.addWidget(head2, 0, 1)
    self.grid.addWidget(head3, 0, 2)
    self.spacer = QWidget()
    self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.grid.setColumnStretch(2, 1)
    _list = QWidget()
    _list.setLayout(self.grid)
    scroll = QScrollArea()
    scroll.setWidget(_list)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    hbox = QHBoxLayout()
    hbox.addWidget(self.allButton)
    hbox.addWidget(self.activeButton)
    hbox.addWidget(self.noneButton)
    hbox.addSpacing(20)
    hbox.addStretch(1)

    vbox = QVBoxLayout()
    vbox.setAlignment(Qt.AlignTop)
    vbox.addWidget(scroll)
    vbox.addLayout(hbox)

    _widget = QWidget()
    _widget.setLayout(vbox)

    self.setWidget(_widget)

    self.setMinimumWidth(300)

    self.allButton.clicked.connect(self.select_all)
    self.activeButton.clicked.connect(self.select_active)
    self.noneButton.clicked.connect(self.select_none)

  def set_list(self):
    for i in self.orbLabels + self.orbCheckBoxes + self.orbNotes:
      i.hide()
      del i
    self.grid.removeWidget(self.spacer)
    self.orbLabels = []
    self.orbCheckBoxes = []
    self.orbNotes = []
    if (self.parent().notes is not None):
      for i,orb in enumerate(self.parent().notes):
        l = QLabel(orb['name'])
        self.orbLabels.append(l)
        c = QCheckBox()
        c.setChecked(orb['density'])
        c.stateChanged.connect(partial(self.density, i))
        c.setToolTip('Include the orbital in density calculations?')
        c.setWhatsThis('If checked, this orbital is included when computing the electron and spin density.')
        if (self.parent().isGrid):
          c.setEnabled(False)
        self.orbCheckBoxes.append(c)
        e = QLineEdit()
        e.setText(orb['note'])
        e.editingFinished.connect(partial(self.note, i))
        e.setToolTip('Add free custom note to the orbital')
        e.setWhatsThis('You can write any text as an annotation for the orbital, but this will not be saved.')
        self.orbNotes.append(e)
    for i,(l,c,n) in enumerate(zip(self.orbLabels, self.orbCheckBoxes, self.orbNotes)):
      self.grid.addWidget(l, i+1, 0)
      self.grid.addWidget(c, i+1, 1, Qt.AlignCenter)
      self.grid.addWidget(n, i+1, 2)
    self.grid.addWidget(self.spacer, len(self.orbLabels)+1, 0)

  def density(self, num, new):
    self.parent().notes[num]['density'] = bool(new)
    self.modified = True
    if (self.ready):
      self.redraw()

  def note(self, num):
    self.parent().notes[num]['note'] = str(self.orbNotes[num].text())

  def select_all(self):
    self.modified = False
    self.ready = False
    for i in self.orbCheckBoxes:
      if (i.isEnabled()):
        i.setChecked(True)
    self.ready = True
    if (self.modified):
      self.redraw()

  def select_active(self):
    self.modified = False
    self.ready = False
    if (self.parent().orbitals.MO_b):
      alphaMO = self.parent().orbitals.MO_a
    else:
      alphaMO = self.parent().orbitals.MO
    for i,o in zip(self.orbCheckBoxes, [j for i in zip_longest(alphaMO, self.parent().orbitals.MO_b) for j in i if (j is not None)]):
      if (i.isEnabled()):
        tp = o['type']
        if ('newtype' in o):
          tp = o['newtype']
        if (tp in ['1', '2', '3']):
          i.setChecked(True)
        else:
          i.setChecked(False)
    self.ready = True
    if (self.modified):
      self.redraw()

  def select_none(self):
    self.modified = False
    self.ready = False
    for i in self.orbCheckBoxes:
      if (i.isEnabled()):
        i.setChecked(False)
    self.ready = True
    if (self.modified):
      self.redraw()

  def redraw(self):
    if (self.parent().orbital < 1):
      self.parent().build_surface()
    self.modified = False

  def closeEvent(self, *args):
    self.parent().listButton.setChecked(False)
    super().closeEvent(*args)

class TransformDock(QDockWidget):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.init_UI()
    self.pos = False

  def init_UI(self):
    self.setWindowTitle('Transformation')
    self.rotLabel = QLabel('Transformation matrix:')
    self.rotXXBox = QLineEdit()
    self.rotXYBox = QLineEdit()
    self.rotXZBox = QLineEdit()
    self.rotYXBox = QLineEdit()
    self.rotYYBox = QLineEdit()
    self.rotYZBox = QLineEdit()
    self.rotZXBox = QLineEdit()
    self.rotZYBox = QLineEdit()
    self.rotZZBox = QLineEdit()
    self.transLabel = QLabel('Translation:')
    self.transXBox = QLineEdit()
    self.transYBox = QLineEdit()
    self.transZBox = QLineEdit()
    self.applyButton = QPushButton('Apply')
    self.resetButton = QPushButton('Reset')
    self.cancelButton = QPushButton('Cancel')

    rotText = u'These elements define the 3×3 transformation matrix applied to the grid box.'
    self.rotXXBox.setToolTip('Element 1,1 of the rotation matrix')
    self.rotXXBox.setWhatsThis(rotText)
    self.rotXYBox.setToolTip('Element 1,2 of the rotation matrix')
    self.rotXYBox.setWhatsThis(rotText)
    self.rotXZBox.setToolTip('Element 1,3 of the rotation matrix')
    self.rotXZBox.setWhatsThis(rotText)
    self.rotYXBox.setToolTip('Element 2,1 of the rotation matrix')
    self.rotYXBox.setWhatsThis(rotText)
    self.rotYYBox.setToolTip('Element 2,2 of the rotation matrix')
    self.rotYYBox.setWhatsThis(rotText)
    self.rotYZBox.setToolTip('Element 2,3 of the rotation matrix')
    self.rotYZBox.setWhatsThis(rotText)
    self.rotZXBox.setToolTip('Element 3,1 of the rotation matrix')
    self.rotZXBox.setWhatsThis(rotText)
    self.rotZYBox.setToolTip('Element 3,2 of the rotation matrix')
    self.rotZYBox.setWhatsThis(rotText)
    self.rotZZBox.setToolTip('Element 3,3 of the rotation matrix')
    self.rotZZBox.setWhatsThis(rotText)
    transText = 'These elements define the translation vector applied to the grid box.'
    self.transXBox.setToolTip('Element 1 of the translation vector')
    self.transXBox.setWhatsThis(transText)
    self.transYBox.setToolTip('Element 2 of translation vectortrix')
    self.transYBox.setWhatsThis(transText)
    self.transZBox.setToolTip('Element 3 of translation vectortrix')
    self.transZBox.setWhatsThis(transText)
    self.applyButton.setToolTip('Apply transformation matrix to the box')
    self.applyButton.setWhatsThis('By clicking this button the transformation defined here is applied to the grid box and the display is updated.')
    self.resetButton.setToolTip('Reset to unit matrix')
    self.resetButton.setWhatsThis('Reset the transformation to the identity (do nothing).')
    self.cancelButton.setToolTip('Reset transformation matrix to the current one')
    self.cancelButton.setWhatsThis('Restore the transformation as it was the last time the Apply button was used.')

    grid = QGridLayout()
    grid.addWidget(self.rotLabel, 0, 0, 1, 3)
    grid.addWidget(self.rotXXBox, 1, 0)
    grid.addWidget(self.rotXYBox, 1, 1)
    grid.addWidget(self.rotXZBox, 1, 2)
    grid.addWidget(self.rotYXBox, 2, 0)
    grid.addWidget(self.rotYYBox, 2, 1)
    grid.addWidget(self.rotYZBox, 2, 2)
    grid.addWidget(self.rotZXBox, 3, 0)
    grid.addWidget(self.rotZYBox, 3, 1)
    grid.addWidget(self.rotZZBox, 3, 2)
    grid.addWidget(self.transLabel, 4, 0, 1, 3)
    grid.addWidget(self.transXBox, 5, 0)
    grid.addWidget(self.transYBox, 5, 1)
    grid.addWidget(self.transZBox, 5, 2)

    hbox = QHBoxLayout()
    hbox.addWidget(self.applyButton)
    hbox.addStretch(1)
    hbox.addWidget(self.resetButton)
    hbox.addWidget(self.cancelButton)

    vbox = QVBoxLayout()
    vbox.setAlignment(Qt.AlignTop)
    vbox.addLayout(grid)
    vbox.addLayout(hbox)

    _widget = QWidget()
    _widget.setLayout(vbox)

    self.setWidget(_widget)

    self.rotXXBox.returnPressed.connect(self.set_transform)
    self.rotXYBox.returnPressed.connect(self.set_transform)
    self.rotXZBox.returnPressed.connect(self.set_transform)
    self.rotYXBox.returnPressed.connect(self.set_transform)
    self.rotYYBox.returnPressed.connect(self.set_transform)
    self.rotYZBox.returnPressed.connect(self.set_transform)
    self.rotZXBox.returnPressed.connect(self.set_transform)
    self.rotZYBox.returnPressed.connect(self.set_transform)
    self.rotZZBox.returnPressed.connect(self.set_transform)
    self.transXBox.returnPressed.connect(self.set_transform)
    self.transYBox.returnPressed.connect(self.set_transform)
    self.transZBox.returnPressed.connect(self.set_transform)
    self.applyButton.clicked.connect(self.set_transform)
    self.resetButton.clicked.connect(self.reset)
    self.cancelButton.clicked.connect(self.set_boxes)

  def set_pos(self):
    if (not self.pos):
      self.move(self.parent().frameGeometry().topLeft() + self.parent().rect().center() - self.rect().center())
      self.pos = True

  def set_boxes(self, value=None):
    if ((value is None) or (type(value) is bool)):
      value = self.parent().transform
    self.rotXXBox.setText('{}'.format(value[0]))
    self.rotXYBox.setText('{}'.format(value[1]))
    self.rotXZBox.setText('{}'.format(value[2]))
    self.rotYXBox.setText('{}'.format(value[4]))
    self.rotYYBox.setText('{}'.format(value[5]))
    self.rotYZBox.setText('{}'.format(value[6]))
    self.rotZXBox.setText('{}'.format(value[8]))
    self.rotZYBox.setText('{}'.format(value[9]))
    self.rotZZBox.setText('{}'.format(value[10]))
    self.transXBox.setText('{}'.format(value[3]))
    self.transYBox.setText('{}'.format(value[7]))
    self.transZBox.setText('{}'.format(value[11]))

  def set_transform(self):
    value = [0]*16
    try:
      value[0]  = self.rotXXBox.text()
      value[1]  = self.rotXYBox.text()
      value[2]  = self.rotXZBox.text()
      value[4]  = self.rotYXBox.text()
      value[5]  = self.rotYYBox.text()
      value[6]  = self.rotYZBox.text()
      value[8]  = self.rotZXBox.text()
      value[9]  = self.rotZYBox.text()
      value[10] = self.rotZZBox.text()
      value[3]  = self.transXBox.text()
      value[7]  = self.transYBox.text()
      value[11] = self.transZBox.text()
      value[15] = 1.0
      self.parent().transform = [float(i) for i in value]
    except:
      self.set_boxes()

  def reset(self):
    value = np.eye(4).flatten().tolist()
    value[15] = 1.0
    self.set_boxes(value)

  def set_enabled(self, value):
    self.rotLabel.setEnabled(value)
    self.rotXXBox.setEnabled(value)
    self.rotXYBox.setEnabled(value)
    self.rotXZBox.setEnabled(value)
    self.rotYXBox.setEnabled(value)
    self.rotYYBox.setEnabled(value)
    self.rotYZBox.setEnabled(value)
    self.rotZXBox.setEnabled(value)
    self.rotZYBox.setEnabled(value)
    self.rotZZBox.setEnabled(value)
    self.transLabel.setEnabled(value)
    self.transXBox.setEnabled(value)
    self.transYBox.setEnabled(value)
    self.transZBox.setEnabled(value)
    self.applyButton.setEnabled(value)
    self.resetButton.setEnabled(value)
    self.cancelButton.setEnabled(value)

  def closeEvent(self, *args):
    self.parent().transformButton.setChecked(False)
    super().closeEvent(*args)

class TextureDock(QDockWidget):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._ambient = None
    self._diffuse = None
    self._specular = None
    self._power = None
    self._interpolation = None
    self._representation = None
    self._size = None
    self._negcolor = None
    self._zerocolor = None
    self._poscolor = None
    self._specularcolor = None
    self.init_UI()
    self.pos = False

  def init_UI(self):
    self.setWindowTitle('Texture')
    self.ambientLabel = QLabel('Ambient:')
    self.ambientSlider = QSlider(Qt.Horizontal)
    self.ambientBox = QLineEdit()
    self.ambientBox.setFixedWidth(60)
    self.ambientLabel.setBuddy(self.ambientBox)
    self.diffuseLabel = QLabel('Diffuse:')
    self.diffuseSlider = QSlider(Qt.Horizontal)
    self.diffuseBox = QLineEdit()
    self.diffuseBox.setFixedWidth(60)
    self.diffuseLabel.setBuddy(self.diffuseBox)
    self.specularLabel = QLabel('Specular:')
    self.specularSlider = QSlider(Qt.Horizontal)
    self.specularBox = QLineEdit()
    self.specularBox.setFixedWidth(60)
    self.specularLabel.setBuddy(self.specularBox)
    self.powerLabel = QLabel('Power:')
    self.powerSlider = QSlider(Qt.Horizontal)
    self.powerBox = QLineEdit()
    self.powerBox.setFixedWidth(60)
    self.powerLabel.setBuddy(self.powerBox)
    self.presetsLabel = QLabel('Presets:')
    self.matteButton = QPushButton('Matte')
    self.metalButton = QPushButton('Metal')
    self.plasticButton = QPushButton('Plastic')
    self.cartoonButton = QPushButton('Cartoon')
    self.interpolationLabel = QLabel('Interpolation:')
    self.interpolationButton = QComboBox()
    self.interpolationButton.addItems([u'Flat', u'Gouraud', u'Phong'])
    self.representationLabel = QLabel('Representation:')
    self.representationButton = QComboBox()
    self.representationButton.addItems([u'Points', u'Wireframe', u'Surface'])
    self.sizeLabel = QLabel('Point/line size:')
    self.sizeBox = QSpinBox()
    self.sizeBox.setMinimum(0)
    self.colorsLabel = QLabel('Colors:')
    self.negColorButton = QToolButton()
    self.negColorButton.setText(u'⊖')
    self.zeroColorButton = QToolButton()
    self.zeroColorButton.setText(u'⊗')
    self.posColorButton = QToolButton()
    self.posColorButton.setText(u'⊕')
    self.specColorButton = QToolButton()
    self.specColorButton.setText(u'⊙')
    self.presets2Label = QLabel('Presets:')
    self.GBSButton = QPushButton('GBS')
    self.BWButton = QPushButton('B&&W')
    self.RGBButton = QPushButton('RGB')
    self.CMYButton = QPushButton('CMY')

    grid = QGridLayout()
    grid.addWidget(self.ambientLabel, 0, 0)
    grid.addWidget(self.ambientSlider, 0, 1)
    grid.addWidget(self.ambientBox, 0, 2)
    grid.addWidget(self.diffuseLabel, 1, 0)
    grid.addWidget(self.diffuseSlider, 1, 1)
    grid.addWidget(self.diffuseBox, 1, 2)
    grid.addWidget(self.specularLabel, 2, 0)
    grid.addWidget(self.specularSlider, 2, 1)
    grid.addWidget(self.specularBox, 2, 2)
    grid.addWidget(self.powerLabel, 3, 0)
    grid.addWidget(self.powerSlider, 3, 1)
    grid.addWidget(self.powerBox, 3, 2)

    hbox1 = QHBoxLayout()
    hbox1.addWidget(self.presetsLabel)
    hbox1.addWidget(self.matteButton)
    hbox1.addWidget(self.metalButton)
    hbox1.addWidget(self.plasticButton)
    hbox1.addWidget(self.cartoonButton)
    hbox1.setAlignment(Qt.AlignLeft)

    box = QVBoxLayout()
    box.addLayout(grid)
    box.addLayout(hbox1)
    textureGroup = QGroupBox()
    textureGroup.setLayout(box)

    hbox2 = QHBoxLayout()
    hbox2.addWidget(self.interpolationLabel)
    hbox2.addWidget(self.interpolationButton)
    hbox2.setAlignment(Qt.AlignLeft)
    hbox3 = QHBoxLayout()
    hbox3.addWidget(self.representationLabel)
    hbox3.addWidget(self.representationButton)
    hbox3.addWidget(self.sizeLabel)
    hbox3.addWidget(self.sizeBox)
    hbox3.setAlignment(Qt.AlignLeft)

    hbox4 = QHBoxLayout()
    hbox4.addWidget(self.colorsLabel)
    hbox4.addWidget(self.negColorButton)
    hbox4.addWidget(self.zeroColorButton)
    hbox4.addWidget(self.posColorButton)
    hbox4.addWidget(self.specColorButton)
    hbox4.setAlignment(Qt.AlignLeft)

    hbox5 = QHBoxLayout()
    hbox5.addWidget(self.presets2Label)
    hbox5.addWidget(self.GBSButton)
    hbox5.addWidget(self.BWButton)
    hbox5.addWidget(self.RGBButton)
    hbox5.addWidget(self.CMYButton)
    hbox5.setAlignment(Qt.AlignLeft)

    box = QVBoxLayout()
    box.addLayout(hbox4)
    box.addLayout(hbox5)
    colorsGroup = QGroupBox()
    colorsGroup.setLayout(box)

    vbox = QVBoxLayout()
    vbox.setAlignment(Qt.AlignTop)
    vbox.addWidget(textureGroup)
    vbox.addLayout(hbox2)
    vbox.addLayout(hbox3)
    vbox.addWidget(colorsGroup)

    _widget = QWidget()
    _widget.setLayout(vbox)

    self.setWidget(_widget)

    self.ambientSlider.setRange(0, 100)
    self.diffuseSlider.setRange(0, 100)
    self.specularSlider.setRange(0, 100)
    self.powerSlider.setRange(0, 1000)

    self.negColorButton.setAutoFillBackground(True)
    self.negColorButton.setToolButtonStyle(Qt.ToolButtonTextOnly)
    self.zeroColorButton.setAutoFillBackground(True)
    self.zeroColorButton.setToolButtonStyle(Qt.ToolButtonTextOnly)
    self.posColorButton.setAutoFillBackground(True)
    self.posColorButton.setToolButtonStyle(Qt.ToolButtonTextOnly)
    self.specColorButton.setAutoFillBackground(True)
    self.specColorButton.setToolButtonStyle(Qt.ToolButtonTextOnly)

    self.ambientSlider.setToolTip('Amount of "ambient" illumination, independent of lighting')
    self.ambientSlider.setWhatsThis('This gives the amount of the surface color that will show up regardless of its orientation with respect to the light sources.')
    self.ambientBox.setToolTip(self.ambientSlider.toolTip())
    self.diffuseSlider.setToolTip('Amount of "diffuse" illumination, basic light and shadows')
    self.diffuseSlider.setWhatsThis('This gives the amount of surface color due to diffuse light reflection, it is brighter where the surface faces the light sources.')
    self.diffuseBox.setToolTip(self.diffuseSlider.toolTip())
    self.specularSlider.setToolTip('Amount of "specular" illumination, which gives the highlights')
    self.specularSlider.setWhatsThis('This gives the amount of specular color that shows in the highlights.')
    self.specularBox.setToolTip(self.specularSlider.toolTip())
    self.powerSlider.setToolTip('Size of the highlights: the higher, the smaller')
    self.powerSlider.setWhatsThis('This controls the size of the highlights, the higher the power the smaller and brighter the highlights.')
    self.powerBox.setToolTip(self.powerSlider.toolTip())
    self.matteButton.setToolTip('A matte texture with no highlights')
    self.matteButton.setWhatsThis('Loads the default matte texture.')
    self.metalButton.setToolTip('A sort of metallic texture')
    self.metalButton.setWhatsThis('Loads the metal texture.')
    self.plasticButton.setToolTip('A sort of plastic texture with tight highlights')
    self.plasticButton.setWhatsThis('Loads the plastic texture.')
    self.cartoonButton.setToolTip('A cartoon-like texture with flat colors')
    self.cartoonButton.setWhatsThis('Loads the cartoon texture.')
    self.interpolationButton.setToolTip('Choose interpolation method for the surface normals')
    self.interpolationButton.setWhatsThis('Selects between different types on interpolation for the surface normal: flat (no interpolation), Gouraud and Phong (both give the same smooth result).')
    self.representationButton.setToolTip('Choose the type of representation for the isosurface')
    self.representationButton.setWhatsThis('Selects between different types of representation: points, wireframe or surface.')
    self.sizeBox.setToolTip('Point or line width for points and wireframe representations')
    self.sizeBox.setWhatsThis('Size for the points in the point representation or width for the lines in wireframe representation.')
    self.negColorButton.setToolTip('Color used for the negative parts of the isosurfaces')
    self.negColorButton.setWhatsThis('When an isosurface has (or can have) both negative and positive parts, the negative parts are drawn with this color.')
    self.zeroColorButton.setToolTip('Color used for unsigned isosurfaces (density')
    self.zeroColorButton.setWhatsThis('When an isosurface is unsigned (the electron density), it is drawn with this color.')
    self.posColorButton.setToolTip('Color used for the positive parts of the isosurfaces')
    self.posColorButton.setWhatsThis('When an isosurface has (or can have) both negative and positive parts, the positive parts are drawn with this color.')
    self.specColorButton.setToolTip('Color of the highlights')
    self.specColorButton.setWhatsThis('This is the color used for the specular highlights. Ambient and diffuse use the surface color.')
    self.GBSButton.setToolTip('Gold, bronze and silver colors')
    self.GBSButton.setWhatsThis('Loads a preset with gold color for positive, bronze color for negative and silver color for unsigned.')
    self.BWButton.setToolTip('Black, grey and white colors')
    self.BWButton.setWhatsThis('Loads a preset with white for positive, black for negative and grey for unsigned.')
    self.RGBButton.setToolTip('Red, green and blue colors')
    self.RGBButton.setWhatsThis('Loads a preset with blue for positive, red for negative and green for unsigned.')
    self.CMYButton.setToolTip('Cyan, magenta and yellow colors')
    self.CMYButton.setWhatsThis('Loads a preset with yellow for positive, magenta for negative and cyan for unsigned.')

    self.ambientSlider.valueChanged.connect(self.ambientSlider_changed)
    self.ambientBox.editingFinished.connect(self.ambientBox_changed)
    self.diffuseSlider.valueChanged.connect(self.diffuseSlider_changed)
    self.diffuseBox.editingFinished.connect(self.diffuseBox_changed)
    self.specularSlider.valueChanged.connect(self.specularSlider_changed)
    self.specularBox.editingFinished.connect(self.specularBox_changed)
    self.powerSlider.valueChanged.connect(self.powerSlider_changed)
    self.powerBox.editingFinished.connect(self.powerBox_changed)
    self.matteButton.clicked.connect(partial(self.preset, 'matte'))
    self.metalButton.clicked.connect(partial(self.preset, 'metal'))
    self.plasticButton.clicked.connect(partial(self.preset, 'plastic'))
    self.cartoonButton.clicked.connect(partial(self.preset, 'cartoon'))
    self.interpolationButton.currentIndexChanged.connect(self.interpolation_changed)
    self.representationButton.currentIndexChanged.connect(self.representation_changed)
    self.sizeBox.valueChanged.connect(self.sizeBox_changed)
    self.posColorButton.clicked.connect(partial(self.choose_color, 'pos'))
    self.negColorButton.clicked.connect(partial(self.choose_color, 'neg'))
    self.zeroColorButton.clicked.connect(partial(self.choose_color, 'zero'))
    self.specColorButton.clicked.connect(partial(self.choose_color, 'spec'))
    self.GBSButton.clicked.connect(partial(self.color_preset, 'GBS'))
    self.BWButton.clicked.connect(partial(self.color_preset, 'B&W'))
    self.RGBButton.clicked.connect(partial(self.color_preset, 'RGB'))
    self.CMYButton.clicked.connect(partial(self.color_preset, 'CMY'))

    self.interpolationButton.setCurrentIndex(1) # Gouraud
    self.representationButton.setCurrentIndex(2) # Surface
    self.sizeBox.setValue(1)
    self.preset('metal')
    self.color_preset('GBS')

  def set_pos(self):
    if (not self.pos):
      self.move(self.parent().frameGeometry().topLeft() + self.parent().rect().center() - self.rect().center())
      self.pos = True

  @property
  def ambient(self):
    return self._ambient

  @ambient.setter
  def ambient(self, value):
    old = self._ambient
    self._ambient = value
    self._ambient_changed(value, old)

  @property
  def diffuse(self):
    return self._diffuse

  @diffuse.setter
  def diffuse(self, value):
    old = self._diffuse
    self._diffuse = value
    self._diffuse_changed(value, old)

  @property
  def specular(self):
    return self._specular

  @specular.setter
  def specular(self, value):
    old = self._specular
    self._specular = value
    self._specular_changed(value, old)

  @property
  def power(self):
    return self._power

  @power.setter
  def power(self, value):
    old = self._power
    self._power = value
    self._power_changed(value, old)

  @property
  def interpolation(self):
    return self._interpolation

  @interpolation.setter
  def interpolation(self, value):
    old = self._interpolation
    self._interpolation = value
    self._interpolation_changed(value, old)

  @property
  def representation(self):
    return self._representation

  @representation.setter
  def representation(self, value):
    old = self._representation
    self._representation = value
    self._representation_changed(value, old)

  @property
  def size(self):
    return self._size

  @size.setter
  def size(self, value):
    old = self._size
    self._size = value
    self._size_changed(value, old)

  @property
  def negcolor(self):
    return self._negcolor

  @negcolor.setter
  def negcolor(self, value):
    old = self._negcolor
    self._negcolor = value
    self.color_changed('neg', value, old)

  @property
  def zerocolor(self):
    return self._zerocolor

  @zerocolor.setter
  def zerocolor(self, value):
    old = self._zerocolor
    self._zerocolor = value
    self.color_changed('zero', value, old)

  @property
  def poscolor(self):
    return self._poscolor

  @poscolor.setter
  def poscolor(self, value):
    old = self._poscolor
    self._poscolor = value
    self.color_changed('pos', value, old)

  @property
  def specularcolor(self):
    return self._specularcolor

  @specularcolor.setter
  def specularcolor(self, value):
    old = self._specularcolor
    self._specularcolor = value
    self.color_changed('spec', value, old)

  def _ambient_changed(self, new, old):
    if (new == old):
      return
    slider_value = round(self.ambientSlider.minimum() + new * (self.ambientSlider.maximum() + self.ambientSlider.minimum()))
    self.ambientSlider.blockSignals(True)
    self.ambientSlider.setValue(slider_value)
    self.ambientSlider.blockSignals(False)
    if (self.parent().surface is None):
      return
    self.parent().surface.GetProperty().SetAmbient(new)
    self.parent().vtk_update()

  def ambientSlider_changed(self, value):
    new = (value - self.ambientSlider.minimum())/(self.ambientSlider.maximum() - self.ambientSlider.minimum())
    self.ambientBox.setText('{:.2f}'.format(new))
    self.ambient = new

  def ambientBox_changed(self):
    try:
      value = float(self.ambientBox.text())
      assert 0.0 <= value <= 1.0
      self.ambient = value
    except:
      self.ambientBox.setText('{:.2f}'.format(self.ambient))

  def _diffuse_changed(self, new, old):
    if (new == old):
      return
    slider_value = round(self.diffuseSlider.minimum() + new * (self.diffuseSlider.maximum() + self.diffuseSlider.minimum()))
    self.diffuseSlider.blockSignals(True)
    self.diffuseSlider.setValue(slider_value)
    self.diffuseSlider.blockSignals(False)
    if (self.parent().surface is None):
      return
    self.parent().surface.GetProperty().SetDiffuse(new)
    self.parent().vtk_update()

  def diffuseSlider_changed(self, value):
    new = (value - self.diffuseSlider.minimum())/(self.diffuseSlider.maximum() - self.diffuseSlider.minimum())
    self.diffuseBox.setText('{:.2f}'.format(new))
    self.diffuse = new

  def diffuseBox_changed(self):
    try:
      value = float(self.diffuseBox.text())
      assert 0.0 <= value <= 1.0
      self.diffuse = value
    except:
      self.diffuseBox.setText('{:.2f}'.format(self.diffuse))

  def _specular_changed(self, new, old):
    if (new == old):
      return
    slider_value = round(self.specularSlider.minimum() + new * (self.specularSlider.maximum() + self.specularSlider.minimum()))
    self.specularSlider.blockSignals(True)
    self.specularSlider.setValue(slider_value)
    self.specularSlider.blockSignals(False)
    if (self.parent().surface is None):
      return
    self.parent().surface.GetProperty().SetSpecular(new)
    self.parent().vtk_update()

  def specularSlider_changed(self, value):
    new = (value - self.specularSlider.minimum())/(self.specularSlider.maximum() - self.specularSlider.minimum())
    self.specularBox.setText('{:.2f}'.format(new))
    self.specular = new

  def specularBox_changed(self):
    try:
      value = float(self.specularBox.text())
      assert 0.0 <= value <= 1.0
      self.specular = value
    except:
      self.specularBox.setText('{:.2f}'.format(self.specular))

  def _power_changed(self, new, old):
    if (new == old):
      return
    logrange = np.log(300/0.03)
    reldist = np.log(new/0.03)/logrange
    slider_value = round(self.powerSlider.minimum() + reldist * (self.powerSlider.maximum() + self.powerSlider.minimum()))
    self.powerSlider.blockSignals(True)
    self.powerSlider.setValue(slider_value)
    self.powerSlider.blockSignals(False)
    if (self.parent().surface is None):
      return
    self.parent().surface.GetProperty().SetSpecularPower(new)
    self.parent().vtk_update()

  def powerSlider_changed(self, value):
    logrange = np.log(300/0.03)
    reldist = (value - self.powerSlider.minimum())/(self.powerSlider.maximum() - self.powerSlider.minimum())
    new = 0.03*np.exp(reldist*logrange)
    self.powerBox.setText('{:.2f}'.format(new))
    self.power = new

  def powerBox_changed(self):
    try:
      value = float(self.powerBox.text())
      assert 0.03 <= value <= 300
      self.power = value
    except:
      self.powerBox.setText('{:.2f}'.format(self.power))

  def _interpolation_changed(self, new, old):
    if (new == old):
      return
    self.interpolationButton.blockSignals(True)
    self.interpolationButton.setCurrentIndex(new)
    self.interpolationButton.blockSignals(False)
    if (self.parent().surface is None):
      return
    self.parent().surface.GetProperty().SetInterpolation(new)
    self.parent().vtk_update()

  def interpolation_changed(self, new):
    try:
      self.interpolation = new
    except:
      pass

  def _representation_changed(self, new, old):
    if (new == old):
      return
    self.representationButton.blockSignals(True)
    self.representationButton.setCurrentIndex(new)
    self.representationButton.blockSignals(False)
    if (self.parent().surface is None):
      return
    self.parent().surface.GetProperty().SetRepresentation(new)
    self.parent().vtk_update()

  def representation_changed(self, new):
    try:
      self.representation = new
    except:
      pass

  def _size_changed(self, new, old):
    if (new == old):
      return
    if (self.parent().surface is None):
      return
    self.parent().surface.GetProperty().SetLineWidth(new)
    self.parent().surface.GetProperty().SetPointSize(new)
    self.parent().vtk_update()

  def sizeBox_changed(self, value):
    try:
      value = float(value)
      assert 0.0 <= value
      self.size = value
    except:
      self.sizeBox.setValue(self.size)

  def color_changed(self, which, new, old):
    if (new == old):
      return
    if (which == 'neg'):
      try:
        self.parent().lut.SetTableValue(0, *new)
      except AttributeError:
        pass
    elif (which == 'zero'):
      try:
        self.parent().lut.SetTableValue(1, *new)
        if (self.parent().surface is not None):
          self.parent().surface.GetProperty().SetAmbientColor(new)
          self.parent().surface.GetProperty().SetDiffuseColor(new)
      except AttributeError:
        pass
    elif (which == 'pos'):
      try:
        self.parent().lut.SetTableValue(2, *new)
      except AttributeError:
        pass
    elif (which == 'spec'):
      try:
        if (self.parent().surface is not None):
          self.parent().surface.GetProperty().SetSpecularColor(new)
      except AttributeError:
        pass
    self.parent().vtk_update()

  def preset(self, preset):
    if (preset == 'matte'):
      self.ambientBox.setText('0.0')
      self.diffuseBox.setText('1.0')
      self.specularBox.setText('0.0')
      self.powerBox.setText('1.0')
    elif (preset == 'metal'):
      self.ambientBox.setText('0.0')
      self.diffuseBox.setText('0.7')
      self.specularBox.setText('0.7')
      self.powerBox.setText('3.0')
    elif (preset == 'plastic'):
      self.ambientBox.setText('0.1')
      self.diffuseBox.setText('0.9')
      self.specularBox.setText('1.0')
      self.powerBox.setText('50')
    elif (preset == 'cartoon'):
      self.ambientBox.setText('0.7')
      self.diffuseBox.setText('0.0')
      self.specularBox.setText('0.2')
      self.powerBox.setText('0.03')
    ready = self.parent().ready
    self.parent().ready = False
    self.ambientBox.editingFinished.emit()
    self.diffuseBox.editingFinished.emit()
    self.specularBox.editingFinished.emit()
    self.powerBox.editingFinished.emit()
    self.parent().ready = ready
    self.parent().vtk_update()

  def choose_color(self, which, _color=None):
    color = QColor()
    if (not _color):
      if (which == 'neg'):
        color.setRgbF(*self.negcolor)
      elif (which == 'zero'):
        color.setRgbF(*self.zerocolor)
      elif (which == 'pos'):
        color.setRgbF(*self.poscolor)
      elif (which == 'spec'):
        color.setRgbF(*self.specularcolor)
      color = QColorDialog().getColor(color, self)
    else:
      color.setRgbF(*_color)
    if (not color.isValid()):
      return
    pal = QPalette()
    pal.setColor(QPalette.Button, color)
    if (which == 'neg'):
      self.negcolor = color.getRgbF()[0:3]
      self.negColorButton.setPalette(pal)
    elif (which == 'zero'):
      self.zerocolor = color.getRgbF()[0:3]
      self.zeroColorButton.setPalette(pal)
    elif (which == 'pos'):
      self.poscolor = color.getRgbF()[0:3]
      self.posColorButton.setPalette(pal)
    elif (which == 'spec'):
      self.specularcolor = color.getRgbF()[0:3]
      self.specColorButton.setPalette(pal)

  def color_preset(self, preset):
    ready = self.parent().ready
    self.parent().ready = False
    if (preset == 'GBS'):
      self.choose_color('neg',  (222/255, 119/255,  61/255))
      self.choose_color('zero', (172/255, 189/255, 208/255))
      self.choose_color('pos',  (204/255, 222/255,  61/255))
      self.choose_color('spec', (172/255, 189/255, 208/255))
    elif (preset == 'B&W'):
      self.choose_color('neg',  ( 20/255,  20/255,  20/255))
      self.choose_color('zero', (128/255, 128/255, 128/255))
      self.choose_color('pos',  (235/255, 235/255, 235/255))
      self.choose_color('spec', (255/255, 255/255, 255/255))
    elif (preset == 'RGB'):
      self.choose_color('neg',  (200/255,  60/255,  60/255))
      self.choose_color('zero', ( 60/255, 200/255,  60/255))
      self.choose_color('pos',  ( 60/255, 120/255, 200/255))
      self.choose_color('spec', (200/255, 200/255, 200/255))
    elif (preset == 'CMY'):
      self.choose_color('neg',  (220/255,   0/255, 220/255))
      self.choose_color('zero', (  0/255, 220/255, 220/255))
      self.choose_color('pos',  (220/255, 220/255,   0/255))
      self.choose_color('spec', (128/255, 220/255, 128/255))
    self.parent().ready = ready
    self.parent().vtk_update()

  def closeEvent(self, *args):
    self.parent().textureButton.setChecked(False)
    super().closeEvent(*args)

app = QApplication(sys.argv)
win = MainWindow()
try:
  win.filename = os.path.abspath(sys.argv[1])
except IndexError:
  pass
rc = app.exec_()
# orderly cleanup
del win
del app
sys.exit(rc)
