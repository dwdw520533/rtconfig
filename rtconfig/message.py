import json
import attr
from rtconfig.utils import convert_dt, strftime


@attr.s
class Message:
    message_type = attr.ib(validator=attr.validators.instance_of(str))
    config_name = attr.ib(validator=attr.validators.instance_of(str))
    hash_code = attr.ib(validator=attr.validators.instance_of(str))
    data = attr.ib(default=dict(), validator=attr.validators.instance_of(dict))
    context = attr.ib(default=dict(), validator=attr.validators.instance_of(dict))
    request = attr.ib(default=None)
    lut = attr.ib(default=None, converter=convert_dt)

    def to_dict(self, indent=0):
        context = self.context
        context.update(
            headers=dict(self.request.headers)
        )
        return dict(
            message_type=self.message_type,
            config_name=self.config_name,
            hash_code=self.hash_code,
            data=self.data,
            context=json.dumps(context, indent=indent) if indent else context,
            lut=strftime(self.lut)
        )

    def to_string(self):
        return json.dumps(dict(
            message_type=self.message_type,
            config_name=self.config_name,
            hash_code=self.hash_code,
            data=self.data,
        ))
