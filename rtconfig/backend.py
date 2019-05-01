import os
import io
import json
import logging
from rtconfig.utils import OSUtils, object_merge


class BaseBackend:
    def read(self):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError


class JsonFileBackend(BaseBackend):
    __charset__ = "utf-8"
    _extension = '.json'

    def __init__(self, directory, config_name, logger=None, merge=True):
        self.directory = directory
        self.config_name = config_name
        self.os_util = OSUtils()
        self.merge_file = merge
        self.logger = logger or logging.getLogger(__name__)

        if not self.os_util.directory_exists(self.directory):
            raise Exception('Json file data store directory not exist: %s' % self.directory)
        self.file_name = config_name + self._extension
        self.file_path = os.path.join(self.directory, self.file_name)

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
