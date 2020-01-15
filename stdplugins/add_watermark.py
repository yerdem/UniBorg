import asyncio
import os
import time
from datetime import datetime

from PyPDF2 import PdfFileReader, PdfFileWriter
from telethon import events
from telethon.tl.types import (DocumentAttributeAudio,
                               DocumentAttributeFilename,
                               DocumentAttributeVideo)


from sample_config import Config
from uniborg.util import admin_cmd


@borg.on(admin_cmd(pattern="watermark"))
async def _(event):
    if event.fwd_from:
        return
    mone = await event.edit("Processing ...")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    watermark_path = "./DOWNLOADS/watermark/"
    if not os.path.isdir(watermark_path):
        os.makedirs(watermark_path)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await borg.download_media(
                reply_message,
                watermark_path,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
        except Exception as e:  
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit("Stored the pdf to `{}` in {} seconds.".format(downloaded_file_name, ms))
        
            watermark(
                inputpdf=downloaded_file_name,
                outputpdf=watermark_path + reply_message.file.name,
                watermarkpdf='./bin/watermark.pdf'
            )
        await event.edit("Uploading now")
        caption_rts = os.path.basename(watermark_path + reply_message.file.name)
        await borg.send_file(
            event.chat_id,
            watermark_path + reply_message.file.name,
            caption=f"`{caption_rts}`",
            reply_to=event.message.id,
        )
        

def watermark(inputpdf, outputpdf, watermarkpdf):
    watermark = PdfFileReader(watermarkpdf)
    watermarkpage = watermark.getPage(0)
    pdf = PdfFileReader(inputpdf)
    pdfwrite = PdfFileWriter()
    for page in range(pdf.getNumPages()):
        pdfpage = pdf.getPage(page)
        pdfpage.mergePage(watermarkpage)
        pdfwrite.addPage(pdfpage)
    with open(outputpdf, 'wb') as fh:
        pdfwrite.write(fh)
