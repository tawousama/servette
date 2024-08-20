odoo.define('theme_decor.product_configurator_options', function(require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    // ajax.loadXML('/theme_decor/static/src/xml/product_configurator.xml', qweb);

    options.registry.theme_decor_product_configurator = options.Class.extend({
        events:{
            'click we-button.biz_change_product':'prod_config',
        },
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.ajax-cart-modal').remove();
            if (!editMode) {
                self.$el.find(".container").on("click", _.bind(self.prod_config, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.prod_config()) {
                this.prod_config().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.bizople_product_configurator').find('[class*=container]').empty();
        },

        drop_select: function(){
                
        },

        prod_config: function(type, value) {
            var self = this;
            var saved_config_html = self.$target[0].outerHTML
            if (type != undefined && type.type == "click" || type == undefined) {
                
                self.$modal = $(qweb.render("theme_decor.select_product_configurator"));
                self.$modal.appendTo('body');
                self.$modal.modal('show');
                var $checkbox = self.$modal.find(".form-check-input"),
                    $product_slider_cancel = self.$modal.find("#cancel"),
                    $pro_sub_data = self.$modal.find("#prod_sub_data");

                $.get("/theme_decor/get_product_configurator_products", {
                    'product_config_id': self.$target.attr('product_config_id') || '',
                }).then(function(data) {
                    if (data) {
                        self.$modal.find(".products").append(data);
                        bringSelectedProducts();
                        lableinputclick();
                        SliderOptions();
                    }
                });

                /*tab js start*/

                $('.nav-tabs .nav-link').on('click', function() {
                    var thishash = $(this)[0].hash
                    if(thishash == "#display_config_tab"){
                        self.$modal.find("#display_config_tab").addClass('active show')
                        self.$modal.find("#product_select_tab").removeClass('active show')
                    }
                    if(thishash == "#product_select_tab"){
                        self.$modal.find("#display_config_tab").removeClass('active show')
                        self.$modal.find("#product_select_tab").addClass('active show')
                    }
                });

                /*tab js end*/



                
                /* ek var configuration save karya pachi biji var open kare to saved config select lave start */

                    /* ek var product select karya pachi fari modal open kare to aee product selected lai avse start*/
                    function bringSelectedProducts() {
                        var current_product_id = self.$target.attr('product_id')
                        const id_array = current_product_id.split(",")
                        id_array.pop();
                        var label_list = $(".products label.form-check-label")
                        $(label_list).each(function(){
                            var prod_id = this.attributes[1].value;
                            $.each(id_array, function( key, value ) {
                                if(prod_id == value){
                                    var current_label= $('.products').find("[prod_id='" + prod_id + "']");
                                    $(current_label).parent().removeClass("d-none")
                                    $(current_label).children().attr('checked','checked')

                                    var product_name = $(current_label).find('input').attr('name')
                                    var product_id = $(current_label).find('input').attr('id')
                                    var product_row = '<div id="'+product_id+'" class="d-flex justify-content-between"><div class="image"><img width="80" height="80" class="selected_product_image img img-fluid" src="/web/image/product.template/'+product_id+'/image_1920"/></div><div class="selected_product_name"><h6>'+product_name+'</h6></div></div>'
                                    self.$modal.find('.selected_product').append(product_row);
                                }
                            });
                        });
                    }

                    function SliderOptions() {
                        var autoslide = self.$modal.find('#autoslide').is(":checked");
                        var sliderspeed = self.$modal.find('.slider_slidespeed');
                        if(autoslide == 1){
                            self.$target.attr('autoslide','true');
                            $(sliderspeed).removeClass('d-none');
                        }
                        else{
                            self.$target.attr('autoslide','false');
                            $(sliderspeed).addClass('d-none');
                        }

                        var targetAutoSlide = self.$target.attr("autoslide");
                        if (targetAutoSlide == "false") {
                            self.$modal.find("#autoslide").prop("checked", false);
                            $(sliderspeed).addClass('d-none');
                        }
                        else{
                            self.$modal.find("#autoslide").prop("checked", true);
                            $(sliderspeed).removeClass('d-none');
                        }
                    }

                    var $auto = self.$modal.find('#autoslide');
                    $auto.on('click',function () {
                        SliderOptions();
                    });
                    

                    /* ek var product select karya pachi fari modal open kare to aee product selected lai avse end*/

                    /* Configuration nu title hye to input ma aee lai avse modal open thai tyre start */

                    if (self.$target.attr('config_title')){
                        var current_title = self.$target.attr('config_title');
                        $('.config_title').val(current_title)
                    }
                    if (self.$target.attr('config_slider_description')){
                        var current_slider_description = self.$target.attr('config_slider_description');
                        $('.config_slider_description').val(current_slider_description)
                    }
                    

                    /* Configuration nu title hye to input ma aee lai avse modal open thai tyre end */

                    /* dropdown btn ma selected value lai ave start */

                    if (self.$target.hasClass("grid_style")){
                        self.$modal.find(".display_style .dropdown-toggle").html('Grid')
                        self.$modal.find('.column_limit').removeClass('d-none')
                        self.$modal.find('.product_limit_one_slide').addClass('d-none')
                        self.$modal.find(".product_preview").addClass('grid_style')
                        self.$modal.find(".card_style").removeClass('d-none')
                        self.$modal.find(".product_slider_description").addClass('d-none')
                        self.$modal.find("a[display_options=show_description]").removeClass('d-none')
                        self.$modal.find('.slider_autoslide').addClass('d-none')
                        self.$modal.find('.slider_slidespeed').addClass('d-none')
                    }
                    if (self.$target.hasClass("list_style")){
                        self.$modal.find(".display_style .dropdown-toggle").html('List')
                        self.$modal.find('.product_limit_one_slide').addClass('d-none')
                        self.$modal.find('.column_limit').addClass('d-none')
                        self.$modal.find(".product_preview").addClass('list_style')
                        self.$modal.find(".card_style").addClass('d-none')
                        self.$modal.find(".product_slider_description").addClass('d-none')
                        self.$modal.find("a[display_options=show_description]").addClass('d-none')
                        self.$modal.find('.slider_autoslide').addClass('d-none')
                        self.$modal.find('.slider_slidespeed').addClass('d-none')
                    }
                    if (self.$target.hasClass("slider_style")){
                        self.$modal.find(".display_style .dropdown-toggle").html('Grid Slider')
                        self.$modal.find('.product_limit_one_slide').removeClass('d-none')
                        self.$modal.find('.column_limit').addClass('d-none')
                        self.$modal.find(".product_preview").addClass('slider_style')
                        self.$modal.find(".card_style").removeClass('d-none')
                        self.$modal.find(".product_slider_description").removeClass('d-none')
                        self.$modal.find("a[display_options=show_description]").removeClass('d-none')
                        self.$modal.find('.slider_autoslide').removeClass('d-none')
                        // self.$modal.find('.slider_slidespeed').removeClass('d-none')
                    }
                    if(self.$target.hasClass("list_slider_style")){
                        self.$modal.find(".display_style .dropdown-toggle").html('List Slider')
                        self.$modal.find(".card_style").addClass('d-none')
                        self.$modal.find(".product_slider_description").removeClass('d-none')
                        self.$modal.find('.column_limit').addClass('d-none')
                        self.$modal.find("a[display_options=show_description]").removeClass('d-none')
                        self.$modal.find(".product_preview").addClass('list_slider_style')
                        self.$modal.find('.product_limit_one_slide').addClass('d-none')
                        self.$modal.find('.slider_autoslide').removeClass('d-none')
                        // self.$modal.find('.slider_slidespeed').removeClass('d-none')

                    }

                    if (self.$target.hasClass("layout_style_1")){
                        self.$modal.find(".layout_style .dropdown-toggle").html('Style 1')
                        self.$modal.find(".product_preview").addClass('layout_style_1')
                    }
                    if (self.$target.hasClass("layout_style_2")){
                        self.$modal.find(".layout_style .dropdown-toggle").html('Style 2')
                        self.$modal.find(".product_preview").addClass('layout_style_2')
                    }
                    if (self.$target.hasClass("layout_style_3")){
                        self.$modal.find(".layout_style .dropdown-toggle").html('Style 3')
                        self.$modal.find(".product_preview").addClass('layout_style_3')
                    }

                    if (self.$target.hasClass("vertical_card")){
                        self.$modal.find(".card_style .dropdown-toggle").html('Veritcal')
                        self.$modal.find(".product_preview").addClass('vertical_card')
                    }
                    if (self.$target.hasClass("horizontal_card")){
                        self.$modal.find(".card_style .dropdown-toggle").html('Horizontal')
                        self.$modal.find(".product_preview").addClass('horizontal_card')
                    }

                    if (self.$target.attr("product_limit")){
                        var saved_product_limit = self.$target.attr("product_limit");
                        self.$modal.find(".product_limit .dropdown-toggle").html(saved_product_limit)
                    }
                    if (self.$target.attr("column_limit")){
                        var saved_column_limit = self.$target.attr("column_limit");
                        self.$modal.find(".column_limit .dropdown-toggle").html(saved_column_limit)
                    }
                    if (self.$target.attr("slider_speed")){
                        var saved_slider_speed = self.$target.attr("slider_speed");
                        self.$modal.find(".slider_slidespeed .dropdown-toggle").html(saved_slider_speed)
                    }
                    if (self.$target.attr("autoslide")){
                        var saved_auto_slide = self.$target.attr("autoslide");
                        if(saved_auto_slide == "false"){
                            self.$modal.find("#autoslide").prop("checked", false);
                        }
                        else{
                            self.$modal.find("#autoslide").prop("checked", true);
                        }
                    }
                    if (self.$target.attr("one_slide_limit")){
                        var saved_one_slide_limit = self.$target.attr("one_slide_limit");
                        self.$modal.find(".product_limit_one_slide .dropdown-toggle").html(saved_one_slide_limit)
                    }

                    if (self.$target.hasClass("show_cart")){
                        self.$modal.find("a[display_options=show_cart]").addClass('active')
                        self.$modal.find(".product_preview").addClass('show_cart')
                    }
                    if (self.$target.hasClass("img_bg_color")){
                        self.$modal.find("a[display_options=img_bg_color]").addClass('active')
                        self.$modal.find(".product_preview").addClass('img_bg_color')
                    }
                    if (self.$target.hasClass("show_wishlist")){
                        self.$modal.find("a[display_options=show_wishlist]").addClass('active')
                        self.$modal.find(".product_preview").addClass('show_wishlist')
                    }
                    if (self.$target.hasClass("show_compare")){
                        self.$modal.find("a[display_options=show_compare]").addClass('active')
                        self.$modal.find(".product_preview").addClass('show_compare')
                    }
                    if (self.$target.hasClass("show_quickview")){
                        self.$modal.find("a[display_options=show_quickview]").addClass('active')
                        self.$modal.find(".product_preview").addClass('show_quickview')
                    }
                    if (self.$target.hasClass("show_label")){
                        self.$modal.find("a[display_options=show_label]").addClass('active')
                        self.$modal.find(".product_preview").addClass('show_label')
                    }
                    if (self.$target.hasClass("show_price")){
                        self.$modal.find("a[display_options=show_price]").addClass('active')
                        self.$modal.find(".product_preview").addClass('show_price')
                    }
                    if (self.$target.hasClass("show_ratings")){
                        self.$modal.find("a[display_options=show_ratings]").addClass('active')
                        self.$modal.find(".product_preview").addClass('show_ratings')
                    }
                    if (self.$target.hasClass("show_description")){
                        self.$modal.find("a[display_options=show_description]").addClass('active')
                        self.$modal.find(".product_preview").addClass('show_description')
                    }

                    /* dropdown btn ma selected value lai ave end */

                /* ek var configuration save karya pachi biji var open kare to saved config select lave end */

                $('.form-product-search').keyup(function(){
                    var input_value = this.value.toUpperCase();
                    var checkbox_list = $(".products label.form-check-label")
                    $(".products label.form-check-label").each(function() {
                        var labe_text = this.innerText
                        var prod_id = this.attributes[1].value;
                        var current_label= $('.products').find("[prod_id='" + prod_id + "']"); 
                        if (labe_text.toUpperCase().indexOf(input_value) > 0) {
                            $(current_label).parent().removeClass("d-none")
                        } else{
                            $(current_label).parent().addClass("d-none")
                        }
                    });
                });

                function lableinputclick() {
                    self.$modal.find('label.form-check-label input').on('click', function() {
                        var product_name = $(this).attr('name')
                        var product_id = $(this).attr('id')
                        var product_row = '<div id="'+product_id+'" class="d-flex justify-content-between"><div class="image"><img width="80" height="80" class="selected_product_image img img-fluid" src="/web/image/product.template/'+product_id+'/image_1920"/></div><div class="selected_product_name"><h6>'+product_name+'</h6></div></div>'

                        if($(this).is(":checked")){
                            self.$modal.find('.selected_product').append(product_row);
                        } else{
                            self.$modal.find('.selected_product div[id="'+product_id+'"]').remove();
                        }
                    });
                }
                    
                $('.config_title').keyup(function(){
                    var input_value = this.value;
                    self.$target.attr('config_title',input_value);
                });
                $('.config_slider_description').keyup(function(){
                    var input_description_value = this.value;
                    self.$target.attr('config_slider_description',input_description_value);
                });
                

                $('.product_configurator_option .dropdown-item').on('click', function() {
                    var dropdownbtn = $(this).parent().parent().find('.dropdown-toggle');
                    $(dropdownbtn).html($(this).html());
                    if($(this).attr('data-select-display-class')){
                        var add_class = $(this).attr('data-select-display-class');
                        self.$target.removeClass('grid_style list_style slider_style list_slider_style')
                        self.$target.addClass(add_class);
                        self.$modal.find('.product_preview').removeClass('grid_style list_style slider_style list_slider_style')
                        self.$modal.find('.product_preview').addClass(add_class);
                        if (add_class == "grid_style"){
                            self.$modal.find('.column_limit').removeClass('d-none')
                            self.$modal.find('.product_limit_one_slide').addClass('d-none')
                            self.$modal.find(".card_style").removeClass('d-none')
                            self.$modal.find(".product_slider_description").addClass('d-none')
                            self.$modal.find("a[display_options=show_description]").removeClass('d-none active')
                            self.$modal.find(".product_preview").removeClass('show_description')
                            self.$modal.find('.slider_autoslide').addClass('d-none')
                            self.$modal.find('.slider_slidespeed').addClass('d-none')
                        }
                        if (add_class == "slider_style"){
                            self.$modal.find('.product_limit_one_slide').removeClass('d-none')
                            self.$modal.find('.column_limit').addClass('d-none')
                            self.$modal.find(".card_style").removeClass('d-none')
                            self.$modal.find(".product_slider_description").removeClass('d-none')
                            self.$modal.find("a[display_options=show_description]").removeClass('d-none active')
                            self.$modal.find(".product_preview").removeClass('show_description')
                            self.$modal.find('.slider_autoslide').removeClass('d-none')
                            // self.$modal.find('.slider_slidespeed').removeClass('d-none')
                        }
                        if (add_class == "list_style"){
                            self.$modal.find('.product_limit_one_slide').addClass('d-none')
                            self.$modal.find('.column_limit').addClass('d-none')
                            self.$modal.find(".card_style").addClass('d-none')
                            self.$modal.find(".product_slider_description").addClass('d-none')
                            self.$modal.find("a[display_options=show_description]").addClass('d-none')
                            self.$modal.find(".product_preview").removeClass('show_description')
                            self.$target.removeClass('show_description')
                            self.$modal.find('.slider_autoslide').addClass('d-none')
                            self.$modal.find('.slider_slidespeed').addClass('d-none')
                        }
                        if (add_class == "list_slider_style"){
                            self.$modal.find('.product_limit_one_slide').addClass('d-none')
                            self.$modal.find('.column_limit').addClass('d-none')
                            self.$modal.find(".card_style").addClass('d-none')
                            self.$modal.find(".product_slider_description").removeClass('d-none')
                            self.$modal.find("a[display_options=show_description]").removeClass('d-none')
                            self.$target.removeClass('show_description')
                            self.$modal.find('.slider_autoslide').removeClass('d-none')
                            // self.$modal.find('.slider_slidespeed').removeClass('d-none')
                        }
                    }

                    if($(this).attr('data-select-layout-class')){
                        var add_class = $(this).attr('data-select-layout-class');
                        self.$target.removeClass('layout_style_1 layout_style_2 layout_style_3')
                        self.$target.addClass(add_class);
                        self.$modal.find('.product_preview').removeClass('layout_style_1 layout_style_2 layout_style_3')
                        self.$modal.find('.product_preview').addClass(add_class);
                    }

                    if($(this).attr('data-select-card-class')){
                        var add_class = $(this).attr('data-select-card-class');
                        self.$target.removeClass('vertical_card horizontal_card')
                        self.$target.addClass(add_class);
                        self.$modal.find('.product_preview').removeClass('vertical_card horizontal_card')
                        self.$modal.find('.product_preview').addClass(add_class);
                    }

                    if($(this).attr('product-limit')){
                        var add_class = $(this).attr('product-limit');
                        self.$target.attr('product_limit',add_class);
                    }

                    if($(this).attr('one_slide_limit')){
                        var add_class = $(this).attr('one_slide_limit');
                        self.$target.attr('one_slide_limit',add_class);
                    }

                    if($(this).attr('column_limit')){
                        var add_class = $(this).attr('column_limit');
                        self.$target.attr('column_limit',add_class);
                    }

                    if($(this).attr('slider_speed')){
                        var add_class = $(this).attr('slider_speed');
                        self.$target.attr('slider_speed',add_class);
                    }

                    if($(this).attr('autoslide')){
                        var add_class = $(this).attr('autoslide');
                        self.$target.attr('autoslide',add_class);
                    }
                });

                $('.product_configurator_option .display-btns .btn').on('click', function() {
                    var add_class = $(this).attr('display_options');
                    if($(this).hasClass('active')){
                        $(this).removeClass('active');
                        self.$target.removeClass(add_class);
                        self.$modal.find('.product_preview').removeClass(add_class);
                    } else{
                        $(this).addClass('active');
                        self.$target.addClass(add_class);
                        self.$modal.find('.product_preview').addClass(add_class);
                    }
                });

                self.$modal.find("#remove_modal").on('click', function() {
                    $('body').removeClass('modal-open')
                    self.$target.replaceWith(saved_config_html);
                    $(this).parent().parent().parent().parent().parent().find('.modal-backdrop').remove()
                    $(this).parent().parent().parent().parent().remove()
                });
                $('.modal_shown').on("click", function(e) {
                    if (!$(e.target).closest('.modal-dialog').length) {
                        if($(e.target).hasClass('modal_shown')){
                            $(e.target).remove()
                            self.$target.replaceWith(saved_config_html);
                        }
                    }
                });

                $pro_sub_data.on('click', function() {
                    // self.find('.product_configurator_content').remove();
                    // save button par default class remove karvano: upr varo
                    var checkbox_checked = self.$modal.find(".form-check-input:checked")
                    self.$target.attr('product_id'," ")
                    $(checkbox_checked).each(function(){
                        var current_id = self.$target.attr('product_id');
                        var new_id = this.value
                        self.$target.attr('product_id', new_id+','+current_id)
                    });
                    $('body').removeClass('modal-open')
                    $(this).parent().parent().parent().parent().parent().find('.modal-backdrop').remove()
                    $(this).parent().parent().parent().parent().remove()
                });
                $product_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                });
            } else {
                return;
            }
        },
    });
});