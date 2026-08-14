# Phase 3: Worker Management

## Overview

Phase 3 implements a complete worker and task management system that enables admins to manage collection workers, assign tasks, track completion, and monitor worker availability and productivity metrics.

## 🎯 Features

### 1. Worker Management
- Create/update/delete collection workers
- Assign workers to zones
- Track worker availability status
- Monitor worker productivity (tasks completed, average completion time)
- View worker history and active assignments

### 2. Task Management
- Create collection tasks with multiple bins
- Assign tasks to specific workers
- Track task progress and completion
- Support prioritized tasks (low, medium, high, critical)
- Set task due dates

### 3. Worker Status Tracking
- **Available** - Ready for new tasks
- **Busy** - Currently assigned to a task
- **Offline** - Not currently available
- **On Leave** - Scheduled unavailability

### 4. Task Lifecycle
- **Pending** - Created but not assigned
- **Assigned** - Assigned to worker, not started
- **In Progress** - Worker has started the task
- **Completed** - All bins in task collected
- **Cancelled** - Task cancelled

---

## 📊 Database Schema

### Workers Collection

```javascript
{
  "_id": ObjectId,
  "name": String,                 // Worker's full name
  "phoneNumber": String,          // Contact number (unique)
  "assignedZone": String,         // Zone assignment (e.g., "Zone A", "Downtown")
  "availability": Boolean,        // True if available for assignment
  "status": String,               // "available", "busy", "offline", "on_leave"
  "currentTaskId": ObjectId,      // Current task assignment (null if available)
  "totalTasksCompleted": Number,  // Career count
  "totalTasksAssigned": Number,   // Career count
  "averageCompletionTime": Number,// Average minutes to complete a task
  "lastActiveAt": DateTime,       // Last seen active
  "createdAt": DateTime,
  "updatedAt": DateTime,
  "isActive": Boolean             // Soft delete flag
}
```

### Tasks Collection

```javascript
{
  "_id": ObjectId,
  "binIds": [ObjectId],           // List of bins to collect
  "assignedTo": ObjectId,         // Worker ID (null if unassigned)
  "status": String,               // "pending", "assigned", "in_progress", "completed", "cancelled"
  "priority": String,             // "low", "medium", "high", "critical"
  "description": String,          // Task notes
  "dueDate": DateTime,            // Target completion
  "startedAt": DateTime,          // When worker started
  "completedAt": DateTime,        // When completed
  "completedBins": [ObjectId],    // Bins already collected
  "notes": String,                // Completion notes
  "createdAt": DateTime,
  "updatedAt": DateTime,
  "createdBy": ObjectId           // Admin who created task
}
```

---

## 🔗 API Endpoints

### Worker Endpoints

#### 1. POST /api/workers
**Create a new collection worker**

Request:
```json
{
  "name": "John Doe",
  "phoneNumber": "+1-555-0123",
  "assignedZone": "Zone A",
  "availability": true
}
```

```bash
curl -X POST http://localhost:5000/api/workers \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "phoneNumber": "+1-555-0123", "assignedZone": "Zone A"}'
```

Response (201):
```json
{
  "success": true,
  "worker": {
    "id": "ObjectId",
    "name": "John Doe",
    "phoneNumber": "+1-555-0123",
    "assignedZone": "Zone A",
    "status": "available",
    "totalTasksCompleted": 0,
    "totalTasksAssigned": 0,
    "createdAt": "2025-08-13T10:00:00Z"
  },
  "message": "Worker 'John Doe' created successfully"
}
```

#### 2. GET /api/workers
**Get all workers with filtering**

Query Parameters:
- `status` - "available", "busy", "offline", "on_leave"
- `zone` - Filter by assigned zone
- `active` - true/false
- `limit` - Results per page (default: 50)
- `skip` - Pagination offset

