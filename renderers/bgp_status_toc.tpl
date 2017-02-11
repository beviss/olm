<html>
<style>
td {border : solid 1px black; }
table {border-spacing: 0; border-collapse:collapse}
</style>
<body>
<h1>{{ devname }} </h1>
Generated at: {{ date }}
{% for dev in result %}
<br>
<a href="/netmonitor/bgp_netconf/{{ dev }}.html">{{dev}}</a>
{% endfor%}
</body>
