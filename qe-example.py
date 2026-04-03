shape = {
    "workchain": {
        "protocol": "fast",
        "spin_type": "none",
        "electronic_type": "metal",
        "relax_type": "none",
        "properties": ["bands"],
    },
    "advanced": {
        "initial_magnetic_moments": None,
        "pw": {
            "parameters": {
                "SYSTEM": {
                    "tot_charge": 0.0,
                    "ecutwfc": 30.0,
                    "ecutrho": 240.0,
                    "vdw_corr": "none",
                    "smearing": "cold",
                    "degauss": 0.0275,
                },
                "CONTROL": {"forc_conv_thr": 0.001, "etot_conv_thr": 0.0002},
                "ELECTRONS": {
                    "conv_thr": 8e-10,
                    "electron_maxstep": 80,
                    "mixing_beta": 0.4,
                },
            },
            "pseudos": {"Si": "b194f7bb-116f-48a7-a737-a561b3a7e0e7"},
        },
        "clean_workdir": False,
        "kpoints_distance": 0.3,
        "optimization_maxsteps": 50,
        "pseudo_family": "SSSP/1.3/PBEsol/efficiency",
    },
    "bands": {"projwfc_bands": False},
    "codes": {
        "global": {
            "codes": {
                "quantumespresso__pw": {
                    "options": [
                        ("pw-7.4@localhost", "67dea70e-b7a3-479d-a041-9862df163e33")
                    ],
                    "code": "67dea70e-b7a3-479d-a041-9862df163e33",
                    "nodes": 1,
                    "cpus": 1,
                    "ntasks_per_node": 1,
                    "cpus_per_task": 1,
                    "max_wallclock_seconds": 43200,
                    "parallelization": {},
                },
                "quantumespresso__projwfc": {
                    "options": [
                        (
                            "projwfc-7.4@localhost",
                            "aefc0c54-a19e-4a59-a8db-4a6dc9b4b5c9",
                        )
                    ],
                    "code": "aefc0c54-a19e-4a59-a8db-4a6dc9b4b5c9",
                    "nodes": 1,
                    "cpus": 1,
                    "ntasks_per_node": 1,
                    "cpus_per_task": 1,
                    "max_wallclock_seconds": 43200,
                },
            }
        },
        "bands": {
            "override": False,
            "codes": {
                "pw": {
                    "options": [
                        ("pw-7.4@localhost", "67dea70e-b7a3-479d-a041-9862df163e33")
                    ],
                    "code": "67dea70e-b7a3-479d-a041-9862df163e33",
                    "nodes": 1,
                    "cpus": 1,
                    "ntasks_per_node": 1,
                    "cpus_per_task": 1,
                    "max_wallclock_seconds": 43200,
                    "parallelization": {},
                },
                "projwfc_bands": {
                    "options": [
                        (
                            "projwfc-7.4@localhost",
                            "aefc0c54-a19e-4a59-a8db-4a6dc9b4b5c9",
                        )
                    ],
                    "code": "aefc0c54-a19e-4a59-a8db-4a6dc9b4b5c9",
                    "nodes": 1,
                    "cpus": 1,
                    "ntasks_per_node": 1,
                    "cpus_per_task": 1,
                    "max_wallclock_seconds": 43200,
                },
            },
        },
    },
}