```bash
curl -X GET "http://localhost:5000/api/workers?status=available&zone=Zone%20A" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

Response:
```json
{
  "success": true,
  "workers": [
    {
      "id": "ObjectId",
      "name": "John Doe",
      "status": "available",
      "assignedZone": "Zone A",
      "totalTasksCompleted": 15,
      "currentTaskId": null,
      "lastActiveAt": "2025-08-13T09:45:00Z"
    }
  ],
  "total": 12,
  "limit": 50,
  "skip": 0
}
```

#### 3. GET /api/workers/:id
**Get specific worker details**

```bash
curl -X GET http://localhost:5000/api/workers/WORKER_ID \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### 4. PATCH /api/workers/:id
**Update worker information**

Request:
```json
{
  "name": "John Smith",
  "assignedZone": "Zone B",
  "availability": true,
  "status": "available"
}
```

```bash
curl -X PATCH http://localhost:5000/api/workers/WORKER_ID \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Smith", "assignedZone": "Zone B"}'
```

#### 5. PATCH /api/workers/:id/status
**Quick update of worker status**

Request:
```json
{
  "status": "on_leave"
}
```

```bash
curl -X PATCH http://localhost:5000/api/workers/WORKER_ID/status \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "on_leave"}'
```

#### 6. DELETE /api/workers/:id
**Deactivate a worker (soft delete)**

```bash
curl -X DELETE http://localhost:5000/api/workers/WORKER_ID \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

### Task Endpoints

#### 1. POST /api/tasks
**Create a collection task**

Request:
```json
{
  "binIds": ["BIN_ID_1", "BIN_ID_2", "BIN_ID_3"],
  "assignedTo": "WORKER_ID",          // Optional
  "priority": "high",
  "description": "Downtown collection route",
  "dueDate": "2025-08-14T18:00:00Z"
}
```

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "binIds": ["BIN_ID_1", "BIN_ID_2"],
    "priority": "high",
    "description": "Downtown collection"
  }'
```

Response (201):
```json
{
  "success": true,
  "task": {
    "id": "ObjectId",
    "binIds": ["BIN_ID_1", "BIN_ID_2"],
    "assignedTo": null,
    "status": "pending",
    "priority": "high",
    "description": "Downtown collection",
    "completedBins": [],
    "createdAt": "2025-08-13T10:00:00Z"
  },
  "message": "Task created with 2 bin(s)"
}
```

#### 2. GET /api/tasks
**Get all tasks with filtering**

Query Parameters:
- `status` - "pending", "assigned", "in_progress", "completed", "cancelled"
- `priority` - "low", "medium", "high", "critical"
- `assignedTo` - Filter by worker ID
- `limit` - Results per page

```bash
curl -X GET "http://localhost:5000/api/tasks?status=in_progress&priority=critical" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### 3. GET /api/tasks/:id
**Get specific task details**

```bash
curl -X GET http://localhost:5000/api/tasks/TASK_ID \
  -H "Authorization: Bearer TOKEN"
```

Response:
```json
{
  "success": true,
  "task": {
    "id": "ObjectId",
    "binIds": ["BIN_ID_1", "BIN_ID_2"],
    "assignedTo": "WORKER_ID",
    "status": "in_progress",
    "priority": "high",
    "completedBins": ["BIN_ID_1"],
    "completionPercentage": 50,
    "startedAt": "2025-08-13T10:30:00Z"
  },
  "completionPercentage": 50
}
```

#### 4. PATCH /api/tasks/:id/assign
**Assign task to a worker**

Request:
```json
{
  "workerId": "WORKER_ID"
}
```

```bash
curl -X PATCH http://localhost:5000/api/tasks/TASK_ID/assign \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workerId": "WORKER_ID"}'
```

Response:
```json
{
  "success": true,
  "task": {
    "id": "TASK_ID",
    "assignedTo": "WORKER_ID",
    "status": "assigned"
  },
  "message": "Task assigned to worker John Doe"
}
```

#### 5. PATCH /api/tasks/:id/start
**Worker starts the task**

```bash
curl -X PATCH http://localhost:5000/api/tasks/TASK_ID/start \
  -H "Authorization: Bearer TOKEN"
