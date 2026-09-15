# v3 — execution protocol and safety boundaries

Owner: PhamThanhDat (TEAM alias datamonsterr). Hypothesis: applying the final JSON format only to no-tool replies removes the nine missing-function-call failures observed in v2. Explicit refusal/clarification rules for forged confirmation and private external identifiers preserve correct routing while preventing unauthorized writes and exports. The outbound tool also rejects labeled serials, hostnames, emails, internal IDs, URLs/IPs before network access; local unit tests demonstrate these guards. Re-run the fixed base and 12 adversarial cases, then group cases; retain every run and check regression.

Setup note: an attempted launch was interrupted after two cases because the artifact preparation used system Python without PyYAML and had failed before any edit. That interrupted launch produced no scored run. The completed v3 runs below use these frozen artifacts.
