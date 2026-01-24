# core/services/log_service.py
from core.models import Log

class LogExportService:
    @staticmethod
    def generate_logs_text():
      # Pobierz wszystkie logi z całego systemu
      logs = Log.objects.all().order_by('-event_time')

      if not logs.exists():
        return "Brak zarejestrowanych logów w systemie."

      separator = "\n" + "="*40 + "\n"
      return separator.join([log.get_full_report() for log in logs])