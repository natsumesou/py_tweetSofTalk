#!/usr/bin/python
# -*- coding: utf-8 -*-

class StatusError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'StatusError: an Error has Occured with status code: ' + str(self.value)
