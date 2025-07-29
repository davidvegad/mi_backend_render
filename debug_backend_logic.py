#!/usr/bin/env python3
"""
Debug script to analyze the backend date generation logic
This runs without Django to test the pure date logic
"""

from datetime import date, datetime, timedelta

def simulate_backend_logic():
    print("🔍 Debugging backend LeaveCalendarViewSet date generation...")
    
    # Simulate a leave request from August 5-7, 2025
    class MockLeaveRequest:
        def __init__(self, start_date, end_date, status):
            self.start_date = start_date
            self.end_date = end_date
            self.status = status
            self.id = 1
            self.leave_type = MockLeaveType()
    
    class MockLeaveType:
        def __init__(self):
            self.name = "Vacaciones"
    
    # Create test leave request
    leave_request = MockLeaveRequest(
        start_date=date(2025, 8, 5),  # August 5
        end_date=date(2025, 8, 7),    # August 7
        status='APPROVED'
    )
    
    print(f"Leave request: {leave_request.start_date} to {leave_request.end_date}")
    print(f"Status: {leave_request.status}")
    
    # Simulate backend logic from views.py lines 606-631
    year = 2025
    leave_requests = [leave_request]  # Mock query result
    
    calendar_days = []
    
    for request in leave_requests:
        print(f"\n📅 Processing request: {request.start_date} to {request.end_date}")
        
        # This is the exact backend logic
        start_date = max(request.start_date, datetime(year, 1, 1).date())
        end_date = min(request.end_date, datetime(year, 12, 31).date())
        
        print(f"Adjusted range: {start_date} to {end_date}")
        
        current_date = start_date
        generated_dates = []
        
        while current_date <= end_date:
            status = 'available'
            if request.status == 'APPROVED':
                # Note: datetime.now().date() would vary, let's assume it's before our dates
                if current_date < date(2025, 8, 1):  # Assume we're checking from the future
                    status = 'consumed'
                else:
                    status = 'approved_pending'
            elif request.status == 'SUBMITTED':
                status = 'pending'
            
            calendar_day = {
                'date': current_date.isoformat(),
                'status': status,
                'leave_request_id': request.id,
                'leave_type': request.leave_type.name
            }
            calendar_days.append(calendar_day)
            generated_dates.append(current_date.isoformat())
            
            current_date += timedelta(days=1)
        
        print(f"Generated dates: {generated_dates}")
    
    print(f"\n🎯 Backend API Response:")
    for day in calendar_days:
        print(f"   {day['date']} - {day['status']} ({day['leave_type']})")
    
    return calendar_days

def test_edge_cases():
    print("\n" + "="*60)
    print("🧪 TESTING EDGE CASES")
    print("="*60)
    
    # Test 1: Leave request spanning multiple years
    print("\n1. Testing year boundary crossing:")
    
    class MockRequest:
        def __init__(self, start_date, end_date, status='APPROVED'):
            self.start_date = start_date
            self.end_date = end_date
            self.status = status
            self.id = 1
            self.leave_type = type('obj', (object,), {'name': 'Vacaciones'})()
    
    # Request from Dec 30, 2024 to Jan 2, 2025
    boundary_request = MockRequest(date(2024, 12, 30), date(2025, 1, 2))
    
    year = 2025
    start_date = max(boundary_request.start_date, datetime(year, 1, 1).date())
    end_date = min(boundary_request.end_date, datetime(year, 12, 31).date())
    
    print(f"Request: {boundary_request.start_date} to {boundary_request.end_date}")
    print(f"For year {year}, adjusted to: {start_date} to {end_date}")
    
    current_date = start_date
    boundary_dates = []
    while current_date <= end_date:
        boundary_dates.append(current_date.isoformat())
        current_date += timedelta(days=1)
    
    print(f"Generated dates: {boundary_dates}")
    
    # Test 2: Single day request
    print("\n2. Testing single day request:")
    single_day_request = MockRequest(date(2025, 8, 5), date(2025, 8, 5))
    
    start_date = max(single_day_request.start_date, datetime(year, 1, 1).date())
    end_date = min(single_day_request.end_date, datetime(year, 12, 31).date())
    
    print(f"Request: {single_day_request.start_date} to {single_day_request.end_date}")
    
    current_date = start_date
    single_dates = []
    while current_date <= end_date:
        single_dates.append(current_date.isoformat())
        current_date += timedelta(days=1)
    
    print(f"Generated dates: {single_dates}")
    
    # Test 3: Check for off-by-one errors in the loop
    print("\n3. Testing loop boundary conditions:")
    test_request = MockRequest(date(2025, 8, 5), date(2025, 8, 7))
    
    start_date = test_request.start_date
    end_date = test_request.end_date
    
    print(f"Request: {start_date} to {end_date}")
    print("Loop iterations:")
    
    current_date = start_date
    iteration = 0
    while current_date <= end_date:
        iteration += 1
        print(f"  Iteration {iteration}: current_date = {current_date}")
        print(f"    current_date <= end_date? {current_date <= end_date}")
        print(f"    Will generate: {current_date.isoformat()}")
        
        current_date += timedelta(days=1)
        
        if iteration > 10:  # Safety break
            print("    (Safety break - too many iterations)")
            break
    
    print(f"Expected 3 dates (Aug 5, 6, 7), got {iteration} iterations")

def analyze_datetime_usage():
    print("\n" + "="*60)
    print("🔍 ANALYZING DATETIME USAGE IN BACKEND")
    print("="*60)
    
    # Check the datetime(year, 1, 1).date() pattern used in backend
    year = 2025
    
    print("Backend uses these datetime constructions:")
    
    jan_1 = datetime(year, 1, 1).date()
    print(f"datetime({year}, 1, 1).date() = {jan_1}")
    print(f"Type: {type(jan_1)}")
    
    dec_31 = datetime(year, 12, 31).date()
    print(f"datetime({year}, 12, 31).date() = {dec_31}")
    print(f"Type: {type(dec_31)}")
    
    # Test max/min operations
    test_start = date(2025, 8, 5)
    test_end = date(2025, 8, 7)
    
    adjusted_start = max(test_start, jan_1)
    adjusted_end = min(test_end, dec_31)
    
    print(f"\nFor leave request {test_start} to {test_end}:")
    print(f"max({test_start}, {jan_1}) = {adjusted_start}")
    print(f"min({test_end}, {dec_31}) = {adjusted_end}")
    
    # Check if there's any issue with isoformat()
    print(f"\nDate serialization:")
    print(f"{test_start}.isoformat() = '{test_start.isoformat()}'")
    print(f"{test_end}.isoformat() = '{test_end.isoformat()}'")

if __name__ == "__main__":
    backend_result = simulate_backend_logic()
    test_edge_cases()
    analyze_datetime_usage()
    
    print("\n" + "="*60)
    print("🎯 SUMMARY")
    print("="*60)
    print("Backend logic analysis shows:")
    print("1. Date generation appears correct for August 5-7 range")
    print("2. Loop generates exactly 3 dates as expected")
    print("3. Date serialization uses standard isoformat() method")
    print("4. No obvious off-by-one errors in date iteration")
    print("\nIf users report +1 day offset, the issue is likely:")
    print("- Frontend timezone handling")
    print("- Browser-specific Date constructor behavior")
    print("- Actual data in database differs from expected")
    print("- Calendar display logic in frontend")