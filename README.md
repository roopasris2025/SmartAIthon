CLEANPULSE – Smart Public Waste Monitoring & Overflow Prevention System
1. Project Overview

CLEANPULSE is a smart public waste monitoring and collection management system designed to prevent overflowing waste bins in roadside areas, public streets, markets, bus stands, residential areas and other municipal/public locations.

Traditional waste collection often follows a fixed schedule, such as once every few days or once a week. However, waste generation is not predictable. Some bins may remain partially empty while other bins become completely full before the next scheduled collection. When overflowing bins are not attended to quickly, waste can spill onto roads, create unpleasant conditions, attract dogs and other animals, and spread through wind and rain.

CLEANPULSE changes this approach from fixed-schedule collection to condition-based and priority-based collection.

The system monitors public bins using an ultrasonic fill-level sensor connected to an ESP32. The collected data is sent to the backend, stored historically, analyzed for filling trends and used to predict possible overflow. Administrators and operators can view the situation through a centralized dashboard and map, identify high-risk bins, prioritize collection and communicate with workers.

Workers do not need to have smartphones. For workers using basic phones, the system supports a voice-call-based alert workflow, allowing urgent collection instructions to reach them through a normal telephone call.

2. Problem Statement

Public waste bins are often emptied according to fixed schedules rather than their actual fill condition.

For example:

Collection schedule:
Day 1 → Collection
Day 4 → Collection

But waste generation may look like:

Day 1 → 20%
Day 2 → 55%
Day 3 → 92%
Day 4 → Overflow

The collection team may only arrive on Day 4, by which time the waste may already have:

Overflowed from the bin
Spread onto the roadside
Been scattered by dogs or other animals
Been affected by rain and wind
Created smell and unhygienic conditions
Increased cleaning effort
Required unnecessary emergency intervention

CLEANPULSE addresses this problem by continuously monitoring bin conditions and identifying which bin needs attention first.

3. Main Objective

The main objective of CLEANPULSE is:

To prevent public waste-bin overflow by monitoring bin conditions, predicting overflow, prioritizing collection and intelligently communicating collection requirements to existing sanitation workers.

The system does not replace sanitation workers.

Instead, it helps existing workers and municipal authorities know:

Which bin is filling quickly
Which bin is already critical
Which bin is likely to overflow soon
Which bin should be collected first
Whether the sensor is functioning correctly
Which worker should handle the collection
Whether the worker received the collection instruction
Whether the collection was completed
4. Key Features
4.1 Real-Time Bin Monitoring

Each IoT-enabled bin can periodically provide:

Bin ID
Distance between sensor and waste
Fill percentage
Sensor status
Last reading time
Device/ESP32 status
Collection status

Example:

BIN-014
Location: Market Road
Fill Level: 87%
Filling Rate: +6%/hour
Risk: HIGH
Predicted Overflow: 4 hours
Sensor: ONLINE
Collection: AWAITING
5. IoT-Based Fill-Level Monitoring

The hardware architecture uses:

JSN-SR04T Waterproof Ultrasonic Sensor
                ↓
              ESP32
                ↓
             Wi-Fi
                ↓
          Flask Backend
                ↓
             MongoDB
                ↓
        CLEANPULSE Dashboard

The ultrasonic sensor measures the distance between the sensor and the waste surface.

If the bin is mostly empty:

Sensor
  ↓
Large distance
  ↓
Low fill %

If the bin is nearly full:

Sensor
  ↓
Small distance
  ↓
High fill %
6. Fill-Level Calculation

The system can calculate the approximate fill percentage using the calibrated bin height.

Conceptually:

Fill % = ((Bin Height - Measured Distance) / Bin Height) × 100

For example:

Bin Height = 100 cm
Measured Distance = 20 cm

Fill % = ((100 - 20) / 100) × 100
       = 80%

The actual implementation should also apply minimum/maximum calibration and validation to avoid invalid readings.

7. Sensor Protection

Since the system is designed for outdoor public environments, the sensor must be protected from environmental conditions.

The design includes:

Waterproof ultrasonic sensor
Protective sensor hood
Stable mounting
Protected wiring
Cable routing
Waterproof electronics enclosure
Replaceable sensor design
3D-printed mounting bracket

The sensor should be mounted underneath or near the bin lid so that it can measure the waste while being protected from direct rain exposure.

For the 3D mount, outdoor-suitable materials such as PETG or ASA can be considered.

The project should not claim an exact sensor lifespan without manufacturer/environmental testing. Instead, durability is improved through protection, proper mounting, sealed electronics and periodic maintenance.

