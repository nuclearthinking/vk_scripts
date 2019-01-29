import datetime
import time
from enum import Enum

import click
import vk
from vk.exceptions import VkAPIError

today = datetime.date.today()
ADULT_BIRTH_DATE = datetime.date(today.year - 18, today.month, today.day)

BAN_COMMENTARY = 'Бан по ограничению 18+ (предварительно). Для разбана/подтверждения возраста написать любому из ' \
                 'администраторов группы.'

access_token = "TOKEN"
session = vk.Session(access_token=access_token)
vk_api = vk.API(session, v='5.92')


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

    def ban(self):
        try:
            vk_api.groups.ban(
                group_id=121768940,
                owner_id=self.id,
                comment=BAN_COMMENTARY,
                comment_visible=1
            )
        except VkAPIError as e:
            if 'Captcha needed' not in e.message:
                raise e
            data = e.error_data
            captcha_sid = data.get('captcha_sid')
            captcha_img = data.get('captcha_img')

            print(f'CAPTCHA LINK {captcha_img}')
            captcha_key = input('Input text from captcha: ')

            try:
                vk_api.groups.ban(
                    group_id=121768940,
                    owner_id=self.id,
                    comment=BAN_COMMENTARY,
                    comment_visible=1,
                    captcha_sid=captcha_sid,
                    captcha_key=captcha_key
                )
            except:
                pass


def fetch_items(func, **kwargs):
    result = list()
    count, counter = 1, 0
    while counter < count:
        response = func(offset=counter, **kwargs)
        count = response.get('count')
        items = response.get('items')
        result.extend(items)
        counter += len(items)
        time.sleep(0.5)
    return result


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


def main(count: int):
    banned_users = fetch_items(vk_api.groups.getBanned, group_id=121768940, count=200)
    subscribers = fetch_items(vk_api.groups.getMembers, group_id='box_review', fields='bdate')

    banned_ids = [user['profile']['id'] for user in banned_users if user.get('profile')]

    subscribers_data = list()
    for user in subscribers:
        _id = user.get('id')
        bdate = user.get('bdate')

        if _id in banned_ids:
            print(f'User {_id} already banned')
            continue

        if not bdate:
            subscribers_data.append(Subscriber(id=_id, status=Status.unknown))
            continue

        if not has_birth_year(bdate):
            subscribers_data.append(Subscriber(id=_id, status=Status.unknown))
            continue

        if is_adult(str_to_date(bdate)):
            subscribers_data.append(Subscriber(id=_id, status=Status.is_adult))
            continue

        subscribers_data.append(Subscriber(id=_id, status=Status.not_adult))

    children = [sub for sub in subscribers_data if sub.status in [Status.not_adult]]

    print(f'{len(children)} users wil be banned')
    for child in children:
        print(f'Ban user {child.id}')
        child.ban()
        print(f'User {child.id} successfully banned')
        time.sleep(0.3)

    print('Done')


@click.command()
@click.option('--count',
              default=200,
              type=int,
              help='Amount of users will be banned at this session, 0 if you want ban all users'
              )
def ban(count):
    click.echo(f'count {count}')


if __name__ == '__main__':
    ban()
