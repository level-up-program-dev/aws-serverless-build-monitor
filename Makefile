reqs:
	pipenv lock -r > requirements.txt

deploy-all:
	serverless deploy

package:
	- rm -rf ./dist
	mkdir -p ./dist
	serverless package --package ./dist

run:
	serverless invoke local --function renderRepoDetails