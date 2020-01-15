#    This file is part of NiceGrill.

#    NiceGrill is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    NiceGrill is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with NiceGrill.  If not, see <https://www.gnu.org/licenses/>.

import logging
from datetime import timedelta

from telethon.errors.rpcerrorlist import *
from telethon.tl import functions
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights

from sql_helpers.fban_sql_helper import (add_chat_fban, get_fban,
                                         remove_chat_fban,is_fban)
# from database import admindb as nicedb
from sql_helpers.gban_sql_helper import (add_chat_gban, get_gban,
                                         remove_chat_gban, is_gban)
                            
from sql_helpers.gmute_sql import (is_gmuted, gmute,
                                    ungmute)

from sql_helpers.mute_sql import (is_muted, mute,
                                    unmute)
from uniborg import utils
from uniborg.util import admin_cmd

PROMOTE = ChatAdminRights(
    post_messages=None,
    add_admins=None,
    invite_users=None,
    change_info=True,
    ban_users=None,
    delete_messages=True,
    pin_messages=True,
    edit_messages=None)

DEMOTE = ChatAdminRights(
    post_messages=None,
    add_admins=None,
    invite_users=None,
    change_info=None,
    ban_users=None,
    delete_messages=None,
    pin_messages=None,
    edit_messages=None)

BAN = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True)

UNBAN = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None)

MUTE = ChatBannedRights(
    until_date=timedelta(days=366),
    send_messages=True)

UNMUTE = ChatBannedRights(
    until_date=timedelta(days=366),
    send_messages=False)


