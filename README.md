
# Avoindata.fi API

This repository provides documentation on using the API of [Avoindata.fi/Opendata.fi][avoindata] (or Yhteentoimivuuspalvelut more broadly). Avoindata.fi is built on top of [CKAN](http://ckan.org/) platform, and provides a metadata catalog of Finnish open datasets. With the Avoindata API, you can retrieve and manager datasets with your own programs.

In the CKAN data model, *users* and *datasets* belong to *organizations*. Organizations own datasets and mandate permissions. Datasets are metadata, describing a single, logical set of open data. A dataset has one or more *resource*, which are either files on the server or external links that contain the data itself.

The following code examples are provided under `examples/`:

* **[avoindata_ckanapi.py](examples/avoindata_ckanapi.py):** A Python example that uses the [ckanapi][ckanapilib] library in making the requests. If you are using Python, it is advisable to use this library.
* **[avoindata_rawhttp.py](examples/avoindata_rawhttp.py):** A low-level Python example that uses the [requests][requests] library in making pure HTTP requests. If you need to form the HTTP requests by yourself for some reason (e.g. you use another language that does not have a CKAN API library), this example gives you some basic pointers.

## Getting started

First you need to create a user account to acquire an API key. While you are free to use the API of [Avoindata.fi][avoindata], we hope that you first develop against our development/sandbox environment [beta.avoindata.fi][avoindatabeta]. To acquire an API key:

1. Register to [beta.avoindata.fi][avoindatabeta] (or try the direct link https://beta.avoindata.fi/fi/user/register ).
2. Login and go to your user profile via your name in the upper-right corner of the top bar.
3. Copy your private API key from the user profile.

Install the prerequisites for the code examples. On Ubuntu/Debian systems:

    sudo apt-get install git python-virtualenv
    git clone https://github.com/yhteentoimivuuspalvelut/ytp-api.git
    cd ytp-api
    virtualenv env-avoindata
    source env-avoindata/bin/activate
    pip install pyopenssl ndg-httpsclient pyasn1 certifi
    pip install requests ckanapi

To try out the examples, run the scripts using your API key:

    python examples/avoindata_ckanapi.py https://beta.opendata.fi/data YOUR_API_KEY
    python examples/avoindata_rawhttp.py https://beta.opendata.fi/data YOUR_API_KEY

## Using the API

### Dataset vs. package and organization vs. group

In the (newer) user interface of CKAN, a dataset is called a *dataset*, while in the codebase and the API it is mostly called a *package*. These terms mean the same thing.

In CKAN, groups and organizations are slightly different from each other (see [stackoverflow](http://stackoverflow.com/questions/20963965/whats-the-difference-between-organizations-groups-in-ckan)), but on implementation level, an organization can be viewed as a subclass of group. Thus, when working with organizations, you might get a response from the API with something about *groups*.

### Name vs. id vs. title

CKAN has three different name-like variables for organizations and datasets. An *id* is a random uuid4 that is used to point to a specific object in the database. A *title* is the human-readable name of the dataset or organization. A *name* is a developer-friendly id for an organization or dataset and must consist of alphanumeric character, dashes and underscores. A name must be unique, and when using the web interface, the name is automatically derived from the title.

Many API functions take an *id* as a parameter, but most of the time this actually (and a bit confusingly) means *id-or-name*. Thus unless you really specifically want to, you can use the *name* attribute and pass it to functions like organization_show.

### Required attributes of a new dataset

As the service is constantly developed, we may make changes to the data schema and new required attributes may appear. If you are having trouble creating a new dataset via the API, you can first create a new dataset in the web interface by hand, and then fetch it from the API with package_show to see which attributes it has.

## Known issues

* Deleting an organization or dataset (`organization_delete` and `package_delete`) in CKAN does not actually delete the organization or dataset, but merely changes their state to deleted. Successive creations using the same names will fail, complaining that there is already an entity with that name. Deleting them from the Web interface seem to delete them completely.
* Some methods may falsely return a 405 Not Allowed, for example when requesting for the details of a dataset that does not exist.
* As the server is HTTPS-only, you might run into problems with certificates. Either upgrade to Python 2.7.9, install pyopenssl or do not verify certificates.

## Disclaimer

Any data you import/create into the development version of the service (beta.avoindata.fi) can be lost without notice at any time.

Furthermore, new software is deployed weekly (sometimes several times per day) to the servers from the master branch, so it is expected that the server is occasionally down and that things will break. However, in general, the API should be much more stable than the web interface. If you want a more mature and stable, but more generic CKAN playground, you can also try using the [API](http://demo.ckan.org/api) of the [CKAN demo instance](http://demo.ckan.org).

## Help and support

If you are having trouble with our API, create an [issue at Github](https://github.com/yhteentoimivuuspalvelut/ytp/issues) or join the discussion at [avoindata.net](http://avoindata.net/questions/suomen-avoimen-datan-portaalin-rakentaminen).

## Further reading

* [CKAN API documentation][ckanapidocs]
* [CKAN API client library and CLI][ckanapilib]
* [CKAN API client libraries in other languages (old docs, possibly obsolete)][otherclients]

[avoindata]: https://avoindata.fi
[avoindatabeta]: https://beta.avoindata.fi
[ckanapidocs]: http://docs.ckan.org/en/latest/api/index.html
[ckanapilib]: https://github.com/ckan/ckanapi
[requests]: http://requests.readthedocs.org/en/latest/
[otherclients]: http://docs.ckan.org/en/ckan-1.7.1/api.html#clients
