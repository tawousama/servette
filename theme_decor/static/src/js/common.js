$('body').on('click', function (e) {
    $('[data-bs-toggle=popover]').each(function () {
        // hide any open popovers when the anywhere else in the body is clicked
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});

odoo.define('theme_decor.common', function(require){
    'use strict';
    
      require('web.dom_ready');
      var publicWidget = require('web.public.widget');
      var core = require('web.core');
      var ajax = require('web.ajax');
      var rpc = require('web.rpc');
      var _t = core._t;
    
    
      var publicWidget = require('web.public.widget');
    
      publicWidget.registry.shoppagejs = publicWidget.Widget.extend({
        selector: ".decor_shop",
        start: function () {
          $('.lazyload').lazyload();
    
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
    
        }
      });
      publicWidget.registry.productpage = publicWidget.Widget.extend({
        selector: "#product_detail",
        start: function () {
          setInterval(function(){
            $('.lazyload').lazyload();
          }, 1000);
        }
      });
    
    });

/* close popover end */


function openSearchPopup() {
    $(".search-box").addClass("open");
}

function CartSidebar() {
    $("#cart_sidebar").addClass("toggled");
}
