odoo.define('theme_decor.biz_quickview', function(require){
'use strict';

require('web.dom_ready');
var publicWidget = require('web.public.widget');
var core = require('web.core');
var ajax = require('web.ajax');
var rpc = require('web.rpc');
var _t = core._t;


var publicWidget = require('web.public.widget');

publicWidget.registry.websiteSaleCategoryMobile = publicWidget.Widget.extend({
    selector: '#o_shop_collapse_category_mobile',
    events: {
        'click .fa-chevron-right': '_onOpenClick',
        'click .fa-chevron-down': '_onCloseClick',
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onOpenClick: function (ev) {
        var $fa = $(ev.currentTarget);
        $fa.parent().siblings().find('.fa-chevron-down:first').click();
        $fa.parents('li').find('ul:first').show('normal');
        $fa.toggleClass('fa-chevron-down fa-chevron-right');
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onCloseClick: function (ev) {
        var $fa = $(ev.currentTarget);
        $fa.parent().find('ul:first').hide('normal');
        $fa.toggleClass('fa-chevron-down fa-chevron-right');
    },
});


publicWidget.registry.decorModalPopups = publicWidget.Widget.extend({
    selector: "#wrapwrap",
    events: {
        "click a.quick_btn,button.quick_btn": "_prodqvopen",
        "click a.select_btn": "_prodsvopen",
    },
    _prodqvopen: function(ev) {
        var self = this;
        var pid = $(ev.currentTarget).attr('data-product_template_id');
        window.quick_btn = $(ev.currentTarget);
        var config = window.quick_btn.parents('.bizople_product_configurator');
        if(config.length > 0){
            window.quick_btn_config = window.quick_btn.parents('.product_preview').find('.ajax-cart-modal');
        }
        else{
            window.quick_btn_config = window.quick_btn.parents('form').prev('.ajax-cart-modal');
        }
        var domain_url = encodeURIComponent(window.location.origin);
        
        ajax.jsonRpc('/get_prod_quick_view_details', 'call', {'prod_id':pid, 'href':domain_url}).then(function(data) 
        {
            $(".quick_modal_wrap").append(data);
            self.trigger_up('widgets_start_request', {
                $target: $(".quick_modal_wrap")
            });
            $(".quick-modal-backdrop").fadeIn();
            $(".quick_modal_wrap").css("display", "block");
            $("[data-attribute_exclusions]").trigger('change');
            $("[data-attribute_exclusions]").on('change', function(event) {
                setTimeout(function(){
                    $('.lazyload').lazyload();
                }, 1000);
            });

            $(".quick_close").click(function() {
                $('.quick_modal_wrap').empty(data);
                $('.zoomContainer').remove();
            });
            $('.lazyload').lazyload();
        });
    },
    _prodsvopen: function(ev) {
        var self = this;
        var pid = $(ev.currentTarget).attr('data-product_template_id');
        window.select_btn = $(ev.currentTarget);
        ajax.jsonRpc('/get_prod_select_option_details', 'call', {'prod_id':pid}).then(function(data) 
        {
            $(".quick_modal_wrap").append(data);
            self.trigger_up('widgets_start_request', {
                $target: $(".quick_modal_wrap")
            });
            $(".select-modal-backdrop").fadeIn();
            $(".quick_modal_wrap").css("display", "block");
            $("[data-attribute_exclusions]").trigger('change');
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

            $(".select_close").click(function() {
                $('.quick_modal_wrap').empty(data);
                $('.zoomContainer').remove();
            });
            $('.lazyload').lazyload();
        });
    },
})

var publicWidget = require("web.public.widget");

    publicWidget.registry.openpop = publicWidget.Widget.extend({
        "selector": "#wrapwrap",
        "events":{
            "click .openpop":"_openSignuppopup",
            "click .resetbtn":"_resetForm",
            "click .respass":"_resetPassword",
            "click .loginbtn":"_oauth",
            "click .alreadyuser":"_backToLogin",
            "click .signupbtn":"_userSignup",
            "click .createbtn":"_createAcc"
            
        },
        _resetPassword:function(ev){
            if($("#resetlogin").val().trim() != ""){
                ev.preventDefault();
                return this._rpc({
                    route: "/ajax/web/reset_password",
                    params: {
                            "login":$("#resetlogin").val(),
                        }
                }).then(function (result) {
                    if("error" in result){
                        $("#error").css("display","block").empty().append(result["error"]);
                    }
                    else if ("message" in result){
                        $("#reset_form").css("display","none");
                        $("#msgbox").css("display","block");
                        $("#messager").empty().append(result["message"]);
                    }
                });
            }
        },
        _resetForm:function(){
            $("#nav-reset-tab").click();
        },
        _createAcc:function(){
            $("#nav-register-tab").click();
        },
        _userSignup:function(ev){
            if($("#logins").val().trim() != "" && $("#passwords").val().trim() != ""
                && $("#confirm_passwords").val().trim() != "" && $("#names").val().trim() != ""){
                ev.preventDefault();
                return this._rpc({
                    route: "/ajax/signup/",
                    params: {
                            "login":$("#logins").val(),
                            "name":$("#names").val(),
                            "password":$("#passwords").val(),
                            "confirm_password":$("#confirm_passwords").val(),
                            "token":$("#token").val()
                        }
                }).then(function (result) {
                    if("error" in result){
                        $("#errors").css("display","block").empty().append(result["error"])
                    }
                    else if(result["signup_success"] == true){
                        window.location.reload();
                    }
                });
            }
        },
        _backToLogin:function(){
            $("#nav-login-tab").click();
        },
        _openSignuppopup:function(evt){
            var theme_name = $(evt.currentTarget).attr('data-theme_name');
            return this._rpc({
                route: "/ajax/login/",
                params: {'theme_name':theme_name}
            }).then(function (result) {
                $("#nav-login").empty().append(result["loginview"]);
                $("#nav-login-tab").click();
                // $(".blured-bg").addClass("active");
                if("signupview" in result){
                    $("#nav-register").empty().append(result["signupview"]);
                }
                if("resetview" in result){
                    $("#nav-reset").empty().append(result["resetview"]);
                }
    
            });
        },
        _oauth:function(ev){
            if($("#login").val().trim() != "" && $("#password").val().trim() != ""){
                ev.preventDefault();
                return this._rpc({
                    route: "/ajax/web/login",
                    params: {
                            "login":$("#login").val(),
                            "password":$("#password").val()
                            }
                }).then(function (result) {
                    if(result["login_success"] == true){
                        window.location.reload();
                    }
                    else if("error" in result){
                        $("#errormsg").css("display","block").empty().append(result["error"]);
                    }
                });
            }
        }
    });

publicWidget.registry.infinite_load = publicWidget.Widget.extend({
    selector: ".infinite_loader_div",
    events: {
        'click .infinite_load_button': 'startLoadMoreNextClick',
        'click .infinite_load_button_top': 'startLoadMorePrevClick',
    },
    start: function () {
        var self = this;
        self.startLoadMore();
        var total_product_count = $(".infinite_load_next_page").attr('all-products');
    },
    startLoadMore: function () {
        var next_call = true;
        var prev_call = true;
        var self = this;
        $('#wrapwrap').scroll(function() {
            var scrollTop = $('#wrapwrap').scrollTop();
            var page_url = $(".infinite_load_next_page").attr('next-page-url');
            var prev_page_url = $(".infinite_load_next_page").attr('prev-page-url');
            var first_page_url = $(".infinite_load_next_page").attr('first-page-url');
            var last_page_url = $(".infinite_load_next_page").attr('last-page-url');
            var current_url = $(".infinite_load_next_page").attr('current-page-url');
            var next_page_num = $(".infinite_load_next_page").attr('next-page-num');
            var prev_page_num = $(".infinite_load_next_page").attr('prev-page-num');
            var total_page = $(".infinite_load_next_page").attr('total-page');
            if ($(".decor_shop").hasClass("decor_shop")) {
                var trigger_element = document.querySelector('.decor_bottom_pager');
                var position = trigger_element.getBoundingClientRect();
            }else {
                var position = -1;
            }


            if(position.top >= 0 && position.bottom <= window.innerHeight) {
                if(next_call && current_url != last_page_url){
                    next_call = false;
                    $.ajax({
                        url: page_url,
                        type: 'GET',
                        beforeSend: function(){
                            $(".infinite_loader_div_next").removeClass("d-none");
                        },
                        success: function(data) {
                            $(".infinite_loader_div_next").addClass("d-none");
                            var data_replace = null;

                            var new_page_url = $(data).find('.infinite_load_next_page').attr('next-page-url');
                            $(".infinite_load_next_page").attr('next-page-url',new_page_url);

                            var next_page_num = $(data).find('.infinite_load_next_page').attr('next-page-num');
                            $(".infinite_load_next_page").attr('next-page-num',next_page_num);

                            data_replace = $(data).find("#products_grid .o_wsale_products_grid_table_wrapper tr");
                            if(data_replace){
                                $("#products_grid tbody").append(data_replace);
                            }
                            if(last_page_url !=  page_url)
                            {
                                $("ul.pagination li:last").removeClass("disabled");
                                next_call = true;
                            }else {
                                $("ul.pagination li:last").addClass("disabled");
                            }
                            $("ul.pagination li:first-child").removeClass("disabled");
                            var update_pre_page = $(data).find('.infinite_load_next_page').attr('prev-page-url');
                            $("ul.pagination li:first-child a").attr("href",update_pre_page);
                            $("ul.pagination li:last a").attr("href",new_page_url);

                            var active_page = $(data).find(".infinite_load_next_page").attr('page-number');
                            $("ul.pagination li").removeClass("active");
                            $("ul.pagination li:contains("+active_page+")").addClass("active");

                            var current_page_num = $(data).find(".infinite_load_next_page").attr('current-page-number');
                            $(".infinite_load_next_page").attr('current-page-number',current_page_num);

                            var current_page = $(data).find(".infinite_load_next_page").attr('current-page-url');
                            window.history.replaceState(null, null, current_page);

                            if(current_page_num >= total_page) {
                                $('.infinite_load_button').removeClass('active');
                            }
                            $('.lazyload').lazyload();
                        }
                    });
                }
            }
            if($("#products_grid tbody tr:first").length && scrollTop <= 0)
            {
                if(prev_call && current_url != first_page_url){
                    prev_call = false;
                    $.ajax({
                        url: prev_page_url,
                        type: 'GET',
                        beforeSend: function(){
                            $(".infinite_loader_div").removeClass("d-none");
                        },
                        success: function(data) {
                            $(window).scrollTop(100);
                            $(".infinite_loader_div").addClass("d-none");
                            var data_replace = null;

                            var new_prev_page_url = $(data).find('.infinite_load_next_page').attr('prev-page-url');
                            $(".infinite_load_next_page").attr('prev-page-url',new_prev_page_url);

                            var new_prev_page_num = $(data).find('.infinite_load_next_page').attr('prev-page-num');
                            $(".infinite_load_next_page").attr('prev-page-num',new_prev_page_num);

                            data_replace = $(data).find("#products_grid .o_wsale_products_grid_table_wrapper tr");
                            if(data_replace){
                                $("#products_grid tbody").prepend(data_replace);
                            }

                            var active_page = $(data).find(".infinite_load_next_page").attr('page-number');
                            var current_page_num = $(data).find(".infinite_load_next_page").attr('current-page-number');
                            $(".infinite_load_next_page").attr('current-page-number',current_page_num);
                            $("ul.pagination li").removeClass("active");
                            $("ul.pagination li:contains("+active_page+")").addClass("active");

                            var current_page = $(data).find(".infinite_load_next_page").attr('current-page-url');
                            window.history.replaceState(null, null, current_page);
                            if(first_page_url != prev_page_url)
                            {
                                $("ul.pagination li:first-child").removeClass("disabled");
                                prev_call = true;
                            }else {
                                $("ul.pagination li:first-child").addClass("disabled");
                            }
                            $("ul.pagination li:last-child").removeClass("disabled");
                            var update_next_page = $(data).find('.infinite_load_next_page').attr('next-page-url');
                            $("ul.pagination li:first-child a").attr("href",update_next_page);

                            $("ul.pagination li:last-child a").attr("href",new_prev_page_url);

                            if(current_page_num < 2) {
                                $('.infinite_load_button_top').removeClass('active');
                            }
                            $('.lazyload').lazyload();
                        }
                    });
                }
            }
        });
    },
    
});
return {
    infinite_load : publicWidget.registry.infinite_load,
    openpop : publicWidget.registry.openpop,
    websiteSaleCategoryMobile : publicWidget.registry.websiteSaleCategoryMobile,
}


});
