# -*- coding: utf-8 -*-

import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SpeckleQGIS class from file SpeckleQGIS.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    try:
        from plugin_utils.installer import ensure_dependencies, startDebugger
        from plugin_utils.panel_logging import logger

        # Set qgisInterface to enable log_to_user notifications
        logger.qgisInterface = iface
        iface.pluginToolBar().setVisible(True)

        # Ensure dependencies are installed in the machine
        startDebugger()
        ensure_dependencies("QGISv3")

        from speckle_qgis_v3 import SpeckleQGIS

        return SpeckleQGIS(iface)

    except Exception as e:
        # If there's an error during plugin initialization, raise it with context
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Failed to initialize Speckle QGIS plugin: {str(e)}") from e
