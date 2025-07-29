// FINAL TEST: Prove the timezone issue in calendar date generation

console.log("🎯 FINAL TEST: Root cause of +1 day offset issue\n");

// The issue occurs when users are in certain timezones where
// new Date(year, month, day) creates a local midnight that,
// when converted to UTC via toISOString(), can shift to the next day

console.log("=== THE PROBLEM ===");
console.log("In leave-balance.tsx line 83-84:");
console.log("  const date = new Date(year, month, day);");
console.log("  const dateStr = date.toISOString().split('T')[0];");
console.log("");

console.log("=== THE SOLUTION (from timesheet/page.tsx) ===");
console.log("Line 214 uses UTC to prevent timezone issues:");
console.log("  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));");
console.log("");

// Test the EXACT scenario that causes the issue
function testTimezoneShift() {
    console.log("🧪 Testing timezone scenarios that cause +1 day shift...\n");
    
    // Simulate user in different timezone scenarios
    const testCases = [
        { name: "Normal case (Lima timezone)", offset: -5 },
        { name: "Eastern US (UTC-5)", offset: -5 },
        { name: "Pacific US (UTC-8)", offset: -8 },
        { name: "European (UTC+1)", offset: 1 },
        { name: "Asian (UTC+8)", offset: 8 }
    ];
    
    const year = 2025;
    const month = 7; // August (0-based)
    const day = 5;   // August 5th
    
    console.log(`Testing date creation for August ${day}, ${year}:\n`);
    
    // Current behavior (PROBLEMATIC)
    console.log("CURRENT BEHAVIOR (leave-balance.tsx):");
    const currentDate = new Date(year, month, day);
    const currentDateStr = currentDate.toISOString().split('T')[0];
    
    console.log(`  new Date(${year}, ${month}, ${day}) = ${currentDate.toString()}`);
    console.log(`  .toISOString() = ${currentDate.toISOString()}`);
    console.log(`  Final dateStr = ${currentDateStr}`);
    console.log("");
    
    // Fixed behavior (SOLUTION)
    console.log("FIXED BEHAVIOR (should use UTC):");
    const fixedDate = new Date(Date.UTC(year, month, day));
    const fixedDateStr = fixedDate.toISOString().split('T')[0];
    
    console.log(`  new Date(Date.UTC(${year}, ${month}, ${day})) = ${fixedDate.toString()}`);
    console.log(`  .toISOString() = ${fixedDate.toISOString()}`);
    console.log(`  Final dateStr = ${fixedDateStr}`);
    console.log("");
    
    // Check if they differ
    if (currentDateStr !== fixedDateStr) {
        console.log("❌ PROBLEM DETECTED: Date strings differ!");
        console.log(`   Current approach: ${currentDateStr}`);
        console.log(`   Fixed approach:   ${fixedDateStr}`);
        console.log("   This would cause calendar dates to appear on wrong days!");
    } else {
        console.log("✅ No issue detected in this timezone");
    }
    
    return { currentDateStr, fixedDateStr };
}

function simulateOffsetScenario() {
    console.log("\n" + "=".repeat(60));
    console.log("🌍 SIMULATING THE EXACT OFFSET SCENARIO");
    console.log("=".repeat(60));
    
    // The key insight: when a user is in a timezone where local midnight
    // is several hours ahead of UTC, the date can shift when converted to UTC
    
    console.log("Scenario: User approves vacation for August 5-7");
    console.log("Backend stores: 2025-08-05, 2025-08-06, 2025-08-07");
    console.log("");
    
    // Frontend tries to match these dates
    const backendDates = ['2025-08-05', '2025-08-06', '2025-08-07'];
    const year = 2025;
    const month = 7; // August
    
    console.log("Frontend calendar generation (CURRENT - PROBLEMATIC):");
    
    for (let day = 5; day <= 8; day++) {
        const date = new Date(year, month, day);
        const dateStr = date.toISOString().split('T')[0];
        const hasLeave = backendDates.includes(dateStr);
        
        console.log(`  Day ${day}: new Date(${year}, ${month}, ${day})`);
        console.log(`    -> ${date.toString()}`);
        console.log(`    -> UTC: ${date.toISOString()}`);
        console.log(`    -> dateStr: ${dateStr}`);
        console.log(`    -> Matches backend: ${hasLeave ? '✅' : '❌'}`);
        
        if (hasLeave) {
            console.log(`    -> 🔴 Shows vacation on calendar day ${day}`);
        }
        console.log("");
    }
    
    console.log("WHAT USER SEES:");
    console.log("If dates match backend exactly: vacation shows on correct days 5-7");
    console.log("If there's timezone shift: vacation might show on days 6-8 (+1 offset)");
    
    console.log("\nFrontend calendar generation (FIXED - SOLUTION):");
    
    for (let day = 5; day <= 8; day++) {
        const date = new Date(Date.UTC(year, month, day));
        const dateStr = date.toISOString().split('T')[0];
        const hasLeave = backendDates.includes(dateStr);
        
        console.log(`  Day ${day}: new Date(Date.UTC(${year}, ${month}, ${day}))`);
        console.log(`    -> ${date.toString()}`);
        console.log(`    -> dateStr: ${dateStr}`);
        console.log(`    -> Matches backend: ${hasLeave ? '✅' : '❌'}`);
        console.log("");
    }
}

// Run the tests
const result = testTimezoneShift();
simulateOffsetScenario();

console.log("\n" + "=".repeat(60));
console.log("🎯 ROOT CAUSE IDENTIFIED");
console.log("=".repeat(60));

console.log("PROBLEM:");
console.log("- leave-balance.tsx uses new Date(year, month, day)");
console.log("- This creates dates in user's local timezone");
console.log("- toISOString() converts to UTC, which can shift the date");
console.log("- Calendar displays vacation on wrong days (+1 offset)");
console.log("");

console.log("SOLUTION:");
console.log("- Use new Date(Date.UTC(year, month, day)) instead");
console.log("- This creates dates directly in UTC");
console.log("- No timezone conversion issues");
console.log("- Calendar displays vacation on correct days");
console.log("");

console.log("EVIDENCE:");
console.log("- timesheet/page.tsx already uses this pattern (line 214)");
console.log("- Same approach should be applied to leave-balance.tsx");

console.log("\n📝 RECOMMENDED FIX:");
console.log("In leave-balance.tsx, line 83, change:");
console.log("  FROM: const date = new Date(year, month, day);");
console.log("  TO:   const date = new Date(Date.UTC(year, month, day));")