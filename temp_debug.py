from purviewcli.client._search import Search
import json

search_client = Search()
filter_dict = {"collectionId": "kaydemopurview", "entityType": "powerbi_dataset"}
search_args = {'--filter': json.dumps(filter_dict), '--limit': 1}
result = search_client.searchQuery(search_args)

if result and result.get('value'):
    entity = result['value'][0]
    print(json.dumps(entity, indent=2))
