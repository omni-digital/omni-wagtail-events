# Wagtail Events [![Build Status](https://travis-ci.com/omni-digital/omni-wagtail-events.svg?token=9QKsFUYHUxekS7Q4cLHs&branch=master)](https://travis-ci.com/omni-digital/omni-wagtail-events)

A wagtail library for events, with tools for filtering by date.

## Requirements

Wagtail events requires Django 1.8 or later and Wagtail 1.8 or later.

## Supported Versions

Python: 2.7, 3.4, 3.5, 3.6

Django: 1.8, 1.9, 1.10

Wagtail: 1.8, 1.9, 1.10, 1.11

## Getting started

Installing from pip:

```
pip install omni_wagtail_events
```

Adding to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'wagtail_events',
    ...
]
```

Running the migrations:

```
python manage migrate wagtail_events
```

## Models

### EventIndex

An index/listing page for EventDetail instances, with optional pagination.

### EventDetail

A detail page for an event series, the EventDetail can contain single or multiple EventOccurrence instances.

### EventOccurrence

An single occurrence of an event.

## Future Development Plans:

- EventSingleton: A single event that will only have a single occurrence.

## Warranty

*THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE USE OF THIS SOFTWARE IS WITH YOU.*

*IN NO EVENT WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE THE LIBRARY, BE LIABLE TO YOU FOR ANY DAMAGES, EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.*


Again, see the included LICENSE file for specific legal details.
