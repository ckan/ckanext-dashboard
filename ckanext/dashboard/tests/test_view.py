import mock

import ckan.plugins as p


class TestDashboard(object):

    @classmethod
    def setup_class(cls):
        p.load('dashboard_preview')
        cls.plugin = p.get_plugin('dashboard_preview')

    @classmethod
    def teardown_class(cls):
        p.unload('dashboard_preview')
