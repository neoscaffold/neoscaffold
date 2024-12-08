def resolve_value_path(path: str):
    """Resolve a property path to a list of strings."""
    # temporarily replace instances of "\." with a placeholder
    if not path:
        return []

    replaced = path.replace("\\.", "§")
    property_path_list = replaced.split(".")
    # replace the placeholder with "."
    property_path_list = [x.replace("§", ".") for x in property_path_list]
    return property_path_list
