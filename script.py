import datetime
from enum import Enum

import vk

today = datetime.date.today()
ADULT_BIRTH_DATE = datetime.date(today.year - 18, today.month, today.day)


class Status(Enum):
    is_adult = 'adult'
    not_adult = 'not_adult'
    unknown = 'unknown'


class Subscriber:
    id: int
    status: Status

    def __init__(self, id: int, status: Status) -> None:
        self.id = id
        self.status = status


def chunks(l, n):
    n = max(1, n)
    return (l[i:i + n] for i in range(0, len(l), n))


def has_birth_year(bdate: str):
    dot_count = bdate.count('.')
    if dot_count >= 2:
        return True
    return False


def is_adult(birth_date: datetime.date):
    return birth_date <= ADULT_BIRTH_DATE


def str_to_date(birth_date: str) -> datetime.date:
    birth_date_split = birth_date.split('.')
    return datetime.date(
        day=int(birth_date_split[0]),
        month=int(birth_date_split[1]),
        year=int(birth_date_split[2])
    )


subscribers_data = list()

access_token = "TOKEN"
session = vk.Session(access_token=access_token)
vk_api = vk.API(session, v='5.92')

response = vk_api.groups.getMembers(group_id='pleasuretherapy', fields='bdate')
count = response.get('count')
subscribers = response.get('items')
offset = len(subscribers)



for user in subscribers:
    id = user.get('id')
    bdate = user.get('bdate')

    if not bdate:
        subscribers_data.append(Subscriber(id=id, status=Status.unknown))
        continue

    if not has_birth_year(bdate):
        subscribers_data.append(Subscriber(id=id, status=Status.unknown))
        continue

    if is_adult(str_to_date(bdate)):
        subscribers_data.append(Subscriber(id=id, status=Status.is_adult))
        continue

    subscribers_data.append(Subscriber(id=id, status=Status.not_adult))

print('break point')
