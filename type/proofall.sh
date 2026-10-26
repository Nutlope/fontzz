#!/bin/zsh
cd "$(dirname "$0")"
fams=(${=FAMS:-halden rondel tessera alder mallow strata plaza vesper ledger folio})
for f in $fams; do
  N="$(echo ${f:0:1} | tr a-z A-Z)${f:1}"
  ../.venv/bin/python proof.py "out/$f/${N}[wght].ttf" "out/p_$f.png" "$@"
done
