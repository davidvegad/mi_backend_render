// JavaScript analysis of the timezone issue
// This simulates the frontend date generation logic

console.log("🧪 Analyzing potential timezone issue in calendar date generation...\n");

// Backend timezone: America/Lima (UTC-5)
// Let's simulate the issue for August 2025

const year = 2025;
const month = 7; // August (0-based in JavaScript)

console.log("=== BACKEND SIMULATION ===");
// Backend generates dates as ISO strings (YYYY-MM-DD format)
// For a leave request from August 5-7, backend would generate:
const backendDates = ['2025-08-05', '2025-08-06', '2025-08-07'];
console.log("Backend calendar API returns dates:", backendDates);

console.log("\n=== FRONTEND SIMULATION ===");
console.log("Frontend calendar generation for August 2025...\n");

// Simulate the frontend logic from leave-balance.tsx lines 82-85
const daysInMonth = new Date(year, month + 1, 0).getDate(); // 31 days in August

for (let day = 5; day <= 8; day++) { // Focus on days 5-8
    // This is the problematic line from frontend:
    const date = new Date(year, month, day);
    const dateStr = date.toISOString().split('T')[0];
    
    console.log(`Day ${day}:`);
    console.log(`  new Date(${year}, ${month}, ${day}) creates:`, date.toString());
    console.log(`  date.toISOString() returns:`, date.toISOString());
    console.log(`  dateStr becomes:`, dateStr);
    
    // Check if this matches backend data
    const matchesBackend = backendDates.includes(dateStr);
    console.log(`  Matches backend data: ${matchesBackend ? '✅' : '❌'}`);
    
    if (matchesBackend) {
        console.log(`  🔴 This day would show as having leave`);
    }
    console.log('');
}

console.log("=== TIMEZONE ANALYSIS ===");
console.log("Potential issues:");
console.log("1. JavaScript Date constructor creates dates in local timezone");
console.log("2. toISOString() converts to UTC");
console.log("3. If user is in different timezone than backend, dates might shift");

// Test different timezone scenarios
console.log("\n=== TIMEZONE SCENARIO TESTING ===");

// Let's assume user is in a timezone where midnight local time 
// would be previous day in UTC (like Asia/Tokyo = UTC+9)

// Simulate what happens at different times of day
const testTimes = [
    { hour: 0, minute: 0, desc: "midnight local time" },
    { hour: 12, minute: 0, desc: "noon local time" },
    { hour: 23, minute: 59, desc: "almost midnight local time" }
];

testTimes.forEach(time => {
    console.log(`\nIf user creates calendar at ${time.desc}:`);
    const date = new Date(year, month, 5, time.hour, time.minute); // August 5th
    const dateStr = date.toISOString().split('T')[0];
    console.log(`  new Date(2025, 7, 5, ${time.hour}, ${time.minute}) -> ${dateStr}`);
});

console.log("\n=== ROOT CAUSE HYPOTHESIS ===");
console.log("The issue is likely NOT a timezone problem because:");
console.log("1. Backend stores dates as DATE fields (no time component)");
console.log("2. Backend uses .isoformat() on date objects (YYYY-MM-DD)");
console.log("3. Frontend date.toISOString().split('T')[0] should produce same format");
console.log("4. The Date constructor new Date(year, month, day) creates midnight local time");
console.log("5. Even with timezone conversion, the date part should remain the same");

console.log("\n=== LOOKING FOR OTHER CAUSES ===");
console.log("Alternative hypotheses:");
console.log("1. Off-by-one error in date iteration logic");
console.log("2. Incorrect date range calculation in backend");
console.log("3. Frontend calendar day numbering issue");
console.log("4. Data synchronization timing issue");