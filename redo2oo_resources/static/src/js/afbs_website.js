// avoid beeing defined twice
try {  
    odoo.define('afbs_website.website', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var session = require('web.session');
    var base = require('web_editor.base');
    var Tour = require('web.Tour');
    var _t = core._t;
    base.url_translations = '/website/translations';
        $(document).ready(initPage);
        function initPage() {
            $("#srch-term").autocomplete({
                source: function(request, response) {
                    $.ajax({
                    url: "/search/cms/content",
                    method: "POST",
                    dataType: "json",
                    data: { name: request.term},
                    success: function( data ) {
                        response( $.map( data, function( item ) {
                            console.log(item)
                            return {
                                label: item.name,
                                value: item.name,
                                id: item.res_id,
                            }
                        }));
                    },
                    error: function (error) {
                       alert('error: ' + error);
                    }
                    });
                },
                select:function(suggestion,term,item){
                    window.location.href= "cms/"+term.item.id
                },
                minLength: 1
            });
            $('#srch-term').keypress(function(e) {
                if ( e.keyCode == 13 ) {  // detect the enter key
                    $.ajax({
                    url: "/search/cms/content/keypress",
                    method: 'POST',
                    dataType: 'json',
                    data: { data:$('#srch-term').val()},
                    success: function( data ) {
                        window.location.href= '/rendersearch?data='+data
                        }
                    });
                }
            });
            $('#searchbtn').click(function(){
                $.ajax({
                url: '/search/cms/content/button',
                method: 'POST',
                dataType: 'json',
                data: { data:$('#srch-term').val()},
                success: function( data ) {
                    window.location.href= '/rendersearch?data='+data
                    }
                });
            });
            $('#backbutton').click(function(){
                 window.history.go(-1);
            });
        }
        $(window).load(function(){
            // Remove the # from the hash, as different browsers may or may not include it
            var hash = window.location.hash.replace('#','');
            if(hash != '' && hash != 'scrollTop=0'){
               // Clear the hash in the URL
                try {
                     $('html, body').animate({ scrollTop: $('#'+hash).offset().top - 60}, 1000);
                }
                catch(err) {
                    //alert('did not find hash:' + hash)
                    //alert(err)
                    return;
                }
            }
            if (! '?dashboard=true' == $.trim(window.location.search)){
                $('#cms_breadcrump_id').find('a').each(function(){
                    $.each($(this), function(){
                    window.localStorage.removeItem('cms_selector')
                    window.localStorage.setItem('cms_selector', this.innerText)
                    this.href='/?to_ham'
                    });
                });
            }
            else if('?to_ham' == $.trim(window.location.search)){
                var selector = window.localStorage.getItem('cms_selector')
                $.each($('.positionR').find('li span'), function(){
                    var self = this;
                    if (this.innerHTML == selector){
                        $('.overlay').css({"display":"block"})
                        $('.list-group').css({"display":"block"})
                        $($(this).parent()).parent().css({"display":"block"})
                        $($(this).parent()).parent().find('ul').css({"display":"block"})
                    }
                })
            }
        });
    });
}
catch(err) {
    //alert('did not find hash:' + hash)
    //alert(err)
    //return;
}
