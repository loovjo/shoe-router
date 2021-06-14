import time
import asyncio
import aiohttp

import george_status
import analysis

ANAL = None

async def query_page(sess, stati, user):
    start = time.time()
    try:
        stati[user.name] = await george_status.george_status(sess, user.link)
        print(f"{user.name} = success in {time.time() - start:.3}s!")
    except george_status.GeorgeError as e:
        print(user.name, "=epic fail (", e, ")")
    except BaseException as e:
        print(user.name, "= oh no", type(e), e)

async def analyze():
    global ANAL

    async with aiohttp.ClientSession() as sess:
        users = await george_status.read_users(sess)

        stati = {}

        print("querying...")
        await asyncio.gather(*[query_page(sess, stati, user) for user in users])

        state = analysis.GeorgeState.from_data(users, stati)

        ANAL = state.analyze()

if __name__ == "__main__":
    asyncio.run(analyze())
    print(ANAL)
    print(ANAL.into_html())