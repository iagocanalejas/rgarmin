from datetime import datetime


def translate(text: str) -> str:
    text = text.lower()
    if text == "strength_training":
        return "Fuerza"
    elif text == "indoor_rowing":
        return "Remo Indoor"
    elif text == "cycling":
        return "Ciclismo"
    elif text == "running":
        return "Carrera"
    elif text == "monday":
        return "Lunes"
    elif text == "tuesday":
        return "Martes"
    elif text == "wednesday":
        return "Miércoles"
    elif text == "thursday":
        return "Jueves"
    elif text == "friday":
        return "Viernes"
    elif text == "saturday":
        return "Sábado"
    elif text == "sunday":
        return "Domingo"
    elif text == "previous":
        return "Anterior"
    elif text == "next":
        return "Siguiente"
    elif text == "_error_fetching_activities":
        return "Error recuperando actividades"
    else:
        return "Otros"


def format_datetime(d: datetime) -> str:
    return d.strftime("%d-%m-%Y %H:%M:%S")


def format_time(d: datetime, with_seconds: bool = False) -> str:
    return d.strftime("%H:%M:%S") if with_seconds else d.strftime("%H:%M")


def format_duration(seconds: float) -> str:
    total_seconds = round(seconds)  # Round to nearest second
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes:02}min {seconds:02}sec" if hours else f"{minutes}min {seconds:02}sec"
