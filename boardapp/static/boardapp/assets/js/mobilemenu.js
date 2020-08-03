$(document).ready(function ($) {
    $(".mobmenu").click(function() {
      $("#menu,.page_cover,html").addClass("open");
      window.location.hash = "#open";
    });

    window.onhashchange = function() {
      if (location.hash != "#open") {
        $("#menu,.page_cover,html").removeClass("open");
      }
    };
    $(".serching-m>a").click(function(){
        var serch = $(this).next("div");
        if( serch.is(":visible") )
        {
            serch.slideUp();
        }
        else
        {
            serch.slideDown();
        }
    });
 });