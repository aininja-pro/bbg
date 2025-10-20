flowchart TD
    Start[Upload Excel File] --> Validate[Validate File Structure]
    Validate --> Decision{Validation Result}
    Decision -->|Critical Errors| ErrorBlock[Show Errors and Block Processing]
    Decision -->|Warnings| Preview[Show Preview with Warnings]
    Decision -->|No Issues| Preview
    Preview --> Options[Select Export Options]
    Options --> ExportType{Choose Export Type}
    ExportType -->|Merged CSV| Merge[Generate Merged CSV]
    ExportType -->|Individual CSVs| Batch[Generate Individual CSVs Zip]
    Merge --> Download[Download File]
    Batch --> Download
    Download --> End[Process Complete]
    subgraph RulesManagement
        RulesTab[Open Rules Tab] --> ManageRules[Add Edit Delete Reorder Rules]
        ManageRules --> SaveRules[Save Rules]
    end
    subgraph LookupManagement
        LookupsTab[Open Lookups Tab] --> SelectTable[Select Lookup Table]
        SelectTable --> CRUD[Add Edit Delete Records]
        CRUD --> SaveLookup[Save Lookups]
    end