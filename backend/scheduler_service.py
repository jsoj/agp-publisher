import random
import datetime
from zoneinfo import ZoneInfo

TZ_SAO_PAULO = ZoneInfo("America/Sao_Paulo")

def calculate_next_random_run(start_time_str: str, end_time_str: str, reference_date: datetime.date = None) -> datetime.datetime:
    """
    Calcula um horário aleatório entre start_time_str e end_time_str (formato HH:MM)
    para o dia de execução subsequente (hoje se o horário gerado for no futuro, senão amanhã).
    """
    if not reference_date:
        reference_date = datetime.datetime.now(TZ_SAO_PAULO).date()
        
    try:
        sh, sm = map(int, start_time_str.split(':'))
        eh, em = map(int, end_time_str.split(':'))
    except Exception as e:
        raise ValueError(f"Formato de hora inválido. Use 'HH:MM'. Erro: {e}")
        
    start_minutes = sh * 60 + sm
    end_minutes = eh * 60 + em
    
    if end_minutes <= start_minutes:
        raise ValueError("O horário final deve ser maior que o horário inicial.")
        
    # Sorteia um minuto dentro do intervalo
    chosen_minutes = random.randint(start_minutes, end_minutes)
    
    chosen_hour = chosen_minutes // 60
    chosen_minute = chosen_minutes % 60
    
    # Monta o datetime correspondente na timezone local
    now_local = datetime.datetime.now(TZ_SAO_PAULO)
    scheduled_datetime = datetime.datetime.combine(
        reference_date, 
        datetime.time(chosen_hour, chosen_minute), 
        tzinfo=TZ_SAO_PAULO
    )
    
    # Se o horário já passou hoje, agenda para amanhã
    if scheduled_datetime < now_local:
        scheduled_datetime += datetime.timedelta(days=1)
        
    return scheduled_datetime
