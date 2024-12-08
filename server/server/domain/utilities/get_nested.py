def get_nested(data, *args):
    # print("get_nested", data, args)
    try:
        if args and data:
            element = args[0]
            if element:
                # handle the case where the value is a list
                if isinstance(data, list) and element.isdigit():
                    # if arg is a number, return the value at that index
                    value = data[int(element)]
                else:
                    value = data.get(element)

                return value if len(args) == 1 else get_nested(value, *args[1:])
    except Exception as e:
        print(e)
    return None