class Admin:

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    @borg.on(admin_cmd(pattern="promot ?(.*)"))
        async def promote_uniborg(message):
            await message.edit("<b>Promoting...</b>")
            chat = message.input_chat
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id
                    if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditAdminRequest(chat, user, PROMOTE, "Admin"))
                await message.edit("<b>Successfully promoted</b>")
            except TypeError:
                await message.edit("<b>Are you sure this is a genuine chat?</b>")
            except AdminsTooMuchError:
                await message.edit("<b>There are too many admins in this chat</b>")
            except UserPrivacyRestrictedError:
                await message.edit("<b>The user's privacy settings do not allow you to do this</b>")
            except UserNotMutualContactError:
                await message.edit("<b>The provided user is not a mutual contact</b>")
            except UserIdInvalidError:
                await message.edit("<b>Specified user is a no go</b>")
            except UserCreatorError:
                await message.edit("<b>Wtf, that is the chat owner..</b>")
            except RightForbiddenError:
                await message.edit(
                    "<b>You either don't have enough permissions or there's something wrong with the admin rights</b>")
            except ChatAdminRequiredError:
                await message.edit("<b>Oh honey, I'm not admin enough to promote this user 🙄</b>")

    @borg.on(admin_cmd(pattern="demot ?(.*)"))
        async def demot_uniborg(message):
            await message.edit("<b>Demoting...</b>")
            chat = message.input_chat
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id
                    if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditAdminRequest(chat, user, DEMOTE, "User"))
                await message.edit("<b>Successfully demoted</b>")
            except TypeError:
                await message.edit("<b>Are you sure this is a genuine chat?</b>")
            except AdminsTooMuchError:
                await message.edit("<b>There are too many admins in this chat</b>")
            except UserPrivacyRestrictedError:
                await message.edit("<b>The user's privacy settings do not allow you to do this</b>")
            except UserNotMutualContactError:
                await message.edit("<b>The provided user is not a mutual contact</b>")
            except UserIdInvalidError:
                await message.edit("<b>Specified user is a no go</b>")
            except UserCreatorError:
                await message.edit("<b>Wtf, that is the chat owner..</b>")
            except RightForbiddenError:
                await message.edit(
                    "<b>You either don't have enough permissions or"
                    " there's something wrong with the admin rights</b>")
            except ChatAdminRequiredError:
                await message.edit("<b>Oh honey, I'm not admin enough to demote this user 🙄</b>")

    @borg.on(admin_cmd(pattern="mute ?(.*)"))
        async def mute_uniborg(message):
            await message.edit("<b>Muting...</b>")
            chat = message.input_chat
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            if user == (await message.client.get_me()).id:
                await message.edit("<b>Specified user is a no go</b>")
                return
            if not await nicedb.check_user(user):
                await nicedb.add_user(user, True, False, False, message.chat_id)
            else:
                await nicedb.update_user({"User": user}, {"Mute": True})
            try:
                await message.client(EditBannedRequest(chat, user, MUTE))
                await message.edit("<b>Muted</b>")
            except TypeError:
                await message.edit("<b>You need to be in a chat to do this</b>")
                return
            except UserAdminInvalidError:
                await message.edit("<b>You're either not an admin or that's more admin than you</b>")
            except UserIdInvalidError:
                await message.edit("<b>Specified user is a no go</b>")
            except ChatAdminRequiredError:
                await message.edit("<b>Oh honey, I'm not admin enough to mute this user 🙄</b>")

    @borg.on(admin_cmd(pattern="unmute ?(.*)"))
        async def unmute_uniborg(message):
            await message.edit("<b>Unmuting...</b>")
            chat = message.input_chat
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id
                    if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            if not await nicedb.check_user(user):
                await nicedb.add_user(user, False, False, False, message.chat_id)
            else:
                await nicedb.update_user({"User": user}, {"Mute": False})
            try:
                await message.client(EditBannedRequest(chat, user, UNMUTE))
                # add_unmuted(user)
                await message.edit("<b>Unmuted</b>")
            except TypeError:
                await message.edit("<b>You need to be in a chat to do this</b>")
                return
            except TypeError:
                await message.edit("<b>You need to be in a chat to do this</b>")
                return
            except UserAdminInvalidError:
                await message.edit("<b>You're either not an admin or that's more admin than you</b>")
            except UserIdInvalidError:
                await message.edit("<b>Specified user is a no go</b>")
            except ChatAdminRequiredError:
                await message.edit("<b>Oh honey, I'm not admin enough to unmute this user 🙄</b>")

    @borg.on(admin_cmd(pattern="kick ?(.*)"))
        async def kick_uniborg(message):
            chat = message.input_chat
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditBannedRequest(chat, user, ChatBannedRights(
                    until_date=None, view_messages=True)))
                await message.edit("<b>Kicked...</b>")
            except TypeError:
                await message.edit("<b>You need to be in a chat to do this</b>")
                return
            except UserAdminInvalidError:
                await message.edit("<b>You're either not an admin or that's more admin than you</b>")
            except UserIdInvalidError:
                await message.edit("<b>Specified user is a no go</b>")
            except ChatAdminRequiredError:
                await message.edit("<b>Oh honey, I'm not admin enough to kick this user 🙄</b>")

    @borg.on(admin_cmd(pattern="ban ?(.*)"))
        async def ban_uniborg(message):
            chat = message.input_chat
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditBannedRequest(chat, user, BAN))
                await message.edit("<b>Banned</b>")
            except TypeError:
                await message.edit("<b>You need to be in a chat to do this</b>")
                return
            except UserAdminInvalidError:
                await message.edit("<b>You're either not an admin or that's more admin than you</b>")
            except UserIdInvalidError:
                await message.edit("<b>Specified user is a no go</b>")
            except ChatAdminRequiredError:
                await message.edit("<b>Oh honey, I'm not admin enough to ban this user 🙄</b>")

    @borg.on(admin_cmd(pattern="unban ?(.*)"))
        async def unban_uniborg(message):
            chat = message.input_chat
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditBannedRequest(chat, user, UNBAN))
                await message.edit("<b>Alright, fine..All is forgiven, unbanned..</b>")
            except TypeError:
                await message.edit("<b>You need to be in a chat to do this</b>")
                return
            except UserAdminInvalidError:
                await message.edit("<b>You're either not an admin or that's more admin than you</b>")
            except UserIdInvalidError:
                await message.edit("<b>Specified user is a no go</b>")
            except ChatAdminRequiredError:
                await message.edit("<b>Oh honey, I'm not admin enough to unban this user 🙄</b>")

    @borg.on(admin_cmd(pattern="gban ?(.*)"))
        async def pin_uniborg(message):
            reply = await message.get_reply_message()
            loud = True if utils.get_arg(message) == "loud" else False
            if not reply:
                await message.edit("<b>Reply to a message first.</b>")
                return
            await message.client.pin_message(
                message.input_chat, reply.id, notify=loud)
            await message.edit("<b>Pinned succesfully.</b>")
            
    @borg.on(admin_cmd(pattern="gban ?(.*)"))
        async def gban_uniborg(message):
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditBannedRequest(message.chat_id, user, BAN))
            except TypeError:
                pass
            if not await get_fban(user):
                await add_chat_fban(message.chat_id)
            await message.edit("<b>Globally banned</b>")
    @borg.on(admin_cmd(pattern="ungban ?(.*)"))
        async def ungban_uniborg(message):
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditBannedRequest(message.chat_id, user, UNBAN))
            except TypeError:
                pass
            if not await is_gban(user):
                await remove_chat_gban(message.chat_id)
            await message.edit("<b>Global ban lifted</b>")
    @borg.on(admin_cmd(pattern="gmute ?(.*)"))
        async def gmute_uniborg(message):
            await message.edit("<b>Muting...</b>")
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except ValueError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditBannedRequest(message.chat_id, user, MUTE))
            except TypeError:
                pass
            if not await is_gmuted(user):
                await gmute(message.chat_id)
            await message.edit("<b>Globally muted</b>")
    @borg.on(admin_cmd(pattern="ungmute ?(.*)"))
        async def ungmute_uniborg(message):
            await message.edit("<b>Unmuting...</b>")
            try:
                user = (
                    (await message.client.get_entity(utils.get_arg(message))).id if not message.is_reply else
                    (await message.get_reply_message()).sender.id)
            except TypeError:
                await message.edit("<b>No user found in that name</b>")
                return
            try:
                await message.client(EditBannedRequest(message.chat_id, user, UNMUTE))
            except TypeError:
                pass
            if not await is_gmuted(user):
                await ungmute(message.chat_id)
            await message.edit("<b>Global mute lifted</b>")


    @borg.on(admin_cmd(pattern="ungban ?(.*)"))
        async def kickme_uniborg(message):
            await message.edit("<b>Okay, im leaving the chat</b>")
            await message.client(functions.channels.LeaveChannelRequest(channel=message.chat_id))

    @borg.on(events.ChatAction())
        async def watchout(message):
            user = message.sender_id
            chat = message.chat_id
            if await check_user = await message.client.get_entity(user):
                entity = await is_gban(user) and await is_gmuted(user) and is_muted(user)
                gban = is_gban(user)
                gmute = is_gmuted(user)
                mute = is_muted(user)
                if (await message.client.get_me()).id == entity(user):
                    return
                if mute and gmute:
                    await message.delete()
                elif mute and not gmute  == chat:
                    await message.delete()
                if gban:
                    try:
                        await message.client(EditBannedRequest(chat, user, BAN))
                    except Exception:
                        pass
