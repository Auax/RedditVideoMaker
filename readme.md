[comment]: <> (  <img src="./assets/logo.png" width="80">)
<div style="text-align: center">
    <h2>Reddit Video Creator</h2>
    <p>
      Automatically generate Reddit videos.
    </p>
    <img src="https://user-images.githubusercontent.com/16353807/183256021-2772e9fe-f26e-4f5e-bc95-2e093f0ffdaa.png" alt="screenshot" width="100%">
</div>

## Dev instructions

### Get started

1. Install **Python 3.10**
2. Install **FFMPEG**

### Instructions

1. Clone this repository using `git clone https://github.com/Auax/RedditVideoMaker`
2. Run `cd RedditVideoMaker` and run `intall.bat`
5. Fill all the information in the `config.toml` file.
7. Run `python3 main.py`

### Info

- The output video will be saved under `data/results`.
- If you want to add a background, download a video and set the path in `config.toml` (the background will be
  automatically resized to 1920x1080px)
- The render speed will be a lot faster if you use a plain background color instead of a video.
- 14 comments are approximately 10 minutes of video.

### Todo:

- Add more options
- Add title in the video
- Add music

**Maybe add:** automatically choose music and background based on the mood of the title