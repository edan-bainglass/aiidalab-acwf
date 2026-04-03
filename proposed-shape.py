shape = {
    "properties": ["bands"],
    "common": {
        "scf": {
            "protocol": "fast",
            "relax_type": "none",
            "electronic_type": "metal",
            "spin_type": "none",
        },
        "pp": {
            "": "",
        },
    },
    "afm": {
        "": "",
    },
    "codes": {
        "common": {
            "scf": {
                "options": [("scf@localhost", "...")],
                "code": "...",
                "nodes": 1,
                "cpus": 1,
                "ntasks_per_node": 1,
                "cpus_per_task": 1,
                "max_wallclock_seconds": 43200,
                "parallelization": {},
            },
            "pp": {
                "options": [("pp@localhost", "...")],
                "code": "...",
                "nodes": 1,
                "cpus": 1,
                "ntasks_per_node": 1,
                "cpus_per_task": 1,
                "max_wallclock_seconds": 43200,
            },
        },
        "afm": {
            "afm": {
                "options": [("ppafm@localhost", "...")],
                "code": "...",
                "nodes": 1,
                "cpus": 1,
                "ntasks_per_node": 1,
                "cpus_per_task": 1,
                "max_wallclock_seconds": 43200,
            },
        },
    },
}
