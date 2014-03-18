import logging
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as helpers
import json
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
