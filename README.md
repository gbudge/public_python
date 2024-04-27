 # Public Python Apps

This repository contains my collection of Python applications that run inside of a Docker container.

 # Applications

## Kubernetes Label Emitter

[Kubernetes Recommended Labels]: https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/

This is a Python app which runs inside a container, emitting an extended version of the [Kubernetes Recommended Labels] to the console, at a configurable regular interval.

I say "extended version" because the labels emitted are an extension to the [Kubernetes Recommended Labels], to support multiple name, component, and version pairs. Actually, there's no limitation to what the label keys are and which have multiple values, as long as they start with `app.kubernetes.io/`.

### Configuration

The label key and value are configured via environment variables, using the following syntax:
 
`APP_KUBERNETES_IO_<KEY>="<VALUE>"`

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

The interval at which the labels will be emitted is via the following environment variable:

`APP_KUBERNETES_IO_INTERVAL=<SECONDS>`
 
 #### Example

 The following is an example of the environment variable syntax in practice:

<pre>APP_KUBERNETES_IO_INTERVAL="300"
APP_KUBERNETES_IO_INSTANCE="my-instance"
APP_KUBERNETES_IO_MANAGED_BY="my-team"
APP_KUBERNETES_IO_PART_OF="my-collection"
APP_KUBERNETES_IO_INVENTORY_0_NAME="my-app"
APP_KUBERNETES_IO_INVENTORY_0_VERSION="v1"
APP_KUBERNETES_IO_INVENTORY_0_COMPONENT="my-component"
APP_KUBERNETES_IO_INVENTORY_1_NAME="my-app2"
APP_KUBERNETES_IO_INVENTORY_1_VERSION="v2"
APP_KUBERNETES_IO_INVENTORY_1_COMPONENT="my-component2"</pre>

The above configuration will produce the following JSON string (pretty formatted):

<pre>{
    "app.kubernetes.io/interval": "300",
    "app.kubernetes.io/instance": "my-instance",
    "app.kubernetes.io/managed-by": "my-team",
    "app.kubernetes.io/part-of": "my-collection",
    "app.kubernetes.io/inventory": [
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

<pre>{"time": "2024-04-27 01:39:30", "level": "INFO", "message": "Starting Kubernetes Label Emitter. Interval: 300 seconds"}
{"time": "2024-04-27 01:39:30", "level": "INFO", "message": "Exporting sample environment variables."}
{"time": "2024-04-27 01:39:30", "level": "INFO", "message": {"app.kubernetes.io/instance": "my-instance", "app.kubernetes.io/managed.by": "my-team", "app.kubernetes.io/part.of": "my-collection", "app.kubernetes.io/inventory": [{"name": "my-app", "version": "v1", "component": "my-component"}, {"name": "my-app2", "version": "v2", "component": "my-component2"}]}}</pre>
