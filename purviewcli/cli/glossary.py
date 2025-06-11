"""
usage: 
    pvw glossary create --payloadFile=<val>
    pvw glossary createCategories --payloadFile=<val>
    pvw glossary createCategory --payloadFile=<val>
    pvw glossary createTerm --payloadFile=<val> [--includeTermHierarchy]
    pvw glossary createTerms --payloadFile=<val> [--includeTermHierarchy]
    pvw glossary createTermsAssignedEntities --termGuid=<val> --payloadFile=<val>
    pvw glossary createTermsExport --glossaryGuid=<val> --termGuid=<val>... [--includeTermHierarchy]
    pvw glossary createTermsImport --glossaryFile=<val> [--glossaryGuid=<val> --includeTermHierarchy]
    pvw glossary delete --glossaryGuid=<val>
    pvw glossary deleteCategory --categoryGuid=<val>
    pvw glossary deleteTerm --termGuid=<val>
    pvw glossary deleteTermsAssignedEntities --termGuid=<val> --payloadFile=<val>
    pvw glossary put --glossaryGuid=<val> --payloadFile=<val>
    pvw glossary putCategory --categoryGuid=<val> --payloadFile=<val>
    pvw glossary putCategoryPartial --categoryGuid=<val> --payloadFile=<val>
    pvw glossary putPartial --glossaryGuid=<val> --payloadFile=<val> [--includeTermHierarchy]
    pvw glossary putTerm --termGuid=<val> --payloadFile=<val> [--includeTermHierarchy]
    pvw glossary putTermPartial --termGuid=<val> --payloadFile=<val> [--includeTermHierarchy]
    pvw glossary putTermsAssignedEntities --termGuid=<val> --payloadFile=<val>
    pvw glossary read [--glossaryGuid=<val> --limit=<val> --offset=<val> --sort=<val> --ignoreTermsAndCategories]
    pvw glossary readCategories --glossaryGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
    pvw glossary readCategoriesHeaders --glossaryGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
    pvw glossary readCategory --categoryGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
    pvw glossary readCategoryRelated --categoryGuid=<val>
    pvw glossary readCategoryTerms --categoryGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
    pvw glossary readDetailed --glossaryGuid=<val> [--includeTermHierarchy]
    pvw glossary readTerm --termGuid=<val> [--includeTermHierarchy]
    pvw glossary readTerms [--glossaryGuid=<val> --limit=<val> --offset=<val> --sort=<val> --extInfo --includeTermHierarchy]
    pvw glossary readTermsAssignedEntities --termGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
    pvw glossary readTermsHeaders --glossaryGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
    pvw glossary readTermsImport --operationGuid=<val>
    pvw glossary readTermsRelated --termGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]

options:
    --purviewName=<val>         [string]  Azure Purview account name.
    --categoryGuid=<val>        [string]  The globally unique identifier of the category.
    --extInfo                   [boolean] extInfo [defaul: false]
    --glossaryGuid=<val>        [string]  The globally unique identifier for glossary.
    --glossaryName=<val>        [string]  The name of the glossary.
    --includeTermHierarchy      [boolean] Include term template references [default: false].
    --ignoreTermsAndCategories  [boolean] Whether to ignore terms and categories [default: false].
    --limit=<val>               [integer] The page size - by default there is no paging [default: 1000].
    --offset=<val>              [integer] Offset for pagination purpose [default: 0].
    --operationGuid=<val>       [string]  The globally unique identifier for async operation/job.
    --payloadFile=<val>         [string]  File path to a valid JSON document.
    --sort=<val>                [string]  ASC or DESC [default: ASC].
    --termGuid=<val>            [string]  The globally unique identifier for glossary term.

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
