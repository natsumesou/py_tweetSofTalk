#!/usr/bin/python
# -*- coding: utf-8 -*-

from statusError import StatusError

try:
    raise StatusError(404)
except StatusError, e:
    print e

