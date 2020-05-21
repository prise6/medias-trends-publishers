# Mediastrends publishers

__Work in progress__

Project to publish trends computed by this project: [prise6/medias-trends](https://github.com/prise6/medias-trends).

Movie pipeline is top priority.

## Requirements

* Set `MEDIASTRENDS_MODE=dev|prod|...` environment variable
* Create a _mediastrends_ config file like this:

```ini
[directory]
base=/package
data=/package/data
logs=${base}/logs
sqlite=/package/sqlite
config=/package/config
sql=/package/sqlite

[db]
database=sqlite

[sqlite]
path=${directory:sqlite}/database_prod.db
backup_dir=${directory:data}

[hash]
file=${directory:config}/hash.txt
```

See [infos](https://github.com/prise6/medias-trends) for details.

## Static website

First version using jina templating, pure js and css: [popular movies](https://prise6.github.io/medias-trends-publishers/)

```bash
git clone https://github.com/prise6/medias-trends-publishers
pip install .
# use --force option if data hasn't changed
python -m mtpublishers publish -p website
```

Wish to improve with:

* static site generator (nuxt ?)
* add legal platform infos to watch a movie (gyde.tv, videospider, guidebox, ...)
* unit testing + mock data to make contribution easier
* ...


## Other publishers

_to do:_

* email
* instagram posts

## Contribute

Feel free to contribute
