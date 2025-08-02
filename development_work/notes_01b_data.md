

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
- name.basics > names.tsv
- titles.basic > movies.tsv

command line commands:
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
> roles.tsv

- create separate headers file for principals:
echo ":END_ID	:START_ID	:TYPE" > roles.unified.tsv
- copy over rest of data (this takes a while...sigh. can't get relationships arg to accept header + data file below, so must do this)
cat roles.tsv >> roles.unified.tsv

- `title.ratings`: 
echo "tconst        averageRating:float     numVotes:int" > ratings.tsv
ggtail -n +2 title.ratings.tsv >> ratings.tsv


**ENDED UP HAVING TO CLEAN UP ROLES IN PYTHON AS WELL**
`--skip-bad-relationships` wasn't enough.
See Notebook.
Le sigh.

- Move files to /input/ folder for DMBS


Resulting fields:
- Person node:
    - nameId
    - titleId
    - ...

Import command (from Neo4j DBMS Terminal)
./bin/neo4j-admin database import full --nodes=Person=import/names.tsv --nodes=Movie=import/movies.tsv --relationships=import/roles.unified.tsv --delimiter="\t" --skip-bad-relationships --overwrite-destination