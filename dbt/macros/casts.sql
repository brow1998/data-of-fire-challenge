{# Socrata serves every field as text; empty strings mean "no value". #}
{% macro text_field(name) -%} nullif(trim(record ->> '{{ name }}'), '') {%- endmacro %}
{% macro int_field(name) -%} ({{ text_field(name) }})::numeric::integer {%- endmacro %}
{% macro money_field(name) -%} ({{ text_field(name) }})::numeric(15, 2) {%- endmacro %}
{% macro ts_field(name) -%} ({{ text_field(name) }})::timestamp {%- endmacro %}
