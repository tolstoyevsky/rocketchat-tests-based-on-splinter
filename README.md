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

## Getting started

Clone the git repository and install the dependencies:

```
git clone https://github.com/tolstoyevsky/rocketchat-tests-based-on-splinter.git
cd  rocketchat-tests-based-on-splinter
pip3 install -r requirements.txt
```

Then, you have the following options:
* run only the general Rocket.Chat tests;
* run the general Rocket.Chat tests with either all the available Hubot scripts tests (see [Features](#features)) or only with specified ones.

For example, to run only the general Rocket.Chat tests, execute

```
./run_tests.sh
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
    <td>http://127.0.0.1:8006</td>
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
    <td align="center" colspan="3"><b>hubot-pugme</b></td>
  </tr>
  <tr>
    <td>PUGS_LIMIT</td>
    <td>Maximum number of pugs.</td>
    <td>5</td>
  </tr>
</table>

## Authors

See [AUTHORS](AUTHORS.md).

## Licensing

rocketchat-tests-based-on-splinter is available under the [Apache License, Version 2.0](LICENSE).
