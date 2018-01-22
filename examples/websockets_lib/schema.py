import random
import asyncio
import graphene

from graphql_ws.pubsub import AsyncioPubsub

p = AsyncioPubsub()


class Query(graphene.ObjectType):
    base = graphene.String(value=graphene.String())

    async def resolve_base(root, info, value='Hello World!'):
        await p.publish('BASE', value)
        return value


class RandomType(graphene.ObjectType):
    seconds = graphene.Int()
    random_int = graphene.Int()


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())
    random_int = graphene.Field(RandomType)
    base_sub = graphene.String()

    async def resolve_base_sub(root, info):
        sub_id, q = p.subscribe('BASE')
        while True:
            payload = await q.get()
            yield payload

    async def resolve_count_seconds(root, info, up_to=5):
        for i in range(up_to):
            print("YIELD SECOND", i)
            yield i
            await asyncio.sleep(1.)
        yield up_to

    async def resolve_random_int(root, info):
        i = 0
        while True:
            yield RandomType(seconds=i, random_int=random.randint(0, 500))
            await asyncio.sleep(1.)
            i += 1


schema = graphene.Schema(query=Query, subscription=Subscription)