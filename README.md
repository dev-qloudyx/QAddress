=====
QAddress
=====

QAddress is a Django app to conduct web-based address.

Quick start
-----------

1. Add "address" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "qaddress",
    ]

2. Include the address URLconf in your project urls.py like this::

    path("qaddress/", include("qaddress.urls")),

3. Run ``python manage.py migrate`` to create the address models.
