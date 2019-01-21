Paxcounter plugin
=================

Paxcounter is a plugin for
https://github.com/aapris/DjangoPluginDemo
and it handles and stores data sent by `paxcounter_readserial.py` script.

Quick start
-----------

1. Create Python virtual environment, create installation package and install it:
    ```
    # Create virtualenv first using python3.6 or newer
    mv -v dist/ /tmp/  # Remove old installation package, if it exists
    python setup.py sdist
    pip install dist/django-paxcounter-plugin-0.1.tar.gz
    pip install -r requirements.txt
    ```  

1. Add "paxcounter" to your INSTALLED_APPS setting like this:
    ```
        INSTALLED_APPS = [
            ...
            'paxcounter',
        ]
    ```

1. Run `python manage.py migrate` to create Paxcounter  models.

1. Run `python manage.py runserver` to start development server.

1. Create "paxcounter" endpoint in [Django admin](http://127.0.0.1:8000/admin/businesslogic/endpoint/).

Reading MAC data from serial port
---------------------------------

`paxcounter_readserial.py --port /dev/tty.SLAB_USBtoUART --url http://127.0.0.1:8000/paxcounter`

NOTE: you need slightly modified version of [PAXCOUNTER](https://github.com/cyberman54/ESP32-Paxcounter)
firmware for ESP32, which uses static (not random) salt. In 
[maxsniff.cpp](https://github.com/cyberman54/ESP32-Paxcounter/blob/80866adecf176ba47321dbffa04c0dc1ab89d75a/src/macsniff.cpp#L14) 
replace
```
salt = (uint16_t)random(65536);
```
with
```
salt = 42;  // Any number between 0 and 65535 
```

In addition, by default PAXCOUNTER outputs only 32 least significant bits of MAC address.
To get all 48 bits you need to add them to 
[debug output](https://github.com/cyberman54/ESP32-Paxcounter/blob/80866adecf176ba47321dbffa04c0dc1ab89d75a/src/macsniff.cpp#L117)
in the same file. (Some coding experience is needed.)
