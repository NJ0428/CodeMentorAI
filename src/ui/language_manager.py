
import gettext
import os
from src.config.settings import settings

class LanguageManager:
    def __init__(self):
        self.current_lang = settings.ui.language
        self.localedir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'locale')
        self.translation = gettext.translation(
            'messages',
            localedir=self.localedir,
            languages=[self.current_lang],
            fallback=True
        )

    def get_translator(self):
        return self.translation.gettext

_language_manager = None

def get_language_manager():
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager

def get_translator():
    return get_language_manager().get_translator()
