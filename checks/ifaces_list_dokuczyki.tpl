<pre>
{% for devname, cards in result.iteritems() %}
===== {{ devname }} =====
{%   for card, ports in cards.iteritems() %}
==== {{ card }} ====
^     ^ {%     for port in ports %} {{ port.name }} ^{%     endfor %}
|up? | {%      for port in ports %} {% if port.up %} UP {% else %} DOWN {% endif %} | {% endfor %}
|descr | {%      for port in ports %} {{ port.descr }} | {% endfor %}
|vlans | {%      for port in ports %} {% for vtag, vname, vtagness in port.vlans %} {{vname}}({{vtag}})\\ {%endfor%} | {% endfor %}
|remarks | {%      for port in ports %} | {% endfor %}
{%   endfor %}
{% endfor %}
</pre>
