"""
Utilidades para cálculos de vacaciones y días laborables
"""
from datetime import date, timedelta
from typing import List, Tuple
from .models import Country, Holiday, UserProfile


def get_business_days(start_date: date, end_date: date, country: Country) -> int:
    """
    Calcula el número de días laborables entre dos fechas,
    excluyendo fines de semana y feriados del país.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin (inclusiva)
        country: País para determinar días laborables y feriados
    
    Returns:
        Número de días laborables
    """
    if start_date > end_date:
        return 0
    
    business_days = 0
    current_date = start_date
    
    # Obtener feriados del país en el rango de fechas
    holidays = set(
        Holiday.objects.filter(
            country=country,
            date__range=[start_date, end_date],
            is_active=True
        ).values_list('date', flat=True)
    )
    
    # Días laborables del país (1=Lunes, 7=Domingo)
    work_days = set(country.work_days) if country.work_days else {1, 2, 3, 4, 5}
    
    while current_date <= end_date:
        # weekday() retorna 0=Lunes, 6=Domingo, necesitamos convertir a 1-7
        day_of_week = current_date.weekday() + 1
        
        # Si es día laborable y no es feriado
        if day_of_week in work_days and current_date not in holidays:
            business_days += 1
        
        current_date += timedelta(days=1)
    
    return business_days


def calculate_vacation_days_needed(start_date: date, end_date: date, user_id: int) -> Tuple[int, int]:
    """
    Calcula cuántos días de vacaciones se necesitan para un rango de fechas,
    considerando días laborables y feriados.
    
    Args:
        start_date: Fecha de inicio de vacaciones
        end_date: Fecha de fin de vacaciones
        user_id: ID del usuario
    
    Returns:
        Tuple con (días_calendario, días_laborables)
    """
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        country = user_profile.country
    except UserProfile.DoesNotExist:
        # Default: contar todos los días como laborables
        calendar_days = (end_date - start_date).days + 1
        return calendar_days, calendar_days
    
    if not country:
        # Sin país definido, contar todos los días
        calendar_days = (end_date - start_date).days + 1
        return calendar_days, calendar_days
    
    calendar_days = (end_date - start_date).days + 1
    business_days = get_business_days(start_date, end_date, country)
    
    return calendar_days, business_days


def check_vacation_conflicts(start_date: date, end_date: date, user_id: int, exclude_request_id: int = None) -> List[dict]:
    """
    Verifica si hay conflictos con otras solicitudes de vacaciones aprobadas.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        user_id: ID del usuario
        exclude_request_id: ID de solicitud a excluir (para ediciones)
    
    Returns:
        Lista de conflictos encontrados
    """
    from .models import LeaveRequest
    
    conflicts = []
    
    # Buscar solicitudes aprobadas que se solapen
    overlapping_requests = LeaveRequest.objects.filter(
        user_id=user_id,
        status='APPROVED',
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    if exclude_request_id:
        overlapping_requests = overlapping_requests.exclude(id=exclude_request_id)
    
    for request in overlapping_requests:
        # Calcular días de solapamiento
        overlap_start = max(start_date, request.start_date)
        overlap_end = min(end_date, request.end_date)
        overlap_days = (overlap_end - overlap_start).days + 1
        
        conflicts.append({
            'request_id': request.id,
            'leave_type': request.leave_type.name,
            'start_date': request.start_date,
            'end_date': request.end_date,
            'overlap_days': overlap_days,
            'overlap_start': overlap_start,
            'overlap_end': overlap_end
        })
    
    return conflicts


def calculate_accumulated_vacation_days(user_id: int, year: int) -> float:
    """
    Calcula los días de vacaciones que deben acumularse para el año siguiente.
    
    Args:
        user_id: ID del usuario
        year: Año a evaluar
    
    Returns:
        Días a acumular para el siguiente año
    """
    from django.db import models
    from .models import LeaveRequest
    
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        annual_entitlement = float(user_profile.leave_balance_days)
    except UserProfile.DoesNotExist:
        return 0.0
    
    # Calcular días usados en el año (solo vacaciones que descuentan del balance)
    used_days = LeaveRequest.objects.filter(
        user_id=user_id,
        leave_type__deducts_from_balance=True,
        status='APPROVED',
        start_date__year=year
    ).aggregate(total=models.Sum('days_requested'))['total'] or 0
    
    # Días no utilizados
    unused_days = annual_entitlement - float(used_days)
    
    # Solo acumular días positivos (no se pueden acumular déficits)
    return max(0.0, unused_days)


def process_year_end_accumulation(year: int) -> dict:
    """
    Procesa la acumulación de días no utilizados al final del año para todos los usuarios.
    
    Args:
        year: Año que está terminando
    
    Returns:
        Resumen del procesamiento
    """
    from django.db import models
    
    processed_users = 0
    total_accumulated = 0.0
    
    # Obtener todos los perfiles de usuario activos
    user_profiles = UserProfile.objects.filter(is_active=True)
    
    for profile in user_profiles:
        # Calcular días a acumular
        days_to_accumulate = calculate_accumulated_vacation_days(profile.user.id, year)
        
        if days_to_accumulate > 0:
            # Agregar a los días acumulados existentes
            profile.accumulated_vacation_days += days_to_accumulate
            profile.save()
            
            processed_users += 1
            total_accumulated += days_to_accumulate
    
    return {
        'year_processed': year,
        'users_processed': processed_users,
        'total_days_accumulated': total_accumulated,
        'average_per_user': total_accumulated / processed_users if processed_users > 0 else 0
    }


def get_holidays_in_range(start_date: date, end_date: date, country: Country) -> List[dict]:
    """
    Obtiene todos los feriados en un rango de fechas para un país.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        country: País
    
    Returns:
        Lista de feriados en el rango
    """
    holidays = Holiday.objects.filter(
        country=country,
        date__range=[start_date, end_date],
        is_active=True
    ).order_by('date')
    
    return [
        {
            'name': holiday.name,
            'date': holiday.date,
            'is_recurring': holiday.is_recurring
        }
        for holiday in holidays
    ]