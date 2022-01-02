#! python3

from lcu_driver import Connector
import random

connector = Connector()

async def create_lobby(connection):
    data = {
        "customGameLobby": {
            "configuration": {
                "gameMode": "PRACTICETOOL",
                "gameMutator": "",
                "gameServerRegion": "",
                "mapId": 11,
                "mutators": {
                    "id": 1
                },
                "spectatorPolicy": "AllAllowed",
                "teamSize": 5,
            },
            "lobbyName": "5v5 Practice Tool",
            "lobbyPassword": ""
        },
        "isCustom": True,
    }
    
    print('[INFO] Creating 5v5 Practice Tool Lobby')
    lobby = await connection.request('post', '/lol-lobby/v2/lobby', data=data)

    if lobby.status == 200:
        print('[INFO] Lobby created')
    else:
        print('[ERROR] Failed to create lobby')

async def delete_lobby(connection):
    lobby = await connection.request('delete', '/lol-lobby/v2/lobby')

    if lobby.status == 204:
        print('[INFO] Lobby deleted')
    else:
        print('[ERROR] Failed to delete lobby')

async def do_add_bots(connection, data):
    res = await connection.request('post', '/lol-lobby/v1/lobby/custom/bots', data=data)
    if res.status == 204:
        print('[INFO] Bot added')
    else:
        print('[ERROR] Failed to add bot')

async def add_bots(connection, ids):
    for id in ids:
        data = {
            "botDifficulty": "MEDIUM",
            "championId": id,
            "teamId": "200"
        }

        print('[INFO] Adding bot to enemy\'s team')
        await do_add_bots(connection, data)


@connector.ready
async def connect(connection):
    print('[INFO] LCU API connected')

    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    

    if summoner.status != 200:
        print('[ERROR] Couldn\'t fetch summoner\'s profile')
    else:
        champions = []

        while not champions:
            print('[INFO] Fetching champions list')
            champions = await (await connection.request('get', '/lol-lobby/v2/lobby/custom/available-bots')).json()

            if not champions:
                print('[INFO] Creating dummy lobby')
                await create_lobby(connection)
                await delete_lobby(connection)
        
        ids = random.sample([champion['id'] for champion in champions], 5)
        
        await create_lobby(connection)
        await add_bots(connection, ids)


@connector.close
async def disconnect(_):
    print('[INFO] The client has been closed')

if __name__ == "__main__":
    connector.start()