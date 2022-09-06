import sys
from dataclasses import dataclass
from .transcript import Transcript
from .timings import Timings
import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.speedx import speedx
from enum import Enum, unique
import tempfile



@unique
class LengthenMode(Enum):
    freeze = 'freeze'
    stretch = 'stretch'


@dataclass
class Video:
    source_file: str
    target_file: str
    output_path: str
    srt_path: str = None

    DUBBED_VIDEO_SUBDIR = 'dubbed-videos'

    def extract_audio(self, output):
        if not output[-4:] != "wav":
            output += ".wav"

        # TODO: can we output MP3?
        AudioSegment \
            .from_file(self.source_file) \
            .set_channels(1) \
            .export(output, format="wav")

    def dub_audio(self, transcript: Transcript, lang: str, timing_scheme: str, source_audio: str,
                   lengthen_mode: LengthenMode = LengthenMode.stretch, overwrite: bool = False,
                  overlay_gain: int = -20, source_gain: int = None, use_source_audio: bool = False):
        # if os.path.exists(self.target_file):
        #     return

        output_files = os.listdir(self.output_path)

        if not overwrite and os.path.exists(self.target_file):
            print(f"Video file {self.target_file} already exists.", file=sys.stderr)
            return

        if source_gain is None:
            source_gain = -50
            if timing_scheme == Timings.TRANSLATION:
                source_gain = 0

        print(f"Loading audio for {lang}", file=sys.stderr)

        if timing_scheme == Timings.TRANSLATION:
            lengthen_mode = LengthenMode.freeze

        if use_source_audio or timing_scheme == Timings.TRANSLATION:
            # grab the original audio
            dubbed = AudioSegment.from_file(source_audio)
            dubbed = dubbed.apply_gain(source_gain)
        else:
            dubbed = AudioSegment.silent(duration=transcript.duration(lang, timing_scheme)*1000)

        print(f"Building video for {lang}", file=sys.stderr)
        clip = VideoFileClip(self.source_file)

        if lengthen_mode == LengthenMode.stretch:
            clip = clip.fx(speedx, clip.duration / transcript.duration(lang, timing_scheme))
        elif lengthen_mode == LengthenMode.freeze:
            sys.setrecursionlimit(10000)

        print(f"Dubbing audio for {lang}", file=sys.stderr)
        # Place each computer-generated audio at the correct timestamp
        frozen = 0
        for phrase in transcript.phrases:
            target = phrase.get_target(lang)
            timing = target.timings.get(timing_scheme)

            lang_clip = AudioSegment.from_mp3(target.duration_audio.file_name)
            if 'azure' in target.duration_audio.file_name:
                lang_clip = lang_clip[100:lang_clip.duration_seconds*1000-750]

            dubbed = dubbed.overlay(
                lang_clip,
                position=timing.start_time * 1000,
                gain_during_overlay=overlay_gain
            )
            if lengthen_mode == LengthenMode.freeze and timing.freeze_time is not None:  # and frozen < 1000:
                print(f"freezing at: {timing.freeze_time}")
                freeze_time = timing.freeze_time
                if freeze_time > clip.duration:
                    freeze_time = clip.duration - 0.05
                clip = freeze(clip, t=freeze_time, freeze_duration=timing.freeze_duration)
                frozen += 1

        # Write the final audio to a temporary output file
        audio_file = tempfile.NamedTemporaryFile()
        dubbed.export(audio_file)
        audio_file.flush()

        # Add the new audio to the video and save it
        audio = AudioFileClip(audio_file.name)
        clip = clip.set_audio(audio)

        # Add transcripts, if supplied
        if self.srt_path:
            width, height = clip.size[0] * 0.75, clip.size[1] * 0.20

            def generator(txt):
                return TextClip(
                    txt,
                    font='Georgia-Regular',
                    size=[width, height],
                    color='black',
                    method="caption"
                )

            subtitles = SubtitlesClip(
                self.srt_path,
                generator
            ).set_pos(("center", "bottom"))
            clip = CompositeVideoClip([clip, subtitles])

        clip.write_videofile(
            self.target_file,
            codec='libx264',
            audio_codec='aac'
        )

        audio_file.close()
