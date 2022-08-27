import sys
from dataclasses import dataclass
from classes import Phrase, Transcript
import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
from moviepy.video.fx.freeze import freeze
import tempfile


@dataclass
class Video:
    source_file: str
    target_file: str
    output_path: str
    srt_path: str = None

    DUBBED_VIDEO_SUBDIR = 'dubbed-videos'
    AUDIO_CLIPS_SUBDIR = 'audio-clips'

    def extract_audio(self, output):
        if not output[-4:] != "wav":
            output += ".wav"

        # TODO: can we output MP3?
        AudioSegment \
            .from_file(self.source_file) \
            .set_channels(1) \
            .export(output, format="wav")

    def dub_audio(self, transcript: Transcript, lang: str, timing_scheme: str, source_audio: str, overwrite: bool = False, overlay_gain: int = -30):
        # if os.path.exists(self.target_file):
        #     return

        output_files = os.listdir(self.output_path)

        print(f"Synthesizing audio for {lang}", file=sys.stderr)

        if os.path.exists(self.target_file):
            print(f"Video file {self.target_file} already exists.", file=sys.stderr)
            return

        # Also, grab the original audio
        dubbed = AudioSegment.from_file(source_audio)

        clip = VideoFileClip(self.source_file)

        sys.setrecursionlimit(10000)
        # Place each computer-generated audio at the correct timestamp
        frozen = 0
        for phrase in transcript.phrases:
            target = phrase.get_target(lang)
            timing = target.timings.get(timing_scheme)
            dubbed = dubbed.overlay(
                AudioSegment.from_mp3(target.natural_audio.file_name),
                position=timing.start_time * 1000,
                gain_during_overlay=overlay_gain
            )
            if timing.freeze_time is not None:  # and frozen < 1000:
                print(f"freezing at: {timing.freeze_time}")
                clip = freeze(clip, t=timing.freeze_time, freeze_duration=timing.freeze_duration)
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
