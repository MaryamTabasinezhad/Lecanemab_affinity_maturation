# Manifests — batch work assignments

For batch work (e.g. score N variants × M targets), the coordinator writes a TSV
assigning tasks to a cluster. Workers update `status` pending → complete | failed.

## Format — manifest_stage<N>_<cluster>.tsv
```tsv
variant_id           target            cluster   status
LEC-AM-T1-0042       abeta_protofibril narval    pending
LEC-AM-T1-0042       abeta_monomer     narval    pending
LEC-AM-T1-0042       caa_fibril        narval    pending
```

Use manifests only for concrete parallelizable lists; use inbox messages for
instructions/decisions/questions.
