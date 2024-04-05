#!/usr/bin/env bash

## Download mechanism of action
wget --recursive --no-parent --no-host-directories --cut-dirs 8 ftp://ftp.ebi.ac.uk/pub/databases/opentargets/platform/24.03/output/etl/json/mechanismOfAction

## Download Drug Targets
wget --recursive --no-parent --no-host-directories --cut-dirs 8 ftp://ftp.ebi.ac.uk/pub/databases/opentargets/platform/24.03/output/etl/json/targets

## Download Drugs (molecules)
wget --recursive --no-parent --no-host-directories --cut-dirs 8 ftp://ftp.ebi.ac.uk/pub/databases/opentargets/platform/24.03/output/etl/json/molecule