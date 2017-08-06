$SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
  $(function() {
    $('submit#calculate').bind('click', function() {
      alert("Hi");
      $.getJSON($SCRIPT_ROOT + '/', {
        a: $('input[name="searchcity"]').val(),
        b: $('input[name="count"]').val()
      }, function(data) {
        $("#result").text("Hi");
      });
      return false;
    });
  });


function getWeatherForcaset(city, count){

  alert(city, count);

}