8. ESP32 Role

The ESP32 acts as the IoT controller/device.

Its responsibilities include:

Connecting to Wi-Fi
Reading the ultrasonic sensor
Calculating/obtaining distance
Calculating fill percentage
Identifying the bin
Checking sensor status
Sending telemetry to the backend
Retrying communication when necessary
Reporting errors
Periodically sending readings

Example telemetry:

{
  "bin_id": "BIN-001",
  "distance_cm": 15.2,
  "fill_level": 84,
  "sensor_status": "online",
  "timestamp": "2026-08-29T10:30:00",
  "firmware_version": "1.0.0"
}
9. Simulation Mode

The physical sensor is not required during the initial software-development stage.

CLEANPULSE therefore supports:

SIMULATION MODE

This allows developers to generate realistic sensor readings.

Example:

20%
40%
60%
75%
85%
95%
100%

The simulated data follows the same backend flow as real sensor data.

Simulation
    ↓
Telemetry API
    ↓
MongoDB
    ↓
Prediction
    ↓
Risk
    ↓
Alert
    ↓
Map
    ↓
Collection

Later, the input source can be changed to:

JSN-SR04T
    ↓
ESP32
    ↓
Telemetry API

without redesigning the entire software system.

10. Sensor Health Monitoring

CLEANPULSE does not assume that every sensor reading is correct.

The system monitors:

Sensor online/offline status
Last communication time
Last reading
Invalid readings
Sensor errors
Communication failures
Abnormal readings
Calibration status

Example:

BIN-005
Sensor: OFFLINE
Last Reading: 2 hours ago
Status: MAINTENANCE REQUIRED

The system should never interpret missing sensor data as:

Fill = 0%

Instead:

No data
↓
Sensor Offline
↓
Maintenance Required
11. Abnormal Reading Detection

A sensor may occasionally produce an incorrect reading.

Example:

40%
43%
45%
98%
46%

The sudden 98% reading may be suspicious.

Instead of immediately triggering an overflow alert, the system can:

Detect abnormal reading
        ↓
Validate against previous readings
        ↓
Mark as suspicious/anomaly
        ↓
Check subsequent readings
        ↓
Confirm or reject

This reduces false alerts.

12. Sensor Calibration

Each bin may have different dimensions.

Therefore, calibration information can include:

Bin height
Minimum sensor distance
Maximum sensor distance
Current distance
Fill percentage
Sensor ID
Calibration date
Calibration status

Administrators/operators can use the calibration page to verify sensor readings.

13. Overflow Prediction

CLEANPULSE goes beyond simply checking:

"Is the bin above 80%?"

The system also considers how quickly the bin is filling.

Example:

Bin A
Current fill = 76%
Filling rate = +8%/hour

Possible result:

High risk
Overflow expected soon
Bin B
Current fill = 90%
Filling rate = +1%/day

Possible result:

Lower immediate priority

Therefore, current fill percentage alone does not determine collection priority.

14. Prediction Inputs

The prediction/risk system can consider:

Current fill percentage
Filling rate
Historical filling pattern
Predicted critical time
Historical overflow frequency
Sensor confidence
Recent collection history

If sufficient historical data is unavailable, the system can use a transparent filling-rate-based fallback and display:

Limited historical data

As more data is collected, prediction quality can be improved.

15. Risk Classification

Example configurable risk levels:

0–40%    → LOW
41–70%   → MEDIUM
71–85%   → HIGH
86–100%  → CRITICAL

However, the final collection priority can also consider the filling speed and predicted overflow time.

16. Collection Priority

Instead of sorting bins only by fill percentage, CLEANPULSE creates a priority based on operational risk.

Example:

BIN-001
76% full
Rapid filling
Overflow predicted in 3 hours
→ PRIORITY 1
BIN-002
90% full
Slow filling
Overflow predicted in 2 days
→ Lower immediate priority

This allows collection teams to focus on bins that are most likely to create a problem soon.

17. Google Maps Integration

The system provides a public waste monitoring map.

The map displays:

🟢 Normal
🟡 Moderate
🟠 High
🔴 Critical
⚫ Offline

Selecting a bin shows:

Bin ID
Location
Address
Fill level
Risk
Filling rate
Predicted overflow
Sensor status
Last reading
Collection status

The system can use Google Maps when configured and maintain a Leaflet-based fallback where appropriate.

18. Admin Dashboard

The main dashboard acts as a municipal/public-waste command center.

Important KPIs include:

