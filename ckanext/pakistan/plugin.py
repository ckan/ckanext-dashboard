import os
import logging
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)

available_views = [
  { "icon": "picture",
    "title": "View #1",
    "sizex": 2,
    "sizey": 1 },
  { "icon": "line-chart",
    "title": "View #2",
    "sizex": 1,
    "sizey": 1 },
  { "icon": "compass",
    "title": "View #3",
    "sizex": 1,
    "sizey": 1 },
  { "icon": "picture",
    "title": "View #4",
    "sizex": 1,
    "sizey": 1 }
  ]

current_views = [
  { "title": "View #1",
    "sizex": 2,
    "sizey": 1,
    "row": 1,
    "col": 1 },
  { "title": "View #2",
    "sizex": 1,
    "sizey": 1,
    "row": 1,
    "col": 3 },
  { "title": "View #3",
    "sizex": 1,
    "sizey": 1,
    "row": 1,
    "col": 3 },
  { "title": "View #4",
    "sizex": 1,
    "sizey": 1,
    "row": 2,
    "col": 4 }
  ]

def get_available_views():
    return available_views

def get_current_views():
    return current_views

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
    p.implements(p.ITemplateHelpers)

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
                'iframed': False}

    def can_view(self, data_dict):
        return True

    def view_template(self, context, data_dict):
        return 'dashboard_view.html'

    def form_template(self, context, data_dict):
        return 'dashboard_form.html'

    def add_default_views(self, context, data_dict):
        resources = datapreview.get_new_resources(context, data_dict)
        for resource in resources:
            view = {'title': 'Dashboard',
                    'description': 'Dashboard description here',
                    'resource_id': resource['id'],
                    'view_type': 'dashboard'}
            context['defer_commit'] = True
            p.toolkit.get_action('resource_view_create')(context, view)
            context.pop('defer_commit')

    def after_update(self, context, data_dict):
        self.add_default_views(context, data_dict)

    def after_create(self, context, data_dict):
        self.add_default_views(context, data_dict)

    def get_helpers(self):
        return {'get_available_views': get_available_views,
                'get_current_views': get_current_views}


