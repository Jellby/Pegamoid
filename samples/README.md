Samples
-------

This directory contains some example files that can be directly opened with
Pegamoid (note that to open the `.*Orb` files, the corresponding `.h5` file
must have been loaded first). The inputs used to generate these files can be
found in the ``input`` directory. These calculations are meant to demonstrate
the features of Pegamoid, and not as a scientifically sound reference.

Some of the features to pay attention to:

* ``acrolein.guessorb.h5``:
  Large basis set (828 functions, 1284 primitives), including h functions.

* ``acrolein.UhfOrb``:
  Alpha and beta orbitals.

* ``azulene.lus``:
  Luscus file with a subset of all orbitals.

* ``cyclopentadienyl.scf.molden``:
  Alpha and beta orbitals.

* ``ferrocene.caspt2.h5``:
  Symmetry-related atoms, CASPT2 orbitals.

* ``NH3.cube``:
  Cube file with a non-orthogonal grid.

* ``NiCO4.scf.h5``:
  Symmetry, ghost atoms, mixed Cartesian, spherical harmonics and contaminant functions.

* ``NO.rasscf.h5``:
  SA-CASSCF spin densities, with symmetry.

* ``O2.scf.h5``:
  Natural UHF orbitals.

* ``QMMM.scf.h5``
  MM atoms (without basis functions), box fitted to atoms with basis functions.

* ``uracil.LocOrb``:
  Localized orbitals, easy to choose an active space.

* ``uracil.rasscf.h5``:
  RAS1 and RAS3 orbitals, natural transition orbitals.

* ``water.grid``:
  Grid file with all orbitals (minimal basis).
