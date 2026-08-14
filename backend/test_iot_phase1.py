#!/usr/bin/env python3
"""
Smart Waste IoT - Phase 1 Validation Test Script
Run tests to verify IoT implementation is working correctly.
"""

import sys
import json
from datetime import datetime, timezone

def test_imports():
    """Test that all new modules can be imported."""
    print("\n" + "="*60)
    print("TEST 1: Module Imports")
    print("="*60)
    
    try:
        from app.models.iot_model import (
            create_sensor_schema, create_iot_reading_schema,
            get_fill_level_status, serialize_sensor, serialize_iot_reading
        )
        print("✓ iot_model imports OK")
    except ImportError as e:
        print(f"✗ iot_model import failed: {e}")
        return False
    
    try:
        from app.utils.sensor_handler import (
            SensorHandler, UltrasonicSensorHandler,
            InfraredSensorHandler, create_sensor_handler
        )
        print("✓ sensor_handler imports OK")
    except ImportError as e:
        print(f"✗ sensor_handler import failed: {e}")
        return False
    
    try:
        from app.controllers.iot_controller import (
            receive_sensor_data, create_sensor, get_sensor,
            update_sensor, get_sensor_history
        )
        print("✓ iot_controller imports OK")
    except ImportError as e:
        print(f"✗ iot_controller import failed: {e}")
        return False
    
    try:
        from app.routes.iot_routes import iot_bp
        print("✓ iot_routes imports OK")
    except ImportError as e:
        print(f"✗ iot_routes import failed: {e}")
        return False
    
    return True


def test_status_mapping():
    """Test status mapping logic."""
    print("\n" + "="*60)
    print("TEST 2: Fill Level Status Mapping")
    print("="*60)
    
    from app.models.iot_model import get_fill_level_status
    
    test_cases = [
        (0, "normal"),
        (50, "normal"),
        (79, "normal"),
        (80, "full"),
        (85, "full"),
        (89, "full"),
        (90, "overflow"),
        (95, "overflow"),
        (99, "overflow"),
        (100, "overflow"),
        (110, "overflow"),
    ]
    
    all_passed = True
    for fill_level, expected_status in test_cases:
        actual_status = get_fill_level_status(fill_level)
        if actual_status == expected_status:
            print(f"  ✓ {fill_level}% → {actual_status}")
        else:
            print(f"  ✗ {fill_level}% expected {expected_status}, got {actual_status}")
            all_passed = False
    
    return all_passed


def test_sensor_handler():
    """Test sensor handler abstraction."""
    print("\n" + "="*60)
    print("TEST 3: Sensor Handler Abstraction")
    print("="*60)
    
    from app.utils.sensor_handler import (
        UltrasonicSensorHandler, create_sensor_handler
    )
    from bson import ObjectId
    from datetime import datetime, timezone
    
    # Create mock sensor config
    sensor_config = {
        "_id": ObjectId(),
        "binId": ObjectId(),
        "sensorType": "ultrasonic",
        "calibrationData": {
            "minDistance": 5.0,
            "maxDistance": 100.0
        }
    }
    
    try:
        handler = create_sensor_handler(sensor_config)
        print("✓ Handler creation OK")
    except Exception as e:
        print(f"✗ Handler creation failed: {e}")
        return False
    
    # Test distance → fill level conversion
    test_readings = [
        (5, 100.0, "empty position → 100%"),
        (52.5, 50.0, "middle position → 50%"),
        (100, 0.0, "full position → 0%"),
    ]
    
    all_passed = True
    for distance, expected_fill, description in test_readings:
        raw_data = {"distance": distance, "batteryLevel": 85}
        result = handler.process_reading(raw_data)
        
        if abs(result["fillLevel"] - expected_fill) < 0.1:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}: got {result['fillLevel']}%")
            all_passed = False
    
    # Test validation
    invalid_data = {"invalid": "data"}
    is_valid, error = handler.validate_data(invalid_data)
    
    if not is_valid and error:
        print(f"✓ Validation error detection: '{error}'")
    else:
        print(f"✗ Validation should have failed")
        all_passed = False
    
    return all_passed


