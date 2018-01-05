#!/usr/bin/env python
# -*- coding: utf-8 -*-

__name__ = 'Pegamoid'
__author__ = 'Ignacio Fdez. Galván'
__copyright__ = 'Copyright 2018'
__license__ = 'GPL v3.0'
__version__ = '1.0'

from traits.api import HasTraits, Range, Bool, Str, Int, Float, CFloat, List, Dict, Enum, File, Button, Instance, Any, on_trait_change
from traitsui.api import View, Item, Group, RangeEditor, EnumEditor, CSVListEditor, ButtonEditor, \
                         TextEditor, HTMLEditor, TableEditor, ObjectColumn, StatusItem, Action, Handler
from traitsui.extras.checkbox_column import CheckboxColumn
from traitsui.key_bindings import KeyBinding, KeyBindings
from traitsui.message import Message, error
from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MlabSceneModel, SceneEditor, MayaviScene
from tvtk.api import tvtk
from pyface.api import GUI, ImageResource, FileDialog, OK

import h5py
import numpy as np
from fractions import Fraction
from threading import Thread

import sys
import os
import os.path
import codecs
import struct
import re
from copy import deepcopy
from itertools import izip_longest
from tempfile import mkdtemp, NamedTemporaryFile
from shutil import rmtree
from socket import gethostname
from datetime import datetime

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
      self.irrep = [i.strip() for i in f.attrs['IRREP_LABELS']]
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
      self.centers = [{'name':l.strip().decode('utf8'), 'Z':int(q), 'xyz':x} for l,q,x in zip(labels, charges, coords)]
      self.geomcenter = (np.amin(coords, axis=0) + np.amax(coords, axis=0))/2
      # Then read the primitives and assign them to the centers
      prims = f['PRIMITIVES'][:]    # (exponent, coefficient)
      prids = f['PRIMITIVE_IDS'][:] # (center, l, shell)
      # The basis_id contains negative l if the shell is Cartesian
      if (sym > 1):
        basis_function_ids = 'DESYM_BASIS_FUNCTION_IDS'
      else:
        basis_function_ids = 'BASIS_FUNCTION_IDS'
      bf_id = np.rec.fromrecords(f[basis_function_ids][:], names='c, s, l, m') # (center, shell, l, m)
      bf_cart = bf_id[bf_id['l'] < 0][['c','l','s']].tolist()
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
            if ((i+1, -l, s+1) in bf_cart):
              c['cart'][(l, s)] = True
            # get exponents and coefficients
            ll.append([pp.tolist() for p,pp in zip(prids, prims) if ((p[0] == i+1) and (p[1] == l) and (p[2] == s+1))])
          c['basis'].append(ll)
      # At this point each center[i]['basis'] is a list of maxl items, one for each value of l,
      # each item is a list of shells,
      # each item is a list of primitives,
      # each item is a list of [exponent, coefficient]
      # Now get the indices for sorting all the basis functions (2l+1 or (l+1)(l+2)/2 for each shell)
      # by center, l, m, shell
      # To get the correct sorting for Cartesian shells, invert l
      for b in bf_id:
        if (b['l'] < 0):
          b['l'] *= -1
      self.bf_sort = np.argsort(bf_id, order=('c', 'l', 'm', 's'))
      # And sph_c can be computed
      self.set_sph_c(maxl)
    # Reading the basis set invalidates the orbitals, if any
    self.MO = None
    self.MO_b = None

  # Read molecular orbitals from an HDF5 file
  def read_h5_MO(self):
    with h5py.File(self.file, 'r') as f:
      # Read the orbital properties
      if ('MO_BETA_ENERGIES' in f):
        # If available alpha and beta orbitals are separated
        mo_en = f['MO_ALPHA_ENERGIES'][:]
        mo_oc = f['MO_ALPHA_OCCUPATIONS'][:]
        mo_cf = f['MO_ALPHA_VECTORS'][:]
        mo_en_b = f['MO_BETA_ENERGIES'][:]
        mo_oc_b = f['MO_BETA_OCCUPATIONS'][:]
        mo_cf_b = f['MO_BETA_VECTORS'][:]
        try:
          mo_ti = f['MO_ALPHA_TYPEINDICES'][:]
          mo_ti_b = f['MO_BETA_TYPEINDICES'][:]
        except:
          mo_ti = ['?' for i in mo_oc_b]
          mo_ti_b = ['?' for i in mo_oc_b]
      else:
        mo_en = f['MO_ENERGIES'][:]
        mo_oc = f['MO_OCCUPATIONS'][:]
        mo_cf = f['MO_VECTORS'][:]
        try:
          mo_ti = f['MO_TYPEINDICES'][:]
        except:
          mo_ti = ['?' for i in mo_oc]
        mo_en_b = []
        mo_oc_b = []
        mo_cf_b = []
        mo_ti_b = []
      self.MO = [{'ene':e, 'occup':o, 'type':t} for e,o,t in zip(mo_en, mo_oc, mo_ti)]
      self.MO_b = [{'ene':e, 'occup':o, 'type':t} for e,o,t in zip(mo_en_b, mo_oc_b, mo_ti_b)]
      # Read the coefficients
      ii = [sum(self.N_bas[:i]) for i in range(len(self.N_bas))]
      j = 0
      for i,b,s in zip(ii, self.N_bas, self.irrep):
        for orb,orb_b in izip_longest(self.MO[i:i+b], self.MO_b[i:i+b]):
          orb['sym'] = s
          orb['coeff'] = np.zeros(sum(self.N_bas))
          orb['coeff'][i:i+b] = mo_cf[j:j+b]
          if (orb_b):
            orb_b['sym'] = s
            orb_b['coeff'] = np.zeros(sum(self.N_bas))
            orb_b['coeff'][i:i+b] = mo_cf_b[j:j+b]
          j += b
      # Desymmetrize the MOs
      if (len(self.N_bas) > 1):
        for orb in self.MO + self.MO_b:
          orb['coeff'] = np.matmul(self.mat, orb['coeff'])

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
            self.centers.append({'name':l, 'Z':int(q), 'xyz':np.array(map(float, [x, y, z]))*unit})
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
                  basis[0].append([])
                  if (1 not in basis):
                    basis[1] = []
                  basis[1].append([])
                  for i in range(nprim):
                    e, c1, c2 = map(float, f.readline().split())
                    basis[0][-1].append([e, c1])
                    basis[1][-1].append([e, c2])
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
                  basis[l].append([])
                  # Read exponents and coefficients
                  for i in range(nprim):
                    e, c = map(float, f.readline().split())
                    basis[l][-1].append([e, c])
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
          # each item is a list of primitives,
          # each item is a list of [exponent, coefficient]
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
          lz = b['m']+b['l']-ly*(ly+1)/2
          lx = b['l']-ly
          ly -= lz
          lx = self._binom(2*lx, lx)*np.math.factorial(lx)/2**lx
          ly = self._binom(2*ly, ly)*np.math.factorial(ly)/2**ly
          lz = self._binom(2*lz, lz)*np.math.factorial(lz)/2**lz
          self.fact[i] = 1.0/np.sqrt(float(lx*ly*lz))
      # And get the indices for sorting the basis functions by center, l, m, shell
      self.bf_sort = np.argsort(bf_id, order=('c', 'l', 'm', 's'))
      self.head = f.tell()
      self.N_bas = [len(bf_id)]
      self.set_sph_c(maxl)
    # Reading the basis set invalidates the orbitals, if any
    self.MO = None
    self.MO_b = None

  # Read molecular orbitals from a Molden file
  def read_molden_MO(self):
    self.MO = []
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
            self.MO.append({'ene':ene, 'occup':occ, 'sym':sym, 'type':'?', 'coeff':self.fact*cff})
        except:
          break
    # Build the list of irreps from the orbitals
    self.irrep = []
    for o in self.MO + self.MO_b:
      if (o['sym'] not in self.irrep):
        self.irrep.append(o['sym'])

  # Read molecular orbitals from an InpOrb file
  def read_inporb_MO(self, infile):
    if (self.type != 'hdf5'):
      return False
    self.file = infile
    self.inporb = 0
    with open(infile, 'r') as f:
      line = f.readline()
      # First read the header section and make sure the number
      # of basis functions matches the current values
      while ((not line.startswith('#INFO')) and (line != '')):
        line = f.readline()
      line = f.readline()
      uhf, nsym, _ = map(int, f.readline().split())
      N_bas = np.array(map(int, f.readline().split()))
      nMO = np.array(map(int, f.readline().split()))
      if (not np.array_equal(N_bas, self.N_bas)):
        return False
      # Decide whether or not beta orbitals will be read
      if (uhf):
        self.MO_b = deepcopy(self.MO)
      else:
        self.MO_b = []
      # Read orbital coefficients, only the non-zero (by symmetry)
      # coefficients are written in the file
      while ((not line.startswith('#ORB')) and (line != '')):
        line = f.readline()
      ii = [sum(self.N_bas[:i]) for i in range(len(self.N_bas))]
      j = 0
      for i,b,s in zip(ii, self.N_bas, self.irrep):
        for orb in self.MO[i:i+b]:
          orb['sym'] = s
          orb['coeff'] = np.zeros(sum(self.N_bas))
          cff = []
          f.readline()
          while (len(cff) < b):
            cff.extend(f.readline().split())
          orb['coeff'][i:i+b] = map(float, cff)
          j += b
      if (uhf):
        while ((not line.startswith('#UORB')) and (line != '')):
          line = f.readline()
        ii = [sum(self.N_bas[:i]) for i in range(len(self.N_bas))]
        j = 0
        for i,b,s in zip(ii, self.N_bas, self.irrep):
          for orb in self.MO_b[i:i+b]:
            orb['sym'] = s
            orb['coeff'] = np.zeros(sum(self.N_bas))
            cff = []
            f.readline()
            while (len(cff) < b):
              cff.extend(f.readline().split())
            orb['coeff'][i:i+b] = map(float, cff)
            j += b
      # Desymmetrize the orbital coefficients
      if (len(self.N_bas) > 1):
        for orb in self.MO + self.MO_b:
          orb['coeff'] = np.matmul(self.mat, orb['coeff'])
      # Read the occupations
      while ((not line.startswith('#OCC')) and (line != '')):
        line = f.readline()
      f.readline()
      occ = []
      for i,b in zip(ii, self.N_bas):
        while (len(occ) < i+b):
          occ.extend(f.readline().split())
      if (uhf):
        while ((not line.startswith('#UOCC')) and (line != '')):
          line = f.readline()
        f.readline()
        for i,b in zip(ii, self.N_bas):
          while (len(occ) < len(self.MO)+i+b):
            occ.extend(f.readline().split())
      for i,o in enumerate(self.MO + self.MO_b):
        o['occup'] = float(occ[i])
      # Read the energies
      while ((not line.startswith('#ONE')) and (line != '')):
        line = f.readline()
      f.readline()
      ene = []
      for i,b in zip(ii, self.N_bas):
        while (len(ene) < i+b):
          ene.extend(f.readline().split())
      if (uhf):
        while ((not line.startswith('#UONE')) and (line != '')):
          line = f.readline()
        f.readline()
        for i,b in zip(ii, self.N_bas):
          while (len(ene) < len(self.MO)+i+b):
            ene.extend(f.readline().split())
      for i,o in enumerate(self.MO + self.MO_b):
        o['ene'] = float(ene[i])
      # Read the orbital types (same for alpha and beta)
      while ((not line.startswith('#INDEX')) and (line != '')):
        line = f.readline()
      cff = ''
      for i,b in zip(ii, self.N_bas):
        line = f.readline()
        while (len(cff) < i+b):
          cff += f.readline().split()[1]
      for i,o in enumerate(self.MO):
        o['type'] = cff[i].upper()
      for i,o in enumerate(self.MO_b):
        o['type'] = cff[i].upper()
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
      # For Cartesians shells, m does not actually contain m, but:
      # m = T(ly+lz)-(lx+ly), where T(n) = n*(n+1)/2 is the nth triangular number
      ly = int(np.floor((np.sqrt(8*(m+l)+1)-1)/2))
      lz = m+l-ly*(ly+1)/2
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
  def rad(self, r2, l, ec):
    rad = 0
    for e,c in ec:
      if (c != 0.0):
        # Combine total normalization factor and coefficient
        N = np.power((2*e)**(3+2*l)/np.pi**3, 0.25) * c
        rad += N * np.exp(-e*r2)
    return rad

  # Compute an atomic orbital as product of angular and radial components
  def ao(self, x, y, z, ec, l, m):
    ang = self.ang(x, y, z, l, m)
    r2 = x**2+y**2+z**2
    rad = self.rad(r2, l, ec)
    return ang*rad

  # Compute a molecular orbital, as linear combination of atomic orbitals
  # at different centers. It can use a cache of atomic orbitals to avoid
  # recomputing them. "spin" specifies if the coefficients will be taken
  # from self.MO (alpha) or self.MO_b (beta)
  def mo(self, n, x, y, z, spin='a', cache=None):
    f = 0
    mo = np.zeros_like(x)
    # Reorder MO coefficients
    if (spin == 'b'):
      MO = self.MO_b[n]['coeff'][self.bf_sort]
    elif (spin == 'a'):
      MO = self.MO[n]['coeff'][self.bf_sort]
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
        # For each center, l and m we have different angular parts
        # (the range includes both spherical and Cartesian indices)
        #for m in range(-l, l*(l+1)+1):
        for m in range(-l, l*(l+1)/2+1):
          ao_ang = None
          cart = None
          # Now each shell is an atomic orbital (basis function)
          for s,i in enumerate(ll):
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
              # The AO contribution is either in the cache
              # or we compute it now
              if ((cache is None) or np.isnan(cache[f,0,0,0])):
                # Compute relative coordinates if not done yet
                if (x0 is None):
                  x0, y0, z0 = [x, y, z] - c['xyz'][:, np.newaxis, np.newaxis, np.newaxis]
                  r2 = x0**2 + y0**2 + z0**2
                # Compute angular part if not done yet
                if (ao_ang is None):
                  ao_ang = self.ang(x0, y0, z0, l, m, cart=cart)
                # Compute radial part if not done yet
                if (s not in rad_l):
                  rad_l[s] = self.rad(r2, l, i)
                cch = ao_ang*rad_l[s]
                # Save in the cache if enabled
                if (cache is not None):
                  cache[f] = np.copy(cch)
              elif (cache is not None):
                cch = cache[f]
              # Add the AO contribution to the MO
              mo += MO[f]*cch
            f += 1
    if (cache is not None):
      cache.flush()
    return mo

  # Compute electron density as sum of square of (natural) orbitals times occupation.
  # It can use a cache for MO evaluation and a mask to select only some orbitals.
  def dens(self, x, y, z, cache=None, mask=None, spin=False):
    dens = np.zeros_like(x)
    # Add alternated alpha and beta orbitals
    l = 0
    for i,orb in enumerate([j for i in izip_longest(self.MO, self.MO_b) for j in i]):
      if (orb is None):
        continue
      f = 1.0
      if (i%2 == 0):
        s = 'a'
      else:
        s = 'b'
        if (spin):
          f = -1.0
      if ((mask is None) or mask[l]):
        if (abs(orb['occup']) > self.eps):
          dens += f*orb['occup']*self.mo(i/2, x, y, z, s, cache)**2
      l += 1
    return dens

  # Compute the Laplacian of a field by central finite differences
  # It assumes the grid is regular and Cartesian
  def laplacian(self, xyz, field):
    nx, ny, nz = xyz[0].shape
    dx2, dy2, dz2 = [1/(np.amax(x)-np.amin(x)/n)**2 for x,n in zip(xyz, [nx, ny, nz])]
    data = -2*field*(dx2+dy2+dz2)
    for i in range(nx):
      if ((i == 0) or (i == nx-1)):
        data[i,:,:] = None
      else:
        data[i,:,:] += (field[i-1,:,:]+field[i+1,:,:])*dx2
    for j in range(ny):
      if ((j == 0) or (j == ny-1)):
        data[:,j,:] = None
      else:
        data[:,j,:] += (field[:,j-1,:]+field[:,j+1,:])*dy2
    for k in range(nz):
      if ((k == 0) or (k == nz-1)):
        data[:,:,k] = None
      else:
        data[:,:,k] += (field[:,:,k-1]+field[:,:,k+1])*dz2
    return data

  # Returns binomial coefficient as a fraction
  # Easy overflow for large arguments, but we are interested in
  # relatively small arguments
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
  # the real spherical harmonic Y(l,m)
  # Since the coefficients are square roots of rational numbers, this
  # returns the square of the coefficient as a fraction, with its sign
  #
  # See:
  # Transformation between Cartesian and pure spherical harmonic Gaussians
  # 10.1002/qua.560540202
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
      fo.attrs['MOLCAS_VERSION'] = '{0} {1}'.format(__name__, __version__)
      # Copy some data from the original file
      for a in ['NSYM', 'NBAS', 'NPRIM', 'IRREP_LABELS', 'NATOMS_ALL', 'NATOMS_UNIQUE']:
        fo.attrs[a] = fi.attrs[a]
      for d in ['CENTER_LABELS', 'CENTER_CHARGES', 'CENTER_COORDINATES', 'BASIS_FUNCTION_IDS',
                'DESYM_CENTER_LABELS', 'DESYM_CENTER_CHARGES', 'DESYM_CENTER_COORDINATES', 'DESYM_BASIS_FUNCTION_IDS', 'DESYM_MATRIX',
                'PRIMITIVES', 'PRIMITIVE_IDS']:
        if (d in fi):
          fi.copy(d, fo)
      # Write orbital data from current orbitals
      # (could be loaded from InpOrb and/or have modified types)
      uhf = len(self.MO_b) > 0
      nMO = [(sum(self.N_bas[:i]), sum(self.N_bas[:i+1])) for i in range(len(self.N_bas))]
      if (uhf):
        cff = []
        for i,j in nMO:
          for k in range(i,j):
            cff.extend(self.MO[k]['coeff'][i:j])
        fo.create_dataset('MO_ALPHA_VECTORS', data=cff)
        cff = []
        for i,j in nMO:
          for k in range(i,j):
            cff.extend(self.MO_b[k]['coeff'][i:j])
        fo.create_dataset('MO_BETA_VECTORS', data=cff)
        fo.create_dataset('MO_ALPHA_OCCUPATIONS', data=[o['occup'] for o in self.MO])
        fo.create_dataset('MO_BETA_OCCUPATIONS', data=[o['occup'] for o in self.MO_b])
        fo.create_dataset('MO_ALPHA_ENERGIES', data=[o['ene'] for o in self.MO])
        fo.create_dataset('MO_BETA_ENERGIES', data=[o['ene'] for o in self.MO_b])
        tp = [o['newtype'] if ('newtype' in o) else o['type'] for o in self.MO]
        fo.create_dataset('MO_ALPHA_TYPEINDICES', data=tp)
        tp = [o['newtype'] if ('newtype' in o) else o['type'] for o in self.MO_b]
        fo.create_dataset('MO_BETA_TYPEINDICES', data=tp)
      else:
        cff = []
        for i,j in nMO:
          for k in range(i,j):
            cff.extend(self.MO[k]['coeff'][i:j])
        fo.create_dataset('MO_VECTORS', data=cff)
        fo.create_dataset('MO_OCCUPATIONS', data=[o['occup'] for o in self.MO])
        fo.create_dataset('MO_ENERGIES', data=[o['ene'] for o in self.MO])
        tp = [o['newtype'] if ('newtype' in o) else o['type'] for o in self.MO]
        fo.create_dataset('MO_TYPEINDICES', data=tp)

  # Creates an InpOrb file from scratch
  def create_inporb(self, filename):
    index = create_index(self.MO, self.MO_b, self.N_bas)
    if (index is None):
      return
    uhf = len(self.MO_b) > 0
    nMO = [(sum(self.N_bas[:i]), sum(self.N_bas[:i+1])) for i in range(len(self.N_bas))]
    with open(filename, 'w') as f:
      f.write('#INPORB 2.1\n')
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
          cff = wrap_list(self.MO[k]['coeff'][i:j], 5, '{:21.14E}', sep=' ')
          f.write(' ' + '\n '.join(cff) + '\n')
      if (uhf):
        f.write('#UORB\n')
        for s,(i,j) in enumerate(nMO):
          for k in range(i,j):
            f.write('* ORBITAL{0:5d}{1:5d}\n'.format(s+1, k-i+1))
            cff = wrap_list(self.MO_b[k]['coeff'][i:j], 5, '{:21.14E}', sep=' ')
            f.write(' ' + '\n '.join(cff) + '\n')
      f.write('#OCC\n')
      f.write('* OCCUPATION NUMBERS\n')
      for i,j in nMO:
        occ = wrap_list([o['occup'] for o in self.MO[i:j]], 10, '{:11.4E}', sep=' ')
        f.write(' ' + '\n '.join(occ) + '\n')
      if (uhf):
        f.write('#UOCC\n')
        f.write('* Beta OCCUPATION NUMBERS\n')
        for i,j in nMO:
          occ = wrap_list([o['occup'] for o in self.MO_b[i:j]], 10, '{:11.4E}', sep=' ')
          f.write(' ' + '\n '.join(occ) + '\n')
      f.write('#ONE\n')
      f.write('* ONE ELECTRON ENERGIES\n')
      for i,j in nMO:
        ene = wrap_list([o['ene'] for o in self.MO[i:j]], 10, '{:11.4E}', sep=' ')
        f.write(' ' + '\n '.join(ene) + '\n')
      if (uhf):
        f.write('#UONE\n')
        f.write('* Beta ONE ELECTRON ENERGIES\n')
        for i,j in nMO:
          ene = wrap_list([o['ene'] for o in self.MO_b[i:j]], 10, '{:11.4E}', sep=' ')
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
    self.transform = tvtk.Matrix4x4()
    self.file = gridfile
    self.type = ftype
    if (ftype == 'cube'):
      self.read_cube_header()
    elif (ftype == 'luscus'):
      self.read_luscus_header()
    elif (ftype == 'grid'):
      self.read_grid_header()

  # Read grid header from a Cube format
  def read_cube_header(self):
    self.irrep = ['z']
    with open(self.file, 'r') as f:
      f.readline()
      # Read title and grid origin
      title = f.readline().strip()
      n, x, y, z = f.readline().split()
      num = int(n)
      translate = np.array(map(float, [x, y, z]))
      # Read grid sizes and transformation matrix
      n, x, y, z = f.readline().split()
      ngridx = int(n)
      self.transform.set_element(0,0,float(x))
      self.transform.set_element(1,0,float(y))
      self.transform.set_element(2,0,float(z))
      self.transform.set_element(0,3,translate[0])
      n, x, y, z = f.readline().split()
      ngridy = int(n)
      self.transform.set_element(0,1,float(x))
      self.transform.set_element(1,1,float(y))
      self.transform.set_element(2,1,float(z))
      self.transform.set_element(1,3,translate[1])
      n, x, y, z = f.readline().split()
      ngridz= int(n)
      self.transform.set_element(0,2,float(x))
      self.transform.set_element(1,2,float(y))
      self.transform.set_element(2,2,float(z))
      self.transform.set_element(2,3,translate[2])
      # Read geometry
      self.centers = []
      for i in range(abs(num)):
        q, _, x, y, z = f.readline().split()
        self.centers.append({'name':'{0}'.format(i), 'Z':int(q), 'xyz':np.array(map(float, [x, y, z]))})
      # Compute full volume size
      self.ngrid = [ngridx, ngridy, ngridz]
      self.orig = np.array([0.0, 0.0, 0.0])
      self.end = np.array([float(ngridx-1), float(ngridy-1), float(ngridz-1)])
      # If the number of atoms is negative, there are several orbitals in the file, read their numbers
      if (num < 0):
        data = f.readline().split()
        self.nMO = int(data[0])
        data = data[1:]
        self.MO = []
        while (len(data) < self.nMO):
          data.extend(f.readline().split())
        self.MO = [{'label':'{0}: {1}'.format(i, title), 'ene':0.0, 'occup':0.0, 'type':'?', 'sym':'z'} for i in data]
      else:
        self.nMO = 1
        self.MO = [{'label':title, 'ene':0.0, 'occup':0.0, 'type':'?', 'sym':'z'}]
      self.MO_b = []
      # Number of lines occupied by each "record" (ngridz * nMO)
      self.lrec = int(np.ceil(float(self.nMO)*self.ngrid[2]/6))
      # Save the position after the header
      self.head = f.tell()

  # Read grid header from a Grid format
  def read_grid_header(self):
    with open(self.file, 'r') as f:
      f.readline()
      f.readline()
      # Read the geometry
      num = int(f.readline().split()[1])
      self.centers = []
      for i in range(num):
        l, x, y, z = f.readline().split()
        self.centers.append({'name':l, 'Z':name_to_Z(l), 'xyz':np.array(map(float, [x, y, z]))})
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
      self.ngrid = map(int, f.readline().split()[1:])
      self.ngrid = [i+1 for i in self.ngrid]
      translate = np.array(map(float, f.readline().split()[1:]))
      x, y, z = map(float, f.readline().split()[1:])
      self.transform.set_element(0,0,float(x))
      self.transform.set_element(1,0,float(y))
      self.transform.set_element(2,0,float(z))
      self.transform.set_element(0,3,translate[0])
      x, y, z = map(float, f.readline().split()[1:])
      self.transform.set_element(0,1,float(x))
      self.transform.set_element(1,1,float(y))
      self.transform.set_element(2,1,float(z))
      self.transform.set_element(1,3,translate[1])
      x, y, z = map(float, f.readline().split()[1:])
      self.transform.set_element(0,2,float(x))
      self.transform.set_element(1,2,float(y))
      self.transform.set_element(2,2,float(z))
      self.transform.set_element(2,3,translate[2])
      self.orig = np.array([0.0, 0.0, 0.0])
      self.end = np.array([1.0, 1.0, 1.0])
      # Read and parse orbital names
      self.MO = []
      self.MO_b = []
      self.irrep = []
      for i in range(self.nMO):
        name = f.readline()
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
      while (line != ''):
        loc = f.tell()
        line = f.readline()
        if (line.startswith('#INPORB')):
          self.inporb = loc
          break

  # Read grid header from a Luscus format
  def read_luscus_header(self):
    self.irrep = ['z']
    with open(self.file, 'rb') as f:
      # Read the geometry
      angstrom = 0.52917721067
      num = int(f.readline())
      f.readline()
      atom = []
      self.centers = []
      for i in range(num):
        l, x, y, z = f.readline().split()
        self.centers.append({'name':l, 'Z':name_to_Z(l), 'xyz':np.array(map(float, [x, y, z]))/angstrom})
      # Read number of orbitals and block size
      f.readline()
      data = f.readline().split()
      self.nMO = int(data[3])
      self.bsize = int(data[7])
      f.readline()
      # Read grid definition and transform matrix
      self.ngrid = map(int, f.readline().split()[1:])
      translate = np.array(map(float, f.readline().split()[1:]))
      x, y, z = map(float, f.readline().split()[1:])
      self.transform.set_element(0,0,float(x))
      self.transform.set_element(1,0,float(y))
      self.transform.set_element(2,0,float(z))
      self.transform.set_element(0,3,translate[0])
      x, y, z = map(float, f.readline().split()[1:])
      self.transform.set_element(0,1,float(x))
      self.transform.set_element(1,1,float(y))
      self.transform.set_element(2,1,float(z))
      self.transform.set_element(1,3,translate[1])
      x, y, z = map(float, f.readline().split()[1:])
      self.transform.set_element(0,2,float(x))
      self.transform.set_element(1,2,float(y))
      self.transform.set_element(2,2,float(z))
      self.transform.set_element(2,3,translate[2])
      self.orig = np.array([0.0, 0.0, 0.0])
      self.end = np.array([1.0, 1.0, 1.0])
      self.orboff = int(f.readline().split()[2])
      # Read and parse orbital names
      self.MO = []
      self.MO_b = []
      self.irrep = []
      for i in range(self.nMO):
        name = f.readline()
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
        line = f.readline()
        if (line.startswith('#INPORB')):
          self.inporb = loc
          break

  # Read and return precomputed MO values
  def mo(self, n, x, y, z, spin=None, cache=None):
    if (self.type == 'cube'):
      # In Cube format, the nesting is x:y:z:MO, with
      # wrapped lines and forced newlines every lrec values
      vol = np.empty(tuple(self.ngrid))
      with open(self.file, 'r') as f:
        f.seek(self.head)
        for i in range(self.ngrid[0]):
          for j in range(self.ngrid[1]):
            data = ''
            for k in range(self.lrec):
              data += f.readline()
            vol[i,j,:] = map(float, data.split()[n::self.nMO])
    elif (self.type == 'grid'):
      # In Grid format, the nesting is MO:x:y:z, but divided in
      # blocks of length bsize
      data = []
      norb = self.MO[n]['idx']
      with open(self.file, 'r') as f:
        f.seek(self.head)
        num = np.prod(self.ngrid)
        while (len(data) < num):
          lb = min(self.bsize, num-len(data))
          for o in range(self.nMO):
            f.readline()
            if (o == norb):
              for i in range(lb):
                data.append(float(f.readline()))
            else:
              for i in range(lb):
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
          lb = min(self.bsize, num-len(data))
          lbb = lb*struct.calcsize('d')
          f.seek(norb*lbb, 1)
          data.extend(list(struct.unpack(lb*'d', f.read(lbb))))
          f.seek((self.nMO-norb-1)*lbb, 1)
      vol = np.reshape(data, tuple(self.ngrid))
    return vol

