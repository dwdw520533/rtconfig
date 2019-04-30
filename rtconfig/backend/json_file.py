import os
import io
import json
import logging
from rtconfig.backend.base import BaseBackend
from rtconfig.utils import OSUtils, object_merge


class FileBackend(BaseBackend):
    def __init__(self, directory, project_name, extension='.json', logger=None, merge=True):
        self.directory = directory
        self.project_name = project_name
        self.os_util = OSUtils()
        self.merge_file = merge
        self.logger = logger or logging.getLogger(__name__)

        if not self.os_util.directory_exists(self.directory):
            raise Exception('Json file data store directory not exist: %s' % self.directory)
        self.file_name = project_name + extension
        self.file_path = os.path.join(self.directory, self.file_name)


class JsonFileBackend(FileBackend):
    __charset__ = "utf-8"

    def exists(self):
        return self.os_util.directory_exists(self.file_path)

    def read(self):
        try:
            with io.open(self.file_path, encoding=self.__charset__) as open_file:
                source_data = json.load(open_file)
            self.logger.debug("Backend read json: {}".format(self.file_path))
        except IOError:
            self.logger.debug("Backend read json: {} (Ignored, file not Found)".format(self.file_path))
            source_data = {}
        return source_data

    def write(self, source_data):
        if self.exists() and self.merge_file:
            with io.open(self.file_path, encoding=self.__charset__) as open_file:
                object_merge(json.load(open_file), source_data)

        with io.open(self.file_path, "w", encoding=self.__charset__) as open_file:
            json.dump(source_data, open_file)
