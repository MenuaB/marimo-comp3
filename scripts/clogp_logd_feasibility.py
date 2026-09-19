"""Compare RDKit cLogP with measured LogD in the released ExpansionRx test split."""

from pathlib import Path

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Crippen


ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "expansion_data_test.csv")
df["LogD"] = pd.to_numeric(df["LogD"], errors="coerce")
df = df.loc[df["LogD"].notna()].copy()
mols = [Chem.MolFromSmiles(smiles) for smiles in df["SMILES"]]
if any(mol is None for mol in mols):
    raise ValueError("A molecule with numeric LogD could not be parsed")

df["cLogP"] = [Crippen.MolLogP(mol) for mol in mols]
df["absolute_gap"] = (df["cLogP"] - df["LogD"]).abs()
window = df["cLogP"].between(1.4, 2.9)
outside = ~df.loc[window, "LogD"].between(1.4, 2.9)

print(f"Measured LogD molecules: {len(df)}")
print(f"Pearson correlation: {df[['cLogP', 'LogD']].corr().iloc[0, 1]:.3f}")
print(f"Median absolute gap: {df['absolute_gap'].median():.3f}")
print(f"Absolute gap >= 1: {(df['absolute_gap'] >= 1).sum()}/{len(df)}")
print(f"cLogP in 1.4-2.9, measured LogD outside: {outside.sum()}/{window.sum()}")