#===============================================================================

# Create an index section from alpha and beta orbitals
def create_index(MO, MO_b, nMO):
  index = []
  orbs = list(izip_longest(MO, MO_b))
  i = 0
  for s in nMO:
    index.append('* 1234567890')
    types = ''
    # Try to merge different alpha and beta types
    for oa,ob in orbs[i:i+s]:
      if ('newtype' in oa):
        tpa = oa['newtype'].lower()
      else:
        tpa = oa['type'].lower()
      if (ob is None):
        tp = tpa
      else:
        if ('newtype' in ob):
          tpb = ob['newtype'].lower()
        else:
          tpb = ob['type'].lower()
        if (tpb == tpa):
          tp = tpa
        elif (tpa+tpb in ['is', 'si']):
          tp = '2'
        else:
          error(message='Alpha and beta types differ', title='Error', buttons=['OK'])
          return None
      types += tp
    i += s
    for j,l in enumerate(wrap_list(types, 10, '{}')):
      index.append('{0} {1}'.format(j, l))
  return index

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

# from http://jmol.sourceforge.net/jscolors/
def cpk(Z):
  cpklist = [[255,  0,  0,255], #X
             [255,255,255,255], #H
             [217,255,255,255], #He
             [204,128,255,255], #Li
             [194,255,  0,255], #Be
             [255,181,181,255], #B
             [144,144,144,255], #C
             [ 48, 80,248,255], #N
             [255, 13, 13,255], #O
             [144,224, 80,255], #F
             [179,227,245,255], #Ne
             [171, 92,242,255], #Na
             [138,255,  0,255], #Mg
             [191,166,166,255], #Al
             [240,200,160,255], #Si
             [255,128,  0,255], #P
             [255,255, 48,255], #S
             [ 31,240, 31,255], #Cl
             [128,209,227,255], #Ar
             [143, 64,212,255], #K
             [ 61,255,  0,255], #Ca
             [230,230,230,255], #Sc
             [191,194,199,255], #Ti
             [166,166,171,255], #V
             [138,153,199,255], #Cr
             [156,122,199,255], #Mn
             [224,102, 51,255], #Fe
             [240,144,160,255], #Co
             [ 80,208, 80,255], #Ni
             [200,128, 51,255], #Cu
             [125,128,176,255], #Zn
             [194,143,143,255], #Ga
             [102,143,143,255], #Ge
             [189,128,227,255], #As
             [255,161,  0,255], #Se
             [166, 41, 41,255], #Br
             [ 92,184,209,255], #Kr
             [112, 46,176,255], #Rb
             [  0,255,  0,255], #Sr
             [148,255,255,255], #Y
             [148,224,224,255], #Zr
             [115,194,201,255], #Nb
             [ 84,181,181,255], #Mo
             [ 59,158,158,255], #Tc
             [ 36,143,143,255], #Ru
             [ 10,125,140,255], #Rh
             [  0,105,133,255], #Pd
             [192,192,192,255], #Ag
             [255,217,143,255], #Cd
             [166,117,115,255], #In
             [102,128,128,255], #Sn
             [158, 99,181,255], #Sb
             [212,122,  0,255], #Te
             [148,  0,148,255], #I
             [ 66,158,176,255], #Xe
             [ 87, 23,143,255], #Cs
             [  0,201,  0,255], #Ba
             [112,212,255,255], #La
             [255,255,199,255], #Ce
             [217,255,199,255], #Pr
             [199,255,199,255], #Nd
             [163,255,199,255], #Pm
             [143,255,199,255], #Sm
             [ 97,255,199,255], #Eu
             [ 69,255,199,255], #Gd
             [ 48,255,199,255], #Tb
             [ 31,255,199,255], #Dy
             [  0,255,156,255], #Ho
             [  0,230,117,255], #Er
             [  0,212, 82,255], #Tm
             [  0,191, 56,255], #Yb
             [  0,171, 36,255], #Lu
             [ 77,194,255,255], #Hf
             [ 77,166,255,255], #Ta
             [ 33,148,214,255], #W
             [ 38,125,171,255], #Re
             [ 38,102,150,255], #Os
             [ 23, 84,135,255], #Ir
             [208,208,224,255], #Pt
             [255,209, 35,255], #Au
             [184,184,208,255], #Hg
             [166, 84, 77,255], #Tl
             [ 87, 89, 97,255], #Pb
             [158, 79,181,255], #Bi
             [171, 92,  0,255], #Po
             [117, 79, 69,255], #At
             [ 66,130,150,255], #Rn
             [ 66,  0,102,255], #Fr
             [  0,125,  0,255], #Ra
             [112,171,250,255], #Ac
             [  0,186,255,255], #Th
             [  0,161,255,255], #Pa
             [  0,143,255,255], #U
             [  0,128,255,255], #Np
             [  0,107,255,255], #Pu
             [ 84, 92,242,255], #Am
             [120, 92,227,255], #Cm
             [138, 79,227,255], #Bk
             [161, 54,212,255], #Cf
             [179, 31,212,255], #Es
             [179, 31,186,255], #Fm
             [179, 13,166,255], #Md
             [189, 13,135,255], #No
             [199,  0,102,255], #Lr
             [204,  0, 89,255], #Rf
             [209,  0, 79,255], #Db
             [217,  0, 69,255], #Sg
             [224,  0, 56,255], #Bh
             [230,  0, 46,255], #Hs
             [235,  0, 38,255]] #Mt
  try:
    cpk = cpklist[Z]
  except:
    cpk = [255, 255, 255, 128]
  return cpk

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
# Class for computing or reading the grid data in a separate thread, so the GUI
# is not blocked

