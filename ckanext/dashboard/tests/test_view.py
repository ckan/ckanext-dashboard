import mock

import ckan.plugins as p


class TestDashboard(object):

    @classmethod
    def setup_class(cls):
        p.load('viewhelpers')
        p.load('dashboard_preview')
        cls.plugin = p.get_plugin('dashboard_preview')

    @classmethod
    def teardown_class(cls):
        p.unload('dashboard_preview')
        p.unload('viewhelpers')

    @mock.patch('ckan.plugins.toolkit')
    def test_resources_not_in_datastore_have_filters_enabled_false(self, toolkit):
        toolkit.request.GET = {}
        context = {}
        resource = {
            'id': 'resource_id',
            'name': 'resource_name'
        }
        resource_view = {}
        data_dict = {
            'resource_view': resource_view,
            'package': {},
            'resource': resource
        }

        result = self.plugin.setup_template_variables(context, data_dict)

        assert not result['filters_enabled']
        assert 'fields' not in result
        assert 'dropdown_values' not in result
        assert 'field_label_mapping' not in result
        assert 'current_dropdown_values' not in result

    @mock.patch('ckan.plugins.toolkit')
    def test_resources_in_datastore_have_filters_enabled_true(self, toolkit):
        toolkit.request.GET = {}
        context = {}
        resource = {
            'id': 'resource_id',
            'name': 'resource_name',
            'datastore_active': True
        }
        resource_view = {}
        data_dict = {
            'resource_view': resource_view,
            'package': {},
            'resource': resource
        }

        result = self.plugin.setup_template_variables(context, data_dict)

        assert result['filters_enabled']
        assert 'fields' in result
        assert 'dropdown_values' in result
        assert 'field_label_mapping' in result
        assert 'current_dropdown_values' in result
