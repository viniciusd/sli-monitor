# sli-monitor

*Keep track of your service level indicators!*

sli-monitor is a set of two tools. The first one is a worker that keeps pooling specified URLs and measuring their response time and status. The other tool is for visualization purpuses only, it displays the URLs in a table together with their SLOs and indicating whether or not they meet what is required for them. 

## Installing

Clone the repository on your machine.  Then, create a virtual environment for managing dependencies.
Note this is a Python3 project. If your have Python 3.3 or greater, you should already have both pip and venv installed.

```shell
python3 -m venv your_env
```

Activate the virtual environment.

```shell
source your_env/bin/activate
```

Install the dependencies.

```shell
pip install -r requirements.txt
```

## Configuring and Running

You can set the URLs and their respective SLOs in the config.yaml file. Yeah, it's YAML! Good bye, XML.
This file is already configured with an example, just change it as you may.

Then, if you haven't already for this session, activate the virtual environment.

```shell
cd your_env
source bin/activate
```

Finally, run it.

```shell
python slo_worker.py &
python index.py &
```

Running index.py in its own screen session should be a better call to keep track of its output. For now, slo_worker has no output, yet you can screen it as well to avoid problems with sighup if it is running in a remote machine.

## TO-DOs:

* Add propper logging to the SLO worker
* Add better layout to the web interface
* Change the YAML schema in a way the url will be a dictionary instead of a list, where the url will be the key
* Use web socket to get real time stats
