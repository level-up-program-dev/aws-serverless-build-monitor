reqs:
	pipenv requirements > requirements.txt

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