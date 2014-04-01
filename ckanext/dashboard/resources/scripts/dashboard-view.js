this.ckan.module('dashboard-view-edit', function ($, _) {
  return {
    options: {
      size: 130,
      i18n: {
        edit: _('Edit'),
        remove: _('Remove')
      }
    },

    initialize: function () {
      $.proxyAll(this, /_/);

      $('#dashboard-view-edit-new a').on('click', this._add);
      $('.dashboard-grid .btn-danger', this.el).on('click', this._remove);
      $('#dashboard-view-add-url-button').on('click', this._add_from_url)

      this.gridster = $('.dashboard-grid', this.el)
        .gridster({
          widget_margins: [10, 10],
          widget_base_dimensions: [this.options.size, this.options.size],
          min_cols: 6,
          max_cols: 6,
          draggable: {
            stop: this._serialize
          },
          resize: {
            enabled: true,
            stop: this._serialize
          },
          serialize_params: function($w, wgd) {
            return { col: wgd.col, row: wgd.row, sizex: wgd.size_x, sizey: wgd.size_y, id: $w.attr('id') }
          }
        })
        .data('gridster');

      $(".dashboard-grid .module .module-heading", this.el).dotdotdot({
        // configuration
        after: "a.readmore"
      });

      this._serialize();
    },

    _add: function (e) {
      e.preventDefault();
      var view_id = $(e.target).data('view_id');
      template = '<li id="' + view_id + '"></li>'
      this.gridster.add_widget(template, 2, 2);
      this._serialize();
      $(this.el.parent()).find('[name="preview"]').click()
    },

    _remove: function (e) {
      e.preventDefault();
      var widget = $(e.target).parents('.box');
      this.gridster.remove_widget(widget);
      this._serialize();
    },

    _add_from_url: function (e) {
      e.preventDefault();
      var view_url = $(e.target).siblings().val().trim();
      var view_id = view_url.substr(view_url.length-36, 36);
      template = '<li id="' + view_id + '"></li>'
      this.gridster.add_widget(template, 2, 2);
      this._serialize();
      $(this.el.parent()).find('[name="preview"]').click()

    },

    _serialize: function () {
      var items = this.gridster.serialize();
      var data = JSON.stringify(items);
      $('input[name="json"]', this.el).val(data);
    }

  };
});

this.ckan.module('dashboard-view', {
  options: {
    size: 130,
  },
  initialize: function () {
    $('.dashboard-grid', this.el).gridster({
      widget_margins: [10, 10],
      widget_base_dimensions: [this.options.size, this.options.size],
      min_cols: 6,
      max_cols: 6
    }).data('gridster').disable();

    $(".dashboard-grid .module .module-heading", this.el).dotdotdot({
      // configuration
      after: "a.readmore"
    });
  }
});

this.ckan.module('dashboard-dropdown', {
  options: {
    values: {}
  },
  initialize: function () {
    var self = this;
    this.el.on("change", function(e) {
      var name = $(e.target).attr("name");
      var inputs = $(e.target).parent().children('input');
      var position = inputs.index(e.target);

      name = $(e.target).attr("name");
      var value = $(e.target).val();

      var filters = ckan.views.viewhelpers.filters;
      var filterValues = filters.get(name);
      var routeFilters = filters.get();
      if (filterValues) {
        filterValues[position] = value;
        filters.set(name, filterValues);
      } else {
        filters.set(name, value);
      }
    });

    this.el.select2({data: this.options.values, "width": 200});
  }
});
