<html>
  <head>
    <link rel="stylesheet" type="text/css" href="vlan_mismatches.css">
  </head>
  <body>
  Generated at: {{ result.date }}
  {% for (groupname, devs, ports, vlans, all_vlans, vlan_names) in result.rtgs %}
    <h2>{{ devs[0] }}: {{ groupname }}</h2>
    <br>
    <table>
    <tr>
      <th></th><th></th>
      {% for dev in devs %}
      <th class="left">{{dev}}</th>
      {% endfor %}
    </tr>
    <tr>
      <td></td>
      <td></td>
      {% for port in ports %}
      <td>{{ port[0] }}</td>
      {% endfor %}
    </tr>
    <tr>
      <td></td>
      <td></td>
      {% for port in ports %}
      <td>{{ port[1] }}</td>
      {% endfor %}
    </tr>
    {% for vlan in all_vlans %}
    <tr>
      <td>{{ vlan }}</td>
      <td>{{ vlan_names[vlan].name }}</td>
      {% for dev_vlans in vlans %}
        {% if vlan in dev_vlans %}
      <td class="right {% if dev_vlans[vlan] != vlans[0][vlan] %} X{%endif%}">{% if dev_vlans[vlan] %} T {% else %} U {% endif %}</td>
        {% else %}
      <td class="right X">X</td>
        {% endif %}
      {% endfor %}
    </tr>
    {% endfor %}
    </table>
  {% endfor %}
  </body>
</html>
