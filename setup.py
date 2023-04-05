from setuptools import setup

setup(
    name='dubbing_tools',
    version='0.1',
    description='Tools for Dubbing Videos',
    url='https://www.supplee.com',
    author='Your Name',
    author_email='your.name@example.com',
    license='MIT',
    packages=['dubbing_tools'],
    scripts=[
        'dt-build-dub-timings',
        'dt-build-source-audio',
        'dt-build-translation-timings',
        'dt-build-video',
        'dt-burn-ass-subtitles',
        'dt-burn-subtitles',
        'dt-chunk-source-audio',
        'dt-cp-lang',
        'dt-duration-stats',
        'dt-export-csv',
        'dt-export-manuscript',
        'dt-export-subtitles',
        'dt-extract-wav',
        'dt-gap-stats',
        'dt-import-csv',
        'dt-import-manuscript',
        'dt-rebuild-phrases',
        'dt-reset-timings',
        'dt-translate',
        'dt-tts-duration',
        'dt-tts-natural',
        'dt-find-slides',
    ],
    install_requires=[
        'ffmpeg-python',
        'fire',
        'google-api-core',
        'google-auth',
        'google-cloud-core',
        'google-cloud-speech',
        'google-cloud-storage',
        'google-cloud-texttospeech',
        'google-cloud-translate',
        'google-crc32c',
        'google-resumable-media',
        'googleapis-common-protos',
        'pydub',
        'moviepy',
        'python-dotenv',
        'dataclasses-json',
        'jinja2',
        'dotted-dict',
        'azure-cognitiveservices-speech',
        'srt',
        'spacy',
        'opencv-python',
        'scikit-image',

    ],
    zip_safe=False
)