class ComputeGrid(Thread):

  def __init__(self, parent, cache=None, **kwargs):
    Thread.__init__(self, **kwargs)
    self.daemon = True
    self.parent = parent
    self.cache = cache

  def run(self):
    orb = self.parent.orb
    spin = 'b' if (self.parent.spin == 'beta') else 'a'
    x, y, z = self.parent.xyz
    if (orb == 0):
      mask = [o.selected for o in self.parent.notes]
      data = self.parent.orbitals.dens(x, y, z, self.cache, mask=mask)
    elif (orb == -1):
      mask = [o.selected for o in self.parent.notes]
      data = self.parent.orbitals.dens(x, y, z, self.cache, mask=mask, spin=True)
    elif (orb == -2):
      mask = [o.selected for o in self.parent.notes]
      data = self.parent.orbitals.dens(x, y, z, self.cache, mask=mask)
      data = self.parent.orbitals.laplacian(self.parent.xyz, data)
    else:
      data = self.parent.orbitals.mo(orb-1, x, y, z, spin, self.cache)
    GUI.invoke_later(self.parent._assign_vol, data)

#===============================================================================

class OrbInList(HasTraits):
  name = Str
  selected = Bool(True)
  note = Str

class Viewer(HasTraits):
  # UI controls
  file = File
  load_button = Button
  save_hdf5 = Button
  save_orbs = Button
  save_cube = Button
  val = CFloat(0.05)
  ngrid = Range(2, 201, 30)
  edge = List(Float, value=[0.0])
  orbitals = Any
  notes = List
  notelist = Button
  sym = Str
  spin = Str
  orb = Int(-10)
  nodes = Bool(False)
  box = Bool(False)
  surface = Bool(True)
  nuc = Bool(True)
  lab = Bool(False)
  status = Str
  # 3D objects
  scene = Instance(MlabSceneModel, ())
  surf = Instance(PipelineBase)
  node = Instance(PipelineBase)
  cube = Instance(PipelineBase)
  mol = Instance(PipelineBase)
  counts = Instance(PipelineBase)
  atomnames = List
  # Auxiliary
  ready = Bool(True)
  isGrid = Bool(False)
  haveOrb = Bool(False)
  shownotes = Any
  nosym = Bool(True)
  symlist = List
  spinlist = List
  orblist = Dict
  xyz = List
  bxyz = List
  vol = Any(0.0)
  minval = CFloat(1.0e-6)
  maxval = CFloat(1.0)

  def __init__(self):
    HasTraits.__init__(self)
    self.grid_changed = False
    self.tmpdir = mkdtemp()
    self.cache_file = None
    # Set icon for the viewer classes
    with NamedTemporaryFile(mode='w+b', suffix='.png', delete=False, dir=self.tmpdir) as f:
      f.write(codecs.decode('''
      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
      ''', 'base64'))
      self.icon = ImageResource(f.name)
    main_view.icon = self.icon
    orbital_list.icon = self.icon

  # Clean up when exiting
  def __del__(self):
    try:
      if (self.cache_file is not None):
        del self.cache_file
      rmtree(self.tmpdir)
    except:
      pass

  # Return a string with orbital information for the drop-down list
  def orb_to_list(self, n, orb):
    if ('label' in orb):
      return '{0:04}:{1}'.format(n, orb['label'])
    else:
      # Build irrep and local numbering
      if (self.nosym):
        numsym = ''
      else:
        if (self.sym == 'All'):
          numsym = ' [{0}]'.format(orb['sym'])
        else:
          m = [o['sym'] for o in self.MO[:n]].count(orb['sym'])
          numsym = ' [{0}, {1}]'.format(orb['sym'], m)
      # Add new type if it has been modified
      tp = orb['type']
      if (('newtype' in orb) and (orb['newtype'] != tp)):
        tp += '->' + orb['newtype']
      return '{0:04}:{0}{1}: {2:.4f} ({3:.4f}) {4}'.format(n, numsym, orb['ene'], orb['occup'], tp)

  # Detect the format of an input file
  def detect_format(self, infile):
    if (not os.path.isfile(infile)):
      return None
    try:
      with h5py.File(infile, 'r') as f:
        return 'hdf5'
    except IOError:
      with open(infile, 'r') as f:
        line = f.readline()
        if (re.search(r'\[MOLDEN FORMAT\]', line, re.IGNORECASE)):
          return 'molden'
        elif (line.startswith('#INPORB')):
          return 'inporb'
        else:
          try:
            N = int(line)
            line = f.readline()
            for i in range(N):
              line = f.readline()
            assert (f.readline().strip() == '<GRID>')
            return 'luscus'
          except:
            f.seek(0)
            line = f.readline()
            line = f.readline()
            line = f.readline()
            if (line.startswith('Natom=')):
              return 'grid'
            else:
              try:
                data = line.split()
                N = int(data[0])
                o = map(float, data[1:])
                return 'cube'
              except:
                pass
    return 'unknown'

  @on_trait_change('load_button')
  def set_file(self, *args):
    dlg = FileDialog(title='Load file', action='open')
    if (dlg.open() == OK):
      self.file = dlg.path

  # When a new file is selected, detect the format and load the file:
  # assign an instance of the appropriate class to self.orbitals
  @on_trait_change('file')
  def load_file(self, new):
    ftype = self.detect_format(new)
    if (ftype is None):
      error(message='File {0} not found'.format(new), title='Error', buttons=['OK'])
    elif (ftype == 'unknown'):
      error(message='Format of {0} not recognized'.format(new), title='Error', buttons=['OK'])
    # If a format with basis set, use Orbitals
    elif (ftype in ['hdf5', 'molden']):
      try:
        self.orbitals = Orbitals(new, ftype)
      except:
        raise
        error(message='Error processing {0} file {1}'.format(ftype, new), title='Error', buttons=['OK'])
    # If InpOrb, it must be loaded after an HDF5
    elif (ftype in ['inporb']):
      try:
        assert (self.orbitals.type == 'hdf5')
      except:
        error(message='The InpOrb format does not contain basis set information, it must be loaded after an HDF5 file (*.h5)', title='Error', buttons=['OK'])
      # self.orbitals has not changed, but the new data has to be processed
      if (self.orbitals.read_inporb_MO(new)):
        self.new_orbitals(self.orbitals)
      else:
        error(message='Incompatible InpOrb data', title='Error', buttons=['OK'])
    # If a precomputed grid format, use Grid
    elif (ftype in ['grid', 'luscus', 'cube']):
      try:
        self.orbitals = Grid(new, ftype)
      except:
        error(message='Error processing {0} file {1}'.format(ftype, new), title='Error', buttons=['OK'])
        raise

  # When new data has been loaded, most things have to be changed:
  # graphical (3D) objects and dynamic UI elements
  @on_trait_change('orbitals')
  def new_orbitals(self, new):
    if (isinstance(self.orbitals, Grid)):
      self.isGrid = True
    else:
      self.isGrid = False
    self.haveOrb = new.inporb is not None
    if (self.surf is not None):
      self.surf.remove()
      self.surf = None
    if (self.node is not None):
      self.node.remove()
      self.node = None
    if (self.cube is not None):
      self.cube.remove()
      self.cube = None
    # Create the molecule and box
    self.ready = False
    self.orb = -10
    self._new_box(new)
    self._new_mol(new)
    # Generate list of spins
    self.spin = 'alpha'
    self.spinlist = ['alpha']
    maxocc = 2.0
    if (len(new.MO_b) > 0):
      self.spinlist.append('beta')
      maxocc = 1.0
    self.new_spin(self.spin)
    self.ready = True
    # Generate list of irreps
    # Remove irrep if there's only one and always add an item "All"
    self.sym = ''
    self.symlist = []
    for o in new.MO + new.MO_b:
      if (o['sym'] not in self.symlist):
        self.symlist.append(o['sym'])
    if ('z' in self.symlist):
      self.symlist.remove('z')
    if (len(self.symlist) > 1):
      self.nosym = False
    else:
      self.nosym = True
      if (len(self.symlist) == 1):
        del self.symlist[0]
    self.symlist.insert(0, 'All')
    self.sym = 'All'
    # Generate list of orbitals (for notes)
    self.notes = []
    for i,orb in enumerate([j for i in izip_longest(new.MO, new.MO_b) for j in i]):
      if (orb is None):
        continue
      if ('label' in orb):
        self.notes.append(OrbInList(name=orb['label']))
      else:
        if (i%2 == 0):
          num = '{0}'.format(i/2+1)
        else:
          num = '{0}b'.format(i/2+1)
        if (self.nosym):
          self.notes.append(OrbInList(name='#{0} {1:.4f} {2}'.format(num, orb['ene'], orb['type'])))
        else:
          self.notes.append(OrbInList(name='#{0} [{1}] {2:.4f} {3}'.format(num, orb['sym'], orb['ene'], orb['type'])))
    # Select initial orbital
    minene = -np.inf
    orb = -10
    for i,o in enumerate(self.MO):
      if ((o['occup'] >= maxocc/2) and (o['ene'] >= minene)):
        orb = i+1
        minene = o['ene']
    if (orb < 0):
      orb = 1
    self.orb = orb

  # When changing the selected spin, switch the set of visible MOs
  @on_trait_change('spin')
  def new_spin(self, new):
    if (new == 'alpha'):
      self.MO = self.orbitals.MO
    elif (new == 'beta'):
      self.MO = self.orbitals.MO_b
    # Make sure the list is updated and the orbital redrawn
    r = self.ready
    self.ready = False
    self.new_sym(self.sym)
    self.ready = r
    self.update_grid()

  @on_trait_change('sym')
  def new_sym(self, new):
    if (new == ''):
      return
    # Generate list of orbitals to select from
    if (new == 'All'):
      self.orblist = {i+1:self.orb_to_list(i+1, o) for i,o in enumerate(self.MO)}
      if (not self.isGrid):
        self.orblist[0] = '0000:Density'
        # unfortunately the "label" is not sorted numerically, so it doesn't match
        if (len(self.spinlist) > 1):
          self.orblist[-1] = '-999:Spin density'
        self.orblist[-2] = '-998:Laplacian (numerical)'
      return
    n = self.symlist.index(new)
    self.orblist = {i+1:self.orb_to_list(i+1, o) for i,o in enumerate(self.MO) if (o['sym'] == new)}
    # Select new orbital if out of range
    s = self.MO[self.orb-1]['sym']
    if (s != new):
      ls = [o['sym'] for o in self.MO]
      lo = ls[:self.orb].count(s)
      c = 0
      for i,o in enumerate(self.MO):
        if (o['sym'] == new):
          c += 1
          if (c == lo):
            self.orb = i+1
            return
      self.orb = ls.index(new)+1

  def _new_box(self, orbitals):
    # Center molecule and compute max/min extent (with clearance)
    clearance = 4.0
    xyz = np.array([c['xyz'] for c in orbitals.centers])
    extent = np.array([np.amin(xyz, axis=0), np.amax(xyz, axis=0)])
    self.edge = np.ceil(extent[1]-extent[0]+2*clearance).tolist()
    # Force updating even if edge didn't change
    self.rebuild_grid()

  @on_trait_change('edge, ngrid')
  def rebuild_grid(self):
    if (self.isGrid):
      # For precomputed grids, just take the defined grid
      lims = np.array([self.orbitals.orig, self.orbitals.end])
      ngrid = [i*1j for i in self.orbitals.ngrid]
    else:
      # Parse the edge value to a 3-item list
      edge = self.edge[:]
      if (len(edge) == 0):
        edge.append(5.0)
      while (len(edge) < 3):
        edge.append(edge[-1])
      edge = edge[0:3]
      lims = np.array([[-0.5*x for x in edge], [0.5*x for x in edge]])
      lims += self.orbitals.geomcenter
      # Get the actual number of points according to the maximum set on the UI
      dim = [abs(x-y) for x,y in zip(lims[1], lims[0])]
      size = max(dim)/(self.ngrid-1)
      if (size == 0.0):
        size = 1.0
      ngrid = [min(int(np.ceil(x/size))+1,self.ngrid)*1j for x in dim]
    self.bxyz = [i for i in np.mgrid[lims[0,0]:lims[1,0]:2j, lims[0,1]:lims[1,1]:2j, lims[0,2]:lims[1,2]:2j]]
    self.xyz = [i for i in np.mgrid[lims[0,0]:lims[1,0]:ngrid[0], lims[0,1]:lims[1,1]:ngrid[1], lims[0,2]:lims[1,2]:ngrid[2]]]

  @on_trait_change('bxyz')
  def update_box(self, new):
    self.scene.disable_render = True
    x, y, z = (new[0].ravel(), new[1].ravel(), new[2].ravel())
    if (self.cube is None):
      corners = self.scene.mlab.pipeline.scalar_scatter(x, y, z, np.zeros_like(x))
      corners.mlab_source.dataset.lines = [[0, 1, 3, 2, 0], [4, 5, 7, 6, 4], [0, 4], [1, 5], [2, 6], [3, 7]]
      self.cube = self.scene.mlab.pipeline.surface(corners, line_width=1, color=(1, 1, 1), opacity=0.3, reset_zoom=False)
      if (self.isGrid):
        self.cube.actor.actor.poke_matrix(self.orbitals.transform)
        self.cube.update_pipeline()
    self.show_box(self.box)
    self.cube.mlab_source.points = np.vstack([x, y, z]).T
    self.scene.disable_render = False

  @on_trait_change('box')
  def show_box(self, new):
    if (self.cube is not None):
      self.cube.visible = new

  def _new_mol(self, new):
    self.scene.disable_render = True
    if (self.mol is not None):
      self.mol.remove()
    for a in self.atomnames:
      a.remove()
    xyz = np.array([c['xyz'] for c in new.centers])
    r = np.array([c['Z'] for c in new.centers])
    # Assign colors
    s = np.arange(len(r))
    colors = [cpk(c) for c in r]
    # Assign radii
    try:
      r = np.cbrt(r)
    except:
      r = np.power(r, 1.0/3)
    r[r<0.5] = 0.5
    while (len(colors) < 2):
      colors.append(cpk(0))
    self.mol = self.scene.mlab.quiver3d(xyz[:,0], xyz[:,1], xyz[:,2], r, r, r, scalars=s, mode='sphere', resolution=20, scale_factor=0.2)
    self.mol.glyph.glyph.clamping = False
    self.mol.glyph.glyph_source.glyph_source.center = [0, 0, 0,]
    self.mol.glyph.color_mode = 'color_by_scalar'
    self.mol.module_manager.scalar_lut_manager.lut.table = colors
    self.show_nuc(self.nuc)
    self.atomnames = []
    for c in new.centers:
      self.atomnames.append(self.scene.mlab.text(c['xyz'][0], c['xyz'][1], c['name'], z=c['xyz'][2]))
      self.atomnames[-1]._property.justification = 'centered'
      self.atomnames[-1]._property.vertical_justification = 'centered'
      self.atomnames[-1]._property.shadow = True
      self.atomnames[-1]._property.color = (0,0,0)
      self.atomnames[-1]._property.bold = True
      self.atomnames[-1].actor.text_scale_mode = 'none'
    self.show_lab(self.lab)
    self.scene.disable_render = False

  @on_trait_change('nuc')
  def show_nuc(self, new):
    if (self.mol is not None):
      self.mol.visible = new

  @on_trait_change('lab')
  def show_lab(self, new):
    self.scene.disable_render = True
    for a in self.atomnames:
      a.visible = new
    self.scene.disable_render = False

  @on_trait_change('xyz')
  def update_cache(self, new):
    if (self.orbitals is None):
      return
    if (self.cache_file is not None):
      del self.cache_file
    ngrid = new[0].shape
    if (self.isGrid):
      self.cache_file = None
    else:
      self.cache_file = np.memmap(os.path.join(self.tmpdir, '{0}.cache'.format(__name__.lower())), dtype='float32', mode='w+', shape=(sum(self.orbitals.N_bas), ngrid[0], ngrid[1], ngrid[2]))
      self.cache_file[:,0,0,0] = np.nan
    self.grid_changed = True
    self.update_grid()

  @on_trait_change('orb')
  def update_grid(self):
    if (not self.ready):
      return
    if (self.isGrid):
      self.status = 'Reading...'
    else:
      self.status = 'Computing...'
    self.ready = False
    ComputeGrid(self, cache=self.cache_file).start()

  @on_trait_change('notes:selected')
  def update_density(self):
    if (self.orb < 1):
      self.update_grid()

  def _format_num(self, n, t):
    s = '{0:.1e}'.format(n)
    num, exp = s.split('e')
    num = float(num)
    exp = int(exp)
    if (t == 'down'):
      if (float(s) > n):
        num -= 0.1
    elif (t == 'up'):
      if (float(s) < n):
        num += 0.1
    if (abs(num) < 1.0):
      exp -= 1
      num *= 10.0
    elif (abs(num) >= 10.0):
      exp += 1
      num /= 10.0
    num = '{0:.1f}'.format(num)
    s = num
    if (exp != 0):
      s += 'e{0}'.format(exp)
    return s

  def _assign_vol(self, data):
    self.vol = data

  @on_trait_change('vol')
  def update_vol(self, new):
    self.scene.disable_render = True
    maxval = np.nan_to_num(new).max()
    minval = np.nan_to_num(new).min()
    self.range = [minval < 0, maxval > 0]
    if (maxval*minval < 0):
      maxval = max(abs(minval), abs(maxval))
      minval = 0.0
    else:
      minval, maxval = (min(abs(minval), abs(maxval)), max(abs(minval), abs(maxval)))
    if (minval == 0):
      minval = 1e-5*maxval
    if (abs(maxval)+abs(minval) > 0):
      minval = self._format_num(minval, 'down')
      maxval = self._format_num(maxval, 'up')
      self.minval, self.maxval = (minval, maxval)
    # Using this instead of "reset" to avoid error messages from vtk
    if (self.grid_changed):
      if (self.surf is not None):
        self.surf.remove()
        self.surf = None
      if (self.node is not None):
        self.node.remove()
        self.node = None
    eps = np.finfo(np.float).eps
    # Create orbital isosurface
    if (self.surf is None):
      field = self.scene.mlab.pipeline.scalar_field(self.xyz[0], self.xyz[1], self.xyz[2], new)
      self.surf = self.scene.mlab.pipeline.iso_surface(field, contours=[], color=(0.675, 0.741, 0.816), vmin=-eps, vmax=eps)
      self.surf.module_manager.scalar_lut_manager.lut.table = [[222, 119, 61, 255], [255, 255, 255, 255], [204, 222, 61, 255]]
      if (self.isGrid):
        self.surf.actor.actor.poke_matrix(self.orbitals.transform)
        self.surf.update_pipeline()
    else:
      self.surf.mlab_source.set(scalars=new)
      self.surf.contour.contours = []
    self.surf.actor.mapper.scalar_visibility = (self.orb != 0)
    self.update_surf(self.val)
    self.show_surf(self.surface)
    # Create nodal surface. Reset contours to force redraw
    if (self.node is None):
      field = self.scene.mlab.pipeline.scalar_field(self.xyz[0], self.xyz[1], self.xyz[2], new)
      self.node = self.scene.mlab.pipeline.iso_surface(field, contours=[], color=(1.0, 1.0, 1.0), opacity=0.5, vmin=eps, vmax=eps)
      if (self.isGrid):
        self.node.actor.actor.poke_matrix(self.orbitals.transform)
        self.node.update_pipeline()
    else:
      self.node.mlab_source.set(scalars=new)
      self.node.contour.contours = []
    if (all(self.range)):
      self.node.contour.contours = [0]
    self.show_node(self.nodes)
    self.update_background()
    if (self.grid_changed):
      self.scene.reset_zoom()
      self.grid_changed = False
    self.scene.disable_render = False
    self.ready = True
    self.status = 'Done'

  @on_trait_change('surface')
  def show_surf(self, new):
    if (self.surf is not None):
      self.surf.visible = new

  @on_trait_change('val')
  def update_surf(self, new):
    if (self.surf is not None):
      volmin = np.nan_to_num(self.vol).min()
      volmax = np.nan_to_num(self.vol).max()
      if (all(self.range)):
        self.surf.contour.contours = [-new, new]
      elif (self.range[0]):
        self.surf.contour.contours = [-new]
      elif (self.range[1]):
        self.surf.contour.contours = [new]

  @on_trait_change('nodes')
  def show_node(self, new):
    if (self.node is not None):
      self.node.visible = new

  def update_background(self):
    MO = self.MO[self.orb-1]
    if (self.orb < 1):
      tp = ''
    else:
      try:
        if ('newtype' in MO):
          tp = MO['newtype']
        else:
          tp = MO['type']
      except:
        tp = ''
    if (tp == 'F'):
      self.scene.background = (0.449, 0.448, 0.646) # CIELab(50,12,-27)
    elif (tp == 'I'):
      self.scene.background = (0.711, 0.704, 0.918) # CIELab(75,12,-27)
    elif (tp == '1'):
      self.scene.background = (0.605, 0.759, 0.682) # CIELab(75,-17,5.5)
    elif (tp == '2'):
      self.scene.background = (0.569, 0.775, 0.569) # CIELab(75,-27.5,21)
    elif (tp == '3'):
      self.scene.background = (0.735, 0.737, 0.532) # CIELab(75,-8.5,26.5)
    elif (tp == 'S'):
      self.scene.background = (0.883, 0.673, 0.670) # CIELab(75,19.5,8)
    elif (tp == 'D'):
      self.scene.background = (0.609, 0.417, 0.416) # CIELab(50,19.5,8)
    else:
      self.scene.background = (0.466, 0.466, 0.466) # CIELab(50,0,0)
    # Update the description text
    if (self.orb == 0):
      text = 'Density'
    elif (self.orb == -1):
      text = 'Spin density'
    else:
      if ('label' in MO):
        text = MO['label']
      else:
        if (self.nosym):
          sym = ''
        else:
          m = [o['sym'] for o in self.MO[:self.orb]].count(MO['sym'])
          sym = ' [{0}, {1}]'.format(MO['sym'], m)
        text = '#{0}{1}   E: {2:.6f}   occ: {3:.4f}   {4}'.format(self.orb, sym, MO['ene'], MO['occup'], tp)
    # Update the counts
    irrep = [i for i in self.orbitals.irrep if (i != 'z')]
    nsym = len(irrep)
    types = {'F':[0]*nsym, 'I':[0]*nsym, '1':[0]*nsym, '2':[0]*nsym, '3':[0]*nsym, 'S':[0]*nsym, 'D':[0]*nsym}
    for o in self.MO:
      try:
        sym = irrep.index(o['sym'])
        if ('newtype' in o):
          tp = o['newtype']
        else:
          tp = o['type']
        if (tp in types):
          types[tp][sym] += 1
      except:
        pass
    text += '\n' + '   '.join(['{0}: {1}'.format(i, ','.join(map(str, types[i]))) for i in ['F', 'I', '1', '2', '3', 'S', 'D'] if (sum(types[i]) > 0)])
    if (self.counts is None):
      self.counts = self.scene.mlab.text(0.01, 0.01, text)
      self.counts._property.bold = True
      self.counts._property.background_opacity = 0.2
      self.counts.actor.text_scale_mode = 'none'
    else:
      self.counts.text = text

  @on_trait_change('notelist')
  def list_orbitals(self, new):
    if (self.shownotes is None):
      self.shownotes = self.edit_traits(view=orbital_list)

  # Write the current orbital in cube format
  @on_trait_change('save_cube')
  def write_cube(self, *args):
    if (self.vol is None):
      return
    dlg = FileDialog(title='Save cube', action='save as')
    if (dlg.open() == OK):
      ngrid = self.vol.shape
      grid = [(x[-1,-1,-1]-x[0,0,0])/(n-1) for x,n in zip(self.xyz, ngrid)]
      with open(dlg.path, 'w') as f:
        f.write('File generated by {0} from {1}\n'.format(__name__, self.file))
        f.write('{0}\n'.format(self.orblist[self.orb].split(':', 1)[1]))
        orig = [x[0,0,0] for x in self.xyz]
        if (self.isGrid):
          orig.append(1.0)
          orig = self.orbitals.transform.multiply_point(orig)[0:3]
        f.write('{0:5d} {1:11.6f} {2:11.6f} {3:11.6f}\n'.format(len(self.orbitals.centers), *orig))
        axis = [grid[0], 0, 0]
        if (self.isGrid):
          axis.append(0.0)
          axis = self.orbitals.transform.multiply_point(axis)[0:3]
        f.write('{0:5d} {1:11.6f} {2:11.6f} {3:11.6f}\n'.format(ngrid[0], *axis))
        axis = [0, grid[1], 0]
        if (self.isGrid):
          axis.append(0.0)
          axis = self.orbitals.transform.multiply_point(axis)[0:3]
        f.write('{0:5d} {1:11.6f} {2:11.6f} {3:11.6f}\n'.format(ngrid[1], *axis))
        axis = [0, 0, grid[2]]
        if (self.isGrid):
          axis.append(0.0)
          axis = self.orbitals.transform.multiply_point(axis)[0:3]
        f.write('{0:5d} {1:11.6f} {2:11.6f} {3:11.6f}\n'.format(ngrid[2], *axis))
        for c in self.orbitals.centers:
          f.write('{0:5d} {0:11.6f} {1:11.6f} {2:11.6f} {3:11.6f}\n'.format(c['Z'], *c['xyz']))
        for x in self.vol:
          for y in x:
            f.write('\n'.join(wrap_list(y, 6, '{:13.5E}')))
            f.write('\n')

  @on_trait_change('save_hdf5')
  def write_hdf5(self, *args):
    if (self.orbitals.type != 'hdf5'):
      return
    dlg = FileDialog(title='Save HDF5', action='save as')
    if (dlg.open() == OK):
      self.orbitals.write_hdf5(dlg.path)

  @on_trait_change('save_orbs')
  def write_inporb(self, *args):
    if (not self.haveOrb):
      return
    dlg = FileDialog(title='Save InpOrb', action='save as')
    if (dlg.open() == OK):
      if (self.orbitals.inporb == 'gen'):
        self.orbitals.create_inporb(dlg.path)
      else:
        self.patch_inporb(dlg.path)

  # Copy an InpOrb file, changing header and index section
  def patch_inporb(self, outfile):
    nMO = [0 for i in self.symlist if (i not in  ['All', 'z'])]
    for o in self.orbitals.MO:
      try:
        nMO[self.symlist.index(o['sym'])-1] += 1
      except:
        pass
    index = create_index(self.orbitals.MO, self.orbitals.MO_b, nMO)
    if (index is None):
      return
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
            fo.write('* File generated by {0} from {1}\n'.format(__name__, self.file))
            line = f.readline()
            fo.write(line)
            line = f.readline()
            fo.write(line)
            line = f.readline()
            fo.write(line)
            if (map(int, line.split()) != nMO):
              error(message='Wrong number of orbitals', title='Error', buttons=['OK'])
              return
            line = f.readline()
            fo.write(line)
            line = f.readline()
          # Stop at the index section
          if (line.startswith('#INDEX')):
            fo.write(line)
            break
        # Write the new index section
        fo.write('\n'.join(index))
        fo.write('\n')

