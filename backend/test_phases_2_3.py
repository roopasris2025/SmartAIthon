"""
backend/test_phases_2_3.py  –  Validation tests for Phase 2 (Alerts) and Phase 3 (Workers/Tasks)
Run: python test_phases_2_3.py
"""
import sys
import traceback

def test_imports():
    """Test that all new modules import successfully."""
    try:
        print("✓ Testing imports...")
        from app.models.alert_model import (
            create_alert_schema, serialize_alert, get_alert_severity,
            ALERT_TYPE_OVERFLOW, ALERT_TYPE_FULL, ALERT_TYPE_LOW_BATTERY,
        )
        from app.models.worker_model import (
            create_worker_schema, serialize_worker, create_task_schema,
            serialize_task, get_task_completion_percentage,
        )
        from app.controllers.alert_controller import check_and_create_alert
        from app.controllers.worker_controller import (
            create_worker, get_workers, update_worker_status,
        )
        from app.controllers.task_controller import (
            create_task, assign_task, start_task, complete_task_bin,
        )
        from app.routes.alert_routes import alert_bp
        from app.routes.worker_routes import worker_bp
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_alert_models():
    """Test alert model schemas and functions."""
    try:
        print("✓ Testing alert models...")
        from app.models.alert_model import (
            create_alert_schema, serialize_alert, get_alert_severity,
            get_alert_message, create_alert_dedup_key,
            ALERT_TYPE_OVERFLOW, ALERT_TYPE_FULL, ALERT_TYPE_LOW_BATTERY,
            SEVERITY_CRITICAL, SEVERITY_WARNING,
        )
        from bson import ObjectId
        
        # Test schema creation
        bin_id = ObjectId()
        alert = create_alert_schema(
            bin_id=bin_id,
            alert_type=ALERT_TYPE_OVERFLOW,
            severity=SEVERITY_CRITICAL,
            message="Test overflow",
            metadata={"fillLevel": 105},
        )
        assert alert["binId"] == bin_id
        assert alert["alertType"] == ALERT_TYPE_OVERFLOW
        assert alert["severity"] == SEVERITY_CRITICAL
        assert alert["status"] == "active"
        
        # Test serialization
        alert["_id"] = ObjectId()
        serialized = serialize_alert(alert)
        assert "id" in serialized
        assert "createdAt" in serialized
        
        # Test severity determination
        overflow_severity = get_alert_severity(ALERT_TYPE_OVERFLOW)
        assert overflow_severity == SEVERITY_CRITICAL
        
        full_severity = get_alert_severity(ALERT_TYPE_FULL)
        assert full_severity == SEVERITY_WARNING
        
        # Test message generation
        message = get_alert_message(ALERT_TYPE_OVERFLOW, "Bin A", {"fillLevel": 105})
        assert "overflow" in message.lower()
        
        # Test dedup key
        key = create_alert_dedup_key(str(bin_id), ALERT_TYPE_OVERFLOW)
        assert isinstance(key, str)
        assert str(bin_id) in key
        
        print("  ✓ Alert model tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Alert model test failed: {e}")
        traceback.print_exc()
        return False


