from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter


class Subtitle:
    def __init__(self, video_id):
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        manually_created = transcripts._manually_created_transcripts
        generated_transcripts = transcripts._generated_transcripts
        self.transcripts = [manually_created[m] for m in manually_created] + \
                           [generated_transcripts[g] for g in generated_transcripts]
        for sub in transcripts:
            if sub.is_translatable:
                self.translatable = sub
                break

        self.translation_languages = transcripts._translation_languages

    def get_subtitles(self):
        subtitles = []
        for sub in self.transcripts:
            subtitles.append("{subtitle.language_code} (\"{subtitle.language}\")".format(subtitle=sub))
        if self.translatable:
            subtitles += [f"{lang['language']} (translated)" for lang in self.translation_languages]
        return subtitles

    def generate_srt_format(self, index):
        if index < len(self.transcripts):
            yt_format = self.transcripts[index].fetch()
        else:
            yt_format = self.translatable. \
                translate(self.translation_languages[index - len(self.transcripts)]['language_code']).fetch()
        srt_format = SRTFormatter().format_transcript(yt_format)

        return srt_format

    def get_lang_code(self, index):
        if index < len(self.transcripts):
            transcript = self.transcripts[index].language
        else:
            transcript = self.translatable. \
                translate(self.translation_languages[index - len(self.transcripts)]['language_code']).language
        return transcript
