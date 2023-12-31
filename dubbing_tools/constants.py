
__all__ = [
    'AZURE_VOICES',
    'DESIRED_GAP',
    'GAP_INCREMENT',
    'GOOGLE_VOICES',
    'MINIMUM_GAP',
    'SERVICE_AZURE',
    'SERVICE_GOOGLE',
    'SERVICE_SOURCE',
    'SERVICES',
    'SPEED_ACCEPTABLE',
    'SPEED_FAST',
    'SPEED_HIGH_MODERATE',
    'SPEED_MODERATE',
    'SPEED_VERY_FAST',
    'SUBDIR_AUDIO',
    'SUBDIR_VIDEO',
    'TRANSCRIPT_FILE',
    'VOICE_SPEAKER',
]

SUBDIR_AUDIO = 'audio-clips'
SUBDIR_VIDEO = 'videos'

VOICE_SPEAKER = 'speaker'

GOOGLE_VOICES = {
    'ar': 'ar-XA-Wavenet-B',
}
AZURE_VOICES = {
    'ar': 'ar-EG-ShakirNeural',
    'ar-EG': 'ar-EG-ShakirNeural',
    'ar-JO': 'ar-JO-TaimNeural',
    'ar-LB': 'ar-LB-RamiNeural',
    'ar-MA': 'ar-MA-JamalNeural',
    'ar-SA': 'ar-SA-HamedNeural',
    'ar-SY': 'ar-SY-LaithNeural',
    'pt': 'pt-BR-AntonioNeural',
}

SERVICE_AZURE = 'azure'
SERVICE_GOOGLE = 'google'
SERVICE_SOURCE = 'source'
SERVICES = [
    SERVICE_AZURE,
    SERVICE_GOOGLE,
    SERVICE_SOURCE,
]
MINIMUM_GAP = 0.5
DESIRED_GAP = 0.8

GAP_INCREMENT = 0.05
SPEED_VERY_FAST = 1.4
SPEED_FAST = 1.3
SPEED_HIGH_MODERATE = 1.2
SPEED_MODERATE = 1.1
SPEED_ACCEPTABLE = 1.05
TRANSCRIPT_FILE = 'transcript.json'

