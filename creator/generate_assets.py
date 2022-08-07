import os.path
import shutil
import subprocess
from pathlib import Path

import exceptions
import globals
from creator.tiktok_tts import TikTokTTS
from globals import toml_config, is_comment_valid, console


def node_error(error_message: str, stdout: str):
    console.log(f"[bold red]{error_message}[/bold red]")
    ask = console.input("Show NODE error info? y/n: ")
    if "y" in ask.casefold():
        console.print(stdout)
    raise exceptions.CleanExit


class GenerateAssets:
    def __init__(self):
        self.tts_instance = TikTokTTS()

    def generate_assets(self, comments_data, n_of_comments: int = 20) -> None:
        """
        Generate the images and TTS sounds
        :param comments_data: the data returned by `get_comments()`
        :param n_of_comments: the amount of comments to use
        :return: None
        """

        # TODO: use seed to randomly generate the same numbers in node and in python

        # Where to save the title
        save_title_dir = globals.abs_path("data/results/temp/title")
        # Where to save the comments (will create subdirectories inside the specified path)
        save_comments_dir = globals.abs_path("data/results/temp/comments")

        post_title = comments_data["title"]
        post_author = comments_data["author"]
        post_score = str(comments_data["score"])

        # region Images
        # This NODE project uses a NPM library to render HTML as an image and save it
        node_title_renderer_path = "node_image_renderer/screenshot_title.js"
        node_comment_renderer_path = "node_image_renderer/screenshot_comments.js"
        json_path_abs = globals.abs_path("data/results/comments.json")

        # Generate title image
        console.log("Calling NODE to render title (`screenshot_title.js`)...")
        result = subprocess.run(
            ["node", "--no-warnings", node_title_renderer_path,
             "--path", save_title_dir,
             "--author", post_author,
             "--title", post_title,
             "--score", post_score],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        stdout = result.stdout.decode('utf-8')
        if "Title saved!" not in stdout:
            node_error("Couldn't render title!", stdout)
        else:
            console.log(f"[bold green]NODE[/bold green]: {stdout}")

        # Generate comments images
        console.log("Calling NODE to render comments (`screenshot_comments.js`)...")
        result = subprocess.run(
            ["node", "--no-warnings", node_comment_renderer_path,
             "--path", save_comments_dir,
             "--json", json_path_abs,
             "--max", str(n_of_comments)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        stdout = result.stdout.decode('utf-8')
        if "Comments saved!" not in stdout:
            node_error("Couldn't render title!", stdout)
        else:
            console.log(f"[bold green]NODE[/bold green]: {stdout}")

        # endregion

        # region TTS
        console.log("Generating TTS sounds...")
        tts_settings = toml_config["settings"]["tts"]
        comment_voice = tts_settings["tiktok_comment_voice"]
        reply_voice = tts_settings["tiktok_reply_voice"]

        # Title
        tts_success = self.tts_instance.run(
            f"r slash ask reddit. {post_title}",
            os.path.join(save_title_dir, "title.mp3"),
            globals.toml_config["settings"]["tts"]["tiktok_title_voice"]
        )

        if not tts_success:
            if not tts_success:
                console.log("[bold orange3]TTS[/bold orange3] >> Couldn't generate the title's TTS.")
                shutil.rmtree(save_title_dir)

        # Generate comment's TTS
        for idx, comment in enumerate(comments_data["comments"].items()):
            # If we reached the max number of comments, break the loop
            if idx >= n_of_comments:
                break

            author = comment[0]
            content = comment[1]["text"]

            # If the comment is too long or it contains a link, skip
            if not is_comment_valid(content):
                n_of_comments += 1
                continue

            base_dir = os.path.join(save_comments_dir, author)
            Path(base_dir).mkdir(parents=True, exist_ok=True)  # Create folder

            reply = None
            # Only add reply if there is an image generated for it already
            # This is because we randomly save replies
            # if os.path.exists(os.path.join(base_dir, "2.png")):
            # Add reply
            if replies := comment[1]["replies"]:
                _ = list(replies.items())[0]
                # if random.randint(0, 1) == 1 and is_comment_valid(_):  # Randomly add reply and check that it's valid
                if is_comment_valid(_[1]):  # Randomly add reply and check that it's valid
                    reply = _

            # Generate tts (this takes some time)
            # Generate first in case there is an error with the text
            tts_success = self.tts(
                folder=base_dir,
                content=content,
                reply_content=reply[1]["text"] if reply else None,
                comment_voice=comment_voice,
                reply_voice=reply_voice)

            if not tts_success:
                console.log("[bold orange3]TTS[/bold orange3] >> Skipping comment.")
                shutil.rmtree(base_dir)
                continue
        # endregion

    def tts(self,
            folder: str,
            content: str,
            reply_content: str = None,
            comment_voice: str = None,
            reply_voice: str = None) -> bool:
        """
        Generate the TTS audios
        :param folder: the base folder to save the audios
        :param content: the text content
        :param reply_content: the reply content
        :param comment_voice: the voice to use in the comment. (None = auto)
        :param reply_voice: the voice to use in the reply. (None = auto)
        :return: bool (true=success, false=failed)
        """
        success = self.tts_instance.run(content, os.path.join(folder, "tts_1.mp3"), comment_voice)

        if reply_content:
            success = success and self.tts_instance.run(reply_content, os.path.join(folder, "tts_2.mp3"), reply_voice)

        return success
