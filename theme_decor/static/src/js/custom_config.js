odoo.define('theme_decor.custom_config', function(require){
	'use strict';
	
	require('web.dom_ready');
	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	var ajax = require('web.ajax');
	var rpc = require('web.rpc');
	var _t = core._t;
	
	var publicWidget = require('web.public.widget');
	
	// When Slider Style in Product Configurator selected, ajax cart popup requires transform unset, that is added here
	publicWidget.registry.ProductConfigAjaxPopup = publicWidget.Widget.extend({
		selector: ".bizople_product_configurator, .bizople_product_banner",
		events: {
			'click .a-submit.ajax-cart-btn': '_AddClassOnClick',
			'click #cnt_shopping,.ajax-cart-modal .close': '_RemoveClassOnClick',
			'click .ajax-cart-modal': '_RemoveClassOnClickContent',
		},
		_AddClassOnClick: function (ev) {
			$('body').addClass('ajax-require-body');
			$(ev.currentTarget).parents('form').prev('.ajax-cart-modal').modal('show');
		},
		_RemoveClassOnClick: function () {
			$('body').removeClass('ajax-require-body');
		},
		_RemoveClassOnClickContent: function (ev) {
			if (!$(ev.currentTarget).closest('.modal-content').length) {
				$('body').removeClass('ajax-require-body');
			}
		},
	});
	
	publicWidget.registry.imghotspotpopover = publicWidget.Widget.extend({
		selector: ".image_hotspot",
		events: {
			'click .hotspot_info': '_openhotspotpopover',
		},
		
		init: function () {
			this._super.apply(this, arguments);
			this._popoverRPC = null;
		},
		start: function () {
			var popover_bg = this.$el.find(".static_image_hotspot_info").css('background-color');
			this.$el.find('.hotspot_info').popover({
				trigger: 'manual',
				animation: true,
				html: true,
				container: 'body',
				placement: 'bottom',
				trigger: 'focus',
				template: '<div class="popover hotspot-popover" style="background-color: '+popover_bg+'; border-color: '+popover_bg+'" role="tooltip"><div class="arrow" style="border-color: '+popover_bg+'"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
			});
			$("body").addClass("image_hotspot_active");
		},
		
		_openhotspotpopover: function (ev) {
			var self = this;
			$(this.selector).not(ev.currentTarget).popover('hide');
			self.$el.find('.hotspot_info').popover("show");
		}
	});
	
	publicWidget.registry.headerrelatedjs = publicWidget.Widget.extend({
		selector: "header.decor-header",
		start: function () {
			/*mbl btm bar start*/
			$("body").addClass("blured-bg");
			var size = $(window).width();
			if (size <= 992){
				$(function() {
					
					/*show bottom bar start*/
					$('#wrapwrap').scroll(function() {
						if ($(this).scrollTop() > 100) {
							$('.bizople-mbl-bottom-bar').addClass('show-bottom-bar');
						} else {
							$('.bizople-mbl-bottom-bar').removeClass('show-bottom-bar');
						}
					});
					/*show bottom bar start*/
					
					/*shop page hide shop menu from bottom bar start*/
					if ($('.decor_shop').hasClass('decor_shop')) {
						$('.bottom-bar-filter').removeClass('d-none');
						$('.bottom-bar-shop').addClass('d-none');
					}else {
						$('.bottom-bar-filter').addClass('d-none');
						$('.bottom-bar-shop').removeClass('d-none');
					}
					/*shop page hide shop menu from bottom bar end*/
				});
			}
			/*mbl btm bar end*/
			
			/*mbl btm bar extra menu start and sticky cart start*/
			$(".open-extra-menu").click(function() {
				if($('.extra-menu-bar').hasClass('open')){
					$(".extra-menu-bar").removeClass("open");
					$(".bottom-bar-extra-menu").removeClass("active");
					$(".cart_product_sticky_section").removeClass("goup");
				} else {
					$(".extra-menu-bar").addClass("open");
					$(".bottom-bar-extra-menu").addClass("active");
					$(".cart_product_sticky_section").addClass("goup");
				}
			});
			/*mbl btm bar extra menu start and sticky cart end*/
			
			/* header category menu start*/
			$(function() {
				var categ_target = $(".decor-header-category > li.dropdown-submenu > .nav-link > i.ti");
				var parent_categ = $(categ_target).parent().parent();
				if ($(categ_target).hasClass("ti")) {
					$(parent_categ).addClass('dropend');
				}
			});
			/* header category menu end*/
			
			/*header 2 search js start*/
			if (size <= 1400 && size > 992){
				$(function(){
					var to_toggle = $(".header-search-btn .bizople-search");
					$(".header-search-btn > button").click(function() {
						if($(to_toggle).hasClass('toggled')){
							$(to_toggle).removeClass("toggled");
						} else {
							$(to_toggle).addClass("toggled");
						}
					});
				});
			}
			/*header 2 search js end*/
			
			
			/*search popup start*/
			$(".close-search").click(function() {
				$(".search-box").removeClass("open");
			});
			/*search popup end*/
			
			function openSearchPopup() {
				$(".search-box").addClass("open");
			}
			
			/* menu sidebar js for ipad and mbl */
			$("#show-sidebar").on("click", function(e) {
				$(".sidebar-wrapper").addClass("toggled");
				$(".blured-bg").addClass("active");
				e.stopPropagation()
			});
			$("#show_header4_mbl_menu").on("click", function(e) {
				$(".sidebar-wrapper").addClass("toggled");
				$(".blured-bg").addClass("active");
				e.stopPropagation()
			});
			$(".bottom-show-sidebar").on("click", function(e) {
				$(".sidebar-wrapper").addClass("toggled");
				$(".blured-bg").addClass("active");
				e.stopPropagation()
			});
			$("#close_mbl_sidebar").on("click", function(e) {
				$(".sidebar-wrapper").removeClass("toggled");
				$(".blured-bg").removeClass("active");
				e.stopPropagation()
			});
			$(document).on("click", function(e) {
				if (!$(e.target).closest('.sidebar-wrapper').length) {
					$(".sidebar-wrapper").removeClass("toggled");
					$(".blured-bg").removeClass("active");
				}
			});
			
			$(document).on("click", function(e) {
				if (!$(e.target).closest('.category-sidebar').length) {
					$(".category-sidebar").removeClass("toggled");
					$(".blured-bg").removeClass("active");
				}
				if (!$(e.target).closest('.bizople-search-results').length) {
					$(".bizople-search-results").hide("dropdown-menu");
				}
				if (!$(e.target).closest('.bizople-search-text').length) {
					$(".bizople-search-text").hide("dropdown-menu");
				}
			});
			$("#categbtn-popup,#categbtn").on("click", function(e) {
				$(".bizople-search-results").hide("dropdown-menu");
				$(".bizople-search-text").hide("dropdown-menu");
			});
			
			/*header 4 sidebar*/
			$("#show_header4_menu").on("click", function(e) {
				$(".sidebar-wrapper.header4_sidebar").addClass("toggled");
				$(".blured-bg").addClass("active");
				e.stopPropagation()
			});
			$("#close_header4_sidebar").on("click", function(e) {
				$(".sidebar-wrapper.header4_sidebar").removeClass("toggled");
				$(".blured-bg").removeClass("active");
				e.stopPropagation()
			});
		}
	});
	
	publicWidget.registry.shoppagejs = publicWidget.Widget.extend({
		selector: ".decor_shop",
		events: {
			'click .decor_grid_button > .grid4': '_grid4',
			'click .decor_grid_button > .grid3': '_grid3',
			'click .decor_grid_button > .grid2': '_grid2',
			'click .decor_grid_button > .sale_list': '_salelist',
		},
		start: function () {
			$("body").addClass("blured-bg");
			/*brand check box */
			$("a.active").find('.mycheckbox').prop('checked', true);
			
			$('.lazyload').lazyload();
			/*brand check box end */
			
			// Price slider code start --- shoppage
			/* var minval = $("input#m1").attr('value'),
			maxval = $('input#m2').attr('value'),
			minrange = $('input#ra1').attr('value'),
			maxrange = $('input#ra2').attr('value'),
			website_currency = $('input#decor_website_currency').attr('value');
			if (!minval) {
				minval = 0;
			}
			if (!maxval) {
				maxval = maxrange;
			}
			if (!minrange) {
				minrange = 0;
				
			}
			if (!maxrange) {
				maxrange = 2000;
			}
			
			$("div#priceslider").ionRangeSlider({
				keyboard: true,
				min: parseInt(minrange),
				max: parseInt(maxrange),
				type: 'double',
				from: minval,
				skin: "square",
				to: maxval,
				step: 1,
				prefix: website_currency,
				grid: true,
				onFinish: function(data) {
					$("input[name='min1']").attr('value', parseInt(data.from));
					$("input[name='max1']").attr('value', parseInt(data.to));
					$("div#priceslider").closest("form").submit();
				},
			}); */
			// Price slider code end --- shoppage
			
			/* Product hover image js start */
			setInterval(function(){
				$(".product_extra_hover_image").hover(function(){
					var product_id = $(this).find('.has_extra_hover_image .extra_hover_image').attr('productid');
					var target_image = $(this).find('.has_extra_hover_image .extra_hover_image img');
					$(target_image).attr('data-src', '/web/image/product.template/' + product_id +'/hover_image');
					$('.lazyload').lazyload();
				}, function(){
					var target_image = $(this).find('.has_extra_hover_image .extra_hover_image img');
					$(target_image).delay(200).attr('data-src', ' ');
				});
			}, 1000);
			/* Product hover image js end */
			
			/* add selector shop page start*/
			SetClass();
			
			function SetClass() {
				// before assigning class check local storage if it has any value
				$(".decor_shop #products_grid").addClass(localStorage.getItem("class"));
				ActiveClass();
			}
			var self = this;
			function ActiveClass() {
				if ($(".decor_shop #products_grid").hasClass("o_wsale_layout_list")) {
					$(".decor_product_pager .o_wsale_apply_layout .sale_list").addClass("active");
				}else if ($(".decor_shop #products_grid").hasClass("sale_layout_grid3"))  {
					$(".decor_product_pager .o_wsale_apply_layout .grid3").addClass("active");
				}else if ($(".decor_shop #products_grid").hasClass("sale_layout_grid4"))  {
					$(".decor_product_pager .o_wsale_apply_layout .grid4").addClass("active");
				}else if ($(".decor_shop #products_grid").hasClass("sale_layout_grid2"))  {
					$(".decor_product_pager .o_wsale_apply_layout .grid2").addClass("active");
				} else {
					$(".decor_product_pager .o_wsale_apply_layout .grid4").click();
				}
			}
			
			setTimeout(function(){
				$('#products_grid').fadeIn();
			}, 500);
			
			var size = $(window).width();
			if (size >= 1200){
				$(function() {
					if ( !$(".decor_shop #products_grid .grid4").hasClass("active") && !$(".decor_shop #products_grid .grid3").hasClass("active") && !$(".decor_shop #products_grid .grid2").hasClass("active") && !$(".decor_shop #products_grid .sale_list").hasClass("active")) {
						$(".decor_shop #products_grid .grid4").addClass("active");
					}
				});
			}
			if (size <= 1199){
				$(function() {
					if ( !$(".decor_shop #products_grid .grid3").hasClass("active") && !$(".decor_shop #products_grid .grid2").hasClass("active") && !$(".decor_shop #products_grid .sale_list").hasClass("active")) {
						$(".decor_shop #products_grid .grid3").addClass("active");
					}
				});
			}
			if (size <= 767){
				$(function() {
						$(".decor_shop #products_grid").removeClass("o_wsale_layout_list");
					
				});
			}
			
			/* add selector shop page end*/
			
			/* category sidebar js shop page */
			/* $(".filter_btn").on("click", function(e) {
				$(".category-sidebar").addClass("toggled");
				$(".mobile-categ-sidebar").addClass("toggled");
				$(".blured-bg").addClass("active");
				e.stopPropagation()
			}); */
			/* $(".bottom_bar_filter_button").on("click", function(e) {
				$(".category-sidebar").addClass("toggled");
				$(".mobile-categ-sidebar").addClass("toggled");
				$(".blured-bg").addClass("active");
				e.stopPropagation()
			}); */
			/* $("#category_close").on("click", function(e) {
				$(".category-sidebar").removeClass("toggled");
				$(".mobile-categ-sidebar").removeClass("toggled");
				$(".blured-bg").removeClass("active");
				e.stopPropagation()
			});
			$("#category_close_mobile").on("click", function(e) {
				$(".category-sidebar").removeClass("toggled");
				$(".mobile-categ-sidebar").removeClass("toggled");
				$(".blured-bg").removeClass("active");
				e.stopPropagation()
			});
			$(document).on("click", function(e) {
				if (!$(e.target).closest('.category-sidebar').length) {
					$(".category-sidebar").removeClass("toggled");
					$(".mobile-categ-sidebar").removeClass("toggled");
					$(".blured-bg").removeClass("active");
				}
			}); */
			/* category sidebar js end shop page */
			
			// shop page banner category slider start
			$("#decor_categ_slider").owlCarousel({
				autoPlay: 3000, //Set AutoPlay to 3 seconds
				responsiveClass: true,
				items : 5,
				loop: false,
				center: false,
				margin: 0,
				nav:true,
				navText: [
					'<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
					'<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
				],
				responsive: {
					0: {
						items: 3,
					},
					420: {
						items: 3,
					},
					768: {
						items: 3,
					},
					1024: {
						items: 5,
					},
					1200: {
						items: 5,
					},
					1400: {
						items: 5,
					},
				},
			});
			
			$("#decor_sub_categ_slider").owlCarousel({
				autoPlay: 3000, //Set AutoPlay to 3 seconds
				responsiveClass: true,
				items : 4,
				loop: false,
				center: false,
				margin: 0,
				nav:true,
				navText: [
					'<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
					'<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
				],
				responsive: {
					0: {
						items: 3,
					},
					420: {
						items: 3,
					},
					768: {
						items: 3,
					},
					1024: {
						items: 5,
					},
					1200: {
						items: 5,
					},
					1400: {
						items: 5,
					},
				},
			});
			
			// shop page banner category slider end
			
		},
		
		_grid4: function () {
			if ($(".decor_product_pager .o_wsale_apply_layout .grid4").hasClass("active")) {
				$(".decor_shop #products_grid").removeClass("sale_layout_grid4");
			}else {
				$(".decor_product_pager .o_wsale_apply_layout .grid4").addClass('active');
				$(".decor_shop #products_grid").addClass("sale_layout_grid4");
				localStorage.setItem("class", "sale_layout_grid4");
				$(".decor_shop #products_grid").removeClass("o_wsale_layout_list");
				$(".decor_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid3");
				$(".decor_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid2");
				$(".decor_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
			}
		},
		
		_grid3: function () {
			if ($(".decor_product_pager .o_wsale_apply_layout .grid3").hasClass("active")) {
				$(".decor_shop #products_grid").removeClass("sale_layout_grid3");
			}else {
				$(".decor_product_pager .o_wsale_apply_layout .grid3").addClass('active');
				$(".decor_shop #products_grid").addClass("sale_layout_grid3");
				localStorage.setItem("class", "sale_layout_grid3");
				$(".decor_shop #products_grid").removeClass("o_wsale_layout_list");
				$(".decor_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid4");
				$(".decor_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid2");
				$(".decor_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
			}
		},
		
		_grid2: function () {
			if ($(".decor_product_pager .o_wsale_apply_layout .grid2").hasClass("active")) {
				$(".decor_shop #products_grid").removeClass("sale_layout_grid2");
			}else {
				$(".decor_product_pager .o_wsale_apply_layout .grid2").addClass('active');
				$(".decor_shop #products_grid").addClass("sale_layout_grid2");
				localStorage.setItem("class", "sale_layout_grid2");
				$(".decor_shop #products_grid").removeClass("o_wsale_layout_list");
				$(".decor_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid4");
				$(".decor_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid3");
				$(".decor_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
			}
		},
		
		_salelist: function () {
			if ($(".decor_product_pager .o_wsale_apply_layout .sale_list").hasClass("active")) {
				$(".decor_shop #products_grid").removeClass("o_wsale_layout_list");
			}else {
				$(".decor_product_pager .o_wsale_apply_layout .sale_list").addClass('active');
				$(".decor_shop #products_grid").addClass("o_wsale_layout_list");
				localStorage.setItem("class", "o_wsale_layout_list");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid3");
				$(".decor_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid4");
				$(".decor_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
				$(".decor_shop #products_grid").removeClass("sale_layout_grid2");
				$(".decor_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
			}
		},
		
	});
	
	
	
	publicWidget.registry.productpageand404js = publicWidget.Widget.extend({
		selector: "#product_detail, .template_404_page",
		start: function () {
			/*product page highlight start*/
			$('[data-bs-toggle="popover"]').popover()
			/*product page highlight end*/
			
			/*404 page start try inherit */
			if($('.template_404_page').hasClass('template_404_page')){
				$('.template_404_page').parent().siblings('hr').addClass('d-none');
			}
			$("#product_details > form input[name=product_id]").on('change', function(event) {
				var product_var_id = $('#product_details > form input[name=product_id]').val()
				$('#product_details > .cart_product_sticky_section .cart_product_sticky_details input[name=product_id]').val(product_var_id)
			});
			/*404 page end*/
			/*var sale = new publicWidget.registry.WebsiteSale();
			$("[data-attribute_exclusions]").on('change', function(event) {
				setTimeout(function(){
					$('.lazyload').lazyload();
				}, 500);
			});
			$(".css_attribute_color input").click(function(event){   
				setTimeout(function(){
					$('.lazyload').lazyload();
				}, 500);
			});*/
			setInterval(function(){
				$('.lazyload').lazyload();
			}, 1000);
		}
	});
	
	publicWidget.registry.sliderjs = publicWidget.Widget.extend({
		selector: "#product_detail",
		
		start: function () {
			
			// accessories product slider js
			$("#vogue_accessory_product_slider").owlCarousel({
				margin: 20,
				dots: false,
				rewind: true,
				autoPlay: 3000, //Set AutoPlay to 3 seconds
				responsiveClass: true,
				items : 3,
				loop: false,
				nav:true,
				navText: [
					'<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
					'<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
				],
				responsive: {
					0: {
						items: 1,
					},
					420: {
						items: 1,
					},
					768: {
						items: 2,
					},
					1024: {
						items: 4,
					},
					1200: {
						items: 4,
					},
					1400: {
						items: 4,
					},
				},
			});
			
			// alternative product slider js
			$("#vogue_alternative_product_slider").owlCarousel({
				margin: 20,
				dots: false,
				rewind: true,
				autoPlay: 3000, //Set AutoPlay to 3 seconds
				responsiveClass: true,
				items : 3,
				loop: false,
				nav:true,
				navText: [
					'<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
					'<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
				],
				responsive: {
					0: {
						items: 1,
					},
					420: {
						items: 1,
					},
					768: {
						items: 2,
					},
					1024: {
						items: 3,
					},
					1200: {
						items: 3,
					},
					1400: {
						items: 3,
					},
				},
			});
		}
		
	});
	
});