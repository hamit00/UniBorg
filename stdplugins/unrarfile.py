""" command: .unrar
coded by @By_Azade
"""

import asyncio
import logging
import os
import time
from datetime import datetime

from telethon.tl.types import DocumentAttributeVideo

import patoolib
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from sample_config import Config
from uniborg.util import admin_cmd, progress

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)



@borg.on(admin_cmd(pattern="unrar"))  
async def _(event):
    if event.fwd_from:
        return
    mone = await event.edit("Processing ...")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    extracted = Config.TMP_DOWNLOAD_DIRECTORY + "extracted/"
    thumb_image_path = Config.TMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"
    if not os.path.isdir(extracted):
        os.makedirs(extracted)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await borg.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit("Stored the rar to `{}` in {} seconds.".format(downloaded_file_name, ms))

        patoolib.extract_archive(downloaded_file_name, outdir=extracted)
        filename = sorted(get_lst_of_files(extracted, []))
        #filename = filename + "/"
        await event.edit("Unraring now")
        # r=root, d=directories, f = files
        for single_file in filename:
            if os.path.exists(single_file):
                # https://stackoverflow.com/a/678242/4723940
                caption_rts = os.path.basename(single_file)
                force_document = False
                supports_streaming = True
                document_attributes = []
                if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
                    metadata = extractMetadata(createParser(single_file))
                    duration = 0
                    width = 0
                    height = 0
                    if metadata.has("duration"):
                        duration = metadata.get('duration').seconds
                    if os.path.exists(thumb_image_path):
                        metadata = extractMetadata(createParser(thumb_image_path))
                        if metadata.has("width"):
                            width = metadata.get("width")
                        if metadata.has("height"):
                            height = metadata.get("height")
                    document_attributes = [
                        DocumentAttributeVideo(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True
                        )
                    ]
                try:
                    await borg.send_file(
                        event.chat_id,
                        single_file,
                        caption=f"UnRarred `{caption_rts}`",
                        force_document=force_document,
                        supports_streaming=supports_streaming,
                        allow_cache=False,
                        reply_to=event.message.id,
                        attributes=document_attributes,
                        # progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        #     progress(d, t, event, c_time, "trying to upload")
                        # )
                    )
                except Exception as e:
                    await borg.send_message(
                        event.chat_id,
                        "{} caused `{}`".format(caption_rts, str(e)),
                        reply_to=event.message.id
                    )
                    # some media were having some issues
                    continue
                os.remove(single_file)
        os.remove(downloaded_file_name)







def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return get_lst_of_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst
