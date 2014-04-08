ckanext-dashboard
=================

![Sample dashboard](doc/sample-dashboard.png)

This extension adds a dashboard to CKAN, which provides way to organize many of
the new Resource View being developed in
https://github.com/ckan/ckan/tree/1251-resource-view in a single page.

Installation
------------

This extension depends on
[ckanext-viewhelpers](https://github.com/ckan/ckanext-viewhelpers). You'd have
to install it first.

After that, simply clone this repository and run ```python setup.py install```.
Then add ```dashboard_preview``` to the list in ```ckan.plugins``` in your CKAN
config file. Make sure to put it after ```ckanext-viewhelper```.

Restart your webserver. You should see the new "Dashboard" chart type as an
option in the view type's list on any resource.

License
-------

Copyright (C) 2014 Open Knowledge Foundation

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
