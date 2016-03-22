class DummyModule(object):
    """DummyModule - Do no quality control
    ===============

    A call to DummyModule.getReport always returns:

        {
            "dummy" : "nothing to report"
        }

    """
    def __init__(self, app):
        """Initialise a DummyModule for QC handling"""
        self.app = app

    def getReport(self, session_id):
        return dict(dummy='nothing to report')