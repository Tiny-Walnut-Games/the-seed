EXP-07: LUCA Bootstrap Test
Hypothesis
You can start from LUCA (minimal bit-chain) and reconstruct the entire Seed space.

Method
Create LUCA: Define the primordial bit-chain (minimal content, L=1, Lum=0.0)
Bootstrap generation 1: Generate immediate children (L=2) from LUCA
Verify lineage: All L=2 nodes have L=1 as parent
Cascade: Generate L=3, L=4, etc. up to some depth
Full reconstruction: Can you reconstruct the entire state from LUCA + generation sequence?
Expected Result
✓ LUCA can serve as true ground state ✓ Every subsequent generation can be derived from prior generation ✓ Full system state is computable from LUCA + lineage info

Failure Handling
If bootstrap fails:

LUCA might be under-defined (needs more core information)
Lineage alone might not capture enough information (need Adjacency copies)
Or the system is genuinely not bootstrappable (major architecture problem)

```stat7_entity.py:295-317
    # ========================================================================
    # LUCA Bootstrap
    # ========================================================================
    
    @property
    def luca_distance(self) -> int:
        """Distance from LUCA (Last Universal Common Ancestor)"""
        return self.stat7.lineage
    
    def get_luca_trace(self) -> Dict[str, Any]:
        """
        Get path back to LUCA bootstrap origin.
        In a real system, this would trace parent entities.
        """
        return {
            'entity_id': self.entity_id,
            'luca_distance': self.luca_distance,
            'realm': self.stat7.realm.value,
            'lineage': self.stat7.lineage,
            'created_at': self.created_at.isoformat(),
            'migration_source': self.migration_source,
            'event_count': len(self.lifecycle_events)
        }
```
