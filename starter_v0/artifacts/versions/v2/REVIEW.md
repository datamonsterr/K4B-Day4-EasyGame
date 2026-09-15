# v2 review

21/30 vs 24/30; zero provider errors. Multi-turn confirmation failures eliminated, but overall hypothesis failed because routing regressed. Regressions: ['H01_service_status_routing', 'M06_switch_tool', 'H15_compare_environments', 'H18_user_and_asset', 'M08_correct_then_parallel', 'M10_latest_intent_wins']. Nine failures all lack structured tool calls; the required JSON final format competes with function calling. v3 must explicitly separate function calls from final user-facing JSON and never narrate unexecuted work.
