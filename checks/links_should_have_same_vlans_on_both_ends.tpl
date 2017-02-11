<html>
  <head>
    <link rel="stylesheet" type="text/css" href="vlan_mismatches.css">
  </head>
  <body>
  {% for ((dev1, dev2, port1, port2), vlans) in result.iteritems() %}
    <br>
    <table>
    <tr>
      <th class="left">{{dev1}}</th><th></th><th class="right">{{dev2}}</th>
    </tr>
    <tr>
      <td class="left">{{port1}}</td><td></td><td class="right">{{port2}}</td>
    </tr>
    {% for tag, (state1, state2) in vlans %}
    <tr>
      {% if (state1 == 'X') or (state2 == 'X') %}
      <td class="left {% if state1 == 'X'%}X" {%else%} " {%endif%}>{{state1}}</td><td class="middle">{{tag}}</td><td class="right {% if state2 == 'X'%} X" {%else%} " {%endif%}>{{state2}}</td>
      {% elif state1 != state2 %}
      <td class="left X">{{state1}}</td><td class="middle">{{tag}}</td><td class="X right">{{state2}}</td>
      {% else %}
      <td class="left">{{state1}}</td><td class="middle">{{tag}}</td><td class="right">{{state2}}</td>
      {% endif %}
    </tr>
    {% endfor %}
    </table>
  {% endfor %}
  </body>
</html>