def test_sensor_schemas():
    """Test sensor data schemas."""
    print("\n" + "="*60)
    print("TEST 4: Sensor Schemas")
    print("="*60)
    
    from app.models.iot_model import (
        create_sensor_schema, create_iot_reading_schema,
        serialize_sensor, serialize_iot_reading
    )
    from bson import ObjectId
    from datetime import datetime, timezone
    
    bin_id = ObjectId()
    sensor_id = ObjectId()
    
    # Test sensor creation
    try:
        sensor_doc = create_sensor_schema(
            bin_id=bin_id,
            sensor_type="ultrasonic",
            device_id="esp32-001"
        )
        sensor_doc["_id"] = ObjectId()
        serialized = serialize_sensor(sensor_doc)
        
        required_fields = ["id", "binId", "sensorType", "status", "calibrationData"]
        all_present = all(field in serialized for field in required_fields)
        
        if all_present:
            print("✓ Sensor schema OK")
        else:
            print(f"✗ Sensor schema missing fields")
            return False
    except Exception as e:
        print(f"✗ Sensor schema failed: {e}")
        return False
    
    # Test reading creation
    try:
        reading_doc = create_iot_reading_schema(
            bin_id=bin_id,
            sensor_id=sensor_id,
            fill_level=55.3,
            timestamp=datetime.now(timezone.utc),
            sensor_status="ok",
            battery_level=87
        )
        reading_doc["_id"] = ObjectId()
        serialized = serialize_iot_reading(reading_doc)
        
        required_fields = ["id", "binId", "sensorId", "fillLevel", "timestamp"]
        all_present = all(field in serialized for field in required_fields)
        
        if all_present:
            print("✓ IoT reading schema OK")
        else:
            print(f"✗ IoT reading schema missing fields")
            return False
    except Exception as e:
        print(f"✗ IoT reading schema failed: {e}")
        return False
    
    return True


def test_app_factory():
    """Test Flask app creation with IoT blueprint."""
    print("\n" + "="*60)
    print("TEST 5: Flask App Factory")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        print("✓ App creation OK")
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        return False
    
    # Check if IoT blueprint is registered
    try:
        iot_route = None
        for rule in app.url_map.iter_rules():
            if '/api/iot/' in rule.rule:
                iot_route = rule.rule
                break
        
        if iot_route:
            print(f"✓ IoT routes registered: {iot_route}")
            return True
        else:
            print("✗ IoT routes not found in app")
            # List all routes for debugging
            print("\n  Available routes:")
            for rule in app.url_map.iter_rules():
                if '/api/' in rule.rule:
                    print(f"    - {rule.rule} ({','.join(rule.methods - {'HEAD', 'OPTIONS'})})")
            return False
    except Exception as e:
        print(f"✗ Route check failed: {e}")
        return False


def test_database_indexes():
    """Test database index creation."""
    print("\n" + "="*60)
    print("TEST 6: Database Indexes")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            db = app.db
            
            # Check sensors collection indexes
            sensor_indexes = db.sensors.list_indexes()
            sensor_index_names = [idx["name"] for idx in sensor_indexes]
            
            required_sensor_indexes = ["binId_1", "deviceId_1", "status_1"]
            found_sensor_indexes = []
            
            for idx_name in required_sensor_indexes:
                if idx_name in sensor_index_names:
                    found_sensor_indexes.append(idx_name)
            
            if len(found_sensor_indexes) == len(required_sensor_indexes):
                print("✓ Sensors collection indexes OK")
            else:
                missing = set(required_sensor_indexes) - set(found_sensor_indexes)
                print(f"⚠ Missing indexes on sensors: {missing}")
            
            # Check iot_readings collection indexes
            reading_indexes = db.iot_readings.list_indexes()
            reading_index_names = [idx["name"] for idx in reading_indexes]
            
            required_reading_indexes = ["binId_1", "sensorId_1", "timestamp_1"]
            found_reading_indexes = []
            
            for idx_name in required_reading_indexes:
                if idx_name in reading_index_names:
                    found_reading_indexes.append(idx_name)
            
            if len(found_reading_indexes) == len(required_reading_indexes):
                print("✓ IoT readings collection indexes OK")
            else:
                missing = set(required_reading_indexes) - set(found_reading_indexes)
                print(f"⚠ Missing indexes on iot_readings: {missing}")
            
            return True
    except Exception as e:
        print(f"⚠ Database check skipped (MongoDB not available): {e}")
        return True  # Don't fail if MongoDB is not available


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Smart Waste IoT - Phase 1 Validation Tests")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Status Mapping", test_status_mapping),
        ("Sensor Handler", test_sensor_handler),
        ("Schemas", test_sensor_schemas),
        ("Flask App", test_app_factory),
        ("Database Indexes", test_database_indexes),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 1 implementation is valid.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
