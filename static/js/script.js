$(document).ready(function () {
  $('.sidenav').sidenav();
  $('select').formSelect();
  $('.collapsible').collapsible();
  $('.tabs').tabs();
  $('.datepicker').datepicker({
    format: "dd mmmm, yyyy",
    yearRange: 4,
    showClearBtn: true,
    i18n: {
      done: "Select"
    }
  });
  $('.tooltipped').tooltip();

  $('#textarea1').val('New Text');
  M.textareaAutoResize($('#textarea1'));
});
