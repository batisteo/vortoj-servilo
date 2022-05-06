# Vortoj servilo

###### Servilo por konservi uzantoj kaj agordoj por la ludo Vortoj

## Komenci

Vi bezonas `Git`, `Python 3.8`, `Poetry` kaj eble `Docker`.

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
```

```bash
git clone git@github.com:batisteo/vortoj-servilo.git
cd vortoj-servilo
python3.8 -m venv .venv
poetry install
cp .env.example .env
make init
make run
```
