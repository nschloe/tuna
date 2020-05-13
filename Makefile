VERSION=$(shell python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['version'])")

default:
	@echo "\"make publish\"?"

tag:
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then exit 1; fi
	# @echo "Tagging v$(VERSION)..."
	# git tag v$(VERSION)
	# git push --tags
	curl -H "Authorization: token `cat $(HOME)/.github-access-token`" -d '{"tag_name": "v$(VERSION)"}' https://api.github.com/repos/nschloe/tuna/releases

dep:
	npm install
	cp -r node_modules/bootstrap/dist/css/bootstrap.min.css tuna/web/static/
	cp -r node_modules/d3/dist/d3.min.js tuna/web/static/

upload:
	# Make sure we're on the master branch
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then exit 1; fi
	rm -rf dist/*
	# python3 setup.py sdist bdist_wheel
	# https://stackoverflow.com/a/58756491/353337
	python3 -m pep517.build --source --binary .
	twine upload dist/*

update:
	curl https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css > tuna/web/static/bootstrap.min.css
	curl https://d3js.org/d3.v5.min.js > tuna/web/static/d3.min.js

publish: tag upload

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
	@rm -rf *.egg-info/ build/ dist/ node_modules/

lint:
	flake8 .
	black --check .
	eslint tuna/web/static/icicle.js
	htmlhint tuna/web/index.html

black:
	black .

format:
	isort -rc .
	black .
