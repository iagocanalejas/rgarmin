# Introduction

This projects tries to provide a simple way of visualizing the data from a Garmin user.

# Technologies

- Python
- FastAPI
- Htmx
- TailwindCSS
- GarminAPI

# Development

```sh
npm install
pip install -r requirements-dev.txt

rsync -a --ignore-existing templates/*.js static/js
npm run dev  # starts tailwind watcher
fastapi dev api.py
```
