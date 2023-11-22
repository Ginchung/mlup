############################################################################
# Modified from maml pack, basic source: https://github.com/materialsvirtuallab/maml/blob/master/maml/apps/pes/_mtp.py
############################################################################
"""Convert data list to docs or pool existing data lists for training."""
from __future__ import annotations
from collections import OrderedDict

import itertools
import numpy as np
import pandas as pd
from pymatgen.core import Structure
from monty.serialization import loadfn

def doc_from(structure, energy=None, force=None, stress=None):
    """
    Method to convert structure and its properties into doc
    format for further processing. If properties are None, zeros
    array will be used.

    Args:
        structure (Structure): Pymatgen Structure object.
        energy (float): The total energy of the structure.
        force (np.array): The (m, 3) forces array of the structure
            where m is the number of atoms in structure.
        stress (list/np.array): The (6, ) stresses array of the
            structure.

    Returns:
        (dict)
    """
    energy = energy if energy is not None else 0
    force = force if force is not None else np.zeros((len(structure), 3))
    stress = stress if stress is not None else np.zeros(6)
    outputs = dict(energy=energy, forces=force, virial_stress=stress)
    return dict(structure=structure.as_dict(), num_atoms=len(structure), outputs=outputs)


def pool_from(structures, energies=None, forces=None, stresses=None):
    """
    Method to convert structures and their properties in to
    datapool format.

    Args:
        structures ([Structure]): The list of Pymatgen Structure object.
        energies ([float]): The list of total energies of each structure
            in structures list.
        forces ([np.array]): List of (m, 3) forces array of each structure
            with m atoms in structures list. m can be varied with each
            single structure case.
        stresses (list): List of (6, ) virial stresses of each
            structure in structures list.

    Returns:
        ([dict])
    """
    energies = energies if energies is not None else [None] * len(structures)
    forces = forces if forces is not None else [None] * len(structures)
    stresses = stresses if stresses is not None else [None] * len(structures)
    return [
        doc_from(structure, energy, force, stress)
        for structure, energy, force, stress in zip(structures, energies, forces, stresses)
    ]

def write_cfg(elements, filename, cfg_pool):
    """
    Write configurations to file
    Args:
        filename (str): filename
        cfg_pool (list): list of configurations.

    Returns:

    """
    if not elements:
        raise ValueError("No species given.")

    lines = []
    for dataset in cfg_pool:
        if isinstance(dataset["structure"], dict):
            structure = Structure.from_dict(dataset["structure"])
        else:
            structure = dataset["structure"]
        energy = dataset["outputs"]["energy"]
        forces = dataset["outputs"]["forces"]
        virial_stress = dataset["outputs"]["virial_stress"]
        virial_stress = [virial_stress[vasp_stress_order.index(n)] for n in mtp_stress_order]
        lines.append(_line_up(elements,structure, energy, forces, virial_stress))

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    return filename

def _line_up(elements, structure, energy, forces, virial_stress):
    """
    Convert input structure, energy, forces, virial_stress to
    proper configuration format for mlip usage.

    Args:
        structure (Structure): Pymatgen Structure object.
        energy (float): DFT-calculated energy of the system.
        forces (list): The forces should have dimension (num_atoms, 3).
        virial_stress (list): stress should has 6 distinct
            elements arranged in order [xx, yy, zz, yz, xz, xy].
    """
    inputs = OrderedDict(
        Size=structure.num_sites,
        SuperCell=structure.lattice,
        AtomData=(structure, forces),
        Energy=energy,
        Stress=virial_stress,
    )

    lines = ["BEGIN_CFG"]

    if "Size" in inputs:
        lines.append(" Size")
        lines.append(f"{inputs['Size']:>7d}")
    if "SuperCell" in inputs:
        lines.append(" SuperCell")
        for vec in inputs["SuperCell"].matrix:
            lines.append(f"{vec[0]:>17.6f}{vec[1]:>14.6f}{vec[2]:>14.6f}")
    if "AtomData" in inputs:
        format_str = "{:>14s}{:>5s}{:>15s}{:>14s}{:>14s}{:>13s}{:>13s}{:>13s}"
        format_float = "{:>14d}{:>5d}{:>15f}{:>14f}{:>14f}{:>13f}{:>13f}{:>13f}"
        lines.append(
            format_str.format("AtomData:  id", "type", "cartes_x", "cartes_y", "cartes_z", "fx", "fy", "fz")
        )
        for i, (site, force) in enumerate(zip(structure, forces)):
            lines.append(format_float.format(i + 1, elements.index(str(site.specie)), *site.coords, *force))
    if "Energy" in inputs:
        lines.append(" Energy")
        lines.append(f"{inputs['Energy']:>24.12f}")
    if "Stress" in inputs:
        if True: #if not hasattr(self, "version") or self.version == "mlip-2":
            format_str = "{:>16s}{:>12s}{:>12s}{:>12s}{:>12s}{:>12s}"
            lines.append(format_str.format("PlusStress:  xx", "yy", "zz", "yz", "xz", "xy"))
        #if self.version == "mlip-dev":
        #    format_str = "{:>12s}{:>12s}{:>12s}{:>12s}{:>12s}{:>12s}"
        #    lines.append(format_str.format("Stress:  xx", "yy", "zz", "yz", "xz", "xy"))
        format_float = "{:>12f}{:>12f}{:>12f}{:>12f}{:>12f}{:>12f}"
        lines.append(format_float.format(*np.array(virial_stress)))

    lines.append("END_CFG")

    return "\n".join(lines)


data = loadfn('data.json')
train_structures = [d['structure'] for d in data]
train_energies = [d['outputs']['energy'] for d in data]
train_forces = [d['outputs']['forces'] for d in data]
train_stresses = [d['outputs']['stress'] for d in data]

vasp_stress_order = ["xx", "yy", "zz", "xy", "yz", "xz"]
mtp_stress_order = ["xx", "yy", "zz", "yz", "xz", "xy"]
train_pool = pool_from(train_structures, train_energies, train_forces, train_stresses)
elements = sorted(set(itertools.chain(*[struct.species for struct in train_structures])))
elements = [str(element) for element in elements]
atoms_filename = "train.cfgs"
atoms_filename = write_cfg(elements=elements,filename=atoms_filename, cfg_pool=train_pool)