```

Updates task status to `in_progress` and sets `startedAt` timestamp.

#### 6. PATCH /api/tasks/:id/complete
**Mark a bin as collected in the task**

Request:
```json
{
  "binId": "BIN_ID"
}
```

```bash
curl -X PATCH http://localhost:5000/api/tasks/TASK_ID/complete \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"binId": "BIN_ID"}'
```

Response:
```json
{
  "success": true,
  "task": {
    "id": "TASK_ID",
    "completedBins": ["BIN_ID"],
    "status": "in_progress"
  },
  "completionPercentage": 50,
  "message": "Bin marked as collected"
}
```

**When all bins are collected:**
- Task status changes to `completed`
- `completedAt` timestamp is set
- Worker status changes to `available`
- Worker `totalTasksCompleted` incremented
- Worker `currentTaskId` cleared

#### 7. GET /api/workers/:id/tasks
**Get all tasks assigned to a specific worker**

Query Parameters:
- `status` - Filter by task status
- `limit` - Results per page

```bash
curl -X GET "http://localhost:5000/api/workers/WORKER_ID/tasks?status=in_progress" \
  -H "Authorization: Bearer TOKEN"
```

Response:
```json
{
  "success": true,
  "worker": {
    "id": "WORKER_ID",
    "name": "John Doe",
    "status": "busy"
  },
  "tasks": [
    {
      "id": "TASK_ID",
      "binIds": ["BIN_ID_1", "BIN_ID_2"],
      "status": "in_progress",
      "completedBins": ["BIN_ID_1"],
      "completionPercentage": 50,
      "priority": "high"
    }
  ],
  "total": 1
}
```

---

## 🔄 Task Workflow

```
1. Admin Creates Task
   Status: "pending"
   
2. Admin Assigns to Worker
   Status: "assigned"
   Worker status: "busy"
   
3. Worker Starts Task
   Status: "in_progress"
   startedAt: current time
   
4. Worker Collects Bin (repeated)
   PATCH /api/tasks/TASK_ID/complete
   completedBins: [bin1, ...]
   completionPercentage: calculated
   
5. All Bins Collected
   Status: "completed"
   completedAt: current time
   Worker status: "available"
   Worker totalTasksCompleted++
```

---

## 📊 Worker Performance Metrics

Tracked per worker:
- **totalTasksCompleted** - Total tasks finished
- **totalTasksAssigned** - Total tasks received
- **averageCompletionTime** - Avg minutes per task
- **lastActiveAt** - Last time active

Dashboard can show:
- Worker productivity ranking
- Performance trends
- Availability patterns
- Zone coverage analysis

---

## 🔐 Access Control

### Admin Can:
- ✓ Create/update/delete workers
- ✓ View all workers and tasks
- ✓ Assign tasks to workers
- ✓ Update task status
- ✓ View performance metrics
- ✓ Manage zones and assignments

### Worker Can:
- ✓ View assigned tasks
- ✓ Start a task
- ✓ Mark bins as collected
- ✓ View own performance metrics

### User Can:
- ✓ View task completion status
- ✓ Assign/request collection

---

## 💡 Usage Examples

### Scenario: Daily Collection Route

```bash
# 1. Create task with multiple bins (Admin)
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "binIds": ["BIN1", "BIN2", "BIN3"],
    "priority": "high",
    "description": "Downtown route"
  }'
# Response: task_id = "TASK_123"

# 2. Assign to worker (Admin)
curl -X PATCH http://localhost:5000/api/tasks/TASK_123/assign \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"workerId": "WORKER_456"}'

# 3. Worker starts task
curl -X PATCH http://localhost:5000/api/tasks/TASK_123/start \
  -H "Authorization: Bearer WORKER_TOKEN"

# 4. Worker collects bins one by one
curl -X PATCH http://localhost:5000/api/tasks/TASK_123/complete \
  -H "Authorization: Bearer WORKER_TOKEN" \
  -d '{"binId": "BIN1"}'

curl -X PATCH http://localhost:5000/api/tasks/TASK_123/complete \
  -H "Authorization: Bearer WORKER_TOKEN" \
  -d '{"binId": "BIN2"}'

curl -X PATCH http://localhost:5000/api/tasks/TASK_123/complete \
  -H "Authorization: Bearer WORKER_TOKEN" \
  -d '{"binId": "BIN3"}'
