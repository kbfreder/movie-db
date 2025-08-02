

# Data Sources

MovieLens - https://grouplens.org/datasets/movielens/
- more geared towards movie reviews / ratings
- doesn't have formatted list of actors
- year appears in title field -- would need to be extracted / parsed


IMDB - 
- Offers non-commercial datasets: https://developer.imdb.com/non-commercial-datasets/


# IMDB
Download from: https://datasets.imdbws.com/
- Don't need:
    - `title.akas.tsv`
        - might not need this one -- more lists the regional titles for films
    - `title.crew.tsv`
        - title id, director nameid, writers ids
        - appears to contain redundant info w/ `principals`


Use / general data notes:
- `name.basics.tsv`
    - name id, name, birth year, death year, etc
- `title.basics.tsv`
    - id, title (primary and original), year, (and year end for TV shows), genre
- `title.principals.tsv`
    - roles played by people: director, actor, producer, etc
    - contains categories like 'self', 'cinematographer', 'composer', etc
        - we are probably only interested in: director, actor, self?, producer?
- `title.ratings.tsv`
    - summary of movie ratins
    - title id, average rating, number of votes

## Data clean up:

In Python, clean up: (see notebook)
- mod.name
- mod.title.basics

from command line:
    - filtering for director or actor only
        awk -F'\t' '$4 == "director" || $4 == "actor" || $4 == "actress"' [FILENAME]
    
    - replacing `tt0000xx` with just `xx`
        sed -E 's/tt0*([0-9]+)/\1/g; s/nm0*([0-9]+)/\1/g' [FILENAME]

    - swap `\N` with actual blank values
        sed -E 's/\\N//g' [FILENAME]
    
    - keep only certain columns: (e.g. 1 & 3)
        cut -f 1,3 [FILENAME]

- `title.principals`:
awk -F'\t' '$4 == "director" || $4 == "actor" || $4 == "actress"' title.principals.tsv | \
cut -f 1,3,4 | \
sed -E 's/\\N//g; s/actress/actor/g' | \
> filt.title.principals.tsv

- `title.ratings`: 
sed -E 's/tt0*([0-9]+)/\1/g; s/\\N//g' title.ratings.tsv > mod.title.rating.tsv

- create separate headers file for principals:
echo ":END_ID	:START_ID	:TYPE" > rels.header.tsv
echo ":END_ID	:START_ID	:TYPE	job:IGNORE	characters:IGNORE" > rels.header.tsv


- then copy over rest of principlas data
gtail -n +2 filt.title.principals.tsv >> mod.rels.tsv

OLD (no longer used)
- headers for importing into Neo4j
    - ruN: `echo "<edited header>" > new_file.tsv`
    - run: `gtail -n +2 old_file.tsv >> new_file.tsv`
- in the end, I loaded into Python to clean up, so I just could have done the header renaming there


** Move `filt_` files to /input/ folder for DMBS **


Resulting fields:
- Person node:
    - nameId
    - titleId
    - ...

Import command (from Neo4j DBMS Terminal)
./bin/neo4j-admin database import full /
    --nodes=Person=import/filt.name.basics.tsv /
    --nodes=Movie=import/filt.titles.basic.tsv /
    --relationships=import/mod.rels.tsv /
    --delimiter="\t" /
    --id-type=integer /
    --skip-bad-relationships /
    --overwrite-destination