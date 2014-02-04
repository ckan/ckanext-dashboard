import os
import logging
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.lib.datapreview as datapreview
import ckan.lib.helpers as helpers
import json
ignore_empty = toolkit.get_validator('ignore_empty')

log = logging.getLogger(__name__)

class PakistanCustomizations(p.SingletonPlugin):
    p.implements(p.IRoutes)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IPackageController, inherit=True)

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

    def before_map(self, route_map):
        return route_map

    def after_map(self, route_map):
        return route_map

class DashboardView(p.SingletonPlugin):
    '''This extenstion makes dashboard views'''

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))

        template_dir = os.path.join(rootdir, 'ckanext', 'pakistan', 'dashboard',
                'templates')
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])

        toolkit.add_resource('dashboard/resources', 'dashboard-view')

    def info(self):
        return {'name': 'dashboard',
                'title': 'Dashboard',
                'icon': 'dashboard',
                'iframed': False,
                'schema': {'json': [ignore_empty, unicode]},
                'preview_enabled': False,
                }

    def can_view(self, data_dict):
        return True

    def view_template(self, context, data_dict):
        return 'dashboard_view.html'

    def form_template(self, context, data_dict):
        return 'dashboard_form.html'

    def setup_template_variables(self, context, data_dict):
        resource_views = []
        for resource in data_dict['package'].get('resources', []):
            views = toolkit.get_action('resource_view_list')(context, resource)
            for view in views:
                view['icon'] = helpers.resource_view_icon(view)
                resource_views.append(view)

        ## When rendering each view we need to provide both the views resource and
        ## the package.  This is expensive todo for each view and due to the 
        ## likelihood the view will be on the same resource/packages
        ## we cache the get action calls so we do not have to repeat the calls for 
        ## packages/resources already fetched.
        resource_cache = {}
        package_cache = {}

        current_dashboard = data_dict['resource_view'].get('json', '[]')
        current_dashboard = json.loads(current_dashboard)
        for view in current_dashboard:
            view.update(
                toolkit.get_action('resource_view_show')(context, view)
            )

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
