<html>
<style>
td {border : solid 1px black; }
table {border-spacing: 0; border-collapse:collapse}
</style>
{% for devname, ports in result.iteritems() %}
<h1>{{ devname }} </h1>
Generated at {{ date }}
<table>
<tr><th>Port</th><th> Name </th><th> VLANs </th><th> Status </th><tr>
{% for port in ports %}<tr><td>{{ port.name }}</td><td> {{ port.descr }} </td><td>

{% for vtag, vname, vtagness in port.vlans %}
{{ vname }}({{ vtag }}) - {% if vtagness %}TAG{% else %}UNTAG{% endif %}  <br>
{% endfor %}

</td><td> {% if port.up %} UP {% else %} DOWN {% endif %}</td></tr>
{% endfor %}

</table>
{% endfor %}
</html>
