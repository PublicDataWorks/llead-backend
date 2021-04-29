def data_period(years):
    results = []
    current_year = None

    for year in sorted(list(set(years))):
        if current_year and year == current_year + 1:
            results[-1].append(year)
        else:
            results.append([year])
        current_year = year

    return [
        f'{item[0]}{f"-{item[-1]}" if len(item) > 1 else ""}'
        for item in results
    ]


def sort_items(items, attrs):
    def get_sort_key(item, item_attrs):
        results = []
        for attr in item_attrs:
            value = getattr(item, attr)
            results.append((value is None, str(value)))
        return results

    return sorted(
        items,
        key=lambda item: get_sort_key(item, attrs)
    )
