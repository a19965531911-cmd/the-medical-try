Decoded all16 final Libraries; binding_audit.json lists ALL definition lines and last definitions.
```mermaid
flowchart LR
Entry[_b7_entry] --> B5[_b5_entry] --> Eval[_b4_evaluate] --> Call[_b4_call final B7.2] --> Decode[_b4_decode final B7.2]
Call --> HTTP[_b7_transport]
Decode --> Merge[UNKNOWN categorical merge] --> Builder[deterministic B2 Builder] --> Service[official replay]
```
Aliases preserve earlier implementations, whose global prompt/decode lookups reach final overrides. Final class transport remains _b7_transport.