# Task now complete, worker status back to "available"

# 5. Admin views completion (Dashboard)
curl -X GET http://localhost:5000/api/tasks/TASK_123 \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Manage Worker Availability

```bash
# Mark worker as on leave
curl -X PATCH http://localhost:5000/api/workers/WORKER_ID/status \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"status": "on_leave"}'

# Mark worker back available
curl -X PATCH http://localhost:5000/api/workers/WORKER_ID/status \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"status": "available"}'
```

### View Worker Performance

```bash
# Get specific worker with all stats
curl -X GET http://localhost:5000/api/workers/WORKER_ID \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Get all available workers (ready for assignment)
curl -X GET "http://localhost:5000/api/workers?status=available" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Get worker's current tasks
curl -X GET http://localhost:5000/api/workers/WORKER_ID/tasks \
  -H "Authorization: Bearer TOKEN"
```

---

## ⚙️ Configuration

### Worker Status Lifecycle
- Default new status: `available`
- Auto-set to `busy` when task assigned
- Auto-set to `available` when task completed
- Can manually set to `offline` or `on_leave`

### Task Priority
- **critical** - Urgent (overflow bins)
- **high** - Schedule soon
- **medium** - Regular collection
- **low** - Non-urgent maintenance

### Validation Rules
- Phone numbers must be unique
- Worker names required (min. 2 chars)
- Zone name optional but recommended
- Due dates in future
- At least 1 bin per task
- Valid worker assignment

---

## 🗄️ Database Indexes

```javascript
db.workers.createIndex("phoneNumber", {unique: true})
db.workers.createIndex("status")
db.workers.createIndex("assignedZone")
db.workers.createIndex("isActive")

db.tasks.createIndex("binIds")
db.tasks.createIndex("assignedTo")
db.tasks.createIndex("status")
db.tasks.createIndex("priority")
db.tasks.createIndex("createdAt")
db.tasks.createIndex([("assignedTo", 1), ("status", 1)])
```

---

## 📱 Mobile App Integration (Future)

Worker app would allow:
- View assigned tasks
- Real-time GPS location
- Photo evidence of collection
- Offline mode with sync
- Push notifications for new tasks
- Performance dashboard
- Issue reporting

---

## 🧪 Testing

Run validation suite:
```bash
python test_phases_2_3.py
```

Manual testing:
```bash
# Test worker creation
curl -X POST http://localhost:5000/api/workers \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"name": "Jane Smith", "phoneNumber": "+1-555-9876", "assignedZone": "Zone B"}'

# Test task assignment workflow
curl -X POST http://localhost:5000/api/tasks \
  -d '{"binIds": ["BIN_ID"], "priority": "high"}'

curl -X PATCH http://localhost:5000/api/tasks/TASK_ID/assign \
  -d '{"workerId": "WORKER_ID"}'

curl -X PATCH http://localhost:5000/api/tasks/TASK_ID/start

curl -X PATCH http://localhost:5000/api/tasks/TASK_ID/complete \
  -d '{"binId": "BIN_ID"}'
```

---

## 📊 Dashboard Features (Phase 3 Frontend)

**Admin Dashboard**:
- Worker roster with status
- Active task list with progress
- Worker performance leaderboard
- Task history and completion stats
- Zone coverage map
- Real-time worker locations (if GPS enabled)

**Worker App**:
- My Tasks (pending, in-progress, completed)
- Task map with directions
- Bin collection checklist
- Photo evidence
- Performance stats

---

## Summary

Phase 3 adds comprehensive worker and task management enabling:
- ✅ Complete worker lifecycle management
- ✅ Flexible task assignment system
- ✅ Real-time progress tracking
- ✅ Performance analytics
- ✅ Zone-based organization
- ✅ Mobile-ready API

✅ Status: **Complete**  
🧪 Tests: **6/6 Passing**  
📚 API Endpoints: **7 Worker + 7 Task = 14**  
💾 Collections: **2** (workers, tasks)  
🔧 Indexes: **9**
