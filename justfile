version := `python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['version'])"`
name := `python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['name'])"`


default:
	@echo "\"just publish\"?"

tag:
	@if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	curl -H "Authorization: token `cat ~/.github-access-token`" -d '{"tag_name": "{{version}}"}' https://api.github.com/repos/nschloe/{{name}}/releases

upload: clean
	@if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	# https://stackoverflow.com/a/58756491/353337
	python3 -m build --sdist --wheel .
	twine upload dist/*

publish: tag upload

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	@rm -rf *.egg-info/ src/*.egg-info/ build/ dist/ .tox/

dep:
	npm install
	cp node_modules/bootstrap/dist/css/bootstrap.min.css tuna/web/static/
	cp node_modules/d3/dist/d3.min.js tuna/web/static/

update:
	npm update
	npm update --save-dev
	npm outdated

lint:
	flake8 .
	black --check .
	# blacken-docs README.md
	npm run prettier

format:
	isort .
	black .
	prettier --write README.md .github tuna/web/static/icicle.js tuna/web/static/tuna.css tuna/web/index.html
