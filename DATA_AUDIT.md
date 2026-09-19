# ExpansionRx first experiment data audit

Run date: 17 September 2026. Reproduce with `python scripts/first_experiment.py` after installing `requirements-audit.txt`. The script downloads fixed source revisions, verifies SHA-256 hashes, writes `outputs/audit.json` and `outputs/first_pressure_data.csv`, and recreates `outputs/first_pressure_plot.png` and `.pdf`.

## Data source and joins

The [molab competition page](https://marimo.io/pages/events/notebook-competition-3) links OpenADMET's ExpansionRx training data. This audit uses the same official train file and the [released test file](https://huggingface.co/datasets/openadmet/openadmet-expansionrx-challenge-data) from OpenADMET's full challenge dataset. It uses [Pat Walters' stored predictions](https://github.com/PatWalters/expansion-ml-comparison) only for the model side of the comparison. Exact upstream revisions, file hashes, and URLs are in `outputs/audit.json` and the script.

- Official split: **5,326 training molecules** and **2,282 test molecules**. The official raw file has 7,618 entries; 10 are outside the released split. Those 10 do not supply a usable numeric LogD and KSOL pair.
- Test measurements: 2,270 numeric LogD; 2,170 numeric kinetic solubility (`KSOL`, µM); **2,160 with both**. Training has 4,934 with both.
- The raw file contains explicit inequality labels on 18 LogD and 122 KSOL records among the 7,608 split molecules. The released split has those entries missing, not treated as exact values. Numeric LogD and KSOL values in the split match the raw file.
- The benchmark's molecule identifiers and SMILES match the official train/test files exactly. Benchmark LogD is unchanged; its `LogS` is `log10(KSOL_µM + 1) - 6`. This transform was verified on every numeric row. The benchmark's stored `y_true` values also match official test measurements under that transform.
- For each of Morgan + LightGBM, Monroe + TabPFN, and ChemProp + CheMeleon, both endpoints have **25 saved predictions for every one of the 2,160 eligible test molecules**. These fits use different training folds but share the same held-out test molecules.

## Structure and split checks

- RDKit parsed every train and test SMILES. No multi-component structures or duplicate canonical structures were found within either split, and there were no exact canonical structures in both splits.
- Of the 2,160 eligible test molecules, **242** have a training molecule with Morgan radius-2, 2,048-bit Tanimoto similarity at least 0.8; the median nearest-training similarity is **0.636**. The benchmark's cluster labels have **59 clusters** represented in both train and test. This is a chemically related holdout, so results should not be sold as performance on entirely new scaffolds.

## First plot and what it shows

The plain [first pressure plot](outputs/first_pressure_plot.png) compares the mean predicted and measured scores among the top 50%, 25%, 10%, 5%, and 2% selected by each model. The score is an **illustrative selection goal**, not a universal definition of a good drug: LogD gets full credit inside the training complete-case interquartile range (**1.4 to 2.9**) and is penalized outside; KSOL gets half credit at the training median (**125.5 µM**) and rises smoothly. The exact formula is in the script and `outputs/audit.json`. These parameters were fixed using training data before viewing this plot.

At the strictest 2% (43 molecules), mean predicted versus measured scores are:

- Morgan + LightGBM: **0.825 predicted; 0.754 measured**.
- Monroe + TabPFN: **0.824 predicted; 0.811 measured**.
- ChemProp + CheMeleon: **0.842 predicted; 0.795 measured**.

Random selection from this same 2,160-molecule cohort has expected measured mean **0.581**. The retrospective measured best 43 have mean **0.843**, shown only as a ceiling. Measured quality **does improve** under stronger model selection. The useful question is how much of the *apparent* extra improvement is real, and why that varies by model. This pilot is descriptive; it does not yet have uncertainty intervals or a chemical explanation for individual winners. Future changes to the default score after seeing these test outcomes must be labeled exploratory.

## Model training clarification

- **CheMeleon in this plot:** Pat Walters' benchmark initializes a ChemProp model from CheMeleon and trains it on the ExpansionRx physicochemical/tissue-binding family, which includes **LogD and LogS**, using training folds. This is an ExpansionRx LogD predictor.
- **Chemlactica/Chemma:** The released general checkpoints document a trained **CLOGP** tag, which is a computed property and is not ExpansionRx experimental LogD. The [Chemlactica paper](https://arxiv.org/html/2407.18897v1) also reports *separate supervised fine-tuning* on MoleculeNet Lipophilicity, which [DeepChem identifies as experimental LogD at pH 7.4](https://github.com/deepchem/deepchem/blob/master/deepchem/molnet/load_function/lipo_datasets.py). That result does not establish that the released general checkpoint is trained to predict ExpansionRx LogD. A specific checkpoint or new fit must be verified before using Chemlactica as a LogD predictor here.

If “Kimblef” names another model, its checkpoint and training data still need a separate audit.
