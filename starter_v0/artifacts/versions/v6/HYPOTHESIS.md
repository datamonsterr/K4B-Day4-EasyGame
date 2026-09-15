# v6 — coverage under boundaries

Owner: PhamThanhDat. Hypothesis: v5 fixed A02/A03/A05 (adversarial 11/12) but its caution regressed H15/H17 (base 28/30) and left A06 refusing the legitimate internal inspection. Sharpening boundary rule 4 (internal inspection MUST run) and stating that boundaries never reduce parallel coverage restores base 30/30 and adversarial 12/12 without new regressions. Run base 30 + adversarial 12 + group 10, same model/temperature/scorer.
