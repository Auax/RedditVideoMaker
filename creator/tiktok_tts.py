import base64
import os
import re

import requests
from requests.adapters import HTTPAdapter, Retry


class TikTokTTS:
    def __init__(self):
        self.URI_BASE = "https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/?text_speaker="
        self.max_chars = 300

    def run(self,
            text: str,
            filename: str,
            voice: str = "en_us_006") -> bool:
        """
        Run the TTS
        :param text: the text for the TTS to say
        :param filename: the result filename (should be .mp3)
        :param voice: the voice identifier to use
        :return: bool (true=success, false=failed)
        """

        split_text = [text]

        # Split the text in sentences in case the text is too long
        if len(text) > self.max_chars:
            split_text = [
                x.group().strip()
                for x in re.finditer(
                    r" *(((.|\n){0," + str(self.max_chars) + "})(\.|.$))", text
                )
            ]

        for text in split_text:
            try:
                r = requests.post(f"{self.URI_BASE}{voice}&req_text={text}&speaker_map_type=0")

            except requests.exceptions.SSLError:
                # See: https://stackoverflow.com/a/47475019/18516611
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                # noinspection HttpUrlsUsage
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                r = session.post(f"{self.URI_BASE}{voice}&req_text={text}&speaker_map_type=0")

            data = r.json()

            print(data)

            msg = data["message"]
            if msg.startswith("Text too long") or msg.startswith("Couldn't load speech"):
                # If we couldn't split the text or the speach couldn't be loaded properly
                if os.path.exists(filename):
                    os.remove(filename)
                return False

            print(data)
            vstr = [data["data"]["v_str"]][0]  # Get data
            b64d = base64.b64decode(vstr)  # Decode data

            with open(filename, "ab") as out:
                out.write(b64d)  # Write data

        return True
