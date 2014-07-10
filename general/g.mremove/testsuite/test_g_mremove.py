"""Test of g.mremove module"""

# TODO: rmapcalc probably fatals, replace or add raise on error?
from grass.script.raster import mapcalc as rmapcalc

import grass.gunittest
from grass.gunittest.gutils import get_current_mapset
from grass.gunittest.gmodules import SimpleModule

# when used user1 must be replaced by current mapset
REMOVE_RASTERS = """rast/test_map_0@user1
rast/test_map_1@user1
rast/test_map_2@user1
rast/test_map_3@user1
rast/test_map_4@user1
rast/test_map_5@user1
rast/test_map_6@user1
rast/test_map_7@user1
rast/test_map_8@user1
rast/test_map_9@user1
rast/test_two@user1
"""

REMOVING_RASTERS_LOG = """Removing raster <test_map_0>
Removing raster <test_map_1>
Removing raster <test_map_2>
Removing raster <test_map_3>
Removing raster <test_map_4>
Removing raster <test_map_5>
Removing raster <test_map_6>
Removing raster <test_map_7>
Removing raster <test_map_8>
Removing raster <test_map_9>
Removing raster <test_two>
"""


class GMRemoveTest(grass.gunittest.TestCase):
    """Test removing with g.mremove"""

    @classmethod
    def setUpClass(cls):
        """Set up small region for fast map creation."""
        cls.use_temp_region()
        cls.runModule("g.region", s=0, n=5, w=0, e=5, res=1)

    @classmethod
    def tearDownClass(cls):
        """Remove temporary region"""
        cls.del_temp_region()

    def test_remove_procedure(self):
        """Test that maps are removed only with -f"""
        for i in range(0, 10):
            rmapcalc("test_map_%i = 100" % i)
        rmapcalc("test_two = 2")

        module = SimpleModule('g.mremove',
                              type='rast', pattern='test_map_*,*two')
        self.assertModule(module)
        self.assertMultiLineEqual(module.outputs.stdout,
                                  REMOVE_RASTERS.replace('user1',
                                                         get_current_mapset()))

        module = SimpleModule('g.mremove', type='rast',
                              pattern='test_map_*,*two', flags='f')
        self.assertModule(module)
        self.assertMultiLineEqual(module.outputs.stdout, '')
        self.assertMultiLineEqual(module.outputs.stderr, REMOVING_RASTERS_LOG)

    def test_remove_procedure_exclude(self):
        """Test that exclude does not list excluded maps"""
        rmapcalc("test_apples = 100")
        rmapcalc("test_oranges = 200")
        rmapcalc("test_apples_big = 300")
        rmapcalc("test_apples_small = 300")
        module = SimpleModule('g.mremove', type='rast',
                              pattern='test_{apples,oranges}*',
                              exclude="*_small")
        self.assertModule(module)
        self.assertMultiLineEqual(module.outputs.stdout,
                                  'rast/test_apples@user1\n'
                                  'rast/test_apples_big@user1\n'
                                  'rast/test_oranges@user1\n'.replace(
                                      'user1', get_current_mapset()))
        module = SimpleModule('g.mremove', type='rast',
                              pattern='test_{apples,oranges}{_small,_big,*}',
                              flags='f')
        self.assertModule(module)
        self.assertMultiLineEqual(module.outputs.stdout, '')
        self.assertRegexpMatches(module.outputs.stderr, "(.*<.+>[^\n]*\n){4}",
                                 msg="4 maps should be removed")


class GMRemoveWrongInputTest(grass.gunittest.TestCase):
    """Test wrong input of parameters for g.mlist module"""

    def test_re_flags(self):
        """Test that -r and -e flags are exclusive"""
        module = SimpleModule('g.mremove', flags='re',
                              type='rast', pattern='xxxyyyzzz')
        self.assertModuleFail(module)
        stderr = module.outputs.stderr
        self.assertIn('-r', stderr)
        self.assertIn('-e', stderr)


if __name__ == '__main__':
    grass.gunittest.test()
