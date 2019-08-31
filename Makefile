VERSION=$(shell python3 -c "import tuna; print(tuna.__version__)")

default:
	@echo "\"make publish\"?"

tag:
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then exit 1; fi
	@echo "Tagging v$(VERSION)..."
	git tag v$(VERSION)
	git push --tags

upload: setup.py
	# Make sure we're on the master branch
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then exit 1; fi
	rm -f dist/*
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	twine upload dist/*

update:
	curl https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/css/bootstrap.min.css > tuna/web/static/bootstrap.min.css
	curl https://d3js.org/d3.v5.min.js > tuna/web/static/d3.v5.min.js

publish: tag upload

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
	@rm -rf *.egg-info/ build/ dist/

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
