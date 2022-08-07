import multiprocessing
from datetime import date, datetime
from glob import iglob
from moviepy.editor import *

import globals


def render_video(n_of_comments: int = 20) -> None:
    """
    Render and export the video
    :param n_of_comments: the amount of comments to use
    :return: None
    """
    # Variables
    last_dir_checked = None  # Last directory checked
    comments_fetched = 0  # The number of comment directories checked
    clip_paths = []  # Image paths
    audio_paths = []
    audio_clips = []  # AudioClip objects
    clips = []  # ImageClip objects
    thread_opacity = globals.toml_config["settings"]["comment"]["opacity"]

    # Transition
    transition_settings = globals.toml_config["settings"]["transition"]
    transition_path = transition_settings["transition_path"]
    transition_exists = os.path.exists(transition_path)
    transition = VideoFileClip(transition_path).set_opacity(1)  # Force opacity to 1 because of the images

    # Video size
    size = (1920, 1080)

    # Add title
    title_audio = AudioFileClip("data/results/temp/title/title.mp3")
    title = ImageClip("data/results/temp/title/title.png") \
        .set_duration(title_audio.duration) \
        .set_opacity(thread_opacity) \
        .set_pos("center", "center") \
        .resize(width=int(size[0] / 1.1))

    audio_clips.append(title_audio)
    clips.append(title)

    # region Background
    bg_settings = globals.toml_config["settings"]["background"]
    if bg_settings["use_solid_bg"]:
        # noinspection PyBroadException
        try:  # Use solid color
            bg_color = tuple(map(int, bg_settings["bg_color"].split(",")))
            background = ColorClip(size, bg_color)  # Plain bgcolor
        except Exception:
            background = ColorClip(size, (24, 24, 24))
    else:
        background = VideoFileClip(bg_settings["bg_path"]).without_audio()
        if tuple(background.size) != size:
            globals.console.log("Resizing background...")
            background = background.resize(newsize=size)  # Resize
        bg_opacity = bg_settings["opacity"]
        if bg_opacity < 1:
            background = background.fx(vfx.colorx, bg_opacity)  # Change brightness

    # endregion

    # region Append Files
    # Check the comment folders ("data/results/temp/<any_folder>")
    for file in iglob("data/results/temp/comments/**/*.*", recursive=True):
        if comments_fetched > n_of_comments:
            break

        dirname = os.path.dirname(file)
        if last_dir_checked != dirname:
            last_dir_checked = dirname
            comments_fetched += 1
            if transition_exists:
                # Transition
                clip_paths.append(transition_path)  # Append transition
                audio_paths.append(None)  # Blank space (represents transition space)

        # Append audio and image paths
        if ".mp3" in file:
            audio_paths.append(file)
        elif ".png" in file:
            clip_paths.append(file)
    # endregion

    # Create video composition

    for clip_filename, audio_filename in zip(clip_paths, audio_paths):
        if clip_filename == transition_path:
            # Transition between each comment
            clips.append(transition)
            audio_clips.append(transition.audio)

        else:
            # Get the duration of the TTS audio
            audio_clip = AudioFileClip(audio_filename)
            duration = audio_clip.duration

            # Append image clips to stick them together after
            clips.append(ImageClip(clip_filename)
                         .set_opacity(thread_opacity)
                         .set_duration(duration)
                         .resize(width=int(size[0] / 1.1))
                         .set_pos("center", "center"))

            audio_clips.append(audio_clip)

    # Composite audios
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])

    # Composite images
    image_concat = concatenate_videoclips(clips)
    # Add audio composite
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background, image_concat.set_pos("center", "center")]) \
        .set_duration(image_concat.duration)

    final.write_videofile(
        f"data/results/auax_reddit_{datetime.now().strftime('%Y.%m.%d - %H.%M.%S')}.mp4",
        fps=30,
        audio_codec="aac",
        audio_bitrate="192k",
        verbose=False,
        threads=multiprocessing.cpu_count(),
    )
