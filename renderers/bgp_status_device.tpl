<html>
<style>
td {border : solid 1px black; padding: 0.5em; }
table {border-spacing: 0; border-collapse:collapse}

.down { background-color: red; }
.up { background-color: lightgreen; }
</style>
<body>
<h1>{{ devname }} </h1>
Generated at: {{ date }}
<table>
<tr>
  <td>Peer address</td>
  <td>Peer AS</td>
  <td>Description</td>
  <td>Group</td>
  <td>State</td>
  <td>Since</td>
  <td># advertised</td>
  <td># received</td>
  <td># accepted</td>
  <td># active</td>
  <td># suppressed</td>
</tr>
{% for session in result %}
<tr class="{% if session['state'] == 'Established' %} up {% else %} down {% endif %}">
  <td>{{session['address']}}</td>
  <td>{{session['as']}}</td>
  <td>{{session['description']}}</td>
  <td>{{session['group']}}</td>
  <td>{{session['state']}}</td>
  <td>{{session['elapsed-time']}}</td>
  <td>{{session['advertised']}}</td>
  <td>{{session['received']}}</td>
  <td>{{session['accepted']}}</td>
  <td>{{session['active']}}</td>
  <td>{{session['suppressed']}}</td>
</tr>
{% endfor%}
</body>
