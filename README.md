# blur_video_by_timecodes
Python wrapper that takes Yaml-config with timecodes and use ffmpeg to blur selected intervals in video

Usage:
```
python3 blur_video_by_timecodes.py timecodes.yml input_video.mp4 output_video.mp4
```

Example config file format:
```
---

- ["start", "00:12:37"]
- ["00:13:37", "00:18:56"]
- ["00:53:36", "00:53:38 "]
- ["01:14:23", "end"]
```