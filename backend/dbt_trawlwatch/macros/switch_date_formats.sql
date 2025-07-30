{% macro switch_date_formats(date_column) %}
    case
        when {{ date_column }} like '%/%' then to_timestamp({{ date_column }}, 'DD/MM/YYYY')
        when {{ date_column }} like '%-%' then to_timestamp({{ date_column }}, 'YYYY-MM-DD')
    end 
{% endmacro %}