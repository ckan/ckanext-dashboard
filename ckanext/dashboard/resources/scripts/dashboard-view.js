this.ckan.module('dashboard-view', {
  options: {
    size: 130,
  },
  initialize: function () {
    var in_preview = ($('[data-module="dashboard-view-edit"]').length !== 0);
    if (in_preview) {
      this.el.addClass('in-preview');
      return;
    }

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

this.ckan.module('dashboard-dropdown', function ($) {
  var in_preview = ($('[data-module="dashboard-view-edit"]').length !== 0);

  return {
    initialize: function () {
      var self = this;
      this.el.on("change", function(e) {
        var name = $(e.target).attr("name");
        var selects = $(e.target).parent().children('select');
        var position = selects.index(e.target);

        name = $(e.target).attr("name");
        var value = $(e.target).val();

        var filters = ckan.views.viewhelpers.filters;
        var filterValues = filters.get(name);
        var routeFilters = filters.get();

        if (filterValues) {
          if (value === "") {
            filters.unset(name, filterValues[position]);
          } else {
            filterValues[position] = value;
            filters.set(name, filterValues);
          }
        } else {
          if (value !== "") {
            filters.set(name, value);
          }
        }
      });

      this.el.select2({
        allowClear: true,
      });
      this.el.select2('enable', !in_preview);
    }
  };
});
