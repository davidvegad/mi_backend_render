// Test specific timezone scenarios that could cause +1 day offset

console.log("🔍 Testing timezone scenarios that could cause +1 day offset...\n");

// The issue likely occurs when the user's browser is in a timezone 
// where creating a Date at midnight shifts to the next day in UTC

console.log("=== CRITICAL TIMEZONE TEST ===");
console.log("Testing what happens when user is in UTC+X timezone...\n");

// Simulate being in different timezones by creating dates at different times
// When a user in UTC+5 (like Pacific timezone) creates a date at midnight,
// it becomes the next day in UTC

function testTimezoneOffset() {
    const year = 2025;
    const month = 7; // August
    
    console.log("Backend returns leave for: 2025-08-05, 2025-08-06, 2025-08-07");
    console.log("\nFrontend calendar generation simulation:\n");
    
    // Test days 5-8 with different time scenarios
    for (let day = 5; day <= 8; day++) {
        console.log(`=== Day ${day} ===`);
        
        // Scenario 1: Normal date creation (should work fine)
        const normalDate = new Date(year, month, day);
        const normalDateStr = normalDate.toISOString().split('T')[0];
        console.log(`Normal: new Date(${year}, ${month}, ${day}) -> ${normalDateStr}`);
        
        // Scenario 2: What if the Date constructor creates a date that
        // when converted to UTC shifts to the next day?
        
        // This would happen if user is in a timezone ahead of UTC
        // and the date creation happens to cross midnight boundary
        
        const testDate = new Date(year, month, day);
        
        // Let's see what happens with DST or timezone edge cases
        console.log(`  Date object: ${testDate.toString()}`);
        console.log(`  UTC string: ${testDate.toUTCString()}`);
        console.log(`  ISO string: ${testDate.toISOString()}`);
        console.log(`  Final dateStr: ${normalDateStr}`);
        
        // Check if this would show vacation
        const backendDates = ['2025-08-05', '2025-08-06', '2025-08-07'];
        const wouldShowVacation = backendDates.includes(normalDateStr);
        console.log(`  Shows vacation: ${wouldShowVacation ? '🔴 YES' : '⚪ NO'}`);
        console.log('');
    }
}

console.log("=== ROOT CAUSE DISCOVERY ===");
console.log("Testing potential Date constructor edge case...\n");

// The real issue might be in how JavaScript handles Date construction
// Let's test the exact frontend logic step by step

function simulateFrontendLogic() {
    const year = 2025;
    const month = 7; // August (0-based)
    
    // Backend data (what the API returns)
    const calendarData = [
        { date: '2025-08-05', status: 'approved_pending', leave_type: 'Vacaciones' },
        { date: '2025-08-06', status: 'approved_pending', leave_type: 'Vacaciones' },
        { date: '2025-08-07', status: 'approved_pending', leave_type: 'Vacaciones' }
    ];
    
    console.log("Backend API returns:");
    calendarData.forEach(item => console.log(`  ${item.date}: ${item.status}`));
    
    console.log("\nFrontend calendar generation:");
    
    // Generate calendar days for August 2025
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    for (let day = 5; day <= 8; day++) {
        // This is the exact frontend logic from leave-balance.tsx
        const date = new Date(year, month, day);
        const dateStr = date.toISOString().split('T')[0];
        const leaveData = calendarData.find(cal => cal.date === dateStr);
        
        console.log(`Day ${day}:`);
        console.log(`  Generated dateStr: ${dateStr}`);
        console.log(`  Found leave data: ${leaveData ? 'YES' : 'NO'}`);
        console.log(`  Status: ${leaveData?.status || 'none'}`);
        console.log('');
    }
}

testTimezoneOffset();
console.log("\n" + "=".repeat(50) + "\n");
simulateFrontendLogic();

console.log("=== HYPOTHESIS ===");
console.log("If the output above shows vacation on days 5, 6, 7 correctly,");
console.log("then the +1 day offset issue might be caused by:");
console.log("1. Different user timezone causing Date constructor issues");
console.log("2. Server-side timezone handling difference");
console.log("3. DST (Daylight Saving Time) transitions");
console.log("4. Browser-specific Date handling quirks");

// Test edge case - what if user is in a timezone where midnight 
// local time creates a UTC date in the next day?
console.log("\n=== EDGE CASE TEST ===");

// Simulate user in UTC+14 (Pacific/Islands) creating dates
// This would be an extreme case where local midnight is UTC+14 hours

const extremeDate = new Date(2025, 7, 5); // August 5 at midnight local
console.log(`User in UTC+14 creates August 5:`);
console.log(`  Local time: ${extremeDate.toString()}`);
console.log(`  UTC time: ${extremeDate.toUTCString()}`);
console.log(`  ISO string: ${extremeDate.toISOString()}`);
console.log(`  Date part: ${extremeDate.toISOString().split('T')[0]}`);

// The key insight: even in extreme timezones, creating a date with 
// new Date(year, month, day) at midnight local time should not
// shift the date when extracting just the date part from ISO string