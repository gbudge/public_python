 # Public Python Apps

This repository contains my collection of Python applications that run inside of a Docker container.

 # Applications

## Environment Variable Logger

[Kubernetes Recommended Labels]: https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/

This is a Python app which runs inside a container, periodically emitting JSON formatted messages to the console, using the [Kubernetes Recommended Labels] format as inspiration.

I say "inspriation" because the labels emitted are an extension to the [Kubernetes Recommended Labels], to support multiple name, component, and version pairs. Actually, there's no limitation to what the label keys are and which have multiple values.

### Configuration

The following environment variables are supported:

|Name|Value|Description|
|-|-|-|
|`EV_LOGGER_PREFIX`|(string)|Mandatory. The prefix all other environment variables need to use.|
|`EV_LOGGER_INTERVAL`|(number)|Optional. The interval in seconds the log is emitted to the console. Default is 300 (5 minutes).<br /><br />It must be greater than 0 and less than 604800 (1 week). Setting this to 0 will result in logging once only and then exiting successfully.|
|`EV_LOGGER_INDENT`|(number)|Optional. The number of spaces to indent the JSON message. Default is 0.<br /><br >Must be greater than or equal to 0.|
|`<EV_LOGGER_PREFIX>_<KEY>`|(string)|Mandatory. The label key and value to log (see below). Must have at least 1.|

The label key and value to log are configured via environment variables, using the following syntax:
 
`<EV_LOGGER_PREFIX>_<KEY>="<VALUE>"`

Where...

|Field|Description|
|-|-|
|`<KEY>`|Represents the key name.|
|`<VALUE>`|Represents the key value.|

If `<VALUE>` contains a string formatted as `<PARENT_KEY>_[ID]_<CHILD_KEY>`, it indicates a JSON array of objects, where:

|Field|Description|
|-|-|
|`<PARENT_KEY>`|Represents the parent key name.|
|`[ID]`|Represents the index of the array element.|
|`<CHILD_KEY>`|Represents the child key name.|

Note: All label keys and sub-keys are converted to lower case.
 
 #### Example

 The following is an example of the environment variable syntax in practice:

<pre>EV_LOGGER_PREFIX="APP_CONTOSO_MS"
EV_LOGGER_INTERVAL=600
EV_LOGGER_INDENT=2
APP_CONTOSO_MS_INTERVAL="300"
APP_CONTOSO_MS_INSTANCE="my-instance"
APP_CONTOSO_MS_MANAGED_BY="my-team"
APP_CONTOSO_MS_PART_OF="my-collection"
APP_CONTOSO_MS_INVENTORY_0_NAME="my-app"
APP_CONTOSO_MS_INVENTORY_0_VERSION="v1"
APP_CONTOSO_MS_INVENTORY_0_COMPONENT="my-component"
APP_CONTOSO_MS_INVENTORY_1_NAME="my-app2"
APP_CONTOSO_MS_INVENTORY_1_VERSION="v2"
APP_CONTOSO_MS_INVENTORY_1_COMPONENT="my-component2"</pre>

The above configuration will produce the following JSON string (pretty formatted):

<pre>{
  "app.contoso.ms/interval": "600",
  "app.contoso.ms/instance": "my-instance",
  "app.contoso.ms/managed-by": "my-team",
  "app.contoso.ms/part-of": "my-collection",
  "app.contoso.ms/inventory": [
    {
      "name": "my-app",
      "version": "v1",
      "component": "my-component"
    },
    {
      "name": "my-app2",
      "version": "v2",
      "component": "my-component2"
    }
  ]
}</pre>

At the console, it will be emitted as follows:

<pre>{"time": "2024-04-27 01:39:30", "level": "INFO", "message": "Starting Kubernetes Label Emitter v2.0.0. Interval: 600 seconds"}
{"time": "2024-04-27 01:39:30", "level": "INFO", "message": "Exporting sample environment variables."}
{"time": "2024-04-27 01:39:30", "level": "INFO", "message": {"app.contoso.ms/instance": "my-instance", "app.contoso.ms/managed.by": "my-team", "app.contoso.ms/part.of": "my-collection", "app.contoso.ms/inventory": [{"name": "my-app", "version": "v1", "component": "my-component"}, {"name": "my-app2", "version": "v2", "component": "my-component2"}]}}</pre>