Total Monitored Bins
Critical Bins
High-Risk Bins
Predicted Overflow Bins
Awaiting Collection
Sensors Offline
Active Collection Tasks
Completed Collections

The dashboard can also contain:

Waste Risk Pulse

Shows the overall operational risk.

Overflow Countdown

Shows the most urgent predicted overflow.

Collection Priority Queue

Shows which bins should be collected first.

Sensor Health

Shows online/offline/faulty sensors.

Prediction Confidence

Shows how reliable the current prediction is.

19. Alert Center

The system generates alerts for:

Critical fill level
Predicted overflow
Sensor offline
Sensor fault
Abnormal reading
Worker not responding
Collection failed
Maintenance required

Example:

CRITICAL ALERT

BIN-014
Market Road

Fill: 94%
Risk: CRITICAL
Predicted Overflow: 2h 20m

Collection Priority: P1
Worker: Assigned

Critical alerts remain visible until acknowledged or resolved.

20. Worker Management

The system maintains worker information such as:

Worker name
Phone number
Availability
Assigned area/zone
Active tasks
Completed collections
Response status

Workers who have smartphones can use the worker interface.

However, a smartphone is not mandatory.

21. Basic Phone Worker Support

One of the important real-world features of CLEANPULSE is support for workers who may use ordinary mobile phones.

The system does not assume:

Worker → Smartphone → App → Internet

Instead:

Critical Bin
    ↓
System detects priority
    ↓
Worker phone number
    ↓
Voice Call
    ↓
Normal mobile phone

The automated call can communicate:

Bin ID
Location
Fill level
Urgency
Collection priority
22. Voice-Call Workflow

The actual workflow is:

Critical Bin
     ↓
Alert Created
     ↓
Identify Assigned Worker
     ↓
Voice Call
     ↓
Worker Answers?
   /       \
 YES       NO
 ↓          ↓
Task       Retry
Accepted    ↓
 ↓       Still No Answer?
Collection    ↓
 ↓        Escalate
Completed     ↓
           Another Worker/
           Supervisor

Possible call statuses:

NOT_CALLED
CALLING
ANSWERED
NOT_ANSWERED
FAILED
RETRYING
ESCALATED

A real telephony API/service can be connected through backend configuration.

API credentials must be stored in environment variables and must never be exposed in frontend code.

A safe test mode should be available during development to prevent accidental real calls.

23. Collection Workflow

The complete operational workflow is:

Bin Monitoring
      ↓
Fill Level Updated
      ↓
Risk Calculation
      ↓
Overflow Prediction
      ↓
Collection Priority
      ↓
Admin Alert
      ↓
Worker Assignment
      ↓
Voice Call / Notification
      ↓
Worker Acknowledgement
      ↓
Collection
      ↓
Mark Collected
      ↓
Fill Level = 0%
      ↓
Collection History Saved
      ↓
Future Prediction Uses History
24. Collection Statuses

The system can use:

AWAITING_COLLECTION
ASSIGNED
ACKNOWLEDGED
IN_PROGRESS
COLLECTED
FAILED
ESCALATED

If collection is completed:

Fill = 0%
Status = COLLECTED
Last Collection = Current timestamp

The event is stored in collection history.

25. Citizen Reporting

Citizens can report public waste problems.

The feature is:

Report a Public Waste Issue

Possible issue types:

Overflowing bin
Scattered waste
Damaged bin
Illegal dumping
Bad smell/unclean area
Blocked collection point

The citizen can submit:

Description
Photo
Location/GPS
Issue type
Waste type
26. Citizen Report Workflow
Citizen
   ↓
Report Issue
   ↓
Photo + Location + Description
   ↓
Admin/Operator
   ↓
Verify Report
   ↓
Link to Bin / Create Task
   ↓
Assign Worker
   ↓
Collection/Cleaning
   ↓
Resolved

Citizen reporting is particularly useful for bins without IoT sensors.

27. IoT + Non-IoT Bin Strategy

Installing a sensor on every public bin immediately may be expensive.

For example:

500 bins × ₹500
= ₹2,50,000

Therefore, CLEANPULSE supports a scalable approach.

High-risk locations
IoT Sensor
+
Continuous monitoring
Medium-risk locations
Periodic inspection
+
Citizen reports
Low-risk locations
Scheduled inspection

Historical data can identify which locations deserve IoT deployment first.

This makes the system more economically practical.

28. Cost Concept

The core sensing node targets approximately ₹500 when low-cost/local/student component pricing is available.

Example:

Component	Approximate Cost
JSN-SR04T	₹250–₹350
ESP32	₹150–₹250
Core electronics target	Around ₹500