#-------------------------------------------------------------------------------

class KeyHandler(Handler):

  def show_help(self, *args):
    message = '''<p>
                 <b>{0}</b> is an orbital viewer ideal for OpenMolcas. {0} can open files in HDF5, Molden, Luscus, grid (ascii) and cube (formatted) formats;
                 after loading an HDF5 file, it can also read files in InpOrb (2.0 or later) format. It can modify orbital types and save the
                 result in HDF5 and InpOrb format, or save the volume data in cube format.
                 </p>
                 <p>
                 <u><i>Hotkeys</i></u><br>
                 <b>F1</b>: Show this help<br>
                 <b>q</b>: Quit<br>
                 <b>Ctrl+l</b>: Load a file<br>
                 <b>Ctrl+h</b>: Save orbitals and basis in HDF5 format<br>
                 <b>Ctrl+o</b>: Save orbitals in InpOrb format<br>
                 <b>Ctrl+c</b>: Save current orbital in cube format<br>
                 <b>Shift+Page up</b>/<b>down</b>: Change selected irrep<br>
                 <b>Page up</b>/<b>down</b>: Change selected orbital<br>
                 <b>a</b>: Switch spin<br>
                 <b>v</b>/<b>V</b>: Decrease/increase isosurface value<br>
                 <b>o</b>: Toggle display of isosurface<br>
                 <b>n</b>: Toggle display of nodal surface<br>
                 <b>m</b>: Toggle display of nuclei<br>
                 <b>z</b>: Toggle display of atom names<br>
                 <b>b</b>: Toggle display of grid box<br>
                 <b>Ctrl+f</b>/<b>i</b>/<b>1</b>/<b>2</b>/<b>3</b>/<b>s</b>/<b>d</b>: Change type of current orbital<br>
                 (<i>frozen</i>/<i>inactive</i>/<i>RAS1</i>/<i>RAS2</i>/<i>RAS3</i>/<i>secondary</i>/<i>deleted</i>)<br>
                 <b>l</b>: Open orbital annotation window<br>
                 </p>

                 <p>Other keys interpreted by Mayavi:<br>
                 <a href="http://docs.enthought.com/mayavi/mayavi/application.html#keyboard-interaction">docs.enthought.com/mayavi/mayavi/application.html</a></p>'''.format(__name__)
    msg = Message(message=message)
    msg.edit_traits(view=View([Item('message', editor=HTMLEditor(), height=400, width=600, show_label=False)],
                              title='Hotkeys', buttons=['OK'], kind='nonmodal', icon=app_icon))

  def prev_sym(self, info):
    if (info.object.orbitals is None):
      return
    syms = info.object.symlist
    idx = info.object.symlist.index(info.object.sym)
    info.object.sym = syms[max(idx-1, 0)]

  def next_sym(self, info):
    if (info.object.orbitals is None):
      return
    syms = info.object.symlist
    idx = syms.index(info.object.sym)
    info.object.sym = syms[min(idx+1, len(syms)-1)]

  def prev_orb(self, info):
    if (info.object.orbitals is None):
      return
    orbs = sorted(info.object.orblist.keys())
    idx = orbs.index(info.object.orb)
    info.object.orb = orbs[max(idx-1, 0)]

  def next_orb(self, info):
    if (info.object.orbitals is None):
      return
    orbs = sorted(info.object.orblist.keys())
    idx = orbs.index(info.object.orb)
    info.object.orb = orbs[min(idx+1, len(orbs)-1)]

  def switch_spin(self, info):
    if (info.object.orbitals is None):
      return
    info.object.spin = info.object.spinlist[info.object.spinlist.index(info.object.spin)-1]

  def dec_val(self, info):
    if (not info.object.surface):
      return
    info.object.val = max(info.object.val/1.01, info.object.minval)

  def inc_val(self, info):
    if (not info.object.surface):
      return
    info.object.val = min(info.object.val*1.01, info.object.maxval)

  def toggle_surface(self, info):
    if (info.object.surf is None):
      return
    info.object.surface = not info.object.surface

  def toggle_nodes(self, info):
    if (info.object.node is None):
      return
    info.object.nodes = not info.object.nodes

  def toggle_nuc(self, info):
    if (info.object.mol is None):
      return
    info.object.nuc = not info.object.nuc

  def toggle_lab(self, info):
    if (info.object.mol is None):
      return
    info.object.lab = not info.object.lab

  def toggle_box(self, info):
    if (info.object.cube is None):
      return
    info.object.box = not info.object.box

  def make_F(self, info):
    self._change('F', info)

  def make_I(self, info):
    self._change('I', info)

  def make_1(self, info):
    self._change('1', info)

  def make_2(self, info):
    self._change('2', info)

  def make_3(self, info):
    self._change('3', info)

  def make_S(self, info):
    self._change('S', info)

  def make_D(self, info):
    self._change('D', info)

  def _change(self, tp, info):
    i = info.object.orb
    try:
      # Instead of rewriting the labels, modify them
      o = info.object.MO[i-1]
      label = info.object.orblist[i]
      if (('newtype' in o) and (o['newtype'] != o['type'])):
        label = label[:-3]
      o['newtype'] = tp
      if (tp != o['type']):
        label = label + '->' + tp
      info.object.orblist[i] = label
      label = info.object.notes[i-1].name[:-1] + tp
      info.object.notes[i-1].name = label
      info.object.update_background()
    except:
      pass

  # Actions for selecting orbitals
  # The first change (if any) is delayed until the end,
  # in order for the notification to trigger a density redraw

  def select_none(self, info):
    if (info.object.orbitals is None):
      return
    info.object.ready = False
    first = None
    for i in info.object.notes:
      if ((first is None) and i.selected):
        first = i
      else:
        i.selected = False
    info.object.ready = True
    if (first is not None):
      first.selected = False

  def select_active(self, info):
    if (info.object.orbitals is None):
      return
    info.object.ready = False
    first = None
    for i,o in zip(info.object.notes, [j for i in izip_longest(info.object.orbitals.MO, info.object.orbitals.MO_b) for j in i if (j is not None)]):
       tp = o['type']
       if ('newtype' in o):
         tp = o['newtype']
       if (tp in ['1', '2', '3']):
         if ((first is None) and not i.selected):
           first = i
         else:
           i.selected = True
       else:
         if ((first is None) and i.selected):
           first = i
         else:
           i.selected = False
    info.object.ready = True
    if (first is not None):
      first.selected = not first.selected

  def select_all(self, info):
    if (info.object.orbitals is None):
      return
    info.object.ready = False
    first = None
    for i in info.object.notes:
      if ((first is None) and not i.selected):
        first = i
      else:
        i.selected = True
    info.object.ready = True
    if (first is not None):
      first.selected = True

  def close_list(self, info):
    info.object.shownotes = None
    self._on_close(info)

  def close_main(self, info):
    if (info.object.shownotes):
      info.object.shownotes.owner.close()
    self._on_close(info)

