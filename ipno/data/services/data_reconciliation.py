import pandas as pd

from brady.models import Brady

DB_COLUMNS_MAP = {
    "brady_brady": {
        "columns": [
            field.name
            for field in Brady._meta.fields
            if field.name not in Brady.BASE_FIELDS
            and field.name not in Brady.CUSTOM_FIELDS
        ],
        "idx_column": "brady_uid",
    },
}


class DataReconcilliation:
    def reconcile_data(self, table_name, csv_file_name):
        columns = DB_COLUMNS_MAP[table_name]["columns"]
        idx_column = DB_COLUMNS_MAP[table_name]["idx_column"]

        # TODO: Remove hard-coded values
        df_csv = pd.read_csv(
            f"./ipno/data/tests/services/test_data/{csv_file_name}", usecols=columns
        ).fillna("")

        # TODO: Remove hard-coded values
        queryset = Brady.objects.all().values()
        df_db = pd.DataFrame(list(queryset), columns=columns).fillna("")

        df_all = pd.merge(df_db, df_csv, how="outer", indicator=True, on=idx_column)
        df_all.iloc[:, :-1].fillna("", inplace=True)

        added = df_all[df_all["_merge"] == "right_only"]
        added_rows = (
            df_csv[df_csv[idx_column].isin(added[idx_column].tolist())]
            .to_numpy()
            .tolist()
        )

        deleted = df_all[df_all["_merge"] == "left_only"]
        deleted_rows = (
            df_db[df_db[idx_column].isin(deleted[idx_column].tolist())]
            .to_numpy()
            .tolist()
        )

        # Create a boolean mask to identify rows where "_merge" is "both"
        merge_mask = df_all["_merge"] == "both"

        # Create a list to store the boolean masks for each column comparison
        diff_masks = []

        # Iterate over the columns and create boolean masks for each comparison
        for i in range(1, len(columns)):
            col_x = columns[i] + "_x"
            col_y = columns[i] + "_y"
            diff_mask = (df_all[col_x] != df_all[col_y]) & merge_mask
            diff_masks.append(diff_mask)

        # Combine the boolean masks using logical OR
        combined_mask = diff_masks[0]
        for mask in diff_masks[1:]:
            combined_mask |= mask

        # Select the rows that satisfy the combined mask
        df_diff = df_all[combined_mask]
        updated_rows = (
            df_csv[df_csv[idx_column].isin(df_diff[idx_column].tolist())]
            .to_numpy()
            .tolist()
        )

        # Reconcile the data
        return {
            "added_rows": added_rows,
            "deleted_rows": deleted_rows,
            "updated_rows": updated_rows,
        }