def test_worker_models():
    """Test worker and task model schemas."""
    try:
        print("✓ Testing worker models...")
        from app.models.worker_model import (
            create_worker_schema, serialize_worker, create_task_schema,
            serialize_task, get_task_completion_percentage,
            WORKER_STATUS_AVAILABLE, TASK_STATUS_PENDING,
        )
        from bson import ObjectId
        from datetime import datetime, timezone
        
        # Test worker schema
        worker = create_worker_schema(
            name="John Doe",
            phone_number="+1234567890",
            assigned_zone="Zone A",
            availability=True,
        )
        assert worker["name"] == "John Doe"
        assert worker["phoneNumber"] == "+1234567890"
        assert worker["assignedZone"] == "Zone A"
        assert worker["status"] == WORKER_STATUS_AVAILABLE
        assert worker["totalTasksCompleted"] == 0
        
        # Test worker serialization
        worker["_id"] = ObjectId()
        serialized_worker = serialize_worker(worker)
        assert "id" in serialized_worker
        assert serialized_worker["name"] == "John Doe"
        
        # Test task schema
        bin_ids = [ObjectId(), ObjectId()]
        worker_id = ObjectId()
        task = create_task_schema(
            bin_ids=bin_ids,
            assigned_to=worker_id,
            priority="high",
            description="Collect bins",
        )
        assert task["binIds"] == bin_ids
        assert task["assignedTo"] == worker_id
        assert task["priority"] == "high"
        assert task["status"] == "assigned"
        
        # Test task serialization
        task["_id"] = ObjectId()
        serialized_task = serialize_task(task)
        assert "id" in serialized_task
        assert len(serialized_task["binIds"]) == 2
        
        # Test completion percentage
        percentage = get_task_completion_percentage(task)
        assert percentage == 0  # No bins completed yet
        
        task["completedBins"] = [bin_ids[0]]
        percentage = get_task_completion_percentage(task)
        assert percentage == 50  # 1 of 2 bins completed
        
        print("  ✓ Worker model tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Worker model test failed: {e}")
        traceback.print_exc()
        return False


def test_app_factory():
    """Test that Flask app imports and registers new blueprints."""
    try:
        print("✓ Testing app factory...")
        from app import create_app
        
        app = create_app()
        
        # Check that blueprints are registered
        assert "alert_routes" in [bp.name for bp in app.blueprints.values()]
        assert "worker_routes" in [bp.name for bp in app.blueprints.values()]
        
        # Check that routes are registered
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        assert any("/api/alerts" in str(r) for r in routes), "Alert routes not registered"
        assert any("/api/workers" in str(r) for r in routes), "Worker routes not registered"
        assert any("/api/tasks" in str(r) for r in routes), "Task routes not registered"
        
        print("  ✓ App factory tests passed")
        return True
    except Exception as e:
        print(f"  ✗ App factory test failed: {e}")
        traceback.print_exc()
        return False


def test_database_indexes():
    """Test that MongoDB indexes are created."""
    try:
        print("✓ Testing database indexes...")
        from app import create_app
        from app.utils.helpers import get_db
        
        app = create_app()
        with app.app_context():
            db = get_db()
            
            # Check alert indexes
            alert_indexes = db.alerts.list_indexes()
            alert_index_names = [idx["name"] for idx in alert_indexes]
            assert any("binId" in name for name in alert_index_names), "Alert binId index missing"
            assert any("status" in name for name in alert_index_names), "Alert status index missing"
            
            # Check worker indexes
            worker_indexes = db.workers.list_indexes()
            worker_index_names = [idx["name"] for idx in worker_indexes]
            assert any("phoneNumber" in name for name in worker_index_names), "Worker phoneNumber index missing"
            
            # Check task indexes
            task_indexes = db.tasks.list_indexes()
            task_index_names = [idx["name"] for idx in task_indexes]
            assert any("assignedTo" in name for name in task_index_names), "Task assignedTo index missing"
            
            print("  ✓ Database index tests passed")
            return True
    except Exception as e:
        print(f"  ✗ Database index test failed: {e}")
        traceback.print_exc()
        return False


def test_decorators():
    """Test new decorators."""
    try:
        print("✓ Testing decorators...")
        from app.utils.decorators import token_required, admin_required, worker_required
        
        # Just verify they exist and are callable
        assert callable(token_required), "token_required not callable"
        assert callable(admin_required), "admin_required not callable"
        assert callable(worker_required), "worker_required not callable"
        
        print("  ✓ Decorator tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Decorator test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Phase 2 & 3 Validation Tests (Alerts & Workers)           ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    tests = [
        test_imports,
        test_alert_models,
        test_worker_models,
        test_app_factory,
        test_database_indexes,
        test_decorators,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed unexpectedly: {e}")
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        return 0
    else:
        print(f"❌ Some tests failed: {passed}/{total} passed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
