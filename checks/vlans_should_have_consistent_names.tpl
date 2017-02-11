<html>
  <head>
    <link rel="stylesheet" type="text/css" href="vlan_names.css">
  </head>

{% for v in result | dictsort %}
  {% set vlan_tag = v.0 %}
  {% set vlan = v.1 %}
  <br>
  <table>
    {% if vlan.1 | length == 0 %}

    <tr>
      <th style='text-align : left' colspan="3">Vlan {{ vlan_tag }} - does not appear on devices - name in DB: {{vlan.0}}</th>
    </tr>

    {% else %}

    <tr>
      <th style='text-align : left' colspan="3">Vlan {{ vlan_tag }}</th>
    </tr>
    <tr class="second_header">
      <td>Occurences</td><td>Name</td><td>Devices</td>
    </tr>
    {% set name_from_db = vlan.0 %}
    {% for name in vlan.1 %}
      {% if name.0 == name_from_db %}
      <tr class="name_from_db">
      {% else %}
      <tr>
      {% endif %}
        <td>{{name.1 | length}}</td><td>{{name.0}}</td><td> {% for dev in name.1 %} {{ dev }}, {% endfor %}</td>
      </tr>
    {% endfor %}
    {% endif %}
  </table>
{% endfor %}

</html>
