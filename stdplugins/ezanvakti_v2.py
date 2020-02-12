import asyncio
import datetime
import json
import logging
import os
import requests
from telethon import events

# from ..bin.namaz_vakti import namazvakti
from uniborg.util import admin_cmd
# from bin.namaz_vakti import namazvakti
from bin.namaz_vakti.namazvakti import namazvakti
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

TEMP = ''


@borg.on(admin_cmd(pattern=("ezanv ?(.*)")))
async def namaz_(event):
    if not event.text.startswith("."):
        return ""

    if not event.pattern_match.group(1):
        LOKASYON = TEMP
        if not LOKASYON:
            await event.edit("Please specify a city or a state.")
            return
    else:
        LOKASYON = event.pattern_match.group(1)
        LOKASYON = LOKASYON.upper()
    namaz = namazvakti()
    sehirler_sonuc = namaz.sehirler(2)
    sonuc_sehirler = {v: k for k, v in sehirler_sonuc['veri'].items()}
    sonuc_sehirler_1 = sonuc_sehirler[LOKASYON]
    yer = './bin/namaz_vakti/db/yerler.ndb'
    with open(yer, "r", encoding="utf8") as f:
        yerler_json = json.load(f)
    print(yerler_json['2']['sehirler'][f"{sonuc_sehirler_1}"]['ilceler'].items())
    inverse_yerler = {v: k for k, v in yerler_json['2']['sehirler'][f"{sonuc_sehirler_1}"]['ilceler'].items()}
    print(inverse_yerler[LOKASYON])
    sonuc = namaz.vakit(inverse_yerler[LOKASYON])
    # print(inverse_yerler)
    # yerlerim = inverse_yerler[LOKASYON]
    await event.edit(sonuc)

#    print(sonuc_sehirler[LOKASYON])
#     print(LOKASYON)






    # url = f'http://muslimsalat.com/{LOKASI}.json?key=bd099c5825cbedb9aa934e255a81a5fc'
    # request = requests.get(url)
    # result = json.loads(request.text)

    # if request.status_code != 200:
    #     await namaz.edit(f"{result['status_description']}")
    #     return

    # tanggal = result["items"][0]["date_for"]
    # lokasi = result["query"]
    # lokasi2 = result["country"]
    # lokasi3 = result["address"]
    # lokasi4 = result["state"]

    # subuh = result["items"][0]["fajr"]
    # syuruk = result["items"][0]["shurooq"]
    # zuhur = result["items"][0]["dhuhr"]
    # ashar = result["items"][0]["asr"]
    # maghrib = result["items"][0]["maghrib"]
    # isya = result["items"][0]["isha"]

    # textkirim = (f"⏱  **Tarih ** `{tanggal}`:\n" +
    #              f"`{lokasi} | {lokasi2} | {lokasi3} | {lokasi4}`\n\n" +
    #              f"**Güneş :** `{subuh}`\n" +
    #              f"**İmsak :** `{syuruk}`\n" +
    #              f"**Öğle :** `{zuhur}`\n" +
    #              f"**İkindi :** `{ashar}`\n" +
    #              f"**Akşam :** `{maghrib}`\n" +
    #              f"**Yatsı :** `{isya}`\n")

    # await namaz.edit(textkirim)
