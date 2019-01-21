import json
import datetime
from dateutil.parser import parse
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.utils import timezone

from businesslogic.endpoint import EndpointProvider
from paxcounter.models import Device, Seen, Scanner


def handle_paxcounterdata(data):
    # now = timezone.now()
    for k, v in data.items():
        _type = data[k].get('type')
        ts = data[k].get('time')  # as a string, might be a good idea to use dateutil's parse to create datetime here?
        device, created = Device.objects.get_or_create(mac=k, type=_type[0])
        scanner, created = Scanner.objects.get_or_create(devid='1111')
        # 1. Old experiment, which updates recent Seen
        # since = now - datetime.timedelta(seconds=60)
        # seen_list = Seen.objects.filter(device=device, scanner=scanner, end__gt=since).order_by('-end')
        # if seen_list.count() == 0:
        #     seen = Seen(device=device, scanner=scanner, start=ts, end=ts)
        # else:
        #     seen = seen_list[0]
        #     seen.end = ts
        # 2. Just create always new Seen object:
        seen = Seen(device=device, scanner=scanner, rssimin=data[k].get('rssi_min', 0),
                    rssimax=data[k].get('rssi_max', 0), start=ts, end=ts)
        seen.save()
    return HttpResponse(f'ok', content_type='text/plain')


class PaxcounterPlugin(EndpointProvider):
    description = 'Process paxcounter mac address data'

    def handle_request(self, request):
        # Handle request here and pass data forward and return response as quickly as possible
        json_str = request.body
        try:
            data = json.loads(json_str)
            response = handle_paxcounterdata(data)
        except json.JSONDecodeError as err:
            # TODO: send to error log
            response = HttpResponseBadRequest(err)
        return response
