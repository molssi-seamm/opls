# -*- Coding: utf-8 -*-
"""Helper class needed for the stevedore integration. Needs to provide
a description() method that returns a dict containing a description of
this node, and a factory() method for creating the graphical and non-graphical
nodes."""

import logging
import pkg_resources
import pprint

logger = logging.getLogger(__name__)


class OPLS(object):
    my_description = {
        'description':
        'An interface for the setup and control of the forcefield',
        'forcefields':
        ['united atom', 'all-atom v1']
    }

    def __init__(self):
        """Initialize this helper class, which is used by
        the application via stevedore to get information about
        this group of forcefields
        """
        self.ff = None
        self.forcefield = None
        self._filepath = None
        
    @property
    def filepath(self):
        """The path to the forcefield file"""
        if self._filepath is None:
            # Default forcefield file
            self._filepath = pkg_resources.resource_filename(
                __name__, 'data/opls.frc')
            logger.info('OPLS forcefield file set to default: {}'
                        .format(self._filepath))
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        if self._filepath is not None:
            self.ff = None
            self.forcefield = None
        self._filepath = filepath

    def description(self):
        """Return a description of what this extension does
        """
        return OPLS.my_description

    def read_forcefield(self, ff_variant='united atom'):
        """Read the requested variant of the forcefield"""
        import forcefield

        self.forcefield = ff_variant
        self.ff = forcefield.Forcefield(filename=self.filepath,
                                        fftype='Biosym')
        self.ff.initialize_biosym_forcefield(forcefield=ff_variant)
        return self.ff
        
    def atom_type(self, **kwargs):
        """Add or correct the atom types on the structure"""
        import forcefield
        import molssi_workflow
        import molssi_util

        structure = molssi_workflow.data.structure
        ff = molssi_workflow.data.forcefield

        smiles = molssi_util.smiles.from_molssi(structure)
        logger.debug('Atom typing -- smiles = ' + smiles)
        ff_assigner = forcefield.FFAssigner(ff)
        atom_types = ff_assigner.assign(smiles, add_hydrogens=False)
        logger.info('Atom types: ' + ', '.join(atom_types))
        atoms = structure['atoms']
        if 'atom_types' not in atoms:
            atoms['atom_types'] = {}
        atoms['atom_types'][self.forcefield] = atom_types

        return atom_types

    def create_eex(self, **kwargs):
        """Generalized energy expression"""
        import molssi_workflow

        structure = molssi_workflow.data.structure

        eex = self.ff.energy_expression(structure, style='LAMMPS')
        logger.debug('energy expression:\n' + pprint.pformat(eex))

        return eex
