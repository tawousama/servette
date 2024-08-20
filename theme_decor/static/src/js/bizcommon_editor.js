odoo.define('theme_decor.bizcommon_editor_js', function(require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    var snippetsEditor = require('web_editor.snippet.editor');

    // stop saving the dynamic content of the configurator in edit mode start
    snippetsEditor.SnippetsMenu.include({
        _onSaveRequest: function (ev) {
            this._super.apply(this, arguments);
            $(this.$scrollingTarget).find('.bizople_product_configurator [class*=container]').empty()
            $(this.$scrollingTarget).find('.bizople_brand_configurator [class*=container]').empty()
            $(this.$scrollingTarget).find('.bizople_category_configurator [class*=container]').empty()
        }
    })
    // stop saving the dynamic content of the configurator in edit mode end

    options.registry.s_bizople_theme_blog_slider_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_slider_owl').empty();
            
            if (!editMode) {
                self.$el.find(".blog_slider_owl").on("click", _.bind(self.theme_decor_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_decor_blog_slider()) {
                this.theme_decor_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            this.$target.find('.blog_slider_owl').empty();
        },
        theme_decor_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_decor.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal('show');
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_decor/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
});