class MockDataReconciliation:
    def __init__(self, return_data):
        self.return_data = return_data

    def reconcile_data(self):
        return self.return_data
