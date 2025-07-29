{% macro evaluate_fishing_rights(zone_beneficiaries, vessel_flag) %}
{# Évaluation des droits de pêche en fonction des bénéficiaires de la zone et du pavillon du navire #}
    case
        -- Si zone_beneficiaries est null, le navire n'est pas exclu des droits de pêche
        when {{ zone_beneficiaries }} is null then 'not_excluded'
        -- Si le pavillon du navire est dans la liste des bénéficiaires de la zone, le navire est inclus
        when {{ vessel_flag }} = any({{ zone_beneficiaries }}) then 'included'
        when {{ vessel_flag }} is null then 'unknown'  -- Si le pavillon est inconnu, on ne peut pas déterminer les droits
        else 'excluded'
    end
{% endmacro %}
