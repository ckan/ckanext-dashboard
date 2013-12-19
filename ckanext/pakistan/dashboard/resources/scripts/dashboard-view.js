this.ckan.module('dashboard-view-edit', function ($, _) {
  return {
    options: {
      i18n: {
        edit: _('Edit'),
        remove: _('Remove')
      }
    },
    template: [
      '<li class="box module module-narrow module-shallow">',
      '<header class="module-heading">',
      '<i class="icon-{{icon}}"></i>',
      '<a href="{{url}}" class="pull-right"><i class="icon-external-link"></i></a>',
      '<strong>{{title}}</strong>',
      '</header>',
      '<footer class="module-footer">',
      '<a href="#" class="btn btn-primary btn-small">{{edit}}</a> ',
      '<a href="#" class="btn btn-danger btn-small">{{remove}}</a>',
      '</footer>',
      '</li>'
    ].join(''),

    initialize: function () {
      $.proxyAll(this, /_/);

      $('#dashboard-view-edit-new a').on('click', this._add);
      $('.dashboard-grid .btn-danger', this.el).on('click', this._remove);

      this.gridster = $('.dashboard-grid', this.el)
        .gridster({
          widget_margins: [10, 10],
          widget_base_dimensions: [206, 206],
          draggable: {
            stop: this._serialize
          }
        })
        .data('gridster');

      this._serialize();
    },

    _add: function (e) {
      e.preventDefault();
      var view = JSON.parse($(e.target).data('json').replace(/'/g, '"'));
      var html = this.template
        .replace('{{icon}}', view.icon)
        .replace('{{title}}', view.title)
        .replace('{{edit}}', this.i18n('edit'))
        .replace('{{remove}}', this.i18n('remove'));
      var template = $(html);
      $('.btn-danger', template).on('click', this._remove);
      this.gridster.add_widget(template, view.sizex, view.sizey);
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
      widget_base_dimensions: [206, 206]
    });
  }
});
