{% for devname, ports in result.iteritems() %}
;
;
{{ devname }} 
;
;
Port ; Name ; VLANs ; Status ; Remarks
{% for port in ports %}{{ port.name }} ; {{ port.descr }} ; ; {% if port.up %} UP {% else %} DOWN {% endif %}
{% endfor %}
{%endfor%}
