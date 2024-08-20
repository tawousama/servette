odoo.define('theme_decor.bizcommon_frontend_js', function(require) {
    'use strict';
    var animation = require('website.content.snippets.animation');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    var publicWidget = require('web.public.widget');
    	
    if ($('.product_description').length < 1) {
        $('#product_detail_tabs').find('li:first-child').find('.nav-link').addClass('active');
        var firstlink = $('#product_detail_tabs').find('li:first-child').find('.nav-link').attr('aria-controls');
        $('.product-tab .tab-pane').removeClass('active show');
        $('#'+ firstlink).addClass('active show');
    }

    animation.registry.theme_decor_image_hotspot = animation.Class.extend({
        selector: ".hotspot_dynamic",
        disabledInEditableMode: false,
        start: function() {
            var self = this.$target;
            if (this.editableMode) {
                self.find('.hotspot_info').removeClass('quick_btn')
            }
            if (!this.editableMode) {
                self.find('.hotspot_info').addClass('quick_btn')
            }
            
        },
    });

    animation.registry.product_configurator_dynamic_product = animation.Class.extend({
        selector: ".bizople_product_configurator",
        disabledInEditableMode: false,
        start: function() {
            var self = this.$target;
            if (this.editableMode) {
                // onclick function called on click of save button in edit mode and removes all sections with product configurator
                $('.o_we_website_top_actions form button.btn-primary').on("click",function () {
                    $('.bizople_product_configurator').find('[class*=container]').empty();
                });
                $("#wrap").addClass("o_editable");
            }
            if (!this.editableMode) {
                var product_id = self.attr('product_id');
                if(self.hasClass('grid_style')){
                    $.get("/theme_decor/get_product_configurator_grid_style", {
                        'product_id': self.attr('product_id') || '',
                        'product_limit': self.attr('product_limit') || 10,
                        'column_limit': self.attr('column_limit') || 4,
                        'config_title': self.attr('config_title') || '',
                    }).then(function(data) {
                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));
                        }
                    });
                }
                if(self.hasClass('list_style')){
                    $.get("/theme_decor/get_product_configurator_list_style", {
                        'product_id': self.attr('product_id') || '',
                        'product_limit': self.attr('product_limit') || 10,
                        'config_title': self.attr('config_title') || '',
                    }).then(function(data) {
                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));
                        }
                    });
                }
                if(self.hasClass('slider_style')){
                    $.get("/theme_decor/get_product_configurator_slider_style", {
                        'product_id': self.attr('product_id') || '',
                        'product_limit': self.attr('product_limit') || 10,
                        'config_title': self.attr('config_title') || '',
                        'config_slider_description': self.attr('config_slider_description') || '',

                    }).then(function(data) {
                        var one_slide_limit = self.attr('one_slide_limit');
                        if(one_slide_limit){
                            var one_slide_limit = one_slide_limit;
                        } else{
                            var one_slide_limit = 4;
                        }

                        var slider_speed = self.attr('slider_speed');
                        if(slider_speed){
                            var slider_speed = slider_speed;
                        } else{
                            var slider_speed = 4000;
                        }
                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));   
                        }
                        $('div#configurator-slider').owlCarousel({
                            margin: 30,
                            responsiveClass: true,
                            items: one_slide_limit,
                            loop: false,
                            dots:false,
                            rows: true,
                            rowsCount: 2,
                            rewind:true,
                            nav:true,
                            navText: [
                                '<i class="fa fa-angle-left" aria-hidden="true"></i>',
                                '<i class="fa fa-angle-right" aria-hidden="true"></i>'
                            ],
                            autoplay:true,
                            autoplayTimeout: slider_speed,
                            autoplayHoverPause:true,
                            responsive: {
                                0: {
                                    items: 1,
                                },
                                420: {
                                    items: 1,
                                },
                                768: {
                                    items: 3,
                                },
                                1000: {
                                    items: one_slide_limit,
                                },
                                1500: {
                                    items: one_slide_limit,
                                },
                            },
                        });
                        
                        setTimeout(function(){
                            var divWidth = self.find('.product-item .p-item-image a').width(); 
                            self.find('.product-item .p-item-image a').height(divWidth);
                        },400);
                    });
                }
                if(self.hasClass('list_slider_style')){
                    $.get("/theme_decor/get_product_configurator_list_slider_style", {
                        'product_id': self.attr('product_id') || '',
                        'product_limit': self.attr('product_limit') || 10,
                        'config_title': self.attr('config_title') || '',
                        'config_slider_description': self.attr('config_slider_description') || '',
                    }).then(function(data) {
                        var slider_speed = self.attr('slider_speed');
                        if(slider_speed){
                            var slider_speed = slider_speed;
                        } else{
                            var slider_speed = 4000;
                        }

                        var autoslide = self.attr('autoslide');
                        if(autoslide){
                            var autoslide = autoslide;
                        } else{
                            var autoslide = true;
                        }
                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));   
                        }
                        $('div#configurator-list-slider').owlCarousel({
                            margin: 0,
                            responsiveClass: true,
                            items: 1,
                            loop: false,
                            dots:false,
                            rows: true,
                            rowsCount: 2,
                            rewind:true,
                            nav:true,
                            navText: [
                                '<i class="fa fa-angle-left" aria-hidden="true"></i>',
                                '<i class="fa fa-angle-right" aria-hidden="true"></i>'
                            ],
                            autoplay: autoslide,
                            autoplayTimeout: slider_speed,
                            autoplayHoverPause:true,
                            responsive: {
                                0: {
                                    items: 1,
                                },
                                420: {
                                    items: 1,
                                },
                                768: {
                                    items: 1,
                                },
                                1000: {
                                    items: 1,
                                },
                                1500: {
                                    items: 1,
                                },
                            },
                        });
                        
                        if(autoslide == "false"){
                            self.find('div#configurator-list-slider').trigger('stop.owl.autoplay')
                        } else{
                            self.find('div#configurator-list-slider').trigger('play.owl.autoplay',[slider_speed])
                        }

                        setTimeout(function(){
                            var divWidth = self.find('.product-item .p-item-image a').width(); 
                            self.find('.product-item .p-item-image a').height(divWidth);
                        },400);
                    });
                }
                setTimeout(function(){
                    self.find('.o_add_compare span').on('hover', function () {
                        var compare_count = $('.o_comparelist_products')[0].childElementCount
                    });
                }, 10000);
            }
        },
    });

    animation.registry.category_configurator_dynamic_category = animation.Class.extend({
        selector: ".bizople_category_configurator",
        disabledInEditableMode: false,
        start: function() {
            var self = this.$target;
            if (this.editableMode) {

                // onclick function called on click of save button in edit mode and removes all sections with product configurator
                $('.o_we_website_top_actions form button.btn-primary').on("click",function () {
                    $('.bizople_category_configurator').find('[class*=container]').empty();
                });
                $("#wrap").addClass("o_editable");
            }
            if (!this.editableMode) {
                var category_id = self.attr('category_id');
                if(self.hasClass('grid_style')){
                    $.get("/theme_decor/get_category_configurator_grid_style", {
                        'category_id': self.attr('category_id') || '',
                        'category_limit': self.attr('category_limit') || 10,
                        'column_limit': self.attr('column_limit') || 4,
                        'config_title': self.attr('config_title') || '',
                    }).then(function(data) {
                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));
                        }
                    });
                }
                if(self.hasClass('list_style')){
                    $.get("/theme_decor/get_category_configurator_list_style", {
                        'category_id': self.attr('category_id') || '',
                        'category_limit': self.attr('category_limit') || 10,
                        'config_title': self.attr('config_title') || '',
                    }).then(function(data) {
                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));
                        }
                    });
                }
                if(self.hasClass('slider_style')){
                    $.get("/theme_decor/get_category_configurator_slider_style", {
                        'category_id': self.attr('category_id') || '',
                        'category_limit': self.attr('category_limit') || 10,
                        'config_title': self.attr('config_title') || '',
                        'config_slider_description': self.attr('config_slider_description') || '',
                    }).then(function(data) {
                        var one_slide_limit = self.attr('one_slide_limit');
                        if(one_slide_limit){
                            var one_slide_limit = one_slide_limit;
                        } else{
                            var one_slide_limit = 4;
                        }

                        var slider_speed = self.attr('slider_speed');
                        if(slider_speed){
                            var slider_speed = slider_speed;
                        } else{
                            var slider_speed = 4000;
                        }

                        var autoslide = self.attr('autoslide');
                        if(autoslide){
                            var autoslide = autoslide;
                        } else{
                            var autoslide = true;
                        }
                        
                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));   
                        }
                        $('div#configurator-slider').owlCarousel({
                            margin: 30,
                            responsiveClass: true,
                            items: one_slide_limit,
                            loop: false,
                            dots:false,
                            rows: true,
                            rowsCount: 2,
                            rewind:true,
                            nav:true,
                            navText: [
                                '<i class="fa fa-angle-left" aria-hidden="true"></i>',
                                '<i class="fa fa-angle-right" aria-hidden="true"></i>'
                            ],
                            autoplay:autoslide,
                            autoplayTimeout:slider_speed,
                            autoplayHoverPause:true,
                            responsive: {
                                0: {
                                    items: 1,
                                },
                                420: {
                                    items: 1,
                                },
                                768: {
                                    items: 3,
                                },
                                1000: {
                                    items: one_slide_limit,
                                },
                                1500: {
                                    items: one_slide_limit,
                                },
                            },
                        });

                        if(autoslide == "false"){
                            self.find('div#configurator-slider').trigger('stop.owl.autoplay')
                        } else{
                            self.find('div#configurator-slider').trigger('play.owl.autoplay',[slider_speed])
                        }
                    });
                }
            }
        },
    });

    animation.registry.brand_configurator_dynamic_brand = animation.Class.extend({
        selector: ".bizople_brand_configurator",
        disabledInEditableMode: false,
        start: function() {
            var self = this.$target;
            if (this.editableMode) {

                // onclick function called on click of save button in edit mode and removes all sections with product configurator
                $('.o_we_website_top_actions form button.btn-primary').on("click",function () {
                    $('.bizople_brand_configurator').find('[class*=container]').empty();
                });
                $("#wrap").addClass("o_editable");
            }
            if (!this.editableMode) {
                var brand_id = self.attr('brand_id');
                if(self.hasClass('grid_style')){
                    $.get("/theme_decor/get_brand_configurator_grid_style", {
                        'brand_id': self.attr('brand_id') || '',
                        'brand_limit': self.attr('brand_limit') || 10,
                        'column_limit': self.attr('column_limit') || 4,
                        'config_title': self.attr('config_title') || '',
                    }).then(function(data) {
                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));
                        }
                    });
                }
                
                if(self.hasClass('slider_style')){
                    $.get("/theme_decor/get_brand_configurator_slider_style", {
                        'brand_id': self.attr('brand_id') || '',
                        'brand_limit': self.attr('brand_limit') || 10,
                        'config_title': self.attr('config_title') || '',
                        'config_slider_description': self.attr('config_slider_description') || '',
                    }).then(function(data) {
                        var one_slide_limit = self.attr('one_slide_limit');
                        if(one_slide_limit){
                            var one_slide_limit = one_slide_limit;
                        } else{
                            var one_slide_limit = 4;
                        }

                        var slider_speed = self.attr('slider_speed');
                        if(slider_speed){
                            var slider_speed = slider_speed;
                        } else{
                            var slider_speed = 4000;
                        }

                        var autoslide = self.attr('autoslide');
                        if(autoslide){
                            var autoslide = autoslide;
                        } else{
                            var autoslide = true;
                        }

                        if (data) {
                            self.find('[class*=container]').empty();
                            $(data).appendTo(self.find('[class*=container]'));   
                        }
                        $('div#configurator-slider').owlCarousel({
                            margin: 10,
                            responsiveClass: true,
                            items: one_slide_limit,
                            loop: false,
                            dots:false,
                            rows: true,
                            rowsCount: 2,
                            rewind:true,
                            nav:true,
                            navText: [
                                '<i class="fa fa-angle-left" aria-hidden="true"></i>',
                                '<i class="fa fa-angle-right" aria-hidden="true"></i>'
                            ],
                            autoplay:autoslide,
                            autoplayTimeout:slider_speed,
                            autoplayHoverPause:true,
                            responsive: {
                                0: {
                                    items: 1,
                                },
                                420: {
                                    items: 1,
                                },
                                768: {
                                    items: 3,
                                },
                                1000: {
                                    items: one_slide_limit,
                                },
                                1500: {
                                    items: one_slide_limit,
                                },
                            },
                        });

                        if(autoslide == "false"){
                            self.find('div#configurator-slider').trigger('stop.owl.autoplay')
                        } else{
                            self.find('div#configurator-slider').trigger('play.owl.autoplay',[slider_speed])
                        }
                    });
                }
            }
        },
    });

    animation.registry.theme_decor_product_banner = animation.Class.extend({
        selector: ".bizople_product_banner",
        disabledInEditableMode: false,
        start: function() {
            var self = this.$target;
            if (this.editableMode) {
                self.find('.edit_mode_product_banner').removeClass('d-none');
                self.find('.product_banner_main_section').remove();
            }
            if (!this.editableMode) {
                self.find('.edit_mode_product_banner').addClass('d-none');
                var product_id = self.attr('data-prod-select-id');
                $.get("/theme_decor/get_product_banner_details_xml", {
                    'product_id': self.attr('data-prod-select-id') || '',
                }).then(function(data) {
                    if (data) {
                        self.find('.product_banner_main_section').remove();
                        $(data).appendTo(self.find('.container'));

                        $("[data-attribute_exclusions]").on('change', function(event) {
                            setTimeout(function(){
                                $('.lazyload').lazyload();
                            }, 1000);
                        });
                        $(".css_attribute_color input").click(function(event){   
                            setTimeout(function(){
                                $('.lazyload').lazyload();
                            }, 1000);
                        });
                        $('.lazyload').lazyload();
                    }
                });
            }
        }
    });
    
    animation.registry.s_bizople_theme_blog_slider_snippet = animation.Class.extend({
        selector: ".blog_slider_owl",
        disabledInEditableMode: false,
        start: function() {
            var self = this;
            if (this.editableMode) {
                var $blog_snip = $('#wrapwrap').find('#biz_blog_slider_snippet');
                var blog_name = _t("Blog Slider")
                
                _.each($blog_snip, function (single){
                    $(single).empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + blog_name + '</h3>\
                                                    </div>\
                                                </div>')
                });
            }
            if (!this.editableMode) {
                var slider_filter = self.$target.attr('data-blog-slider-type');
                $.get("/theme_decor/second_blog_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-blog-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".blog_slider_owl").removeClass('o_hidden');
                        ajax.jsonRpc('/theme_decor/blog_image_effect_config', 'call', {
                            'slider_filter': slider_filter
                        }).then(function(res) {
                            var BlogOwl = self.$target.find('#blog_2_owl_carosel-'+res.slider_id)
                            $(BlogOwl).owlCarousel({
                                margin: 30,
                                items: 3,
                                loop: false,
                                dots:false,
                                autoplay: res.auto_slide,
                                autoplayTimeout:res.auto_play_time,
                                autoplayHoverPause:true,
                                nav:true,
                                navText: [
                                    '<i class="fa fa-angle-left" aria-hidden="true"></i>',
                                    '<i class="fa fa-angle-right" aria-hidden="true"></i>'
                                ],
                                rewind:true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 1,
                                    },
                                    768: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: 3,
                                    },
                                    1500: {
                                        items: 3,
                                    }
                                },
                            });
                        });
                    }
                });
            }
        }
    });
    
    $(function() {
        $('#wrapwrap').scroll(function() {
            var changeprice = $('div#product_details .product_price').html();
            
            var cartheight = $('#wrapwrap').height() / 2 - 100;
            
            if ($(this).scrollTop() > cartheight) {
                $('.cart_product_sticky_section').addClass('d-block');
            } else {
                $('.cart_product_sticky_section').removeClass('d-block');
            }
            
            if( $( ".js_product.js_main_product" ).hasClass( "css_not_available" )){
               $('div#wrapwrap .cart_prod_name_price').html('');
               $(".cart_product_sticky_details .sticky_cart_button#add_to_cart, .cart_product_sticky_details .sticky_cart_button#buy_now").addClass('disabled');
            }
            else{
                $('div#wrapwrap .cart_prod_name_price').html(changeprice);
                $(".cart_product_sticky_details .sticky_cart_button#add_to_cart, .cart_product_sticky_details .sticky_cart_button#buy_now").removeClass('disabled');
            }

            $(".cart_product_sticky_details .sticky_cart_button #add_to_cart").click(function(){
                $("div#cart_product_sticky_details .js_product.js_main_product #add_to_cart").trigger( "click" );
                return false;
            });
            $(".product_details_sticky .sticky_cart_button #buy_now").click(function(){
                $("div#cart_product_sticky_details .js_product.js_main_product #buy_now").trigger( "click" );
                return false;
            });

        });
    });
});