However, ₹500 should not be presented as the complete outdoor deployment cost.

Additional expenses may include:

Waterproof enclosure
Wiring
Power supply/battery
Mounting
Communication
Installation
Maintenance
Replacement

The 3D-printed mount can reduce mounting costs because it can be manufactured using an available 3D printer.

29. Waste Categories

CLEANPULSE can record:

General Municipal Waste
Organic/Wet Waste
Dry/Recyclable Waste
Plastic
Paper
E-Waste
Mixed/Residual Waste

The system itself does not claim to automatically recycle waste.

Instead, it supports proper downstream handling:

Organic
→ Composting

Plastic/Paper
→ Recycling

E-Waste
→ Authorized E-Waste Facility

Residual
→ Municipal Treatment/Disposal
30. Maintenance Management

The maintenance module tracks:

Sensor faults
Sensor replacement
Calibration
Damaged bins
Communication failures
Maintenance status
Service history

Example:

BIN-008

Sensor Status:
FAULTY

Issue:
Invalid ultrasonic readings

Action:
Sensor inspection required

Maintenance:
PENDING
31. User Roles

CLEANPULSE has four main roles.

Admin

Can:

Manage bins
Manage workers
View map
View analytics
Manage alerts
Assign collections
Manage sensors
Manage maintenance
Configure system
Operator

Can:

Monitor bins
View alerts
Verify reports
Manage collection operations
Assign/reassign tasks where permitted
Worker

Can:

View assigned tasks if using the application
Acknowledge tasks
Start collection
Mark collection completed

Workers without smartphones can receive instructions through voice calls.

Citizen

Can:

Report public waste issues
Upload photos
Provide location
Track report status where enabled
32. Authentication

The application provides role-based authentication.

Login
 ↓
Role Detection
 ↓
Admin / Operator / Worker / Citizen
 ↓
Role-Specific Access

Admin accounts should not be freely created through public registration.

Passwords and sensitive credentials must be securely handled.

33. Technology Stack
Frontend
React
JavaScript
Modern responsive UI
Charts
Map integration
REST API communication
Backend
Python
Flask
REST APIs
Authentication
IoT telemetry processing
Prediction/risk logic
Collection management
Voice-call integration
Database
MongoDB

Used for:

Users
Bins
Sensor readings
Alerts
Collections
Worker data
Citizen reports
Maintenance
Historical records
IoT
ESP32
JSN-SR04T waterproof ultrasonic sensor
Wi-Fi
HTTP/REST telemetry
Mapping
Google Maps
Leaflet fallback
AI/Data Analysis
Python
Historical data analysis
Filling-rate calculation
Overflow prediction
Risk analysis
Future integration with ML models
34. System Architecture
                   PUBLIC WASTE BIN
                         │
                         ▼
              JSN-SR04T ULTRASONIC
                         │
                         ▼
                       ESP32
                         │
                       Wi-Fi
                         │
                         ▼
                  Flask REST API
                         │
                         ▼
                     MongoDB
                         │
          ┌──────────────┼───────────────┐
          ▼              ▼               ▼
     Live Monitoring  Prediction     Sensor Health
          │              │               │
          └──────────────┼───────────────┘
                         ▼
                  Risk & Priority
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       Admin Dashboard          Google Maps
             │
             ▼
       Alert Center
             │
             ▼
      Collection Operations
             │
             ▼
      Worker Communication
             │
        ┌────┴─────┐
        ▼          ▼
   App/Portal   Voice Call
        │          │
        └────┬─────┘
             ▼
       Waste Collection
             │
             ▼
        Collection History
             │
             ▼
       Future Prediction
35. Project Phases
Phase 1 – Public Waste Management Foundation

Features:

Remove campus/student functionality
Public bin management
Admin dashboard
Public map
Citizen reporting
Worker management
Collection management
Waste categories
Authentication
Public location data
Phase 2 – IoT Monitoring

Features:

JSN-SR04T
ESP32
Fill-level calculation
Telemetry API
Sensor history
Sensor health
Sensor calibration
Anomaly detection
Offline sensor detection
Simulation Mode
Real Sensor Mode
3D sensor mount
Waterproof protection
Phase 3 – Intelligent Collection

Features:

Historical analysis
Filling-rate analysis
Overflow prediction
Risk scoring
Collection priority
Alerts
Google Maps operations
Worker assignment
Voice-call communication
Retry/escalation
Collection history
Analytics
Maintenance
Waste handling
36. What Makes CLEANPULSE Different?

