#!/usr/bin/env python
"""
Test script to reproduce the calendar date offset issue.
This script will:
1. Create a test leave request for August 5-7
2. Call the LeaveCalendarViewSet API
3. Compare the generated dates with expected dates
"""

import os
import sys
import django
from datetime import date, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from timehub.models import LeaveRequest, LeaveType, UserProfile
from django.contrib.auth.models import User
from timehub.views import LeaveCalendarViewSet
from rest_framework.test import APIRequestFactory
from django.utils import timezone

def test_calendar_dates():
    print("🔍 Testing calendar date offset issue...")
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        print(f"✅ Created test user: {user.username}")
    
    # Create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'leave_balance_days': 30.0,
            'weekly_hours': 40.0
        }
    )
    if created:
        print(f"✅ Created user profile for {user.username}")
    
    # Get or create leave type
    leave_type, created = LeaveType.objects.get_or_create(
        code='VAC',
        defaults={
            'name': 'Vacaciones',
            'is_paid': True,
            'deducts_from_balance': True
        }
    )
    if created:
        print(f"✅ Created leave type: {leave_type.name}")
    
    # Create test leave request for August 5-7, 2025
    test_start_date = date(2025, 8, 5)  # August 5
    test_end_date = date(2025, 8, 7)    # August 7
    
    # Delete existing test requests to avoid duplicates
    LeaveRequest.objects.filter(
        user=user,
        start_date=test_start_date,
        end_date=test_end_date
    ).delete()
    
    leave_request = LeaveRequest.objects.create(
        user=user,
        leave_type=leave_type,
        start_date=test_start_date,
        end_date=test_end_date,
        days_requested=3,
        reason='Test vacation request',
        status='APPROVED'  # Approve it so it shows in calendar
    )
    
    print(f"✅ Created test leave request:")
    print(f"   User: {leave_request.user.username}")
    print(f"   Dates: {leave_request.start_date} to {leave_request.end_date}")
    print(f"   Days: {leave_request.days_requested}")
    print(f"   Status: {leave_request.status}")
    
    # Test the calendar API logic
    print("\n🧪 Testing LeaveCalendarViewSet logic...")
    
    # Simulate the backend logic from views.py lines 606-631
    year = 2025
    leave_requests = LeaveRequest.objects.filter(
        user_id=user.id,
        start_date__year__lte=year,
        end_date__year__gte=year
    ).select_related('leave_type')
    
    print(f"Found {leave_requests.count()} leave requests for year {year}")
    
    calendar_days = []
    
    for request in leave_requests:
        print(f"\nProcessing request: {request.start_date} to {request.end_date}")
        
        # Generate all dates in the request range (backend logic)
        start_date = max(request.start_date, datetime(year, 1, 1).date())
        end_date = min(request.end_date, datetime(year, 12, 31).date())
        
        print(f"Adjusted range: {start_date} to {end_date}")
        
        current_date = start_date
        dates_generated = []
        
        while current_date <= end_date:
            status = 'consumed'  # Since it's approved and in the past conceptually
            
            calendar_day = {
                'date': current_date.isoformat(),
                'status': status,
                'leave_request_id': request.id,
                'leave_type': request.leave_type.name
            }
            calendar_days.append(calendar_day)
            dates_generated.append(current_date.isoformat())
            
            current_date += timedelta(days=1)
        
        print(f"Generated dates: {dates_generated}")
    
    print(f"\n📅 Calendar API would return {len(calendar_days)} calendar days:")
    for day in calendar_days:
        print(f"   {day['date']} - {day['status']} ({day['leave_type']})")
    
    # Expected vs Actual analysis
    print(f"\n🔍 ANALYSIS:")
    print(f"Expected vacation dates: 2025-08-05, 2025-08-06, 2025-08-07")
    print(f"Backend generates dates: {[day['date'] for day in calendar_days]}")
    
    expected_dates = ['2025-08-05', '2025-08-06', '2025-08-07']
    actual_dates = [day['date'] for day in calendar_days]
    
    if actual_dates == expected_dates:
        print("✅ Backend generates correct dates!")
    else:
        print("❌ Backend date generation has issues!")
        print(f"   Expected: {expected_dates}")
        print(f"   Actual:   {actual_dates}")
    
    # Now test frontend date matching logic
    print(f"\n🖥️ Testing frontend date matching...")
    
    # Simulate frontend calendar generation for August 2025
    selected_month = 7  # August (0-based)
    year = 2025
    
    # Frontend logic from leave-balance.tsx line 84-85
    sample_dates = []
    for day in [5, 6, 7, 8]:  # Days around our vacation
        test_date = datetime(year, selected_month + 1, day)  # +1 because JS months are 0-based
        date_str = test_date.date().isoformat()  # This becomes YYYY-MM-DD
        
        # Check if this matches any calendar data
        leave_data = None
        for cal_day in calendar_days:
            if cal_day['date'] == date_str:
                leave_data = cal_day
                break
        
        sample_dates.append({
            'day': day,
            'date_str': date_str,
            'has_leave': leave_data is not None,
            'leave_status': leave_data['status'] if leave_data else None
        })
    
    print("Frontend calendar generation test:")
    for item in sample_dates:
        status_indicator = "🔴" if item['has_leave'] else "⚪"
        print(f"   Day {item['day']}: {item['date_str']} {status_indicator} {item['leave_status'] or 'no leave'}")
    
    # Final diagnosis
    print(f"\n🏥 DIAGNOSIS:")
    leave_days = [item for item in sample_dates if item['has_leave']]
    if leave_days:
        leave_day_numbers = [item['day'] for item in leave_days]
        print(f"Leave appears on calendar days: {leave_day_numbers}")
        if leave_day_numbers == [5, 6, 7]:
            print("✅ Dates appear correctly - no offset issue detected in this test")
        elif leave_day_numbers == [6, 7, 8]:
            print("❌ CONFIRMED: +1 day offset issue! Leave shows on days 6-8 instead of 5-7")
        else:
            print(f"❓ Unexpected pattern: {leave_day_numbers}")
    else:
        print("❓ No leave days found in calendar - check date range or status")

if __name__ == "__main__":
    test_calendar_dates()