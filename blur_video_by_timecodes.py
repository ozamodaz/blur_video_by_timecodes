import yaml
import ffmpeg
import argparse

def parse_timecode(timecode, total_duration):
    """
    Convert timecode in 'HH:MM:SS' format to seconds.
    If timecode is "start", return 0.
    If timecode is "end", return the total duration of the video.
    """
    if timecode == "start":
        return 0
    elif timecode == "end":
        return total_duration
    else:
        h, m, s = map(int, timecode.split(':'))
        return h * 3600 + m * 60 + s

def get_video_duration(video_path):
    """Get the duration of the video in seconds using ffmpeg.probe."""
    probe = ffmpeg.probe(video_path)
    duration = float(probe['format']['duration'])
    return duration

def apply_blur_to_video(video_path, timecodes, output_path):
    """Apply blur effect to specified timecodes in the video."""
    input_video = ffmpeg.input(video_path)
    streams = []
    current_start = 0

    # Get the total duration of the video
    total_duration = get_video_duration(video_path)

    for start_timecode, end_timecode in timecodes:
        start_seconds = parse_timecode(start_timecode, total_duration)
        end_seconds = parse_timecode(end_timecode, total_duration)

        # Add the unmodified segment before the blur
        if current_start < start_seconds:
            streams.append(input_video.trim(start=current_start, end=start_seconds).setpts('PTS-STARTPTS'))

        # Add the blurred segment
        blurred_segment = (
            input_video.trim(start=start_seconds, end=end_seconds)
            .setpts('PTS-STARTPTS')
            .filter('boxblur', lr=20, cr=20)  # Adjust blur strength as needed
        )
        streams.append(blurred_segment)

        current_start = end_seconds

    # Add the remaining unmodified segment after the last blur
    if current_start < total_duration:
        streams.append(input_video.trim(start=current_start).setpts('PTS-STARTPTS'))

    # Concatenate all video segments
    output_video = ffmpeg.concat(*streams, v=1, a=0)

    # Add the original audio stream
    original_audio = input_video.audio

    # Output the final video with original audio and high-quality settings
    (
        ffmpeg.output(output_video, original_audio, output_path, **{
            'c:v': 'libx264',  # Use libx264 for video encoding
            'preset': 'veryslow',  # Use slower preset for better quality
            'crf': '21',       # Constant Rate Factor (lower = better quality, 18 is near-lossless)
            'c:a': 'copy',     # Copy original audio without re-encoding
            'movflags': '+faststart',  # Enable fast start for streaming
        })
        .overwrite_output()
        .run()
    )

def main():
    parser = argparse.ArgumentParser(description="Apply blur effect to specified timecodes in a video.")
    parser.add_argument('config', type=str, help="Path to the YAML config file.")
    parser.add_argument('video', type=str, help="Path to the video file.")
    parser.add_argument('output', type=str, help="Path to the output video file.")
    args = parser.parse_args()

    # Load the YAML config file
    with open(args.config, 'r') as file:
        timecodes = yaml.safe_load(file)

    # Apply blur to the video
    apply_blur_to_video(args.video, timecodes, args.output)

if __name__ == "__main__":
    main()