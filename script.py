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


def ban_user(user_id: int):
    vk_api.groups.ban(
        group_id=-121768940,
        owner_id=user_id,
        comment='18+',
        comment_visible=1
    )


subscribers_data = list()

access_token = "a4182951f78261722340f0d8c8415f58f8757a6c936b1da6f1d11d15efb06ee684f29e5b5a104ba09f463"
session = vk.Session(access_token=access_token)
vk_api = vk.API(session, v='5.92')

response = vk_api.groups.getMembers(group_id='box_review', fields='bdate')
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

children = [sub for sub in subscribers_data if sub.status in [Status.not_adult, Status.unknown]]

for child in children:
    print(f'Ban user {child.id}')
    ban_user(child.id)


print('break point')
