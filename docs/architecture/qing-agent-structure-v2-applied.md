# qing-agent Structure v2 (applied-safe)

## Applied changes
- qing_platform/ -> adapters/platforms/
- Root active tree keeps business modules only
- Legacy reports, runtime caches, tmp scripts already archived out

## Current semantic layout
- database/ repositories/ services/ pipeline/ = core runtime flow
- adapters/platforms/ = platform adapters
- vectorbrain/ = decision brain
- scripts/ = formal run entrypoints
