odoo.define('theme_decor.image_hotspot_options', function(require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    // ajax.loadXML('/theme_decor/static/src/xml/image_hotspot_info.xml', qweb);

    options.registry.add_hotshpot = options.Class.extend({
    	events:{
	        'click we-button.biz_add_hotspot':'_addHotspot',
	    },

	    _addHotspot: function () {
	    	var spot = '<div class="image_hotspot" data-prod-select-id="" style="margin-bottom:0; position: absolute; z-index: 1; top:50%;left: 50%;transform: translate(-50%, -50%);"><a class="hotspot_info" data-container="body" data-bs-toggle="popover"  data-bs-placement="bottom" data-bs-content="product_info" data-bs-html="true"><i class="fa fa-circle text-primary"></i></a></div>';
	    	this.$target.after(spot);

	    }
    });

    options.registry.hotspot_posi = options.Class.extend({
    	events:{
	        'change we-range.horizontal_posi':'_horizontalposi',
	        'change we-range.vertical_posi':'_verticalposi',
	        'click we-select.hotspot_info_type':'_hotspotinfotype',
	        'click we-button.show_preview':'_showstaticpreview',
	        'click we-button.select_hotspot_product':'_selectproductoption',
	    },

	    _horizontalposi: function () {
	    	var horizontal_posi = this.$target.attr('data-horizontal_posi');
	    	var horizontal_posi = horizontal_posi+'%';
	    	this.$target.css('left', horizontal_posi);
	    },

	    _verticalposi: function () {
	    	var vertical_posi = this.$target.attr('data-vertical_posi');
	    	var vertical_posi = vertical_posi+'%';
	    	this.$target.css('top', vertical_posi);
	    },

	    _hotspotinfotype: function () {
	    	if (this.$target.hasClass("hotspot_static")) {
	    		var static_info = $(qweb.render("theme_decor.static_image_hotspot_info"));
                this.$target.find('.static_image_hotspot_info').remove();
	    		static_info.appendTo(this.$target);
                var initial_static_data = this.$target.find(".static_image_hotspot_info").html();
                this.$target.find('.hotspot_info').attr('data-bs-content', '<div class="static_image_hotspot_info">'+initial_static_data+'</div>');
	    	}
	    },

	    _showstaticpreview: function () {
	    	if (this.$target.find(".static_image_hotspot_info").hasClass('show_edit')) {
	    		this.$target.find(".static_image_hotspot_info").removeClass('show_edit')
                var hotspot_btn = this.$target.find('.static_image_hotspot_info .hotspot-link > a');
                var hotspot_btn_style = this.$target.find('.static_image_hotspot_info .hotspot-link > a').attr('style');
                if($(hotspot_btn).find('font').length > 0){
                    var font_text = $(hotspot_btn).find('font').text();
                    var font_style = $(hotspot_btn).find('font').attr('style');
                    $(hotspot_btn).text(font_text);
                    if (hotspot_btn_style == undefined){
                        $(hotspot_btn).attr('style',font_style);
                    } else{
                        $(hotspot_btn).attr('style',hotspot_btn_style + font_style);
                    }
                }
                var static_data = this.$target.find(".static_image_hotspot_info").html();
                var static_data_bgcolor = this.$target.find(".static_image_hotspot_info").css('background-color');
                this.$target.find('.hotspot_info').attr('data-bs-content', '<div class="static_image_hotspot_info" style="background-color: '+static_data_bgcolor+'">'+static_data+'</div>');
	    	} else {
	    		this.$target.find(".static_image_hotspot_info").addClass('show_edit')
	    	}
	    },

	     _selectproductoption: function () {
	    	var self = this.$target;
            self.$modal = $(qweb.render("theme_decor.dynamic_image_hotspot_product_select"));
            self.$modal.appendTo('body');
            self.$modal.modal('show');
            var $dynamic_hotspot_product = self.$modal.find("#dynamic_hotspot_product"),
                $product_slider_cancel = self.$modal.find("#cancel"),
                $pro_sub_data = self.$modal.find("#prod_sub_data");

            ajax.jsonRpc('/theme_decor/hotspot_product_select', 'call', {}).then(function(res) {
                $('#dynamic_hotspot_product option[value!="0"]').remove();
                _.each(res, function(y) {
                    $("select[id='dynamic_hotspot_product'").append($('<option>', {
                        value: y["id"],
                        text: y["name"]
                    }));
                });
            });

            $pro_sub_data.on('click', function() {
                var target = this.$target;
            	self.attr('data-prod-select-id', $dynamic_hotspot_product.val());
            	var product_id = self.attr('data-prod-select-id');
                self.find('.static_image_hotspot_info').remove();
                self.find('.hotspot_info').removeAttr('data-bs-toggle');
                self.find('.hotspot_info').removeAttr('data-container');
                self.find('.hotspot_info').removeAttr('data-bs-placement');
                self.find('.hotspot_info').removeAttr('data-bs-content');
                self.find('.hotspot_info').removeAttr('data-bs-html');
                self.find('.hotspot_info').attr('data-product_template_id', product_id)
                /*$.get("/theme_decor/get_dynamic_hotspot_product_select", {
                    'select-product-id': self.attr('data-prod-select-id') || '',
                }).then(function(data) {
                	if (data) {
                        self.find('.static_image_hotspot_info').remove();
                        self.find('.dynamic_image_hotspot_info').remove();
                        self.find('.oe_structure').remove();
                        $(data).appendTo(self);
                        ajax.jsonRpc('/theme_decor/get_dynamic_hotspot_product_select_two', 'call', {
                            'product_id': product_id
                        }).then(function(res) {
                        	var prod_id = res.p_id;
                        	var prod_name = res.p_name;
                        	var prod_data = res.p_data;
                            var original_price = self.find('.dynamic_image_hotspot_info_price .original_price').text();
                            var discounted_price = self.find('.dynamic_image_hotspot_info_price .discounted_price').text();
                            
                            var image_url = '/web/image/product.template/'+prod_id+'/image_1920';
                            var image_link = '/shop/product/'+prod_id;
                            var show_link = '/shop/product/'+prod_id;
                        	var dynamic_data = '<div class="dynamic_image_hotspot_info"><div class="d-flex align-items-center"><div class="image-box me-2"><a class="image_link" href="'+image_link+'"><img class="image_url img img-fluid" style="max-width: 80px;" src="'+image_url+'"></img></a></div><div class="info-box me-2" style="width: max-content; flex-wrap: wrap;"><p class="mb-0 hotspot-title fw-bold">'+prod_name+'</p><p><span class="discountedprice">'+discounted_price+'</span><del class="originalprice text-primary">'+original_price+'</del></p><p class="hotspot-link mb-0"><a class="show_link" href="'+show_link+'">Shop Now</a></p></div></div></div>'
                        	self.find('.hotspot_info').attr('data-bs-content', dynamic_data);
                        	

                        });
                    }
                });*/
            });
            $product_slider_cancel.on('click', function() {
                self.getParent()._onRemoveClick($.Event("click"))
            });
	    },

    });

});    