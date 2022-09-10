#!/bin/env python
# -*- coding: utf-8 -*-

"""Utility class of Nutanix Rest API v2
(Work In Process)
requirements: python 3.x, requsts
"""
# import json
import requests
import urllib3


# Utils class of API v2
class NutanixRestapiUtils:
    def __init__(self, username, password, base_url):
        self.base_url = base_url
        urllib3.disable_warnings()

        self.s = requests.Session()
        self.s.auth = (username, password)
        self.s.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'})

    def activate_pd(self, payload):
        """Activate protection domain (Unplanned failover)

        Args:
            payload (_type_): _description_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        # todo
        return
