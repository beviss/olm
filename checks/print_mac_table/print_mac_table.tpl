<html>
<head>
<style>

td, th {
  border : 1px solid black;
  padding-left : 5px;
  padding-right : 5px;
}

th {
  background-color: black;
  color : white;
}

table {
 border-collapse : collapse;
 border-spacing :0;
}
</style>
</head>
<body>
Generated at: {{ date }}
<table>
{% for mac in data %}
<tr><td>{{ mac.0 }}</td><td>{{ mac.1 }}</td><td>{{ mac.2 }}</td><td>{{ mac.3 }}</td></tr>
{% endfor %}
</table>
</body>
</html>
