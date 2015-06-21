# coding=utf-8
from __future__ import absolute_import
import os

__author__ = "Jarek Szczepanski <imrahil@imrahil.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2014 Jarek Szczepanski - Released under terms of the AGPLv3 License"

from flask import jsonify
import flask

import octoprint.plugin

class PrintHistoryPlugin(octoprint.plugin.StartupPlugin,
                         octoprint.plugin.EventHandlerPlugin,
                         octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.BlueprintPlugin,
                         octoprint.plugin.TemplatePlugin,
                         octoprint.plugin.AssetPlugin):

    def on_after_startup(self):
        self._logger.info("Plugins folder: %s" % self._settings.getBaseFolder("plugins"))
        self._logger.info("Uploads folder: %s" % self._settings.getBaseFolder("uploads"))

     ##~~ TemplatePlugin API
    def get_template_configs(self):
        return [
            dict(type="tab", name="History")
        ]

    ##~~ AssetPlugin API
    def get_assets(self):
        return {
            "js": ["js/printhistory.js", "js/jquery.flot.pie.js", "js/jquery.flot.time.js", "js/jquery.flot.stack.js", "js/bootstrap-editable.min.js", "js/knockout.x-editable.js"],
            "css": ["css/printhistory.css", "css/bootstrap-editable.css"]
        }

    #~~ EventPlugin API
    def on_event(self, event, payload):
        from . import eventHandler
        return eventHandler.eventHandler(self, event, payload)


    @octoprint.plugin.BlueprintPlugin.route("/history", methods=["GET"])
    def getHistoryData(self):
        import yaml

        self._logger.debug("Rendering history.yaml")
        path = os.path.join(self._settings.getBaseFolder("uploads"), "history.yaml")

        history_dict = {}
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    history_dict = yaml.safe_load(f)
                except:
                    raise IOError("Couldn't read history data from {path}".format(path=path))

            if history_dict is not None:
                self._logger.debug("Returning data")
                # return the dict sorted by timestamp
                history_dict_sorted = history_dict.sort(
                    key=lambda x: x.timestamp, reverse=True)
                return jsonify(history=history_dict_sorted)
            else:
                self._logger.debug("Empty file history.yaml")
                return jsonify({})
        else:
            self._logger.debug("File doesn't exist")
            return jsonify({})

    @octoprint.plugin.BlueprintPlugin.route("/history/<int:identifier>", methods=["DELETE"])
    def deleteHistoryData(self, identifier):
        self._logger.debug("Delete file: %s" % identifier)

        import yaml
        from octoprint.server import NO_CONTENT

        path = os.path.join(self._settings.getBaseFolder("uploads"), "history.yaml")

        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    history_dict = yaml.safe_load(f)

                    if identifier in history_dict:
                        self._logger.debug("Found a identifier: %s" % identifier)
                        del history_dict[identifier]

                        if len(history_dict) == 0:
                            open(path, "w")
                        else:
                            with open(path, "w") as f2:
                                yaml.safe_dump(history_dict, f2, default_flow_style=False, indent="  ", allow_unicode=True)
                except:
                    raise IOError("Couldn't read history data from {path}".format(path=path))

        return NO_CONTENT

    @octoprint.plugin.BlueprintPlugin.route("/savenote", methods=["POST"])
    def saveNote(self):
        identifier = int(flask.request.values["pk"])
        self._logger.debug("Saving note: %s" % identifier)

        import yaml
        from octoprint.server import NO_CONTENT

        path = os.path.join(self._settings.getBaseFolder("uploads"), "history.yaml")

        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    history_dict = yaml.safe_load(f)

                    if identifier in history_dict:
                        self._logger.debug("Found a identifier: %s" % identifier)
                        history_dict[identifier]["note"] = flask.request.values["value"]

                        with open(path, "w") as f2:
                            yaml.safe_dump(history_dict, f2, default_flow_style=False, indent="  ", allow_unicode=True)
                except:
                    raise IOError("Couldn't read history data from {path}".format(path=path))

        return NO_CONTENT

    @octoprint.plugin.BlueprintPlugin.route("/export/<string:exportType>", methods=["GET"])
    def exportHistoryData(self, exportType):
        from . import export
        return export.exportHistoryData(self, exportType)

__plugin_name__ = "Print History Plugin"
__plugin_implementation__ = PrintHistoryPlugin()
