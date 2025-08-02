


Headers for ingesting using `database import` command
https://neo4j.com/docs/getting-started/data-import/csv-import/#batch-importer
- better option for large files (which IMDB files are)

Things we need to do / note:
- if you have repeated IDs across entities, you have to provide the entity (id-group) in parentheses like :ID(Order)
- include `--id-type=string` ?? 
    - indicates that all :ID columns contain alphanumeric values (there is an optimization for numeric-only IDs).
- All other columns are treated as properties but skipped if empty or annotated with :IGNORE.
- put header in separate file?
- :START_ID, :END_ID - relationship file columns referring to the node IDs. For id-groups, use :END_ID(Order).

Database creds:
DB name: neo4j
username: neo4j