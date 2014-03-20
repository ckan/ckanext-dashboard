import logging
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as helpers
import json
import collections
ignore_empty = toolkit.get_validator('ignore_empty')
ignore = toolkit.get_validator('ignore')
not_empty = toolkit.get_validator('not_empty')
ignore_missing = toolkit.get_validator('ignore_missing')
aslist = toolkit.aslist

log = logging.getLogger(__name__)


class DashboardView(p.SingletonPlugin):
    '''This extenstion makes dashboard views'''

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurable, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('resources', 'dashboard-view')

    def configure(self, config):
        self.size = int(config.get('ckan.dashboard.size', 130))

    def get_size(self):
        return self.size

    def get_helpers(self):
        return {'dashboard_size': self.get_size}

    def info(self):
        return {'name': 'dashboard',
                'title': 'Dashboard',
                'icon': 'dashboard',
                'iframed': False,
                'schema': {'json': [ignore_empty, unicode],
                           'added_view_id': [ignore],
                           'user_filter_names': [ignore_missing],
                           'user_filter_fields': [ignore_missing]
                          },
                'preview_enabled': False,
                'full_page_edit': True,
                }

    def can_view(self, data_dict):
        return True

    def view_template(self, context, data_dict):
        return 'dashboard_view.html'

    def form_template(self, context, data_dict):
        return 'dashboard_form.html'

    def setup_template_variables(self, context, data_dict):
        current_dashboard = data_dict['resource_view'].get('json', '[]')
        current_dashboard = json.loads(current_dashboard)

        current_view_ids = set(view['id'] for view in current_dashboard)

        resource_views = []
        for resource in data_dict['package'].get('resources', []):
            views = toolkit.get_action('resource_view_list')(context, resource)
            for view in views:
                if view['id'] in current_view_ids or view['view_type'] == 'dashboard':
                    continue
                view['icon'] = helpers.resource_view_icon(view)
                resource_views.append(view)

        ## When rendering each view we need to provide both the views resource and
        ## the package.  This is expensive todo for each view and due to the
        ## likelihood the view will be on the same resource/packages
        ## we cache the get action calls so we do not have to repeat the calls for
        ## packages/resources already fetched.
        resource_cache = {}
        package_cache = {}

        ##copy dashboard here so we can remove any items if the resource_view got deleted
        for view in current_dashboard[:]:
            try:
                resource_view = toolkit.get_action('resource_view_show')(context, view)
            except toolkit.ObjectNotFound:
                ##skip any deleted views, next save should remove them properely
                current_dashboard.remove(view)
                continue
            if resource_view['view_type'] == 'dashboard':
                ## do not allow dashboards in dashboards as that can lead infinate loop
                current_dashboard.remove(view)
                continue

            ##use resource_view's sizes if there're no sizes defined in view
            resource_view_dimensions = helpers.resource_view_dimensions(resource_view)
            view['sizex'] = view.get('sizex', resource_view_dimensions['sizex'])
            view['sizey'] = view.get('sizey', resource_view_dimensions['sizey'])

            view.update(resource_view)

            resource = resource_cache.get(view['resource_id'])
            if not resource:
                resource = toolkit.get_action('resource_show')(
                    context, {'id': view['resource_id']}
                )
                resource_cache[view['resource_id']] = resource
            view['resource'] = resource

            package = package_cache.get(view['package_id'])
            if not package:
                package = toolkit.get_action('package_show')(
                    context, {'id': view['package_id']}
                )
                package_cache[view['package_id']] = package
            view['package'] = package

        resource = data_dict['resource']
        resource_view = data_dict['resource_view']
        resource_view = self._filter_fields_and_values_as_list(resource_view)

        fields = _get_fields_without_id(resource)
        dropdown_values = get_filter_values(resource)

        field_label_mapping = self._get_field_to_label_mapping(resource_view)
        current_dropdown_values = self._get_dropdown_values(resource_view)

        return {'available_views': resource_views,
                'current_dashboard': current_dashboard,
                'fields': fields,
                'dropdown_values': dropdown_values,
                'field_label_mapping': field_label_mapping,
                'current_dropdown_values': current_dropdown_values}

    def _get_field_to_label_mapping(self, resource_view):
        field_name_mapping = {}
        for field, name in zip(resource_view['user_filter_fields'],
                               resource_view['user_filter_names']):
            if name:
                field_name_mapping[field] = name
            else:
                if field not in field_name_mapping:
                    field_name_mapping[field] = field

        return field_name_mapping

    def _get_dropdown_values(self, resource_view):

        # first we pad out the values with the filters defined in the
        # dashboard form.
        current_dropdown_values = {}
        for field in resource_view['user_filter_fields']:
            if field in current_dropdown_values:
                current_dropdown_values[field].append('')
            else:
                current_dropdown_values[field] = ['']

        # then we actually add the data from the url.
        for field, values in parse_filter_params().items():
            # do not show dropdowns for fields not defined in data
            if field not in resource_view['user_filter_fields']:
                continue
            for num, value in enumerate(values):
                try:
                    current_dropdown_values[field][num] = value
                except IndexError:
                    # extend the data if the parameters have more than
                    # what is defined in the form.
                    current_dropdown_values[field].append(value)

        return current_dropdown_values

    def _filter_fields_and_values_as_list(self, resource_view):
        filter_fields = resource_view.get('user_filter_fields', [])
        filter_values = resource_view.get('user_filter_names', [])

        if isinstance(filter_fields, basestring):
            resource_view['user_filter_fields'] = [filter_fields]
        if isinstance(filter_values, basestring):
            resource_view['user_filter_names'] = [filter_values]

        return resource_view


def parse_filter_params():
    filters = collections.defaultdict(list)
    filter_string = dict(p.toolkit.request.GET).get('filters', '')
    for filter in filter_string.split('|'):
        if filter.count(':') != 1:
            continue
        key, value = filter.split(':')
        filters[key].append(value)
    return dict(filters)

def _get_fields_without_id(resource):
    fields = _get_fields(resource)
    return [{'value': v['id']} for v in fields if v['id'] != '_id']

def _get_fields(resource):
    data = {
        'resource_id': resource['id'],
        'limit': 0
    }
    result = p.toolkit.get_action('datastore_search')({}, data)
    return result['fields']

def get_filter_values(resource):
    ''' Tries to get out filter values so they can appear in dropdown list.
    Leaves input as text box when the table is too big or there are too many
    distinct values.  Current limits are 5000 rows in table and 500 distict
    values.'''

    data = {
        'resource_id': resource['id'],
        'limit': 5001
    }
    result = p.toolkit.get_action('datastore_search')({}, data)
    # do not try to get filter values if there are too many rows.
    if len(result.get('records', [])) == 5001:
        return {}

    filter_values = {}
    for field in result.get('fields', []):
        if field['type'] != 'text':
            continue
        distinct_values = set()
        for row in result.get('records', []):
            distinct_values.add(row[field['id']])
        # keep as input if there are too many distinct values.
        if len(distinct_values) > 500:
            continue
        filter_values[field['id']] = [{'id': value, 'text': value}
                                      for value
                                      in sorted(list(distinct_values))]
    return filter_values
