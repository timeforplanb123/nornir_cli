## Click Multi Commands feature

All commands are loaded 'lazily' from different plugins (about [Click Multi Commands](https://click.palletsprojects.com/en/7.x/commands/?highlight=multi%20command#custom-multi-commands){target="_blank"} + [Click Multi Commands example](https://github.com/pallets/click/tree/master/examples/complex){target="_blank"}. This applies to Nornir plugins and manually written plugins.


In `nornir_cli` Click Multi Commands feature is implemented through class inheritance, created dynamically from `class_factory` function in `nornir_cli/nornir_cli.py`. 
So, you can easily implement your command in `nornir_cli`, by following the rules described in `class_factory` function. 
Add your command to one of the directories:

* **nornir_cli/common_commands** - here are the commands common to all groups/plugins. Here you will find such commands like `init`, `filter`, `show_inventory`
* **nornir_cli/plugin_commands** - here are the commands, that run single Tasks based on Nornir plugins
* **nornir_cli/custom_commands** - directory for your custom commands based on Nornir


Where is these directories?
If you installed `nornir_cli` from pip:
```
$ pip show nornir_cli
...
Location: /home/user/virtenvs/3.8.4/lib/python3.8/site-packages
...
$ ls /home/user/virtenvs/3.8.4/lib/python3.8/site-packages/nornir_cli
common_commands  custom_commands  __init__.py  nornir_cli.py  plugin_commands  __pycache__  transform
```

If you installed `nornir_cli` from git:
```
$ ls nornir_cli
common_commands  custom_commands  __init__.py  nornir_cli.py  plugin_commands  __pycache__  transform
```

## Custom runbooks 

#### How to add custom nornir runbook

You can add a collection of your custom Nornir runbooks in `nornir_cli` and run them for any Hosts, managing the Inventory using `nornir_cli`, directly from the CLI.

All custom Nornir runbooks stored in `custom_commands` directory (see [Click Multi Commands feature](https://timeforplanb123.github.io/nornir_cli/useful/#click-multi-commands-feature)). To create custom groups and add your Nornir runbook to these groups you need to:

* take and wrap your runbook in a wrapper and run it inside that wrapper
    ```python
    from nornir_cli.common_commands import custom


    @custom
    def cli(ctx):
        """
        runbook description
        """
        def nornir_runbook(task):
        # code
        # ...
    task = ctx.run(task=nornir_runbook)
    ```

    `ctx` after decorating with `@custom` is an current `nornir.core.Nornir` object and `cli` is a new `click.command`

* name a file with your runbook as `cmd_something.py` (replace `something` on your own). `something` between `cmd_` and `.py` will be command name

* create directory tree in `custom_commands` direcotry and put your nornir runbooks there. Here the directories are new `nornir_cli` groups, and nornir runbooks are new commands. Easy-peasy. 

    For example, i created two directories, `dhcp` and `mpls`, and put my runbooks there. Let's check `nornir_cli`:

    === "directory tree:"
        ```text
        $ tree ~/virtenvs/py3.8.4/lib/python3.8/site-packages/nornir_cli/custom_commands/
        /home/user/virtenvs/py3.8.4/lib/python3.8/site-packages/nornir_cli/custom_commands/
        ├── dhcp
        │   ├── cmd_dhcp_snooping.py
        │   └── templates
        │       ├── dhcp_snooping.j2
        │       └── disp_int.template
        ├── __init__.py
        └── mpls
            └── cmd_ldp_config.py

        3 directories, 5 files
        ```

    === "nornir_cli:"
        ```text
        $ nornir_cli
        Usage: nornir_cli [OPTIONS] COMMAND [ARGS]...

          Nornir CLI

          Orchestrate your Inventory and start Tasks and Runbooks

        Options:
          --version  Show the version and exit.
          --help     Show this message and exit.

        Commands:
          dhcp
          mpls
          nornir-f5       nornir_f5 plugin
          nornir-jinja2   nornir_jinja2 plugin
          nornir-napalm   nornir_napalm plugin
          nornir-netmiko  nornir_netmiko plugin
          nornir-pyez     nornir_pyez plugin
          nornir-scrapli  nornir_scrapli plugin
        ```

    === "nornir_cli dhcp:"
        ```text
        $ nornir_cli dhcp
        Usage: nornir_cli dhcp [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...



        Options:
          --help  Show this message and exit.

        Commands:
          init            Initialize a Nornir
          filter          Do simple or advanced filtering
          show_inventory  Show current inventory
          dhcp_snooping   Configure dhcp snooping
        ```

    === "nornir_cli mpls:"
        ```text
        $ nornir_cli mpls
        Usage: nornir_cli mpls [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...



        Options:
          --help  Show this message and exit.

        Commands:
          init            Initialize a Nornir
          filter          Do simple or advanced filtering
          show_inventory  Show current inventory
          ldp_config      Configure ldp
        ```

**Runbook collections features:**

* empty directories are not displayed as `nornir_cli` groups
* the commands are displayed only in the latest directories in the directory tree. This is based on the `command chains` ability of `nornir_cli` and on the fact that it's impossible to build `command chains`  in parent and child groups. That is a fair constraint related with Click Multi Commands and Multi Commands Chaining
* you may have noticed, that in the example above, there is a `templates` directory in the `dhcp` directory and it was not displayed. `templates` and `__pycache__` are included in the `custom_exceptions`list in `nornir_cli.py`. But you can use these names for the parent directories. 

    If you want to add your exceptions without fixing `custom_exceptions` list, use the `NORNIR_CLI_GRP_EXCEPTIONS` environment variable:

    ```text
    # as instance, to add temp and tmp groups to custom_exceptions list
    $ export NORNIR_CLI_GRP_EXCEPTIONS=temp,tmp
    ```

* if to add runbooks to `custom_commands` without `runbook collection`, they will be in `custom` group
* all python modules, used in your runbook, must be installed in the virtual environment, otherwise the runbook will not be displayed as command in `nornir_cli`

See [example](https://timeforplanb123.github.io/nornir_cli/examples/#custom-nornir-runbooks) and [Examples](https://timeforplanb123.github.io/nornir_cli/examples/).

## Click Complex Applications

[About Click Complex Application](https://click.palletsprojects.com/en/7.x/complex/#){target="_blank"}

[Click complex app example](https://github.com/pallets/click/tree/1cb86096124299579156f2c983efe05585f1a01b/examples/complex){target="_blank"}

An important role in `nornir_cli` is given to the [Context object](https://click.palletsprojects.com/en/7.x/complex/#contexts){target="_blank"}.
As instance, if we run that command:
```text
$ nornir_cli nornir-scrapli init -u username -p password \
-co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}' \
filter --hosts -s 'name=dev_1' send_command --command "display clock" \
send_interactive --interact_events '[["save", "Are you sure to continue?[Y/N]", false], \
["Y", "Save the configuration successfully.", true]]'
```
Context object will be:
```python
{'queue_functions': [{<function send_interactive at 0x7f01839ba280>: {'interact_events': <class 'inspect._empty'>, 'failed_when_contains': None, 'privilege_level': '', 'timeout_ops': None}}], 'queue_parameters': {<function send_interactive at 0x7f01839ba280>: {'interact_events': <class 'inspect._empty'>, 'failed_when_contains': None, 'privilege_level': '', 'timeout_ops': None}}, 'nornir_scrapli': <module 'nornir_scrapli' from '/home/user/virtenvs/3.8.4/lib/python3.8/site-packages/nornir_scrapli/__init__.py'>, 'original': <function send_interactive at 0x7f01839ba280>, 'queue_functions_generator': <generator object decorator.<locals>.wrapper.<locals>.<genexpr> at 0x7f0182fafba0>}
```

* `ctx.obj["queue_functions"]` - queue(list) of dictionaries, where the key is original function, and the value is a set of argumetns. For Commands chains.
* `ctx.obj["queue_parameters"]` - last original function with arguments (from chain of commands)
* `ctx.obj[plugin]` - where plugin is "nornir_scrapli"
* `ctx.obj["original"]` - last original function without arguments (from chain of commands)
* `ctx.obj["queue_functions_generator"]` - ctx.obj["queue_functions"] in the form of a generator expression

If we run custom runbok (as instance, it's called [`dhcp_snooping`](https://timeforplanb123.github.io/nornir_cli/examples/#custom-nornir-runbooks) from example above), then most likely we use a `@custom` decorator:
```text
$ nornir_cli custom dhcp_snooping
```
and there is no Context object, but the first argument will be Nornir object. [See example](https://timeforplanb123.github.io/nornir_cli/examples/#custom-nornir-runbooks).

## .temp.pkl

`.temp.pkl` - is temporary file that stores the last Nornir object with your Inventory.
The Nornir object gets into this file after you run `init` command or `filter` command with `-s / --save` option.

As instance:

=== "init only:"
	```text
	# this command saves the Nornir object with full Inventory to the .temp.pkl file 
	# and runs send_command Task for all Hosts from Inventoy

	$ nornir_cli nornir-scrapli init send_command --command "display clock"
	```
=== "init and filter:"
	```text
	# this command saves the Nornir object with full Inventory to the .temp.pkl file
	# and then saves the Nornir object with filtered Inventory to the .temp.pkl file
	# and runs send_command Task for all Hosts from filtered Inventory

	$ nornir_cli nornir-scrapli init filter -s -a 'name__contains=spine' send_command --command "display clock"
	```
=== "filter only:"
	```text
	# if we started init earlier, then we already have the Nornir object.
	# It will be enough to filter the Nornir Inventory and save it to temp.pkl

	$ nornir_cli nornir-scrapli filter -a 'name__contains=leaf' send_command --command "display clock" send_command --command "display device"
	```
=== "without init and filter:"
	```text
	# if you run nornir_cli without init, filter commands,
	# the nornir_cli will try to take the last Nornir object from this file (temp.pkl) 

	$ nornir_cli nornir-scrapli send_command --command "display clock"
	```

Where is `temp.pkl`?

```text
# if nornir_cli was installed via pip
 
$ la /home/user/virtenvs/3.8.4/lib/python3.8/site-packages/nornir_cli/common_commands/
cmd_filter.py  cmd_init.py  cmd_show_inventory.py  common.py  __init__.py  __pycache__  .temp.pkl
```

## Transform function

The transform function is implemented "on the knee". But, if you want to use it, then add your code to `adapt_host_data` from `nornir_cli/transform/fucntion.py` file and specify it in the `init`.

## Environment Variables
The username and password can be taken from the environment variables.
Start working with `nornir_cli` by exporting the environment variables:

```text
export NORNIR_CLI_USERNAME=username
export NORNIR_CLI_PASSWORD=password
```

And with `NORNIR_CLI_GRP_EXCEPTIONS` environment variable you can exclude directoiries from being displayed in `Runbook collections` (see [here](https://timeforplanb123.github.io/nornir_cli/useful/#custom-runbooks))

Or you can permanently declare environment variables using `.bash_profile` file:

```text
cd ~
open .bash_profile
# add to file
export NORNIR_CLI_USERNAME=username
export NORNIR_CLI_PASSWORD=password
# save the text file and refresh the bash profile
source .bash_profile
```

And now you can do `init` command

## What else can nornir_cli be useful

#### Useful functions

* `_info`

    use `_info` to add statistic to your nornir runbook

    ```python
    from nornir_cli.common_commands import _info

    # code
    # ...

    _info(nr, task)
    # where is :nr: is nornir.core.Nornir object
    # :task: is nornir.task.Task object
    ```
    The `_info` function show statistic in the following format:

    ```text
    dev_1                                             : ok=1               changed=0               failed=0
    dev_2                                             : ok=1               changed=0               failed=0
    dev_3                                             : ok=1               changed=0               failed=0

    OK      : 3
    CHANGED : 0
    FAILED  : 0
    ```

* `_pickle_to_hidden_file`

    If you don't want to use [`runbook collections`](http://timeforplanb123.github.io/nornir_cli/workflow/#runbook-collections) you can use `nornir_cli` for inventory management only.

    You can get `nornir.core.Nornir` object with inventory, filter this inventory and save it using `nornir_cli`, and then use the result:

    ```text
    # get nornir.core.Nornir object, filter inventory and save it
    $ nornir_cli init nornir-scrapli filter -s -a 'name__contains=dev'
    ```

    ```python
    from nornir_cli.common_commands import _pickle_to_hidden_file

    def cli(nr):
        def task(task):
        # code
        # ...

    if __name__ == "__main__":
        # get current nornir.core.Nornir object from nornir_cli
        nr = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)
        # run task with this object
        cli(nr)
    ```

#### nornir_jinja2 plugin

Why is the `nornir_jinja2` plugin here? And then, together with NetBox, this is a really useful thing. You can use NetBox as a variable source for jinja2 templates. Then `nornir_cli` can replace the tool for generating configs. It also motivates you to keep NetBox up-to-date as a Source of Truth. And we need such a motivation, based on the connectivity of different tools.

## How to craft xml from yang

When using `scrapli_netconf` from `nornir_cli`, you may find it useful to be able to get xml from yang.
Easy way to get xml from yang:

* get a model for your vedor. As instance, [here](https://github.com/YangModels/yang){target="_blank"}
* export yang to html, and copy the path:
```text
cd /to/directory/with/yang/models

# use pyang tool
# huawei is here as example only

$ pyang -f jstree -o huawei-ifm.html huawei-ifm.yang

# open html in browser

$ open huawei-ifm.html
```
* find the path and remove unwanted:
```text
$ echo "/ifm:ifm/ifm:interfaces/ifm:interface/ifm:ifName" | sed 's/ifm://g'
/ifm/interfaces/interface/ifName
```
* filter the [pyang](https://github.com/mbj4668/pyang){target="_blank"} output sample-xml-skeleton using the --sample-xml-skeleton-path and get xml:
```text
$ pyang -f sample-xml-skeleton --sample-xml-skeleton-path \
"/ifm/interfaces/interface/ifName" huawei-ifm.yang | tr -d "\n" \
| sed -r 's/>\s+</></g'

<?xml version='1.0' encoding='UTF-8'?><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<ifm xmlns="http://www.huawei.com/netconf/vrp/huawei-ifm"><interfaces><interface><ifName/>
</interface></interfaces></ifm></data>
```
* [run `scrapli_netconf` from `nornir_cli`](https://timeforplanb123.github.io/nornir_cli/workflow/#what-about-netconf)

Thanks [hellt](https://github.com/hellt){target="_blank"} for this tutorial.

Sources:

* [zero](https://github.com/hpreston/python_networking/blob/master/data_manipulation/yang/pyang-examples.sh){target="_blank"}
* [one](https://netdevops.me/nokia-yang-tree/){target="_blank"}
* [two](https://twitter.com/rganascim/status/1223221183753134080?s=09){target="_blank"}
