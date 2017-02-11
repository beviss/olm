<html>
  <head>
    <link rel="stylesheet" type="text/css" href="vlan_names.css">
    <style>
      table {
        border-spacing: 0px;
        border-collapse: collapse;
      }
      td {
        border: 1px solid black;
        padding: 3px;
      }
      .vpls_id_label {
        color:white;
        background-color: black;
        font-weight: bold;
      }
    </style>
  </head>

{% for dev_name, vplss in result | dictsort %}
  <h1>{{ dev_name }}</h1>
  <table>
  {% for vpls_id, vpls in vplss | dictsort %}
  <tr>
    <td colspan=2 class="vpls_id_label">
    {{ vpls_id }} {{ vpls['name'] }}
    </td>
    </tr>
  {% for peer_label, reason in vpls['nonsense_peers'] %}
    <tr><td>{{peer_label}}</td><td>{{reason}}</td></tr>
  {% endfor %}
  {% endfor %}
  <table>
{% endfor %}

</html>