#-------------------------------------------------------------------------------

keys = KeyBindings(
  KeyBinding(binding1='F1', description='Help', method_name='show_help'),
  KeyBinding(binding1='q', description='Quit', method_name='_on_close'),
  KeyBinding(binding1='Ctrl-l', description='Load file', method_name='set_file'),
  KeyBinding(binding1='Ctrl-h', description='Save HDF5', method_name='write_hdf5'),
  KeyBinding(binding1='Ctrl-o', description='Save orbitals', method_name='write_inporb'),
  KeyBinding(binding1='Ctrl-c', description='Save cube', method_name='write_cube'),
  KeyBinding(binding1='v', description='Decrease value', method_name='dec_val'),
  KeyBinding(binding1='V', description='Increase value', method_name='inc_val'),
  KeyBinding(binding1='Shift-page up', description='Previous irrep', method_name='prev_sym'),
  KeyBinding(binding1='Shift-page down', description='Next irrep', method_name='next_sym'),
  KeyBinding(binding1='Page Up', description='Previous orbital', method_name='prev_orb'),
  KeyBinding(binding1='Page Down', description='Next orbital', method_name='next_orb'),
  KeyBinding(binding1='a', description='Switch spin', method_name='switch_spin'),
  KeyBinding(binding1='o', description='Toggle surface', method_name='toggle_surface'),
  KeyBinding(binding1='n', description='Toggle nodes', method_name='toggle_nodes'),
  KeyBinding(binding1='m', description='Toggle nuclei', method_name='toggle_nuc'),
  KeyBinding(binding1='z', description='Toggle labels', method_name='toggle_lab'),
  KeyBinding(binding1='b', description='Toggle box', method_name='toggle_box'),
  KeyBinding(binding1='Ctrl-f', description='Make frozen', method_name='make_F'),
  KeyBinding(binding1='Ctrl-i', description='Make inactive', method_name='make_I'),
  KeyBinding(binding1='Ctrl-1', description='Make RAS1', method_name='make_1'),
  KeyBinding(binding1='Ctrl-2', description='Make RAS2', method_name='make_2'),
  KeyBinding(binding1='Ctrl-3', description='Make RAS3', method_name='make_3'),
  KeyBinding(binding1='Ctrl-s', description='Make secondary', method_name='make_S'),
  KeyBinding(binding1='Ctrl-d', description='Make deleted', method_name='make_D'),
  KeyBinding(binding1='l', description='List orbitals', method_name='list_orbitals')
)