Basic waste-monitoring systems may provide:

Sensor
 ↓
Fill %
 ↓
Dashboard

CLEANPULSE aims to provide a broader operational workflow:

Sensor
 ↓
Fill Level
 ↓
Sensor Validation
 ↓
Filling Rate
 ↓
Historical Analysis
 ↓
Overflow Prediction
 ↓
Risk
 ↓
Collection Priority
 ↓
Map
 ↓
Worker Communication
 ↓
Voice Call for Basic Phones
 ↓
Escalation if No Response
 ↓
Collection
 ↓
History
 ↓
Future Prediction

The important differentiation is therefore not simply the use of an ultrasonic sensor.

It is the integration of:

low-cost sensing + sensor reliability + prediction + priority-based collection + public reporting + location intelligence + worker communication + basic-phone support + operational history.

37. Why Workers Are Still Important

CLEANPULSE does not attempt to automate physical waste collection.

Instead:

System:
"Which bin needs attention?"

Worker:
"Collects the waste."

System:
"Records and learns from the collection."

This makes the system a decision-support and coordination platform, rather than a replacement for sanitation workers.

38. Security Considerations

The system should:

Use authenticated APIs
Apply role-based authorization
Protect worker phone numbers
Store API credentials in environment variables
Never expose telephony credentials in frontend code
Validate IoT devices
Validate Bin IDs
Reject invalid telemetry
Protect admin operations
Validate uploaded citizen images
Avoid accidental real voice calls during development
39. Error Handling

The system should handle:

Sensor disconnected
Wi-Fi unavailable
Backend unavailable
Database unavailable
Invalid distance
Invalid fill %
Abnormal sensor reading
Unknown Bin ID
Duplicate telemetry
Unauthorized request
Google Maps unavailable
Worker does not answer
Collection failure

Instead of showing a blank screen, the application should show meaningful status information and recovery actions.

40. Example End-to-End Scenario

Suppose:

BIN-014
Market Road

Current reading:

Fill = 72%

After several readings:

72%
76%
81%
86%

The system calculates:

Filling rate = increasing rapidly

Prediction:

Critical level expected soon

Risk:

HIGH

Collection priority:

P1

Admin receives:

⚠ Predicted Overflow

BIN-014
Market Road
86% full
Overflow predicted in 3 hours
Priority: P1

The system contacts the assigned worker:

Voice Call → Worker

Worker answers:

Task acknowledged

Worker collects the waste.

Admin/operator marks:

COLLECTED

System updates:

Fill = 0%
Status = COLLECTED

The event is saved.

Future readings can then be used to improve the filling-rate and prediction logic.

41. Current Development Strategy

The software can be developed before purchasing the physical sensor.

During software development:

Simulation Mode
       ↓
Backend
       ↓
Database
       ↓
Dashboard
       ↓
Prediction
       ↓
Alerts
       ↓
Collection

After purchasing hardware:

JSN-SR04T
       ↓
ESP32
       ↓
Wi-Fi
       ↓
Same Backend
       ↓
Same Database
       ↓
Same Dashboard

Therefore, the lack of physical hardware during the initial development stage does not require rebuilding the software.

42. Future Enhancements

Possible future improvements include:

Multiple sensor types
Solar-powered IoT nodes
LoRaWAN for long-distance communication
Better ML-based time-series prediction
Weather-aware prediction
Route optimization
Vehicle/collection-truck tracking
Automatic collection-route generation
Waste-volume analytics
Municipal reporting
Multi-zone city deployment
Predictive maintenance
Advanced anomaly detection

These should be considered future extensions rather than claiming they are already implemented.

43. Expected Outcome

CLEANPULSE aims to help municipalities and public sanitation teams move from:

Fixed Schedule
       ↓
Wait for Collection Day
       ↓
Overflow
       ↓
Emergency Cleaning

to:

Continuous Monitoring
       ↓
Early Detection
       ↓
Overflow Prediction
       ↓
Risk-Based Priority
       ↓
Worker Notification
       ↓
Timely Collection
       ↓
Cleaner Public Area
44. Conclusion

CLEANPULSE is a public waste intelligence and collection management system designed to reduce overflowing waste in public areas.

The system combines IoT-based monitoring, sensor-health validation, historical analysis, overflow prediction, risk-based collection prioritization, map-based operations, citizen reporting and worker communication.

A major practical consideration is that not every sanitation worker may have a smartphone. Therefore, the system is designed to support voice-call communication through ordinary mobile phones, allowing the technology to adapt to the existing workforce rather than forcing every worker to use a smartphone application.
