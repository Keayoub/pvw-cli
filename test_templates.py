#!/usr/bin/env python3
"""Test script for CSV lineage templates"""

from purviewcli.client.csv_lineage_processor import LineageCSVTemplates

def main():
    templates = LineageCSVTemplates()
    
    print("Available CSV Lineage Templates:")
    print("=" * 40)
    
    for name, description in templates.get_available_templates().items():
        print(f"📋 {name}: {description}")
    
    print("\n🧪 Testing basic template generation...")
    basic_sample = templates.generate_sample_csv("basic", num_samples=3)
    print("Basic template sample:")
    print(basic_sample[:200] + "..." if len(basic_sample) > 200 else basic_sample)

if __name__ == "__main__":
    main()
