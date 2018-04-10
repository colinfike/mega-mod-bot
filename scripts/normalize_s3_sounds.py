"""Script to normalize sounds in S3."""
import boto3
from pydub import AudioSegment
import tempfile


def normalize_me():
    """Normalize all sounds present in S3."""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('mega-mod-bot.sound-clips')
    sound_files = []

    def match_target_amplitude(sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    for file in bucket.objects.all():
        temp_file = tempfile.NamedTemporaryFile()
        bucket.download_fileobj(file.key, temp_file)
        temp_file.seek(0)
        sound_files.append((temp_file, file.key))

    for sound_tuple in sound_files:
        temp_file = sound_tuple[0]
        name = sound_tuple[1]
        sound_clip = AudioSegment.from_file(temp_file.name, format='wav')
        normalized_sound = match_target_amplitude(sound_clip, -30.0)

        export_temp = tempfile.TemporaryFile()
        normalized_sound.export(export_temp, format='wav')
        export_temp.seek(0)

        s3.meta.client.upload_fileobj(export_temp, 'mega-mod-bot.sound-clips', name)


if __name__ == "__main__":
    normalize_me()
