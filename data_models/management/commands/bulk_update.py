import asyncio
import asyncpg

from time import perf_counter
from random import randint
from secrets import token_urlsafe

from django.db import connection
from django.db.models.sql.subqueries import UpdateQuery
from django.core.management.base import BaseCommand

from data_models.models import DataModel

TIMES = 30
OBJECTS = 1000


def random_id():
    return randint(1, 100_000)


def naive_update():
    for _ in range(OBJECTS):
        object = DataModel.objects.get(id=random_id())
        object.text = token_urlsafe(75)
        object.description = token_urlsafe(150)
        object.save()


def bulk_update():
    objects = []
    for _ in range(OBJECTS):
        objects.append(DataModel.objects.get(id=random_id()))

    for item in objects:
        item.text = token_urlsafe(75)
        item.description = token_urlsafe(150)

    DataModel.objects.bulk_update(objects, ['text', 'description'])


def compile_update_query(query_set, update_kwargs):
    query = query_set.query.chain(UpdateQuery)
    query.add_update_values(update_kwargs)
    return str(query)


def query_update():
    queries = []
    cursor = connection.cursor()
    for _ in range(OBJECTS):
        query_set = DataModel.objects.filter(id=random_id())
        update_kwargs = {
            'text': f"'{token_urlsafe(75)}'",  # note \' symbols
            'description': f"'{token_urlsafe(150)}'"  # note \' symbols
        }
        queries.append(compile_update_query(query_set, update_kwargs))

    cursor.execute(';'.join(queries))


async def run_query(q):
    conn = await asyncpg.connect(user='postgres', password='postgres',
                                 database='bulk_test', host='localhost')  # takes 2..6 ms
    await conn.execute(q)
    await conn.close()


def asyncpg_update(loop):
    queries = []
    for _ in range(OBJECTS):
        query_set = DataModel.objects.filter(id=random_id())
        update_kwargs = {
            'text': f"'{token_urlsafe(75)}'",  # note \' symbols
            'description': f"'{token_urlsafe(150)}'"  # note \' symbols
        }
        queries.append(compile_update_query(query_set, update_kwargs))

    loop.run_until_complete(run_query(';'.join(queries)))


class Command(BaseCommand):
    help = f'Updates {OBJECTS} rows {TIMES} times'

    def add_arguments(self, parser):
        parser.add_argument('-q', '--query', action='store_true',
                            help='Perform bulk update with raw SQL query')

        parser.add_argument('-n', '--naive', action='store_true',
                            help='Perform updates in naive way')

        parser.add_argument('--asyncpg', action='store_true',
                            help='Perform updates with `asyncpg` driver')

    def handle(self, *args, **options):
        by_query = options['query']
        naive_way = options['naive']
        by_asyncpg = options['asyncpg']

        tic = perf_counter()

        if by_asyncpg:
            print('by asyncpg')
            loop = asyncio.get_event_loop()
            for _ in range(TIMES):
                asyncpg_update(loop)

        elif by_query:
            print('by query')
            for _ in range(TIMES):
                query_update()

        elif naive_way:
            print('naive way')
            for _ in range(TIMES):
                naive_update()

        else:
            print('by bulk_update')
            for _ in range(TIMES):
                bulk_update()

        toc = perf_counter()

        print(f">> {toc - tic:0.6f} seconds")
