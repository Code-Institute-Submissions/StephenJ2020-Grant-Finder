$(document).ready(function () {
  $('.sidenav').sidenav();
  $('select').formSelect();
  $('.collapsible').collapsible();
  $('.tabs').tabs();

  $('#tab1').show();
  $('#tab2').hide();
  $('#tab3').hide();

  $('#tab1').click(function () {
    $('#tab1').show();
    $('tab2').hide();
    $('tab3').hide();
  });

  $('#tab2').click(function () {
    $('#tab1').hide();
    $('tab2').show();
    $('tab3').hide();
  });

  $('#tab3').click(function () {
    $('#tab1').hide();
    $('tab2').hide();
    $('tab3').show();
  });


});
