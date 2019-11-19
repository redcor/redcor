odoo.define('website_custom_home.website', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var Widget = require('web.Widget');
var session = require('web.session');
var base = require('web_editor.base');
var Tour = require('web.Tour');

var qweb = core.qweb;
var _t = core._t;
base.url_translations = '/website/translations';

$(document).ready(function () {
    if (navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1) {
        /*Here we are in Safary Browser*/
        $("#topnavbar .container").css({"padding-left": "20px !important"});
        $(".event-body ul").css({"padding-left": "16px !important"});
    }
    //The params set when document ready
    if ($(document).find('#oe_main_menu_navbar').length == 0){
        $("#navbrs").css({"display":"none"});
        $('#topnavbar').css({"position":"fixed"});
        $("#banner").css({"margin-top":"126px"});
        $(".s_big_message").css({"margin-top":"40px"});
        $(".list-group").addClass("hamburger-fix");
//        $(".exceptHome").css({"margin-top":"123px"});
        if ($(document).find('.wrapper').length == 1){
            /*HomePage*/
            $(".exceptHome").remove();
            $("#backbutton").css({"display":"none"});
        }
        var viewportWidth = $(window).width();
        if (viewportWidth <= 320){
            $(".positionR").css({"margin-top":"163px"});
        }
        else if (viewportWidth <= 360 && viewportWidth > 320){
            $(".positionR").css({"margin-top":"170px"});
        }
        else if (viewportWidth <= 375 && viewportWidth > 360){
            $("#banner").css({"margin-top":"175px"});
            if ($(document).find('#banner').length){
                $(".positionR").css({"margin-top":"0px"});
            }
            else{
                $(".positionR").css({"margin-top":"163px"});
            }
        }
        else if (viewportWidth <= 414 && viewportWidth > 375){
            $("#banner").css({"margin-top":"175px"});

            if ($(document).find('#banner').length){
                $(".positionR").css({"margin-top":"0px"});
            }
            else{
                $(".positionR").css({"margin-top":"167px"});
            }
        }
        else if (viewportWidth <= 480 && viewportWidth > 414){
            $("#banner").css({"margin-top":"175px"});
            $(".positionR").css({"margin-top": "0px"});
        }
        else if (viewportWidth <= 767 && viewportWidth > 480){
                $(".positionR").css({"margin-top":"0px"});
                $(".exceptHome").css({"margin-top":"123px"});
                if (! $(document).find('#banner').length){
                    $(".positionR").css({"margin-top":"123px"});
                }
        }
        else if (viewportWidth <= 991 && viewportWidth > 767){
            if (! $(document).find('#banner').length){
                    $(".positionR").css({"margin-top":"140px"});
                }
            else{
                $(".positionR").css({"margin-top":"0px"});
            }

        }
        else if (viewportWidth > 1199){
            if (! $(document).find('#banner').length){
                    $(".positionR").css({"margin-top":"140px"});
                }
            else{
                $(".positionR").css({"margin-top":"0px"});
            }
        }
    }
    else if (parseInt($(document).find('#oe_main_menu_navbar').length)){
    //initial
        $('#banner').addClass("hidden");
        $('.top-menu.list-inline.js_language_selector.mt16').addClass("visible-xs");
        if ($(document).find('.wrapper').length == 1){
                /*HomePage*/
                    $(".exceptHome").remove();
                    $("#backbutton").css({"display":"none"});
                    }

        var viewportWidth = $(window).width();
        if (viewportWidth <= 400 && viewportWidth > 375){
            if (($(document).find('#oe_main_menu_navbar').length) == 1){
                $(".positionR").css({"margin-top":"175px"});
                $(".mini-submenu").css({"top":"-9px"});
            }
            else{
                $(".positionR").css({"margin-top":"0"});
            }
        }
        if (viewportWidth <= 414 && viewportWidth > 400){
            if (($(document).find('#oe_main_menu_navbar').length) == 1){
                $(".positionR").css({"margin-top":"175px"});
                $(".mini-submenu").css({"top":"-8px"});
            }
            else{
                $(".positionR").css({"margin-top":"0"});
            }
        }
        if (viewportWidth <= 480 && viewportWidth > 414){
            if (($(document).find('#oe_main_menu_navbar').length) == 1){
                $(".positionR").css({"margin-top":"167px"});
                $(".mini-submenu").css({"top":"0px"});
            }
            else{
                $(".positionR").css({"margin-top":"0"});
            }
        }
        else if (viewportWidth <= 320){

            $(".positionR").css({"margin-top":"163px"});
            $(".mini-submenu").css({"top":"-6px"});

        }
        else if (viewportWidth <= 375 && viewportWidth > 320){
            if (($(document).find('#oe_main_menu_navbar').length) == 0 && (! $(document).find('#banner').length)){
                    $(".positionR").css({"margin-top":"163px"});
                    $(".mini-submenu").css({"top":"-2px"});
                }
                else{
                    $(".mini-submenu").css({"top":"0px"});
                    $(".positionR").css({"margin-top":"163px"});
                }
        }
        else if (viewportWidth <= 767 && viewportWidth > 480){
            if (($(document).find('#oe_main_menu_navbar').length) == 1){
                $(".positionR").css({"margin-top":"123px"});
            }
            else{
                if (! $(document).find('#banner').length){
                    $(".positionR").css({"margin-top":"123px !important"});
                }
                else{
                $(".positionR").css({"margin-top":"0"});
                }
            }
        }
        else if (viewportWidth <= 991 && viewportWidth > 767){
        if (! $(document).find('#banner').length){
            $(".positionR").css({"margin-top":"140px !important"});
            }
            else{
            $(".positionR").css({"margin-top":"0"});
            }

        }
    }
    /*.........................................................................................*/
    /*Function when scrolling to fix nav bar and hamburger*/
    $(window).on("resize scroll",function(e){
        var s = $("#sticker");
        var pos = s.position();
        var viewportWidth = $(window).width();
        var windowpos = $(window).scrollTop();
        var scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        if ($(this).scrollTop() >= 50) {        // If page is scrolled more than 50px
            $('#return-to-top').fadeIn(200);    // Fade in the arrow
        } else {
            $('#return-to-top').fadeOut(200);   // Else fade out the arrow
        }
        if ($(document).find('#oe_main_menu_navbar').length == 0){
            /*logout*/
            if (pos && ($(document).find('#banner').length) == 1){
                if (viewportWidth <= 360 && scrollTop > 0){
                    s.addClass("stick sticklogout");
                }
                else if (viewportWidth <= 480 && viewportWidth > 360 && scrollTop > 169){
                    s.addClass("stick sticklogout");
                }
                else if (viewportWidth <= 560 && viewportWidth > 480 && scrollTop > 160){
                    s.addClass("stick sticklogout");
                }
                else if(viewportWidth <= 991 && viewportWidth > 480 && scrollTop > 210) {//208
                    s.addClass("stick sticklogout");

                }
                else if(viewportWidth <= 1199 && viewportWidth > 991 && scrollTop > 278){
                    s.addClass("stick sticklogout");
                }
                else if (viewportWidth > 1199 && scrollTop > 0){
                    if($(document).find('.wrapper').length == 0){
                        if (viewportWidth > 1199 && scrollTop > 0){
                        s.addClass("stick sticklogout");
                        }
                    }
                    else if (viewportWidth > 1199 && scrollTop > 365){
                        s.addClass("stick sticklogout");
                    }
                    else {
                        s.removeClass("stick sticklogout");
                    }
                }
                else {
                    s.removeClass("stick sticklogout");
                }

            }
            else if(pos && ($(document).find('#banner').length) == 0){
                if (viewportWidth <= 360 && scrollTop > 0){
                    s.addClass("stick sticklogout");
                }
                else if (viewportWidth <= 375 && viewportWidth > 360 && scrollTop > 0){
                    s.addClass("stick sticklogout");
                }
                else if (viewportWidth <= 414 && viewportWidth > 375 && scrollTop > 0){
                    s.addClass("stick sticklogout");
                }
                else if (viewportWidth <= 480 && viewportWidth > 414 && scrollTop > 156){
                    s.addClass("stick sticklogout");
                }
                else if (viewportWidth <= 560 && viewportWidth > 480 && scrollTop > 160){
                    s.addClass("stick sticklogout");
                    $(".positionR").css({"margin-top":"123px"});
                }
                else if(viewportWidth <= 991 && viewportWidth > 480 && scrollTop > 0) {
                    s.addClass("stick sticklogout");
                    if (viewportWidth <= 767 && viewportWidth > 480){
                        $(".positionR").css({"margin-top":"123px"});
                    }
                    else if (viewportWidth <= 991 && viewportWidth > 767){
                        $(".positionR").css({"margin-top":"140px"});
                    }

                }
                else if(viewportWidth <= 1199 && viewportWidth > 991 && scrollTop > 278){
                    s.addClass("stick sticklogout");
                }
                else if (viewportWidth > 1199 && scrollTop > 0){
                    if($(document).find('.wrapper').length == 0){
                        if (viewportWidth > 1199 && scrollTop > 0){
                        s.addClass("stick sticklogout");
                        }
                    }
                    else if (viewportWidth > 1199 && scrollTop > 365){
                        s.addClass("stick sticklogout");
                    }
                    else {
                    s.removeClass("stick sticklogout");
                }
                }
                else {
                    s.removeClass("stick sticklogout");
                }
            }
        }
        else{
            /*......login......*/
            if (pos){
                if (viewportWidth <= 360 && scrollTop > 0){
                    s.addClass("stick sticklogin");
                    $(".positionR").css({"margin-top":"163px"});
                    $('#topnavbar').addClass('topnavbarfixed');
                }
                else if (viewportWidth <= 375 && viewportWidth > 360 && scrollTop > 0){
                    s.addClass("stick sticklogin");
                    $(".mini-submenu").css({"top":"0px"});
                    $('#topnavbar').addClass('topnavbarfixed');
                }
                else if (viewportWidth <= 480 && viewportWidth > 375 && scrollTop > 0){
                    s.addClass("stick sticklogin");
                    $('#topnavbar').addClass('topnavbarfixed');
                }
                else if(viewportWidth <= 767 && viewportWidth > 480 && scrollTop > 0) {
                    s.addClass("stick sticklogin");
                    $('#topnavbar').addClass('topnavbarfixed');
                    $(".positionR").css({"margin-top":"123px"});

                }
                else if(viewportWidth <= 991 && viewportWidth > 767 && scrollTop > 50) {
                    s.addClass("stick sticklogin");
                    $('#topnavbar').addClass('topnavbarfixed');
                    $(".positionR").css({"margin-top":"108px"});

                }
                else if(viewportWidth <= 1199 && viewportWidth > 991 && scrollTop > 24){
                    s.addClass("stick sticklogin");
                    $('#topnavbar').addClass('topnavbarfixed');
                    $("body").css({"margin-top":"100px"});
                }
                else if(viewportWidth > 1199 && scrollTop > 44){
                    $('#topnavbar').addClass('topnavbarfixed');
                    s.addClass("stick sticklogin");
                    $(".positionR").css({"margin-top":"89.97px"});//topnav 43.97 + 90 =144px/1
                }
                else {
                    s.removeClass("stick sticklogin");
                    $(".positionR").css({"margin-top":"123px"});
                    $('#topnavbar').removeClass('topnavbarfixed');
                    if ((viewportWidth > 480)){
                        $(".positionR").css({"margin-top":"0px"});
                    }
                    if ((viewportWidth <= 360 && viewportWidth > 0)){
                        $(".positionR").css({"margin-top":"163px"});
                    }
                    if ((viewportWidth <= 400 && viewportWidth > 360 && viewportWidth >= 361)){
                        $(".positionR").css({"margin-top":"175px"});
                        $(".mini-submenu").css({"top":"-13px"});
                    }
                    if ((viewportWidth <= 414 && viewportWidth > 400 && viewportWidth >= 400)){
                        $(".positionR").css({"margin-top":"169px"});
                        $(".mini-submenu").css({"top":"-2px"});
                    }
                    if ((viewportWidth <= 480 && viewportWidth > 414)){
                        $(".positionR").css({"margin-top":"175px"});
                        $(".mini-submenu").css({"top":"-2px"});
                    }
                }
            }
            else {
                if (viewportWidth <= 360 && scrollTop > 0){
                    $("body").css({"margin-top":"155px"});
                    $('#topnavbar').addClass('topnavbarfixed');
                    }
                else if (viewportWidth <= 480 && viewportWidth > 360 && scrollTop > 44){
                    $("body").css({"margin-top":"170px"});
                    $('#topnavbar').addClass('topnavbarfixed');
                }
                else if(viewportWidth <= 767 && viewportWidth > 480 && scrollTop > 0) {
                    $("body").css({"margin-top":"120px"});
                    $('#topnavbar').addClass('topnavbarfixed');
                }
                else if(viewportWidth <= 991 && viewportWidth > 767 && scrollTop > 20) {
                    $("body").css({"margin-top":"100px"});
                    $('#topnavbar').addClass('topnavbarfixed');
                }
                else if(viewportWidth <= 1199 && viewportWidth > 991 && scrollTop > 24){
                    $("body").css({"margin-top":"120px"});
                    $('#topnavbar').addClass('topnavbarfixed');
                }
                else if(viewportWidth > 1199 && scrollTop > 24){
                    $("body").css({"margin-top":"90px"});
                    $('#topnavbar').addClass('topnavbarfixed');
                }
                else {
                    s.removeClass("stick sticklogin");
                    $("body").css({"margin-top":"0px"});
                    $('#topnavbar').removeClass('topnavbarfixed');
                }
            }
        }
    });
    $('#return-to-top').click(function() {      // When arrow is clicked
        $('body,html').animate({
            scrollTop : 0                       // Scroll to top of body
        }, 500);
    });
    var overlay = $('.overlay');
    $('#slide-submenu').on('click', function () {
        $('.mini-submenu').fadeIn();
        overlay.hide();
        $(this).closest('.list-group').hide('slideInLeft', function () {
            $('#association').css({"margin-top":"0px!important"});
        });
        return false;

    });
    $('.overlay').click(function () {
        $('.mini-submenu').fadeIn();
        overlay.hide();
        $('#slide-submenu').closest('.list-group').hide('slideInLeft', function () {
            $('#association').css({"margin-top":"0px !important"});
        });
        return false;
    });
    // Here we are detecting the device is touch enabled or not.
    // If touch enabled then we do the first click to dropdown the li and second for redirect.
    var isTouchDevice = 'ontouchstart' in document.documentElement;
    if (isTouchDevice){
        $('.afdrop').click(function(ev) {
          var clicks = $.parseJSON($(this).attr('data-clicks')); //should be a boolean , typecasts string to boolean.
          if (clicks) {
            window.location.href = $("a.list-group-item", this).attr('href'); //redirects to the link in case of second click.
          } else {
                ev.preventDefault(); //preventing the default link redirection.
                $('.afdrop').not(this).each(function(){ //here we are omitting the current selected li to listen the second click.
                     $(this).attr('data-clicks', false);
                });
          }
          $(this).attr('data-clicks', !clicks);
        });
    }
    else{
        $('.afdrop').click(function(ev) {
            window.location.href = $("a.list-group-item",this).attr('href');
        });
    }
    $('.mini-submenu').on('click', function () {
        $(this).next('.list-group').show('slideInLeft');
        $('.mini-submenu').hide();
//        $('#association').css({"margin-top":"-250px"});
        overlay.show();
        return false;
    })
    $('.afdrop').hover(function() {
       $(this).find('.sub-menu').stop(true, true).delay(100).slideToggle(400);
            }, function() {
               $(this).find('.sub-menu').stop(true, true).delay(100).slideUp(400);
            });
    });
    /*Image Grid*/
    $(function () {
       $('#ri-grid').gridrotator({
           animSpeed: 1500,
           animType: 'fadeInOut',
           interval : 3000,
           step : 1,
           w480 : {
                rows : 2,
                columns : 6
           },
           onhover: false
       });
    });
});