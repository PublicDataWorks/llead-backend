def data_period(periods, years):
    results = []

    all_years = set(years)
    current_year = None
    for start_year, end_year in periods:
        all_years |= set(range(start_year, end_year + 1))

    for year in sorted(list(all_years)):
        if current_year and year == current_year + 1:
            results[-1].append(year)
        else:
            results.append([year])
        current_year = year

    return [
        f'{item[0]}{f"-{item[-1]}" if len(item) > 1 else ""}'
        for item in results
    ]
