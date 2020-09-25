#! /usr/bin/python
# -*- encoding: utf-8 -*-
__author__ = 'CARLOS JORDAN'

import requests

from anubisoft_billings.models import BusinessBilling
from anubisoft_billings.serializer.anubisoft_billings import AnubisoftBillingsSerializer
from anubisoft_ecommerce.orders.models import Order

from datetime import datetime
import hashlib
import os
from django.utils.encoding import smart_str
from django.db.models import Count
from django.conf import settings
import json

import base64

AS_BILLINGS_URL = "http://www.tu-efactura.ec:8080"


class SRIBillings:
    order: Order = None

    def __init__(self, order: Order = None):
        self.order = order

    def send(self):
        if self.order.pending_to_billing:
            url = "%s/receptorComprobantesNeutros/rest/factura" % (AS_BILLINGS_URL)
            b = BusinessBilling.objects.all().last()
            if b is not None:
                self.order.billing_number = b.secuencial
                self.order.save()
                b.secuencial += 1
                b.save()
            data = json.dumps(self.order, cls=AnubisoftBillingsSerializer, indent=4)
            print(data)
            headers = {'Content-Type': 'application/json'}
            response = requests.request(
                "POST", url,
                data=data, headers=headers
            )
            if response != "":
                data_received = json.loads(response.text)
                url_pdf = "https://www.tu-efactura.ec/visorRideXml/VisorRide?claveAcceso=%s" % data_received.get(
                    "claveAcceso")
                self.order.pending_to_billing = False
                self.order.url_billing = url_pdf
                self.order.save()
                return url_pdf
        return None
