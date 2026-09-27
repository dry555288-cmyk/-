# Production binding discovery — 2026-09-27

This directory preserves the one-shot discovery evidence used before G2 V2.

Key conclusion: MineSim semantic map is custom JSON, not a GeoJSON FeatureCollection. The production loader reads road/intersection/loading_area/unloading_area layer records, follows `link_polygon_token` into polygon records, then `link_node_tokens` into node x/y coordinates.

The original G1 drivable-domain stage script bytes were not found. Therefore G2 V2 uses the actual production loader with strict frozen map/source/count/component/route endpoint checks; it does not claim byte-for-byte recreation of the missing stage script.
