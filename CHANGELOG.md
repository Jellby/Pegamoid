**2.12** (2024-08-29)

Bug fixes:
* Print traceback in case of Qt loading error
* Support for numpy lacking numpy.math

**2.11** (2024-04-04)

New features:
* Antialiasing function to reduce pixelation
* Allow configuring the scene lights
* Support textures like IboView, three presets added (use use the second lights preset)

Bug fixes:
* Reading sp functions in Molden files
* Restoring saved "main" background color

**2.10** (2024-02-28)

New features:
* Keyboard shortcut (Ctrl+R) for overwriting current file
* Show orbital type and title next to filename

Workaround:
* Allow disabling opacity for compatibility in some systems

**2.9** (2023-11-24)

Feature change:
* Orbital sorting is done based on occupation first

**2.8.4** (2023-10-13)

Bug fix:
* Reading Molden files without space after "=" signs

**2.8.3** (2023-08-31)

Bug fix:
* Deletion of cache files (caused issues on Windows)

**2.8.2** (2023-08-31)

Bug fixes:
* Correct detection of TDMs, no crash with 2 roots
* Deletion of density cache

**2.8.1** (2023-08-30)

Bug fix:
* QApplication.desktop is removed in Qt 6

**2.8** (2023-06-29)

New feature:
* Support loading desymmetrized InpOrb files (e.g. SO NTOs), on top of HDF5 files with symmetry

Bug fixes:
* Reading InpOrb files with fewer orbitals than basis functions
* Do not return an error when cancelling save dialogs

**2.7** (2023-02-02)

Bug fixes:
* Support numpy 1.24 (remove deprecated aliases)
* Reading Molden files with omitted (zero) MO coefficients

**2.6.4** (2022-11-01)

Bug fix:
* Reading cube files with no linebreaks in the inner loop

**2.6.3** (2022-10-03)

Bug fix:
* Fit grid button location

**2.6.2** (2022-04-07)

New feature:
* Allow choosing the background color and toggling the color-by-type feature

Workaround:
* Allow re-enabling the options panel if for some reason/bug it gets closed

**2.6.1** (2020-10-21)

Bug fix:
* WFA orbitals with python3

**2.6** (2020-09-15)

Bug fix:
* Basis function primitive coefficients are normalized after reading

**2.5.6** (2020-06-22)

New feature:
* Support for VTK 9.0

**2.5.5** (2020-05-12)

Bug fix:
* Parsing of Molden files with unreadable (starred) energies

**2.5.4** (2020-04-18)

New feature:
* Menu action for overwriting current file (HDF5/InpOrb formats)

Bug fixes:
* Overwriting InpOrb files
* Saving InpOrb from InpOrb (index block was not updated)
* Do not reset camera orientation when loading an InpOrb

**2.5.3** (2020-02-19)

Bug fixes:
* Parsing of Boolean values in config file
* Workaround for VTK bug/misfeature #17791 causing crazy bonds for uncommon elements

**2.5.2** (2020-02-07)

Bug fix:
* Reading of grid/cube/lus files with python3

**2.5.1** (2020-01-31)

New features:
* Keyboard shortcut to select natural UHF orbitals
* Option to hide atoms without basis functions (e.g. MM atoms)
* Density cache to reuse previously computed densities
* Environment variable to disable QtOpenGL

Bug fixes:
* Accept d/D as exponent marker (besides e/E)
* Fix patching of InpOrb files (with blank lines at the end)
* Fix for when there are no orbitals in drop-down list
* Keep atomic numbers within supported range

**2.5** (2019-11-18)

New features:
* Sort orbitals in drop-down list by energy and occupation (across irreps)
* Hide irrelevant orbitals from drop-down list (those not in spin/difference/transition densities)
* Read orbitals written by WFA
* Support densities (and orbitals) in RASSI files
* Transition and unrelaxed difference densities
* Separate alpha and beta orbitals if spin densities are available (also for difference and transition)
* Total number of electrons in densities

Bug fixes:
* Alignment of monoatomic structures
* Workaround for VTK bug #17715

**2.4.2** (2019-09-12)

Bug fixes:
* Fix writing of HDF5
* Write natural UHF orbitals too (if available)

**2.4.1** (2019-09-06)

Bug fixes:
* Fix reading color settings if not present in configuration file
* Fix transparency in PNG screenshots (in some Qt versions)
* Read Molden files with missing tags

**2.4** (2019-08-30)

New features:
* Display atoms with no basis functions (e.g. MM) as transparent balls and exclude them from box
* Options to fit and align box with molecule, manually or automatically on loading
* Improve Molden file reading
* Support two filenames in command line (useful for InpOrb files)

**2.3** (2019-07-25)

New features:
* Save and restore settings and window size/position
* Collapsible and detachable options panel
* Easier scratch configuration
* Allow overwriting current HDF5 file
* Add Fresnel-like transparency and presets

**2.2.2** (2019-05-25)

Bug fix:
* Keep grid fixed after computing Laplacian

**2.2.1** (2019-05-13)

Bug fix:
* Workaround for display issue on some PyQt5 systems

**2.2** (2019-04-23)

New features:
* Color/texture editor and presets
* Show box parameters for grid files
* Allow more control on scratch usage
* Allow interrupting long computations

**2.1.1** (2019-04-13)

Bug fix:
* Numpy compatibility improvement

**2.1** (2019-03-01)

New features:
* Support contaminant functions
* Balls & sticks representation

**2.0.2** (2019-01-21)

Bug fix:
* Correctly reset orbital type after changing it

**2.0.1** (2018-10-30)

Bug fix:
* Corrected electron density

**2.0** (2018-09-12)
* Rewritten to use Qt and VTK directly
* First version on PyPI (installable through `pip`)

New features:
* Density selection (state, difference, transition)
* Root selection
* Support UHF natural orbitals
* Numerical Laplacian
* Support for non-orthogonal grids
* Display atom labels
* Isosurface opacity
* Save image as PNG

**1.0** (2018-01-03)
* Initial public version, using Mayavi and TVTK
* Not available trough `pip`
