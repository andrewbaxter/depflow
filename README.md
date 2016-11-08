#What

Depflow is a library for building pipelined processes where individual steps can be conditionally omitted.  The traditional use case is building software.

Here is an example process using plumbum:

```
```

#Why

Existing build systems generally take a framework approach and are geared around file system changes.  Depflow is a Python library (and an extremely simple one) so it can be embedded in other software such as command line tools and scripts.  It was designed to easily mix file system and non file system dependencies such as API endpoint responses or docker image hashes.

#Defining a process

Define steps in the process as nullary functions decorated with `@depflow.depends(*dependencies)`.  Dependencies can either be other steps or checks such as `depflow.file(path)` and `depflow.file_hash(path)`.  Steps are run as they are defined.

#Managing external inputs

A unique identifier is created to store and compare the state of dependent relations.  This unique identifier is based on the working directory, step name, and the identities of its dependencies.  If you need to separate the results for multiple invitations of the same process, call `depflow.flow_id` with a unique value.

For example, in a process that uses command line arguments:

```
```

#Creating new checks

Depflow accounts for two different types of dependency checks.

Use `@depflow.check` to decorate a function that returns a value representing the state of some resource, where a dependent step only needs to be updated if the state of the resource changes.

Example:

```
```

Use `@depflow.raw_check` to decorate a function that returns a boolean indicating that the dependent step needs to be updated.

Example: 

```
```
