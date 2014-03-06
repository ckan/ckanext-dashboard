import os
import logging
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.lib.datapreview as datapreview
import ckan.lib.helpers as helpers
import json
import collections
import ckanext.pakistan.icons as icons
ignore_empty = toolkit.get_validator('ignore_empty')
ignore = toolkit.get_validator('ignore')
not_empty = toolkit.get_validator('not_empty')
ignore_missing = toolkit.get_validator('ignore_missing')
aslist = toolkit.aslist

log = logging.getLogger(__name__)

class PakistanCustomizations(p.SingletonPlugin):
    p.implements(p.IRoutes)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))

        our_public_dir = os.path.join(rootdir, 'ckanext', 'pakistan', 'theme',
                'public')
        template_dir = os.path.join(rootdir, 'ckanext', 'pakistan', 'theme',
                'templates')
        config['extra_public_paths'] = ','.join([our_public_dir,
                config.get('extra_public_paths', '')])
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])

        toolkit.add_resource('theme/resources', 'pakistan-theme')

        from ckanext.pages.actions import schema
        extra_schema = {"icon": [ignore_missing, unicode],
                        "category": [ignore_missing, unicode],
                        "homepage_order": [ignore_missing, unicode]}
        schema.update(extra_schema)
        config['ckanext.pages.form'] = 'pages_form.html'

    def before_map(self, route_map):
        return route_map

    def after_map(self, route_map):
        return route_map

    def get_helpers(self):
        return {'icon_list': self.get_icons,
                'homepage_order': self.order_list,
                'get_homepage_icons': self.get_homepage_icons}

    def order_list(self):
        icon_list = [('', 'No Homepage Order')]
        for num in range(1, 11):
            icon_list.append((str(num), str(num)))
        return icon_list

    def get_icons(self):
        icon_list = [('', 'No Icon')]
        for icon in sorted(icons.icons):
            icon_list.append((icon, icon[5:]))
        return icon_list

    def get_homepage_icons(self):
        pages = toolkit.get_action('ckanext_pages_list')({}, {'page_type': 'page',
                                                              'private': False})
        homepage_pages = []
        for page in pages:
            if (not page.get('icon') or
                not page.get('category') or
                not page.get('homepage_order')):
                continue
            try:
                page['homepage_order'] = int(page['homepage_order'])
            except ValueError:
                continue
            homepage_pages.append(page)

        return sorted(homepage_pages, key=lambda page: page['homepage_order'])



class DashboardView(p.SingletonPlugin):
    '''This extenstion makes dashboard views'''

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurable, inherit=True)

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))

        template_dir = os.path.join(rootdir, 'ckanext', 'pakistan', 'dashboard',
                'templates')
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])

        toolkit.add_resource('dashboard/resources', 'dashboard-view')

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
                           'added_view_id': [ignore]},
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


        return {'available_views': resource_views,
                'current_dashboard': current_dashboard}

def convert_to_string(value):
    if isinstance(value, list):
        return ','.join(value)
    return value

def validate_fields(value, context):
    resource = {"id": context['resource'].id}
    allowed_fields = set(field['id'] for field in _get_fields(resource))
    for field in value.split(','):
        if field not in allowed_fields:
            raise toolkit.Invalid("Field {field} not in table".format(field=field))
    return value

class BasicGrid(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.ITemplateHelpers)

    def get_helpers(self):
        return {'view_data': _view_data}

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))

        template_dir = os.path.join(rootdir, 'ckanext', 'pakistan', 'basicgrid',
                'templates')
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])

        toolkit.add_resource('basicgrid/resources', 'basicgrid')

    def info(self):
        schema = {
            'filter_fields': [ignore_missing],
            'filter_values': [ignore_missing],
            'fields': [ignore_missing, convert_to_string, validate_fields, unicode],
            'orientation': [ignore_missing],
        }

        return {'name': 'basicgrid',
                'title': 'Basic Grid',
                'icon': 'table',
                'iframed': False,
                'schema': schema,
                }

    def can_view(self, data_dict):
        return True

    def view_template(self, context, data_dict):
        return 'basicgrid_view.html'

    def form_template(self, context, data_dict):
        return 'basicgrid_form.html'

    def setup_template_variables(self, context, data_dict):
        resource = data_dict['resource']
        fields = _get_fields_without_id(resource)
        resource_view = data_dict['resource_view']

        self._filter_fields_and_values_as_list(resource_view)
        field_selection = json.dumps(
            [{"id": field['value'], "text": field['value']} for field in fields]
        )

        orientations = [{'value': 'horizontal'}, {'value': 'vertical'}]

        return {'fields': fields,
                'field_selection': field_selection,
                'orientations': orientations}

    def _filter_fields_and_values_as_list(self, resource_view):
        if 'filter_fields' in resource_view:
            filter_fields = aslist(resource_view['filter_fields'])
            resource_view['filter_fields'] = filter_fields
        if 'filter_values' in resource_view:
            filter_values = aslist(resource_view['filter_values'])
            resource_view['filter_values'] = filter_values
        if 'fields' in resource_view:
            resource_view['fields'] = convert_to_string(resource_view['fields'])


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

def parse_filter_params():
    filters = collections.defaultdict(list)
    filter_string = dict(toolkit.request.GET).get('filters','')
    for filter in filter_string.split('|'):
        if filter.count(':') <> 1:
            continue
        key, value = filter.split(':')
        filters[key].append(value)
    return dict(filters)

def _view_data(resource_view):
    data = {
        'resource_id': resource_view['resource_id'],
        'limit': int(resource_view.get('limit', 100))
    }
    filters = collections.defaultdict(list)

    for key, value in zip(aslist(resource_view.get('filter_fields', [])),
                          aslist(resource_view.get('filter_values', []))):
        filters[key].append(value)

    for key, value in parse_filter_params().items():
        filters[key][:] = value

    if filters:
        data['filters'] = dict(filters)

    fields = resource_view.get('fields')
    data['fields'] = convert_to_string(fields).split(',')

    result = p.toolkit.get_action('datastore_search')({}, data)
    return result


############# MONKEY PATCH ####################

import ckanext.datastore.db
ValidationError = toolkit.ValidationError


def _where(field_ids, data_dict):
    '''Return a SQL WHERE clause from data_dict filters and q'''
    filters = data_dict.get('filters', {})

    if not isinstance(filters, dict):
        raise ValidationError({
            'filters': ['Not a json object']}
        )

    where_clauses = []
    values = []

    for field, value in filters.iteritems():
        if field not in field_ids:
            raise ValidationError({
                'filters': ['field "{0}" not in table'.format(field)]}
            )

        ##### patch here #####
        if isinstance(value, list):
            where_clauses.append(
                u'"{0}" in ({1})'.format(field,
                ','.join(['%s'] * len(value)))
            )
            values.extend(value)
            continue
        ##### patch ends here #####

        where_clauses.append(u'"{0}" = %s'.format(field))
        values.append(value)

    # add full-text search where clause
    if data_dict.get('q'):
        where_clauses.append(u'_full_text @@ query')

    where_clause = u' AND '.join(where_clauses)
    if where_clause:
        where_clause = u'WHERE ' + where_clause
    return where_clause, values

ckanext.datastore.db._where = _where

############# finish patch ####################
