import os.path
import glob
import re
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from .word import Word
from .phrase import Phrase
import json
from .sourcelanguagePhrase import SourceLanguagePhrase
from .languagephrase import LanguagePhrase
from typing import Optional
import sys
from .constants import *
from .timings import Timings
from .phrasetiming import PhraseTiming
import gzip
from .functions import *
import copy
import srt


@dataclass_json
@dataclass
class Transcript:
    """
    Root project data object

    `Transcript` reads and writes data to storage and has methods to perform
    high-level functions on the data.
    """

    name: str = 'Project'
    src_lang: str = 'en-US'
    words: list[Word] = None
    phrases: list[Phrase] = None
    tts_lang: Optional[str] = None
    tts_duration: Optional[float] = None
    has_changed: bool = False
    obey_manuscript_breaks: bool = False

    def phrase_count(self) -> int:
        """
        Number of phrases in the transcript
        """
        return len(self.phrases)

    def words_count(self) -> int:
        """
        Number of words in the transcript
        """
        return len(self.words)

    def duration(self, lang: str, timing_scheme: str) -> float:
        return self.phrases[-1].get_timing(lang, timing_scheme).end_time + 0.5

    def target_languages(self):
        langs = list(self.phrases[0].targets.keys())
        langs.sort()
        return langs

    def target_lang_timings(self, lang: str):
        return self.phrases[0].get_target(lang).timings.schemes()

    def copy_target(self, from_lang: str, to_lang: str, overwrite: bool = False):
        for phrase in self.phrases:
            if not overwrite and phrase.get_target(to_lang) is not None:
                print(f"Language {to_lang} already exists.  To overwrite use --overwrite=1", file=sys.stderr)
                exit(1)

            from_phrase = phrase.get_target(from_lang)
            if from_phrase is None:
                print(f"Language {from_lang} does  not exist in project.", file=sys.stderr)
                exit(1)

            to_phrase = copy.deepcopy(from_phrase)
            to_phrase.lang = to_lang
            to_phrase.natural_audio = None
            to_phrase.duration_audio = None

            phrase.set_target(lang=to_lang, phrase=to_phrase)

        self.has_changed = True

    def delete_target(self, lang: str):
        for phrase in self.phrases:
            phrase.delete_target(lang)

        self.has_changed = True

    def combine_phrases(self, start_index: int, end_index: int):
        print(f"Combining: {start_index} thru {end_index}", file=sys.stderr)
        if end_index < start_index:
            raise ValueError(f'end_index ({end_index}) is less that start_index ({start_index}')
        elif start_index < 0 or start_index >= len(self.phrases):
            raise ValueError(f'start_index ({start_index}) out of bounds')
        elif end_index < 0 or end_index >= len(self.phrases):
            raise ValueError(f'end_index ({end_index}) out of bounds')
        elif start_index == end_index:
            return

        start_phrase = self.phrases[start_index]
        to_delete = []
        for i in range(start_index+1, end_index+1):
            phrase = self.phrases[i]

            start_phrase.source.text += '\n' + phrase.source.text
            start_phrase.source.timings.get(Timings.SOURCE).end_time = phrase.source.timings.get(Timings.SOURCE).end_time

            for lang in phrase.targets:
                target = start_phrase.get_target(lang)
                start_phrase.get_target(lang).text += '\n' + phrase.get_target(lang).text
                start_phrase.get_target(lang).end_time = phrase.get_target(lang).end_time

            to_delete.append(i)

        while len(to_delete) > 0:
            del self.phrases[to_delete.pop()]

        # Renumber phrases
        i = 0
        for phrase in self.phrases:
            phrase.id = i
            phrase.set_children_id(i)
            i += 1

    def to_srt(self, audio_lang: str, timings_lang: str = None, include_source: bool = False) -> str:
        srt = ''
        for phrase in self.phrases:
            srt += phrase.to_srt(
                audio_lang=audio_lang,
                timings_lang=timings_lang,
                include_source=include_source
            )
            srt += "\n\n"

        return srt

    def get_tts_duration_audio(self, lang: str, timing_scheme: str, service: str = SERVICE_AZURE, overwrite: bool = False, voice_name: str = None):
        for phrase in self.phrases:
            phrase.get_target(lang).get_tts_duration_audio(
                timing_scheme=timing_scheme,
                service=service,
                overwrite=overwrite,
                voice_name=voice_name,
            )

    def get_tts_natural_audio(self, lang: str, service: str = SERVICE_AZURE, overwrite: bool = False, voice_name: str = None):
        print(f"Getting natural audio for {lang}", file=sys.stderr)
        for phrase in self.phrases:
            phrase.get_target(lang).get_tts_natural_audio(
                service=service,
                overwrite=overwrite,
                voice_name=voice_name,
            )

    @classmethod
    def _load_file(cls, file) -> Optional['Transcript']:
        data = json.load(file)
        return cls.from_dict(data)

    @classmethod
    def load(cls, path: str) -> Optional['Transcript']:
        if os.path.isdir(path):
            path = os.path.join(path, TRANSCRIPT_FILE)

        f = None
        if os.path.isfile(f"{path}.gz"):
            f = gzip.open(f"{path}.gz", mode='r')
        elif os.path.isfile(path):
            f = open(path, mode='r')

        if f is not None:
            tran = cls._load_file(f)
            tran.has_changed = False
            f.close()
            os.chdir(os.path.dirname(path))
            return tran

        return None

    def import_words_srt(self, srt_file: str) -> None:
        def seconds(sub_time):
            return sub_time.seconds + sub_time.microseconds/1000000

        f = open(srt_file, 'r')
        self.words = []
        for sub in srt.parse(f.read()):
            sub_words = re.split(r'\s+', sub.content)
            letter_count = 0
            for sw in sub_words:
                letter_count += len(sw)

            duration = seconds(sub.end) - seconds(sub.start)
            last_end = seconds(sub.start)
            for sw in sub_words:
                end_time = last_end + duration * len(sw) / letter_count
                self.words.append(
                    Word(
                        id=len(self.words),
                        word=sw,
                        start_time=last_end,
                        end_time=end_time,
                    )
                )
                last_end = end_time

        f.close()
        self.has_changed = True

    @classmethod
    def import_source_srt(cls, srt_file: str, lang: str) -> 'Transcript':
        transcript = cls()
        transcript.phrases = []

        f = open(srt_file, 'r')
        i = 0
        for sub in srt.parse(f.read()):
            source = SourceLanguagePhrase(
                id=i,
                lang=lang,
                text=sub.content,
            )
            source.timings.set(
                timing=PhraseTiming(
                    start_time=sub.start.seconds + sub.start.microseconds/1000000,
                    end_time=sub.end.seconds + sub.end.microseconds/1000000,
                ),
                scheme=Timings.SOURCE,
            )
            phrase = Phrase(
                id=i,
                source=source
            )

            transcript.phrases.append(phrase)

            i += 1

        f.close()

        transcript.has_changed = True

        return transcript

    def import_target_srt(self, srt_file:str, lang: str):
        f = open(srt_file, 'r')
        i = 0
        for sub in srt.parse(f.read()):
            lp = LanguagePhrase(
                id=i,
                lang=lang,
                text=sub.content,
            )
            lp.timings.set(
                timing=PhraseTiming(
                    start_time=sub.start.seconds + sub.start.microseconds/1000000,
                    end_time=sub.end.seconds + sub.end.microseconds/1000000,
                ),
                scheme=Timings.SOURCE,
            )

            self.phrases[i].set_target(lang=lang, phrase=lp)

            i += 1

        f.close()

        self.has_changed = True

    def _save_file(self, file_name) -> bool:
        # print(f"CWD: {os.getcwd()}", file=sys.stderr)
        if os.path.exists(file_name):
            back_path = os.path.join(os.path.dirname(file_name), 'bak')
            if not os.path.exists(back_path):
                os.makedirs(back_path)
            back_file = os.path.join(back_path, os.path.basename(file_name))
            files = [f for f in glob.glob(f"{back_file}.*") if re.search(r'\.(\d+)$', f)]
            if len(files):
                files.sort()
                m = re.search(r'\.(\d+)$', files[-1])
                last_backup = int(m.group(1)) + 1
            else:
                last_backup = 0

            backup_file = f"{back_file}.{str(last_backup).rjust(3,'0')}"
            # print(f"Backup file: {backup_file}", file=sys.stderr)
            os.rename(file_name, backup_file)

        with gzip.open(file_name, mode='w') as f:
            f.write(bytes(self.to_json(indent=2, ensure_ascii=False), 'utf-8'))
            f.close()

        self.has_changed = False

        return True

    def save(self, path: str = None) -> bool:

        if path is None:
            path = TRANSCRIPT_FILE + ".gz"

        elif os.path.isdir(path):
            path = os.path.join(path, TRANSCRIPT_FILE + ".gz")

        return self._save_file(path)

    def export_subtitles(self, audio_lang: str, timing_scheme: str, subtitle_lang: str, sub_type: str = 'ass',
                         include_source: bool = False, debug: bool = False):

        if audio_lang is None:
            audio_lang = self.src_lang

        if sub_type == 'srt':
            subtitles = self.to_srt(
                audio_lang=audio_lang,
                timings_lang=subtitle_lang,
                include_source=include_source
            )
        else:
            subtitles = self.to_ass(
                audio_lang=audio_lang,
                timing_scheme=timing_scheme,
                subtitle_lang=subtitle_lang,
                include_source=include_source,
                debug=debug,
            )

        with open(subtitles_fullpath(audio_lang, timing_scheme, subtitle_lang, sub_type), mode='w', encoding='UTF-8') as f:
            print(subtitles_fullpath(audio_lang, timing_scheme, subtitle_lang, sub_type), file=sys.stderr)
            f.write(subtitles)
            f.close()

    def to_ass(self, audio_lang: str, timing_scheme: str, subtitle_lang: str, include_source: bool = False, debug: bool = False) -> str:
        subtitles = """[Script Info]
; Script generated by transcript.py
Title: Default Aegisub file
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[Aegisub Project Garbage]
Active Line: 6

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Latin,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Arabic,Simplified Arabic,36,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,1,2,10,10,10,178

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        for i in range(len(self.phrases)):
            subtitles += self.phrases[i].to_ass(
                prev_phrase=self.phrases[i-1] if i > 0 else None,
                next_phrase=self.phrases[i+1] if i < len(self.phrases)-1 else None,
                audio_lang=audio_lang,
                timing_scheme=timing_scheme,
                subtitle_lang=subtitle_lang,
                include_source=include_source,
                debug=debug,
            )
            subtitles += "\n"

        return subtitles

    def to_csv(self, lang: str) -> list[tuple]:
        csv = [
            ('Id', 'Start', 'End', 'Source', 'Translation')
        ]
        for phrase in self.phrases:
            try:
                csv.append(phrase.to_csv(lang=lang))
            except AttributeError as exc:
                print(str(phrase), file=sys.stderr)
                print(str(exc), file=sys.stderr)
                exit(2)

        return csv

    @classmethod
    def load_google_tts(cls, tts_file: str, phrase_gap: float = 1.0):
        with open(tts_file, 'r') as f:
            data = json.load(f)

        words = []

        for i, section in enumerate(data['results']):
            section_alt = section['alternatives'][0]
            if 'transcript' in section_alt:
                for j, word in enumerate(section_alt['words']):
                    words.append(Word(
                        id=len(words),
                        word=word['word'],
                        start_time=Word.secs_to_float(word['startTime']),
                        end_time=Word.secs_to_float(word['endTime']),
                        manuscript_break_before=(j == 0),
                    ))

        transcript = cls(
            src_lang=data['results'][0]['languageCode'].split('-')[0],
            tts_lang=data['results'][0]['languageCode'],
            tts_duration=Word.secs_to_float(data['results'][-1]['resultEndTime']),
            words=words,
        )

        transcript.compute_phrases(gap=phrase_gap)

        transcript.has_changed = True

        return transcript

    def build_phrases(self):
        phrases = []
        start = None
        for i, word in enumerate(self.words):
            if word.manuscript_break_before:
                if start is not None:
                    phrase = Phrase(
                        id=len(phrases),
                        source=SourceLanguagePhrase(lang=self.src_lang, text=''),
                    )
                    phrase.source.set_by_word_indices(words=self.words, start=start, end=i-1)
                    phrases.append(phrase)

                start = i

        phrase = Phrase(
            id=len(phrases),
            source=SourceLanguagePhrase(lang=self.src_lang, text=''),
        )
        phrase.source.set_by_word_indices(words=self.words, start=start, end=len(self.words)-1)
        phrases.append(phrase)

        self.phrases = phrases
        self.has_changed = True

    def compute_phrases(self, gap: float = 1.0, mark_breaks: bool = False):
        clauses = [
            ['through', 'that', 'which', 'when', 'whereby', 'is', 'as'],
            ['and', 'or', 'of', 'by', 'about', 'from', 'in', 'into', 'for']
        ]

        not_last_word = ['and', 'or', 'which']

        phrases = []
        phrase: Optional[Phrase] = None
        reason: Optional[str] = None
        for i, word in enumerate(self.words):
            if phrase is None:
                phrase = Phrase(
                    id=len(phrases),
                    source=SourceLanguagePhrase(
                        lang=self.src_lang,
                        text=word.word,
                        start_word=i,
                        end_word=i,
                    ),
                    reason=reason
                )
                phrase.source.timings.DEFAULT = Timings.SOURCE
                phrase.source.timings.set(
                    scheme=Timings.SOURCE,
                    timing=PhraseTiming(
                        start_time=word.start_time,
                        end_time=word.end_time
                    )
                )

            else:
                phrase.source.text += ' ' + word.word
                phrase.source.timings.get().end_time = word.end_time
                phrase.source.end_word = i

            next_word: Optional[Word] = self.words[i+1] if i < len(self.words)-1 else None
            reason = None
            if self.obey_manuscript_breaks:
                if next_word and next_word.manuscript_break_before:
                    reason = 'manuscript_break'

            elif i < len(self.words)-1:
                reason = word.break_reason(next_word=self.words[i+1], gap=gap)

            if reason is not None:
                phrases.append(phrase)
                phrase = None

        if phrase:
            phrases.append(phrase)

        if not self.obey_manuscript_breaks:
            # Process phrases to make sure none are too long
            for small_gap in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]:
                changed = True
                while changed:
                    changed = False
                    shortened = []
                    print(f"gap = {small_gap}", file=sys.stderr)
                    for p, phrase in enumerate(phrases):
                        shortened.append(phrase)
                        print(f"Phrase: {p}", file=sys.stderr)
                        if phrase.source.word_count() > 6:
                            for i in range(phrase.source.start_word+3, phrase.source.end_word-3):
                                reason = self.words[i].break_reason(next_word=self.words[i+1], gap=small_gap)
                                # print(i, reason, file=sys.stderr)
                                if reason is not None:
                                    new = phrase.split(self.words, split_at=i)
                                    new.reason = reason
                                    shortened.append(new)
                                    changed = True
                                    break

                    phrases = shortened

            for intros in clauses:
                changed = True
                while changed:
                    changed = False
                    shortened = []
                    for phrase in phrases:
                        shortened.append(phrase)
                        if phrase.source.word_count() > 6:
                            for i in range(phrase.source.start_word+3, phrase.source.end_word-3):
                                if self.words[i].word in intros:
                                    new = phrase.split(self.words, split_at=i-1)
                                    new.reason = self.words[i].word
                                    shortened.append(new)
                                    changed = True
                                    break

                    phrases = shortened

            for i in range(len(phrases)):
                if re.sub(r'["\';,.?()!@#$%^&*\-=+\\/:]', self.words[phrases[i].source.end_word].word, '') in not_last_word:
                    if i+1 < len(phrases):
                        # move the last word of the phrase to the next phrase
                        phrases[i].source.set_by_word_indices(self.words, phrases[i].source.start_word, phrases[i].source.end_word - 1)
                        phrases[i+1].source.set_by_word_indices(self.words, phrases[i + 1].source.start_word - 1, phrases[i + 1].source.end_word)

        # renumber phrases
        for i, phrase in enumerate(phrases):
            phrase.id = i

        if mark_breaks:
            # set manuscript break to False on every
            for word in self.words:
                word.manuscript_break_before = False

            # set manuscript breaks for first word of each phrase
            for phrase in phrases:
                self.words[phrase.source.start_word].manuscript_break_before = True

        self.phrases = phrases

        self.has_changed = True

    def to_manuscript(self) -> str:
        txt = ''
        section_text = ''
        for word in self.words:
            if word.manuscript_break_before:
                txt += f"{section_text}\n\n"
                section_text = ''

            section_text += (' ` ' if section_text else '') + word.word

        txt += f"{section_text}\n\n"

        return txt

    def reset_timings(self, lang: str, timing_scheme: str):
        for phrase in self.phrases:
            timing = phrase.get_timing(lang=lang, timing_scheme=timing_scheme)
            if timing is None:
                timing = PhraseTiming()
                phrase.set_timing(lang=lang, timing_scheme=timing_scheme, timing=timing)

            timing.reset_timing(phrase.source.timings.get(Timings.SOURCE))

        self.has_changed = True

    def gap_between(self, lang: str, timing_scheme: str, id1: int, id2: int) -> Optional[float]:
        if id2 > self.phrase_count()-1 or id1 < 0:
            return None

        return round(self.phrases[id2].get_timing(lang, timing_scheme).start_time
                     - self.phrases[id1].get_timing(lang, timing_scheme).end_time, 3)

    def build_translation_timings(self, lang: str):
        self.reset_timings(lang=lang, timing_scheme=Timings.TRANSLATION)

        last_end = 0.0
        last_src_end = 0.0
        for phrase in self.phrases:
            src_timing = phrase.source.timings.get(Timings.SOURCE)
            gap = src_timing.start_time - last_src_end
            start = last_end + gap
            end = start + src_timing.duration()
            timing = PhraseTiming(
                start_time=start,
                end_time=end,
            )
            phrase.source.timings.set(timing=timing, scheme=Timings.TRANSLATION)
            last_src_end = src_timing.end_time

            target = phrase.get_target(lang)
            start = end
            # end += target.duration_audio.duration
            end += target.natural_audio.get_duration()
            tgt_timing = PhraseTiming(
                start_time=start,
                end_time=end,
                freeze_time=start,
                freeze_duration=target.natural_audio.duration
            )
            phrase.set_timing(lang=lang, timing_scheme=Timings.TRANSLATION, timing=tgt_timing)

            last_end = end

        self.has_changed = True

    def adjust_dub_timings(self, lang: str):
        from copy import deepcopy
        old_transcript = deepcopy(self)

        # set the start and end times for the target language
        self.reset_timings(lang=lang, timing_scheme=Timings.DUBBED)
        i = 0
        speeds = []  # type: list[Phrase]

        # make sure ids are 0 based
        for phrase in self.phrases:
            phrase.id = i
            i += 1

            speeds.append(phrase)

        iterations = 0
        finished = False
        while not finished and iterations < 4000:
            finished = True
            iterations += 1
            speeds.sort(key=lambda p: p.get_target(lang).audio_speed(timing_scheme=Timings.DUBBED), reverse=True)

            # print("Looping...", file=sys.stderr)
            for phrase in speeds:
                target = phrase.get_target(lang)
                # print(f"Speed: {target.audio_speed()}", file=sys.stderr)

                if target.audio_speed(timing_scheme=Timings.DUBBED) <= SPEED_MODERATE:
                    finished = True
                    break

                if target.audio_speed(timing_scheme=Timings.DUBBED) > SPEED_VERY_FAST:
                    # look ahead and back 3 blocks
                    look = 4

                elif target.audio_speed(timing_scheme=Timings.DUBBED) > SPEED_FAST:
                    # look ahead and back 2 blocks
                    look = 3

                elif target.audio_speed(timing_scheme=Timings.DUBBED) > SPEED_HIGH_MODERATE:
                    # look ahead and back 1 block
                    look = 2

                else:
                    look = 1

                for i in range(0, look+1):
                    gap = self.gap_between(lang, id1=phrase.id+i, id2=phrase.id+i+1, timing_scheme=Timings.DUBBED)
                    if gap is not None and gap > DESIRED_GAP + GAP_INCREMENT:
                        if target.timings.get(Timings.DUBBED).move_end(GAP_INCREMENT):
                            for j in range(i, 0, -1):
                                self.phrases[phrase.id+i].get_timing(lang, Timings.DUBBED).shift(GAP_INCREMENT)
                            finished = False
                            # print(f"Gap+: {gap}, Ratio: {target.audio_speed()} Id: {phrase.id}, Btwn: {phrase.id+i}-{phrase.id+i+1}", file=sys.stderr)
                            break

                    gap = self.gap_between(lang, id1=phrase.id-i-1, id2=phrase.id-i, timing_scheme=Timings.DUBBED)
                    if gap is not None and gap > DESIRED_GAP + GAP_INCREMENT:
                        if target.timings.get(Timings.DUBBED).move_start(-GAP_INCREMENT):
                            for j in range(i, 0, -1):
                                self.phrases[phrase.id-i].get_timing(lang, Timings.DUBBED).shift(-GAP_INCREMENT)
                            finished = False
                            # print(f"Gap-: {gap}, Ratio: {target.audio_speed()}, Id: {phrase.id}, Btwn: {phrase.id-i-1}-{phrase.id-i}", file=sys.stderr)
                            break

                if not finished:
                    break

                # print("Checking for compressible blocks...", file=sys.stderr)
                for i in range(1, look+1):
                    if phrase.id+i < self.phrase_count():
                        next_target = self.phrases[phrase.id+i].get_target(lang)
                        if next_target.audio_speed(timing_scheme=Timings.DUBBED) < SPEED_ACCEPTABLE \
                                and next_target.timings.get(Timings.DUBBED).move_start(GAP_INCREMENT):
                            for j in range(i-1, 0, -1):
                                self.phrases[phrase.id+i].get_timing(lang, Timings.DUBBED).shift(GAP_INCREMENT)
                            finished = False
                            print(f"Compress Id: {phrase.id+i}", file=sys.stderr)
                            break

                    if phrase.id-i >= 0:
                        prev_target = self.phrases[phrase.id-i].get_target(lang)
                        if prev_target.audio_speed(timing_scheme=Timings.DUBBED) < SPEED_ACCEPTABLE \
                                and prev_target.timings.get(Timings.DUBBED).move_end(-GAP_INCREMENT):
                            for j in range(i-1, 0, -1):
                                self.phrases[phrase.id-i].get_timing(lang, Timings.DUBBED).shift(-GAP_INCREMENT)
                            finished = False
                            print(f"Compress Id: {phrase.id-i}", file=sys.stderr)
                            break

        # Apply freezes for sections that are too long
        total_shift = 0.0
        for phrase in self.phrases:
            target = phrase.get_target(lang)
            if total_shift > 0.0:
                target.timings.get(Timings.DUBBED).shift(total_shift)

            expansion = target.natural_audio.duration / SPEED_ACCEPTABLE - target.timings.get(Timings.DUBBED).duration()
            if expansion > 0.0:
                target.timings.get(Timings.DUBBED).expand_and_freeze(expansion)
                total_shift += expansion

            if expansion > 0.0 and phrase.id < self.phrase_count()-1:
                gap = target.timings.get(Timings.DUBBED).gap_between(
                    self.phrases[phrase.id+1].get_timing(lang, Timings.DUBBED)
                ) + total_shift
                if gap < MINIMUM_GAP:
                    extra = MINIMUM_GAP - gap
                    target.timings.get(Timings.DUBBED).freeze_duration += extra
                    total_shift += extra

        # Set dubbing times for the source audio
        for phrase in self.phrases:
            timing = phrase.get_timing(lang=lang, timing_scheme=Timings.DUBBED)
            phrase.source.timings.set(scheme=Timings.DUBBED, timing=PhraseTiming(
                start_time=timing.start_time,
                end_time=timing.start_time + phrase.source.natural_audio.duration
            ))

        # Mark audio changed for changed timings
        for i in range(0, len(self.phrases)):
            timing = self.phrases[i].get_timing(lang, Timings.DUBBED)
            old_timing = old_transcript.phrases[i].get_timing(lang, Timings.DUBBED)
            if old_timing and timing.duration() != old_timing.duration():
                self.phrases[i].get_target(lang).mark_duration_audio_changed()

        self.has_changed = True
