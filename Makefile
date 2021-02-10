VERSION=$(shell python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['version'])")

default:
	@echo "\"make publish\"?"

tag:
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	curl -H "Authorization: token `cat $(HOME)/.github-access-token`" -d '{"tag_name": "v$(VERSION)"}' https://api.github.com/repos/nschloe/tuna/releases

upload: clean
	# Make sure we're on the main branch
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	# https://stackoverflow.com/a/58756491/353337
	python3 -m build --sdist --wheel .
	twine upload dist/*

# update:
# 	curl https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css > tuna/web/static/bootstrap.min.css
# 	curl https://d3js.org/d3.v5.min.js > tuna/web/static/d3.min.js

dep:
	npm install
	cp -r node_modules/bootstrap/dist/css/bootstrap.min.css tuna/web/static/
	cp -r node_modules/d3/dist/d3.min.js tuna/web/static/

update:
	npm update
	npm update --save-dev
	npm outdated

publish: tag upload

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
	@rm -rf *.egg-info/ build/ dist/ node_modules/

lint:
	flake8 .
	black --check .
	eslint tuna/web/static/icicle.js
	htmlhint tuna/web/index.html

format:
	isort .
	black .
