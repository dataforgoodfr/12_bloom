{% macro create_admin_tables() %}
       /* -------------------------------------------------------------------------
        Vue : admin.heaviest_objects
        - Détail : toutes les partitions, indexes, TOAST…
        - Agrégats : taille cumulée d’une table partitionnée (+ indexes),
                        taille cumulée d’un index partitionné.
        ------------------------------------------------------------------------- */
        create schema if not exists admin;

        create or replace view admin.heaviest_objects as
        with relsizes as (
            /* Taille de chaque relation utilisateur (octets) */
            select
                c.oid,
                n.nspname                as schema_name,
                c.relname                as object_name,
                c.relkind,
                pg_total_relation_size(c.oid) as total_bytes
            from pg_class c
            join pg_namespace n on n.oid = c.relnamespace
            where n.nspname not in ('pg_catalog','information_schema')
        ),

        /* --------------------------------------------------------------------- *
        * 1. Lignes DÉTAILLÉES : chaque partition, index, toast, etc.           *
        * --------------------------------------------------------------------- */
        details as (
            select
                case
                    when relkind = 'p'            then 'table_parent'
                    when relkind = 'r'            then 'table_partition_or_simple'
                    when relkind = 'i'            then 'index'
                    when relkind = 'I'            then 'index_parent'
                    when relkind = 't'            then 'toast'
                    else relkind::text
                end                             as object_type,
                schema_name,
                object_name,
                pg_size_pretty(total_bytes)     as total_size,
                total_bytes
            from relsizes
        ),

        /* --------------------------------------------------------------------- *
        * 2. Agrégat TABLE partitionnée  (relkind = 'p')                        *
        *    somme = toutes les partitions + leurs indexes + toast éventuels    *
        * --------------------------------------------------------------------- */
        table_agg as (
            select
                'partitioned_table'           as object_type,
                parent.schema_name,
                parent.object_name,
                pg_size_pretty(sum(child.total_bytes)) as total_size,
                sum(child.total_bytes)         as total_bytes
            from relsizes parent
            join pg_inherits    i  on i.inhparent = parent.oid          -- enfant → table
            join relsizes child on child.oid   = i.inhrelid
            where parent.relkind = 'p'
            group by parent.schema_name, parent.object_name
        ),

        /* --------------------------------------------------------------------- *
        * 3. Agrégat INDEX partitionné (relkind = 'I')                          *
        *    somme = tous les index-fils physiques                              *
        * --------------------------------------------------------------------- */
        index_agg as (
            select
                'partitioned_index'           as object_type,
                parent.schema_name,
                parent.object_name,
                pg_size_pretty(sum(child.total_bytes)) as total_size,
                sum(child.total_bytes)         as total_bytes
            from relsizes parent
            join pg_inherits    i  on i.inhparent = parent.oid          -- enfant → index
            join relsizes child on child.oid   = i.inhrelid
            where parent.relkind = 'I'         -- racine d’index partitionné
            group by parent.schema_name, parent.object_name
        )
        select * from (
            select * from details
            union all
            select * from table_agg
            union all
            select * from index_agg
            order by total_bytes desc
        ) a  where total_bytes > 261000000 -- env. 250 Mo
        order by total_bytes desc;
{% endmacro %} 
