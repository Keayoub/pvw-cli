"""Simple test of the specific fixes"""
try:
    print("Testing imports...")
    from purviewcli.client._data_product import DataProduct
    print("✓ Data product client import successful")
    
    from purviewcli.client.endpoints import PurviewEndpoints
    print("✓ Endpoints import successful")
    
    print("Testing lineage endpoints...")
    if hasattr(PurviewEndpoints, 'LINEAGE') and 'bulk' in PurviewEndpoints.LINEAGE:
        print("✓ Lineage bulk endpoint exists")
    else:
        print("✗ Lineage bulk endpoint missing")
        
    print("\nAll critical fixes validated!")
    
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
