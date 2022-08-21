import json
import os.path
import shutil

from creator import GenerateAssets
from creator.create_video import render_video
from globals import toml_config, console
from exceptions import CleanExit, InvalidCredentials
from reddit_api import RedditHandler


def clean_temp() -> None:
    """
    Clean temp files
    :return: None
    """
    shutil.rmtree("data/results/temp", ignore_errors=True)


def load_data(filename: str = "data/results/comments.json") -> dict:
    """
    Load comments
    :param filename: the path to the comments.json file
    :return: dict
    """
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    # TODO: Title intro + music based of title mood

    # Splash screen
    console.clear()
    with open("data/assets/splash.txt", "r") as splash_file:
        console.print(splash_file.read(), justify="center")
    console.print(":warning:", "Some comments might be skipped (TTS)!",
                  ":warning:", justify="center", style="bright_black")
    console.print("Press CTRL+C to exit", justify="center", style="bright_black")

    while True:
        mode = 1
        ask = console.input("\nChoose an option:\n1. Generate comments\n2. Create video\n>> ")
        try:
            ask = int(ask)
            if ask != 1 and ask != 2:
                console.print("[bold red]Please choose an option![/bold red]")
                continue
            mode = ask

        except ValueError:
            console.print("[bold red]Please enter a number![/bold red]")
            continue

        if mode == 1:
            # Save comments
            console.log("Saving comments...")
            reddit_handler = RedditHandler()
            reddit_handler.save_json(post_id=toml_config["reddit"]["thread"]["post_id"])
            continue

        generate_assets = True
        if os.path.exists("data/results/temp"):
            ask = console.input("Use saved [bold red]assets[/bold red]? y/n: ")
            if ask.casefold() == "y":
                generate_assets = False
            else:
                console.print("New assets will be generated.")

        # Max number of comments to use (the final result might use less comments due to a bug with TTS)
        N_OF_COMMENTS = toml_config["reddit"]["thread"]["n_of_comments"]

        if generate_assets:
            # Clean temporary files (avoid video bugs)
            console.log("Removing temp files...")
            clean_temp()

            # Load data
            data = load_data()

            # Generate the screenshots and tts sounds
            console.log("Generating assets...")
            generator = GenerateAssets()  # Class instance
            generator.generate_assets(data, n_of_comments=N_OF_COMMENTS)

        console.log("Rendering, grab a ", ":coffee:", "...")
        render_video(n_of_comments=N_OF_COMMENTS)
        console.log("Video created")
        os.startfile("data/results")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Keyboard Interrupt![/bold red]")

    except InvalidCredentials:
        console.print("\n[bold red]Invalid credentials. Please check your `config.toml` file![/bold red]")

    except CleanExit:
        console.print("\n[bold red]Clean exit [stopping]...[/bold red]")
