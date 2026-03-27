from importlib.metadata import distributions


def print_error(entry_point, e):
    print(f"\033[91mFailed to load plugin entry point {entry_point.name}.\033[0m")
    print(f"\033[91mError message: {e}\033[0m\n")


# load entry points.
# We give priority to built-in plugins, and then we sort alphabetically
# the rest of the plugins
def get_entries(
    entry_point_name="acwf",
    priority=None,  # Use None as the default value
):
    from importlib_metadata import entry_points

    # sort the entry points: first we put the priority plugins by putting False in their
    # sorted priority. The rest is sorted alphabetically.
    eps = entry_points(group=entry_point_name)
    if not eps.names:
        return {}
    priority = priority or []
    sorted_entry_points = sorted(
        eps,
        key=lambda x: (
            x.name not in priority,
            priority.index(x.name) if x.name in priority else x.name,
        ),
    )

    entries = {}
    for entry_point in sorted_entry_points:
        try:
            # Attempt to load the entry point
            if entry_point.name in entries:
                continue
            loaded_entry_point = entry_point.load()
            entries[entry_point.name] = loaded_entry_point
        except Exception as e:
            print_error(entry_point, e)

    return entries


def get_entry_items(entry_point_name, item_name="outline"):
    entries = get_entries(entry_point_name)
    return {
        name: entry_point.get(item_name)
        for name, entry_point in entries.items()
        if entry_point.get(item_name, False)
    }


def get_entry_points_for_package(package_name: str, group: str = "acwf"):
    """Find the entry points for the specified package"""
    entry_points_list = []

    dist = next(
        (d for d in distributions() if d.metadata["Name"] == package_name), None
    )
    if not dist:
        raise ValueError(f"Package '{package_name}' not found.")
    # Retrieve all entry points associated with this distribution
    if dist.entry_points:
        for ep in dist.entry_points:
            if ep.group == group:
                entry_points_list.append(ep)
    else:
        print(f"No entry points found for package '{package_name}'.")
    return entry_points_list
