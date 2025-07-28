Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices

### RELOAD FULL
cd .\12_bloom-main\backend\dbt_trawl_watch\
dbt run-operation _init_dbt_trawl_watch__generate_all_pg_functions
dbt run-operation _init_dbt_trawl_watch__enforce_incremental_tables_reset
dbt seed
dbt run --select tag:dim 
dbt run --event-time-start "2024-05-01" --event-time-end "{# remplacer par : today+1day #}" --vars '{default_microbatch_size: "day"}'

### Test simple sur le staging des positions pour une période déterminée
cd .\12_bloom-main\backend\dbt_trawl_watch\
dbt run -m stg_vessel_positions --event-time-start "2024-05-31" --event-time-end "2024-06-04" 

### Run au fil de l'eau
cd .\12_bloom-main\backend\dbt_trawl_watch\
dbt run

