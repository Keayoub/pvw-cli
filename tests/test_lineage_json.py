import pytest
import pandas as pd
import json
# from purviewcli.client.csv_operations import CSVBatchProcessor, EntityTemplate  # Replace with _lineage.py or remove if not needed

class DummyPurviewClient:
    async def create_lineage_relationship(self, relationship):
        return {'status': 'success', 'relationship': relationship}
    async def bulk_create_lineage(self, payload):
        return [{'status': 'success', 'relationship': r} for r in payload['relationships']]

@pytest.fixture
def csv_processor():
    return CSVBatchProcessor(DummyPurviewClient())

def test_create_lineage_from_json(tmp_path, csv_processor):
    # Create a sample JSON file for basic_lineage
    json_file = tmp_path / 'lineage.json'
    data = [
        {
            'source_entity_guid': 'source-guid-001',
            'target_entity_guid': 'target-guid-001',
            'relationship_type': 'DataFlow',
            'process_name': 'ETL_Process_1',
            'description': 'Test lineage',
            'confidence_score': 0.9,
            'owner': 'data-team',
            'metadata': '{"tool": "spark"}'
        }
    ]
    with open(json_file, 'w') as f:
        json.dump(data, f)
    df = pd.read_json(json_file)
    template = csv_processor.LINEAGE_TEMPLATES['basic_lineage']
    # Directly call the internal method for test
    import asyncio
    result = asyncio.run(csv_processor._create_lineage_from_csv(df, template))
    assert 'errors' in result
    assert 'success' in result
    assert result['summary']['created'] == 1
