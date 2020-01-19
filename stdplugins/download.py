"""Download Files to your local server
Syntax:
.download
.download url | file.name to download files from a Public Link"""
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
import asyncio
import math
import os
import time
from datetime import datetime

import aiohttp
from pySmartDL import SmartDL
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

from uniborg.util import admin_cmd, humanbytes, progress, time_formatter

from sample_config import Config

def progress(current, total):
    """ Logs the download progress """
    LOGS.info(
        "Downloaded %s of %s\nCompleted %s",
        current, total, (current / total) * 100
    )

@borg.on(admin_cmd(pattern="download ?(.*)", allow_sudo=True))
async def download(target_file):
    """ For .download command, download files to the userbot's server. """
    if not target_file.text[0].isalpha() and target_file.text[0] not in ("/", "#", "@", "!"):
        if target_file.fwd_from:
            return
        await target_file.edit("Processing ...")
        input_str = target_file.pattern_match.group(1)
        if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
            os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
        if target_file.reply_to_msg_id:
            start = datetime.now()
            downloaded_file_name = await target_file.client.download_media(
                await target_file.get_reply_message(),
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=progress,
            )
            end = datetime.now()
            duration = (end - start).seconds
            await target_file.edit(
                "Downloaded to `{}` in {} seconds.".format(downloaded_file_name, duration)
            )
        elif "|" in input_str:
            url, file_name = input_str.split("|")
            url = url.strip()
            # https://stackoverflow.com/a/761825/4723940
            file_name = file_name.strip()
            required_file_name = Config.TMP_DOWNLOAD_DIRECTORY + "" + file_name
            start = datetime.now()
            resp = requests.get(url, stream=True)
            with open(required_file_name, "wb") as file:
                total_length = resp.headers.get("content-length")
                # https://stackoverflow.com/a/15645088/4723940
                if total_length is None:  # no content length header
                    file.write(resp.content)
                else:
                    downloaded = 0
                    total_length = int(total_length)
                    for chunk in resp.iter_content(chunk_size=128):
                        downloaded += len(chunk)
                        file.write(chunk)
                        done = int(100 * downloaded / total_length)
                        download_progress_string = "Downloading ... [%s%s]" % (
                            "=" * done,
                            " " * (50 - done),
                        )
                        LOGS.info(download_progress_string)
            end = datetime.now()
            duration = (end - start).seconds
            await target_file.edit(
                "Downloaded to `{}` in {} seconds.".format(required_file_name, duration)
            )
        else:
            await target_file.edit("Reply to a message to download to my local server.")


async def download_coroutine(session, url, file_name, event, start):
    CHUNK_SIZE = 2341
    downloaded = 0
    display_message = ""
    async with session.get(url) as response:
        total_length = int(response.headers["Content-Length"])
        content_type = response.headers["Content-Type"]
        if "text" in content_type and total_length < 500:
            return await response.release()
        await event.edit("""Initiating Download
URL: {}
File Name: {}
File Size: {}""".format(url, file_name, humanbytes(total_length)))
        with open(file_name, "wb") as f_handle:
            while True:
                chunk = await response.content.read(CHUNK_SIZE)
                if not chunk:
                    break
                f_handle.write(chunk)
                downloaded += CHUNK_SIZE
                now = time.time()
                diff = now - start
                if round(diff % 5.00) == 0 or downloaded == total_length:
                    percentage = downloaded * 100 / total_length
                    speed = downloaded / diff
                    elapsed_time = round(diff) * 1000
                    time_to_completion = round(
                        (total_length - downloaded) / speed) * 1000
                    estimated_total_time = elapsed_time + time_to_completion
                    try:
                        current_message = """**Download Status**
URL: {}
File Name: {}
File Size: {}
Downloaded: {}
ETA: {}""".format(
    url,
    file_name,
    humanbytes(total_length),
    humanbytes(downloaded),
    time_formatter(estimated_total_time)
)
                        if current_message != display_message:
                            await event.edit(current_message)
                            display_message = current_message
                    except Exception as e:
                        logger.info(str(e))
                        pass
        return await response.release()
