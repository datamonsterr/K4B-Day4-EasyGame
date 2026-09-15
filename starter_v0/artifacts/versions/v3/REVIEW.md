# v3 review

29/30, zero provider errors; multi-turn 10/10. All nine v2 missing-call failures fixed. New regression: H16_compare_two_assets called inspect_device only for the first of two assets. v4 will require a separate call for every requested entity in the same response. Runtime privacy unit tests now reject serial/hostname/location/assigned-user suffixes with spaces as well as colon/equal delimiters.
