from dataclasses import dataclass
from classes import Phrase, PhrasesContainer
import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
import tempfile


@dataclass
class Video:
    transcript: PhrasesContainer
    source_file: str
    target_file: str
    output_path: str
    srt_path: str = None

    DUBBED_VIDEO_SUBDIR = 'dubbed-videos'
    AUDIO_CLIPS_SUBDIR = 'audio-clips'

    def dub_audio(self, lang: str, overwrite: bool = False, overlay_gain: int = -30):
        if os.path.exists(self.target_file):
            return

        output_files = os.listdir(self.output_path)

        audio_dir = os.path.join(self.output_path, self.AUDIO_CLIPS_SUBDIR)
        if self.AUDIO_CLIPS_SUBDIR not in output_files:
            os.mkdir(audio_dir)

        print(f"Synthesizing audio for {lang}")
        self.transcript.save_audio(output_path=audio_dir, lang=lang)

        dubbed_path = os.path.join(self.output_path, self.DUBBED_VIDEO_SUBDIR)

        if dubbed_path not in output_files:
            os.mkdir(dubbed_path)

        # Also, grab the original audio
        dubbed = AudioSegment.from_file(self.source_file)

        # Place each computer-generated audio at the correct timestamp
        for phrase in self.transcript.phrases:
            dubbed = dubbed.overlay(
                AudioSegment.from_mp3(phrase.audio_file),
                position=phrase.start_time * 1000,
                gain_during_overlay=overlay_gain
            )

        # Write the final audio to a temporary output file
        audio_file = tempfile.NamedTemporaryFile()
        dubbed.export(audio_file)
        audio_file.flush()

        # Add the new audio to the video and save it
        clip = VideoFileClip(self.source_file)
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
