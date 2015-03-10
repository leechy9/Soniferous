from django.apps import AppConfig

class SignalConfig(AppConfig):
    name = 'music_player'
    verbose_name = 'Music Player'
    def ready(self):
      import music_player.signals
