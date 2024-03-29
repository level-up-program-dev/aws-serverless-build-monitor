<!--
title: 'AWS Python Scheduled Cron example in Python'
description: 'This is an example of creating a function that runs as a cron job using the serverless ''schedule'' event.'
layout: Doc
framework: v3
platform: AWS
language: Python
priority: 2
authorLink: 'https://github.com/rupakg'
authorName: 'Rupak Ganguly'
authorAvatar: 'https://avatars0.githubusercontent.com/u/8188?v=4&s=140'
-->

# Project setup on Ubuntu and possibly other Linuxes
Ubuntu comes installed with a system python. In 22.04 LTS this is Python 3.10. These versions of python are split apart into packages. For example, in a mimimal Ubuntu install, the system python does not have pip or virtualenv installed. They must be installed separately.

Because of this, it is reccomended to use pyenv to setup your Pythons for development purposes. It is easy to switch to the python required, and the time required to download and build a python from source is faster than you would think (A core i7-7700HQ with 16 GB of memory downloaded and built Python 3.9 in just under 5 minutes).

In order to get pyenv, follow the instructions for the Automatic installer (https://github.com/pyenv/pyenv/wiki#suggested-build-environment), setup your shell (https://github.com/pyenv/pyenv/#set-up-your-shell-environment-for-pyenv), and download the requirements for your linux as described here: https://github.com/pyenv/pyenv/wiki#suggested-build-environment

For this project, you'll want to install **3.9:latest**

```sh
pyenv install 3.9:latest
```

and activate it for local use in the current directory of the project, where x is the minor version provided as output to the install command.  _Note: If there is already a .python-version file in the directory, this step is not required.

```sh
pyenv local 3.9.x
```

once you pass the step of bootstrapping in the makefile, be sure to source the virtual environment created before moving onto other steps:

```sh
pipenv shell
```

# Serverless Framework Python Scheduled Cron on AWS

This template demonstrates how to develop and deploy a simple cron-like service running on AWS Lambda using the traditional Serverless Framework.

## Schedule event type

This examples defines two functions, `renderRepoDetails` and `cronHandler`, both of which are triggered by an event of `schedule` type, which is used for configuring functions to be executed at specific time or in specific intervals. For detailed information about `schedule` event, please refer to corresponding section of Serverless [docs](https://serverless.com/framework/docs/providers/aws/events/schedule/).

When defining `schedule` events, we need to use `rate` or `cron` expression syntax.

### Rate expressions syntax

```pseudo
rate(value unit)
```

`value` - A positive number

`unit` - The unit of time. ( minute | minutes | hour | hours | day | days )

In below example, we use `rate` syntax to define `schedule` event that will trigger our `renderRepoDetails` function every minute

```yml
functions:
  renderRepoDetails:
    handler: handler.run
    events:
      - schedule: rate(1 minute)
```

Detailed information about rate expressions is available in official [AWS docs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#RateExpressions).

## Usage

### Deployment

This example is made to work with the Serverless Framework dashboard, which includes advanced features such as CI/CD, monitoring, metrics, etc.

In order to deploy with dashboard, you need to first login with:

```
serverless login
```

and then perform deployment with:

```
serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying aws-serverless-build-monitor to stage dev (us-east-1)

✔ Service deployed to stack aws-serverless-build-monitor-dev (205s)

functions:
  renderRepoDetails: aws-serverless-build-monitor-dev-renderRepoDetails (12 MB)
```

There is no additional step required. Your defined schedules becomes active right away after deployment.

### Local invocation

In order to test out your functions locally, you can invoke them with the following command:

```
serverless invoke local --function renderRepoDetails
```

After invocation, you should see output similar to:

```bash
INFO:handler:Your cron function aws-serverless-build-monitor-dev-renderRepoDetails ran at 15:02:43.203145
```

### Bundling dependencies

In case you would like to include 3rd party dependencies, you will need to use a plugin called `serverless-python-requirements`. You can set it up by running the following command:

```bash
serverless plugin install -n serverless-python-requirements
```

Running the above will automatically add `serverless-python-requirements` to `plugins` section in your `serverless.yml` file and add it as a `devDependency` to `package.json` file. The `package.json` file will be automatically created if it doesn't exist beforehand. Now you will be able to add your dependencies to `requirements.txt` file (`Pipfile` and `pyproject.toml` is also supported but requires additional configuration) and they will be automatically injected to Lambda package during build process. For more details about the plugin's configuration, please refer to [official documentation](https://github.com/UnitedIncome/serverless-python-requirements).
