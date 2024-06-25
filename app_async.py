import asyncio
import aiohttp
import datetime
from more_itertools import chunked
from models import Base, Session, SWPeople, engine, init_db_async

MAX_REQUESTS_CHUNK = 6

SINGLE_VALUE_KEYS = [
    "name",
    "height",
    "mass",
    "hair_color",
    "skin_color",
    "eye_color",
    "birth_year",
    "gender",

]
MULTIPLE_VALUE_KEYS = {
    "films": "title",
    "species": 'name',
    "homeworld": "name",
    "vehicles": "name",
    "starships": "name",

}



async def get_person_data(person_id, http_session) -> dict:
    
    response = await http_session.get(f"https://swapi.py4e.com/api/people/{person_id}")
    person_raw_data = await response.json()
    result_code = response.status
    if result_code == 200:
        result_dict = {key: person_raw_data[key] for key in SINGLE_VALUE_KEYS}
        for key, value in MULTIPLE_VALUE_KEYS.items():
            if len(person_raw_data[key]) != 0:
                result_str = await get_link(value, person_raw_data[key])
            else:
                result_str = "n/a"
            result_dict[key] = result_str
    else:
        result_dict = {key: 'n/a' for key in SINGLE_VALUE_KEYS}
        result_dict = result_dict | {key: 'n/a' for key, value in MULTIPLE_VALUE_KEYS.items()}
    return result_dict


async def get_link(key, raw_data):
    session = aiohttp.ClientSession()
    if type(raw_data) is str:
        raw_data = [raw_data]
    result_list = [await session.get(element) for element in raw_data]
    result_json_list = []
    for element in result_list:
        result_json_list.append(await element.json())

    await session.close()
    result = "' ".join([element[key] for element in result_json_list])
    return result


async def insert_people(people_list_json, person_id):
    people_list = [
        SWPeople(
            person_id=person_id + counter + 1,
            birth_year=person["birth_year"],
            eye_color=person["eye_color"],
            hair_color=person["hair_color"],
            skin_color=person["skin_color"],
            films=person["films"],
            gender=person["gender"],
            height=person["height"],
            homeworld=person["homeworld"],
            mass=person["mass"],
            name=person["name"],
            species=person["species"],
            starships=person["starships"],
            vehicles=person["vehicles"],
        )
        for counter, person in enumerate(people_list_json)
    ]
    async with Session() as session:
        session.add_all(people_list)
        await session.commit()


async def main():

    await init_db_async()
    http_session = aiohttp.ClientSession()

    for person_chunk in chunked(range(1, 50), MAX_REQUESTS_CHUNK):
        person_coros = [get_person_data(person_id, http_session) for person_id in person_chunk]
        people = await asyncio.gather(*person_coros)
        insert_people_coro = insert_people(people, person_chunk[0])
        asyncio.create_task(insert_people_coro)
        print(f"Person #{person_chunk} added.")

    await http_session.close()

    tasks = asyncio.all_tasks()
    current_task = asyncio.current_task()
    tasks.remove(current_task)
    await asyncio.gather(*tasks)
    print("All tasks are finished.")


start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)