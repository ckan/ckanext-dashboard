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
