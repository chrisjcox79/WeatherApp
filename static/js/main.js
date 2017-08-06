$SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
  $(function() {
    $('submit#calculate').bind('click', function() {
      alert("Hi");
      $.getJSON($SCRIPT_ROOT + '/_add_strings', {
        a: $('input[name="searchcity"]').val(),
        b: $('input[name="count"]').val()
      }, function(data) {
        $("#result").text(data.text);
      });
      return false;
    });
  });


function getWeatherForcaset(city, count){

  alert(city, count);

}

