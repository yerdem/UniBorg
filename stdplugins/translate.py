""" Google Google Translate
Available Commands:
.tr LanguageCode as reply to a message
.tr LangaugeCode | text to sepak"""
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
import emoji
from googletrans import Translator
from uniborg.util import admin_cmd
import json

@borg.on(admin_cmd(pattern="tr ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "ml"
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.edit("`.tr LanguageCode` as reply to a message")
        return
    text = emoji.demojize(text.strip())
    lan = lan.strip()
    translator = Translator()
    try:
        translated = translator.translate(text, dest=lan)
        after_tr_text = translated.text
        # TODO: emojify the :
        # either here, or before translation
        database = "./bin/language.json"
        data = json.loads(open(database).read())
        for a in range(len(data)):
            if lan in data[a]["code"]:
                full_lang = data[a]["name"]
                # print(full_lang)
                output_str = """**Text:** __{}__\n**Detected Language:** __{}__\n\n**Translated to:**\n__{}__""".format(
                    # after_tr_text,
                    previous_message.message,
                    full_lang,
                    after_tr_text
                    # translated.src
                )
        await event.edit(output_str)
    except Exception as exc:
        await event.edit(str(exc))