#-------------------------------------------------------------------------------

# The main interface
main_view = View(
  Group(
    Group(
      Item('load_button', label='Load file', show_label=False, tooltip='Load a file to display'),
      Item('file', style='readonly', show_label=True, springy=True, tooltip='Loaded file'),
      Item('save_hdf5', label='Save HDF5', show_label=False, visible_when='orbitals.type == "hdf5"',
           tooltip='Save orbitals and basis in HDF5 format'),
      Item('save_orbs', label='Save orbitals', show_label=False, visible_when='haveOrb',
           tooltip='Save orbitals in InpOrb format'),
      Item('save_cube', label='Save cube', show_label=False, visible_when='surf',
           tooltip='Save current orbital in cube format'),
      orientation='horizontal'
    ),
    Item('scene', editor=SceneEditor(scene_class=MayaviScene), height=600, width=800, show_label=False),
    Group(
      Item('sym', label='Irrep', editor=EnumEditor(name='symlist'), width=60, enabled_when='ready and not nosym', visible_when='not nosym',
           tooltip='Select irrep to filter'),
      Item('orb', label='Orbital', editor=EnumEditor(name='orblist'), width=250, enabled_when='ready',
           tooltip='Select orbital to display'),
      Item('spin', editor=EnumEditor(name='spinlist'), show_label=False, enabled_when='orb > 0', visible_when='len(spinlist) > 1',
           tooltip='Select spin to display'),
      '25',
      Item('notelist', label='List', show_label=False, enabled_when='not shownotes',
           tooltip='Show list of orbitals with notes'),
      orientation='horizontal'
    ),
    Item('val', label='Value', editor=RangeEditor(mode='logslider', low_name='minval', high_name='maxval', label_width=50, format='%.3g'), enabled_when='surface and surf',
         tooltip='Value for isosurfaces'),
    Group(
      Item('surface', label='Surface', enabled_when='surf', tooltip='Display orbital surface'),
      Item('nodes', label='Nodes', enabled_when='node', tooltip='Display nodal surface'),
      Item('nuc', label='Nuclei', enabled_when='mol', tooltip='Display nuclei'),
      Item('lab', label='Names', enabled_when='mol', tooltip='Display atom names'),
      Item('box', label='Box', enabled_when='cube', tooltip='Display grid box'),
      Item('edge', label='Box size', editor=CSVListEditor(auto_set=False, enter_set=True), enabled_when='ready', visible_when='not isGrid',
           tooltip='Grid box size in bohr: one or three comma-separated values'),
      Item('ngrid', label='Grid points', editor=TextEditor(auto_set=False, enter_set=True, evaluate=int), enabled_when='ready', visible_when='not isGrid',
           tooltip='Number of grid points along the largest dimension'),
      orientation='horizontal',
    ),
    orientation='vertical',
  ),
  key_bindings = keys,
  handler = KeyHandler,
  buttons = [Action(name='Help', action='show_help', tooltip='Show help'),
             Action(name='Close', action='close_main', tooltip='Close window')],
  title = __name__,
  statusbar = StatusItem(name='status'),
  resizable = True
)

# List of orbitals with notes and density selection
orbital_list = View(
  Item('notes',
       editor = TableEditor(columns=[ObjectColumn(name='name', label='Orbital', width=150, editable=False),
                                     CheckboxColumn(name='selected', label='Density', width=50),
                                     ObjectColumn(name='note', label='Note')],
                          auto_size=False),
       show_label=False),
  buttons = [Action(name='None', action='select_none', tooltip='Deselect all orbitals for density'),
             Action(name='Active', action='select_active', tooltip='Select only active orbitals for density'),
             Action(name='All', action='select_all', tooltip='Select all orbitals for density'),
             Action(name='Close', action='close_list', tooltip='Close window')],
  handler = KeyHandler,
  height = 600,
  width = 400,
  title = 'Orbital list',
  kind = 'live',
  resizable = True
)

#===============================================================================

window = Viewer()
try:
  window.file = os.path.abspath(sys.argv[1])
except IndexError:
  pass
app_icon = window.icon
window.configure_traits(view=main_view)
