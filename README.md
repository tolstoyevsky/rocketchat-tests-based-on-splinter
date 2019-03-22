# rocketchat-tests-based-on-splinter

A set of [Splinter](https://splinter.readthedocs.io/en/latest/)-based tests of [Rocket.Chat](https://rocket.chat) and some [Hubot](https://hubot.github.com/) scripts.

## Features

The set of tests includes:
* the general tests for Rocket.Chat;
* the tests for the following Hubot scripts:
  * [hubot-happy-birthder](https://github.com/tolstoyevsky/hubot-happy-birthder)
  * [hubot-pugme](https://github.com/tolstoyevsky/hubot-pugme)
  * [hubot-vote-or-die](https://github.com/tolstoyevsky/hubot-vote-or-die)

## Prerequisites

Some of the general Rocket.Chat tests are related to the clipboard, so install xclip.
On Debian or Ubuntu:
```
$ sudo apt-get install xclip
```

On Fedora:
```
$ sudo dnf install xclip
```

## Installation

### Docker

Clone the git repository and build the Docker image:

```
git clone https://github.com/tolstoyevsky/rocketchat-tests-based-on-splinter.git
cd  rocketchat-tests-based-on-splinter/docker
make
```

### Manual

Clone the git repository and install the dependencies:

```
git clone https://github.com/tolstoyevsky/rocketchat-tests-based-on-splinter.git
cd  rocketchat-tests-based-on-splinter
pip3 install -r requirements.txt
```

## Getting started

You have the following options:
* run only the general Rocket.Chat tests;
* run the general Rocket.Chat tests with either all the available Hubot scripts tests (see [Features](#features)) or only with specified ones.

To run only the general Rocket.Chat tests, go to the root of the project and execute

```
./run_tests.sh -s rc
```

To run the general Rocket.Chat tests with all the available Hubot scripts, execute

```
./run_tests.sh -s all
```

To specify a particular Hubot script test, play with the `-s` option. In the following example the general Rocket.Chat tests will be run only with the hubot-happy-birthder tests.

```
./run_tests.sh -s happy_birthder_script
```

Note, that the name of the target test is the name of its Python module without the `_tests.py` prefix.

To run all the available tests in the Docker container, execute

```
./run_tests_in_container.sh
```

To see only the logs related to the tests, execute

```
./run_tests_in_container.sh logs
```

In comparison with `run_tests.sh` all the magic in `run_tests_in_container.sh` is done not via the command line, but via the `docker/docker-compose.yml` file. So, in order to specify a particular Hubot script test and run it in the Docker container, edit the `command` parameter. Under the hood the value of the parameter will be passed to `run_tests.sh`, so have a look at the examples above.

When the tests are done or you simply want them to be interrupted, execute

```
./run_tests_in_container.sh down
```

## Configuration

The tests can be configured via the following environment variables (called parameters) which can be passed via either the `env` program or the `.env` file.

All the parameters mentioned below are **mandatory**, so don't forget to provide the values for the parameters which don't have default values.

<table>
  <tr>
    <td align="center"><b>Parameter</b></td>
    <td align="center"><b>Description</b></td>
    <td align="center"><b>Default</b></td>
  </tr>
  <tr>
    <td align="center" colspan="3"><b>Rocket.Chat</b></td>
  </tr>
  <tr>
    <td>ADDR</td>
    <td>Domain or IP of the Rocket.Chat host.</td>
    <td>127.0.0.1</td>
  </tr>
  <tr>
    <td>BOT_NAME</td>
    <td>Name that will be used as a bot name <b>(for Docker container only)</b>.</td>
    <td>meeseeks</td>
  </tr>
  <tr>
    <td>PORT</td>
    <td>Port the Rocket.Chat server listens on.</td>
    <td>8006</td>
  </tr>
  <tr>
    <td>USERNAME</td>
    <td>Username of an administrator on the server.</td>
    <td></td>
  </tr>
  <tr>
    <td>PASSWORD</td>
    <td>Password of an administrator on the server.</td>
    <td></td>
  </tr>
  <tr>
    <td>PYTHON</td>
    <td>Python interpreter which will be used for running the tests.</td>
    <td>python3</td>
  </tr>
  <tr>
    <td>RUNNING_WAIT</td>
    <td>Number of seconds that tests will be waiting for the bot running <b>(for Docker container only)</b>.</td>
    <td>120</td>
  </tr>
  <tr>
    <td align="center" colspan="3"><b>hubot-pugme</b></td>
  </tr>
  <tr>
    <td>PUGS_LIMIT</td>
    <td>Maximum number of pugs.</td>
    <td>5</td>
  </tr>
  <tr>
    <td align="center" colspan="3"><b>hubot-happy-birthder</b></td>
  </td>
  <tr>
    <td>WAIT</td>
    <td>Amount in second which test script is waiting for hubot reaction.</td>
    <td>100</td>
  </tr>
</table>

Note that the tests are very sensible to:
- the condition of the database. It's recommended to have as compact database as possible to run the Hubot scripts.
- the local configuration of the Hubot scripts you want to test and especially to the timers. We provide some recommended configuration of them to make the tests run:

<table>
  <tr>
    <th align="center">Parameter</th>
    <th align="center">Recommended value</th>
  </tr>
  <tr>
    <th align="center" colspan="3">hubot-happy-birthder</th>
  </tr>
  <tr>
    <td colspan="3">Ensure that the most of the hubot-happy-birthder parameters are set to default values. See the description for all the parameters related to the script in its original <a href="https://github.com/tolstoyevsky/hubot-happy-birthder/blob/master/README.md">README</a>.</td>
  </tr>
  <tr>
    <td>HAPPY_REMINDER_SCHEDULER</td>
    <td>/1 * * * * *</td>
  </tr>
  <tr>
    <td>CREATE_BIRTHDAY_CHANNELS</td>
    <td>true</td>
  </tr>
</table>

## Authors

See [AUTHORS](AUTHORS.md).

## Licensing

rocketchat-tests-based-on-splinter is available under the [Apache License, Version 2.0](LICENSE).
