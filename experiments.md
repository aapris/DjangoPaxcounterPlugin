Random experiments
==================

SQL query to get all Devices and their latest Seen

```
SELECT * FROM (
    SELECT mac, "end", ROW_NUMBER() OVER (
        PARTITION BY mac
    ) AS row_number
    FROM paxcounter_seen s
    INNER JOIN paxcounter_device d
    ON d.id = s.device_id) AS x
WHERE row_number = 1 order by "end" DESC;
```


Add some objects manually (`python manage.py shell`)

```
import datetime
from django.db.models.expressions import RawSQL, Subquery, OuterRef
from django.db.models import Window, F, Max, Prefetch
from django.db.models.functions import RowNumber
from django.utils import timezone
from paxcounter.models import Device, Scanner, Seen

d, created = Device.objects.get_or_create(mac='11BBCCDDEEFF')
s, created = Scanner.objects.get_or_create(devid='123456ABCD')
now = timezone.now()
seen = Seen(device=d, scanner=s, start=now - datetime.timedelta(seconds=150), end=now)
seen.save()
```

Repeat this several times after a short while:

```
now = timezone.now()
seen = Seen(device=d, scanner=s, start=now - datetime.timedelta(seconds=150), end=now)
seen.save()
```

This seems to work (show all devices and their last seen)

```
last_seen = Seen.objects.filter(
    end=Subquery(
        (Seen.objects
            .filter(device=OuterRef('device'))
            .values('device')
            .annotate(last_seen=Max('end'))
            .values('last_seen')[:1]
        )
    )
)

devices = Device.objects.all().prefetch_related(
    Prefetch('seen_set',
        queryset=last_seen,
        to_attr='last_seen'
    )
)

for d in devices:
    print(f'{d.mac} {d.type} {d.last_seen[0].end.isoformat()}')
```
