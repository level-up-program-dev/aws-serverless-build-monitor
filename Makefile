bootstrap-python:
	- pipenv --rm
	pipenv update --dev

bootstrap-serverless:
	npm install -g serverless
	cd src && sls plugin install -n serverless-wsgi
	cd src && sls plugin install -n serverless-python-requirements
	cd src && sls plugin install -n serverless-domain-manager

bootstrap: bootstrap-python bootstrap-serverless

reqs:
	pipenv requirements > src/requirements.txt

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean: clean-pyc
	- rm -rf ./dist
	- cd src && serverless requirements clean

prep: clean reqs

deploy-prod: prep
	cd src && serverless deploy --region us-east-1 --stage prod --verbose

deploy-dev: prep
	cd src && serverless deploy --region us-east-2 --stage dev --verbose

remove-dev:
	cd src && serverless remove --region us-east-2 --stage dev --verbose

remove-prod:
	cd src && serverless remove --region us-east-1 --stage prod --verbose

package-dev: prep
	mkdir -p ./dist
	cd src && serverless package --region us-east-2 --stage dev --package ../dist

package-prod: prep
	mkdir -p ./dist
	cd src && serverless package --region us-east-1 --stage prod --package ../dist

shell:
	pipenv shell

run:
	FLASK_APP=src/app.py pipenv run flask run -h localhost -p 8001

test:
	echo "Not yet implemented"