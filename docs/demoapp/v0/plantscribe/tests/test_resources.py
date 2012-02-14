"""

This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jan 9, 2012.
"""

from StringIO import StringIO
from everest.repository import REPOSITORIES
from everest.resources.interfaces import IResourceRepository
from everest.resources.io import dump_resource
from everest.resources.utils import get_root_collection
from everest.testing import ResourceTestCase
from pkg_resources import resource_filename # pylint: disable=E0611
from plantscribe.interfaces import ICustomer
from plantscribe.interfaces import IIncidence
from plantscribe.interfaces import IProject
from plantscribe.interfaces import ISite
from plantscribe.interfaces import ISpecies
from plantscribe.resources import CustomerMember
from plantscribe.resources import IncidenceMember
from plantscribe.resources import ProjectMember
from plantscribe.resources import SiteMember
from plantscribe.resources import SpeciesMember
from zope.component import getUtility as get_utility # pylint: disable=E0611,F0401

__docformat__ = 'reStructuredText en'
__all__ = []


def populate():
    for ifc, pkg_fn in ((ICustomer, 'data/customers.csv'),
                        (IProject, 'data/projects.csv'),
                        (ISite, 'data/sites.csv'),
                        (ISpecies, 'data/species.csv'),
                        (IIncidence, 'data/incidences.csv'),
                        ):
        fn = resource_filename('plantscribe', pkg_fn)
        rc_repo = get_utility(IResourceRepository, REPOSITORIES.ORM)
        rc_repo.load_representation(ifc, 'file://%s' % fn)


class PlantScribeResourcesTestCase(ResourceTestCase):
    package_name = 'plantscribe'
    ini_file_path = resource_filename('plantscribe', 'plantscribe.ini')
    ini_section_name = 'app:plantscribe'

    __populated = False

    def set_up(self):
        ResourceTestCase.set_up(self)
        populate()

    def test_get_customer(self):
        coll = get_root_collection(ICustomer)
        self.assert_true(len(coll), 2)
        mb = coll.get('smith-peter')
        self.assert_true(isinstance(mb, CustomerMember))
        self.assert_equal(mb.first_name, 'Peter')
        self.assert_equal(mb.last_name, 'Smith')
        self.assert_equal(len(mb.projects), 2)

    def test_get_project(self):
        coll = get_root_collection(IProject)
        self.assert_true(len(coll), 1)
        mb = coll.get('pond')
        self.assert_true(isinstance(mb, ProjectMember))
        self.assert_equal(mb.name, 'Pond')
        self.assert_true(isinstance(mb.customer, CustomerMember))

    def test_get_species(self):
        coll = get_root_collection(ISpecies)
        self.assert_true(len(coll), 6)
        mb = coll.get('caltha-palustris--l.')
        self.assert_true(isinstance(mb, SpeciesMember))
        self.assert_equal(mb.species_name, 'palustris')
        self.assert_equal(mb.genus_name, 'Caltha')
        self.assert_equal(mb.author, 'L.')

    def test_get_nested(self):
        coll = get_root_collection(IProject)
        mb = coll.get('pond')
        self.assert_equal(len(mb.sites), 2)
        site_mb = mb.sites.get('open-water')
        self.assert_true(isinstance(site_mb, SiteMember))
        incidence_mb = site_mb.incidences.get('utricularia-vulgaris--l.')
        self.assert_true(isinstance(incidence_mb, IncidenceMember))

    def test_dump(self):
        prjs = get_root_collection(IProject)
        prj = prjs.get('pond')
        stream = StringIO('w')
        dump_resource(prj, stream)
        self.assert_true(len(stream.getvalue() > 0))