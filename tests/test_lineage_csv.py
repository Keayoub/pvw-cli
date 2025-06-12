import pytest
import pandas as pd
# from purviewcli.client.csv_operations import CSVBatchProcessor, EntityTemplate  # Replace with _lineage.py or remove if not needed

class DummyPurviewClient:
    async def create_lineage_relationship(self, relationship):
        # Simulate successful creation
        return {'status': 'success', 'relationship': relationship}
    async def bulk_create_lineage(self, payload):
        # Simulate successful bulk creation
        return [{'status': 'success', 'relationship': r} for r in payload['relationships']]

@pytest.fixture
def csv_processor():
    return CSVBatchProcessor(DummyPurviewClient())

@pytest.mark.asyncio
async def test_create_lineage_from_csv(tmp_path, csv_processor):
    # Create a sample CSV file for basic_lineage
    csv_file = tmp_path / 'lineage.csv'
    df = pd.DataFrame([
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
    ])
    df.to_csv(csv_file, index=False)
    template = csv_processor.LINEAGE_TEMPLATES['basic_lineage']
    result = await csv_processor.process_csv_file(str(csv_file), 'create_lineage_relationships', template)
    assert 'errors' in result
    assert 'success' in result
    assert result['summary']['created'] == 1

@pytest.mark.asyncio
async def test_bulk_create_lineage_from_csv(tmp_path, csv_processor):
    # Create a sample CSV file for bulk lineage
    csv_file = tmp_path / 'bulk_lineage.csv'
    df = pd.DataFrame([
        {
            'source_entity_guid': f'source-guid-{i:03d}',
            'target_entity_guid': f'target-guid-{i:03d}',
            'relationship_type': 'DataFlow',
            'process_name': f'ETL_Process_{i}',
            'confidence_score': 0.8 + i * 0.01
        } for i in range(3)
    ])
    df.to_csv(csv_file, index=False)
    template = csv_processor.LINEAGE_TEMPLATES['basic_lineage']
    result = await csv_processor.process_csv_file(str(csv_file), 'bulk_create_lineage', template)
    assert 'errors' in result
    assert 'success' in result
    assert result['summary']['created'] == 3
