(function($) {
  "use strict"; // Start of use strict
  // Configure tooltips for collapsed side navigation
  $('.navbar-sidenav [data-toggle="tooltip"]').tooltip({
    template: '<div class="tooltip navbar-sidenav-tooltip" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>'
  })
  // Toggle the side navigation
  $("#sidenavToggler").click(function(e) {
    e.preventDefault();
    $("body").toggleClass("sidenav-toggled");
    $(".navbar-sidenav .nav-link-collapse").addClass("collapsed");
    $(".navbar-sidenav .sidenav-second-level, .navbar-sidenav .sidenav-third-level").removeClass("show");
  });
  // Force the toggled class to be removed when a collapsible nav link is clicked
  $(".navbar-sidenav .nav-link-collapse").click(function(e) {
    e.preventDefault();
    $("body").removeClass("sidenav-toggled");
  });
  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
  $('body.fixed-nav .navbar-sidenav, body.fixed-nav .sidenav-toggler, body.fixed-nav .navbar-collapse').on('mousewheel DOMMouseScroll', function(e) {
    var e0 = e.originalEvent,
      delta = e0.wheelDelta || -e0.detail;
    this.scrollTop += (delta < 0 ? 1 : -1) * 30;
    e.preventDefault();
  });
  // Scroll to top button appear
  $(document).scroll(function() {
    var scrollDistance = $(this).scrollTop();
    if (scrollDistance > 100) {
      $('.scroll-to-top').fadeIn();
    } else {
      $('.scroll-to-top').fadeOut();
    }
  });
  // Configure tooltips globally
  $('[data-toggle="tooltip"]').tooltip()
  // Smooth scrolling using jQuery easing
  $(document).on('click', 'a.scroll-to-top', function(event) {
    var $anchor = $(this);
    $('html, body').stop().animate({
      scrollTop: ($($anchor.attr('href')).offset().top)
    }, 1000, 'easeInOutExpo');
    event.preventDefault();
  });
})(jQuery); // End of use strict

function calcCardBody_h(){
  var filter_card_header_h = $("#filter-accordion .card-header:nth(0)").outerHeight();
  var filter_card_body_h = $("#filter-accordion .card-body").outerHeight(500-4*filter_card_header_h-5);
  

}

function calcSettingCardBody_h(){
  var custom_card_header_h = $("#custom-setting-accordion .card-header:nth(0)").outerHeight();
  var custom_card_body_h = $("#custom-setting-accordion .card-body").outerHeight(500-3*custom_card_header_h-5);
  // var custom_card_body_h = $("#custom-setting-accordion .card-body").outerHeight('275px');
}


function equal_header(){
  var step1header = document.getElementById("step1header");
  document.getElementById("step2header").style.height = step1header.offsetHeight + "px";

}

$(document).ready(function(){
  // calcCardBody_h();
  // calcSettingCardBody_h();
  equal_header();

});


$(window).resize(function(){
  // calcCardBody_h();
  // calcSettingCardBody_h();
  equal_header();

  $("#gene_specific_table").DataTable().destroy();
  $("#gene_specific_table").DataTable({
    autoWidth:false,
    fixedHeader: true,
    scrollY: "300px",
    scrollCollapse: true,
    paging: false,
    info: false,
    searching: false,
    orderFixed: [ 0, 'asc' ],
    columnDefs:[
      {"width":"10%", "targets":0, "orderable": false},
      {"width":"12%", "targets":1},
      {"width":"9%", "targets":2},
      {"width":"30%", "targets":3},
      {"width":"9%", "targets":4},
      {"width":"30%", "targets":5}
    ]
  });
  $("#gene_specific_table_wrapper div.dataTables_scrollBody").css('border-bottom-color', '#a5a7a9')
});