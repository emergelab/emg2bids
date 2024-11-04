from __future__ import annotations

import logging
from typing import Optional

from heudiconv.utils import SeqInfo

lgr = logging.getLogger("heudiconv")


def create_key(
    template: Optional[str],
    outtype: tuple[str, ...] = ("nii.gz",),
    annotation_classes: None = None,
) -> tuple[str, tuple[str, ...], None]:
    if template is None or not template:
        raise ValueError("Template must be a valid format string")
    return (template, outtype, annotation_classes)


def infotodict(
    seqinfo: list[SeqInfo],
) -> dict[tuple[str, tuple[str, ...], None], list[str]]:
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    t1w = create_key("sub-{subject}/anat/sub-{subject}_T1w")
    t2w = create_key("sub-{subject}/anat/sub-{subject}_T2w")
    dwi = create_key("sub-{subject}/dwi/sub-{subject}_acq-{acq}_dir-{dir}_dwi")
    dwi_sbref = create_key("sub-{subject}/dwi/sub-{subject}_acq-{acq}_dir-{dir}_sbref")
    func = create_key(
        "sub-{subject}/func/sub-{subject}_task-{task}_dir-{dir}_run-{run:02d}_bold"
    )
    func_sbref = create_key(
        "sub-{subject}/func/sub-{subject}_task-{task}_dir-{dir}_run-{run:02d}_sbref"
    )
    fmap = create_key("sub-{subject}/fmap/sub-{subject}_dir-{dir}_epi")

    info: dict[tuple[str, tuple[str, ...], None], list[str]] = {
        t1w: [],
        t2w: [],
        fmap: [],
        func: [],
        func_sbref: [],
        dwi: [],
        dwi_sbref: [],
    }

    for s in seqinfo:
        """
        The namedtuple `s` contains the following fields:

        * total_files_till_now
        * example_dcm_file
        * series_id
        * dcm_dir_name
        * unspecified2
        * unspecified3
        * dim1
        * dim2
        * dim3
        * dim4
        * TR
        * TE
        * protocol_name
        * is_motion_corrected
        * is_derived
        * patient_id
        * study_description
        * referring_physician_name
        * series_description
        * image_type
        """

        protocol_name = s.protocol_name.lower()
        series_description = s.series_description.lower()

        # Structural scans
        if "t1w_mpr" in protocol_name:
            if "NORM" not in s.image_type:  # Check if NORM tag is in IMAGE TYPE
                info[t1w].append(s.series_id)

        elif "t2w_spc" in protocol_name:
            if "NORM" not in s.image_type:  # Check if NORM tag is in IMAGE TYPE
                info[t2w].append(s.series_id)

        # Functional scans
        elif "fmri" in protocol_name:
            _, task, dir = protocol_name.split("_")
            run = int(
                task[-1]
            )  # Take the number from task as run number (e.g. rest1 = run_01)
            task = task[
                :-1
            ]  # Remove the numbering for tasks (e.g. rest1, rest2 -> rest)
            dir = dir.upper()  # Make dir uppercase

            if "sbref" in series_description:
                key = func_sbref
            else:
                key = func

            info[key].append(
                {"item": s.series_id, "task": task, "dir": dir, "run": run}
            )

        # Diffusion scans
        elif "dmri" in protocol_name:
            _, acq, dir = protocol_name.split("_")
            dir = dir.upper()

            if "sbref" in series_description:
                key = dwi_sbref
            else:
                key = dwi

            info[key].append({"item": s.series_id, "acq": acq, "dir": dir})

        # Field maps
        elif "spinechofieldmap" in protocol_name:
            if "spinechofieldmap2" in protocol_name:
                continue
            _, dir = protocol_name.split("_")
            dir = dir.upper()

            info[fmap].append({"item": s.series_id, "dir": dir})

    return info
