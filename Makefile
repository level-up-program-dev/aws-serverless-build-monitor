bootstrap:
	npm install -g serverless
	sls plugin install -n serverless-python-requirements
	- pipenv --rm
	pipenv update
	pipenv install -r requirements.txt

reqs:
	pipenv requirements > requirements.txt
	pipenv install -r requirements.txt

deploy: reqs
	serverless deploy

remove:
	serverless remove

package: reqs
	- rm -rf ./dist
	mkdir -p ./dist
	serverless package --package ./dist

run:
	serverless invoke local --function renderRepoDetails