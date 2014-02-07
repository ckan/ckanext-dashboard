this.ckan.module('dashboard-view-edit', function ($, _) {
  return {
    options: {
      i18n: {
        edit: _('Edit'),
        remove: _('Remove')
      }
    },

    initialize: function () {
      $.proxyAll(this, /_/);

      $('#dashboard-view-edit-new a').on('click', this._add);
      $('.dashboard-grid .btn-danger', this.el).on('click', this._remove);

      this.gridster = $('.dashboard-grid', this.el)
        .gridster({
          widget_margins: [10, 10],
          widget_base_dimensions: [130, 130],
          min_cols: 6,
          max_cols: 6,
          draggable: {
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

    _serialize: function () {
      var items = this.gridster.serialize();
      var data = JSON.stringify(items);
      $('input[name="json"]', this.el).val(data);
    }

  };
});

this.ckan.module('dashboard-view', {
  initialize: function () {
    $('.dashboard-grid', this.el).gridster({
      widget_margins: [10, 10],
      widget_base_dimensions: [130, 130],
      min_cols: 6,
      max_cols: 6
    }).data('gridster').disable();

    $(".dashboard-grid .module .module-heading", this.el).dotdotdot({
      // configuration
      after: "a.readmore"
    });
  }
});

