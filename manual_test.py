#!/usr/bin/env python3
"""
Manual test script to validate advanced modules
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all module imports"""
    print("🔍 Testing module imports...")
    
    try:
        from purviewcli.client.scanning_operations import ScanningManager
        print("✅ ScanningManager imported successfully")
    except Exception as e:
        print(f"❌ ScanningManager import failed: {e}")
    
    try:
        from purviewcli.client.business_rules import BusinessRulesEngine
        print("✅ BusinessRulesEngine imported successfully")
    except Exception as e:
        print(f"❌ BusinessRulesEngine import failed: {e}")
    
    try:
        from purviewcli.client.monitoring_dashboard import MonitoringDashboard
        print("✅ MonitoringDashboard imported successfully")
    except Exception as e:
        print(f"❌ MonitoringDashboard import failed: {e}")
    
    try:
        from purviewcli.client.ml_integration import IntelligentDataDiscovery
        print("✅ IntelligentDataDiscovery imported successfully")
    except Exception as e:
        print(f"❌ IntelligentDataDiscovery import failed: {e}")
    
    try:
        from purviewcli.client.lineage_visualization import AdvancedLineageAnalyzer
        print("✅ AdvancedLineageAnalyzer imported successfully")
    except Exception as e:
        print(f"❌ AdvancedLineageAnalyzer import failed: {e}")
    
    try:
        from purviewcli.plugins.plugin_system import PluginManager
        print("✅ PluginManager imported successfully")
    except Exception as e:
        print(f"❌ PluginManager import failed: {e}")

def test_basic_functionality():
    """Test basic functionality of modules"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        from purviewcli.client.scanning_operations import ScanningManager
        # Test basic initialization
        scanning_manager = ScanningManager()
        print("✅ ScanningManager initialization successful")
    except Exception as e:
        print(f"❌ ScanningManager initialization failed: {e}")
    
    try:
        from purviewcli.client.business_rules import BusinessRulesEngine
        # Test basic initialization
        rules_engine = BusinessRulesEngine()
        print("✅ BusinessRulesEngine initialization successful")
    except Exception as e:
        print(f"❌ BusinessRulesEngine initialization failed: {e}")

if __name__ == "__main__":
    print("Enhanced Purview CLI - Manual Module Tests")
    print("=" * 50)
    
    test_imports()
    test_basic_functionality()
    
    print("\n✓ Manual tests completed")
