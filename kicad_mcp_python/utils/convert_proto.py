from google.protobuf.descriptor import FieldDescriptor

from kipy.proto.common.types import KiCadObjectType

from kipy.proto.board import board_types_pb2
from kipy.common_types import *
from pprint import pprint

from kipy.board_types import (
    ArcTrack,
    BoardShape,
    BoardText,
    BoardTextBox,
    Dimension,
    Field,
    Footprint3DModel,
    FootprintInstance,
    Net,
    Pad,
    Track,
    Via,
    Zone,
    # Group, will be addad 
)



descriptor_type_map = {
    FieldDescriptor.TYPE_DOUBLE: 'float',
    FieldDescriptor.TYPE_FLOAT: 'float',
    FieldDescriptor.TYPE_INT64: 'int',
    FieldDescriptor.TYPE_UINT64: 'int',
    FieldDescriptor.TYPE_INT32: 'int',
    FieldDescriptor.TYPE_FIXED64: 'float',
    FieldDescriptor.TYPE_FIXED32: 'float',
    FieldDescriptor.TYPE_BOOL: 'bool',
    FieldDescriptor.TYPE_STRING: 'string',
    FieldDescriptor.TYPE_GROUP: 'None',
    FieldDescriptor.TYPE_MESSAGE: 'message',
    FieldDescriptor.TYPE_BYTES: 'bytes',
    FieldDescriptor.TYPE_UINT32: 'int',
    FieldDescriptor.TYPE_ENUM: 'enum',
    FieldDescriptor.TYPE_SFIXED32: 'float',
    FieldDescriptor.TYPE_SFIXED64: 'float',
    FieldDescriptor.TYPE_SINT32: 'int',
    FieldDescriptor.TYPE_SINT64: 'int',
    FieldDescriptor.MAX_TYPE: 'max',
}


KICAD_TYPE_MAPPING = {
    'Arc': {
        'proto_class': board_types_pb2.Arc,
        'wrapper_class': ArcTrack,
        'object_type': KiCadObjectType.KOT_PCB_ARC
    },
    'BoardGraphicShape': {
        'proto_class': board_types_pb2.BoardGraphicShape,
        'wrapper_class': BoardShape,
        'object_type': KiCadObjectType.KOT_PCB_SHAPE
    },
    'BoardText': {
        'proto_class': board_types_pb2.BoardText,
        'wrapper_class': BoardText,
        'object_type': KiCadObjectType.KOT_PCB_TEXT
    },
    'BoardTextBox': {
        'proto_class': board_types_pb2.BoardTextBox,
        'wrapper_class': BoardTextBox,
        'object_type': KiCadObjectType.KOT_PCB_TEXTBOX
    },
    'Dimension': {
        'proto_class': board_types_pb2.Dimension,
        'wrapper_class': Dimension,
        'object_type': KiCadObjectType.KOT_PCB_DIMENSION
    },
    'Field': {
        'proto_class': board_types_pb2.Field,
        'wrapper_class': Field,
        'object_type': KiCadObjectType.KOT_PCB_FIELD
    },
    'Footprint3DModel': {
        'proto_class': board_types_pb2.Footprint3DModel,
        'wrapper_class': Footprint3DModel,
        'object_type': None  
    },
    'FootprintInstance': {
        'proto_class': board_types_pb2.FootprintInstance,
        'wrapper_class': FootprintInstance,
        'object_type': KiCadObjectType.KOT_PCB_FOOTPRINT
    },
    'Net': {
        'proto_class': board_types_pb2.Net,
        'wrapper_class': Net,
        'object_type': None  
    },
    'Pad': {
        'proto_class': board_types_pb2.Pad,
        'wrapper_class': Pad,
        'object_type': KiCadObjectType.KOT_PCB_PAD
    },
    'Track': {
        'proto_class': board_types_pb2.Track,
        'wrapper_class': Track,
        'object_type': KiCadObjectType.KOT_PCB_TRACE
    },
    'Via': {
        'proto_class': board_types_pb2.Via,
        'wrapper_class': Via,
        'object_type': KiCadObjectType.KOT_PCB_VIA
    },
    'Zone': {
        'proto_class': board_types_pb2.Zone,
        'wrapper_class': Zone,
        'object_type': KiCadObjectType.KOT_PCB_ZONE
    },
    # Not yet implemented in kipy.
    
    # 'Group': {
    #     'proto_class': board_types_pb2.Group,
    #     'wrapper_class': Group,
    #     'object_type': KiCadObjectType.KOT_PCB_GROUP
    # },
}

def get_proto_class(type_name):
    """Return proto class by string type name"""
    return KICAD_TYPE_MAPPING[type_name]['proto_class']

def get_wrapper_class(type_name):
    """Return wrapper class by string type name"""
    return KICAD_TYPE_MAPPING[type_name]['wrapper_class']

def get_object_type(type_name):
    """Return KiCad object type by string type name"""
    return KICAD_TYPE_MAPPING[type_name]['object_type']

def get_wrapper_from_proto(proto_obj):
    """Find wrapper class from proto object"""
    proto_type = type(proto_obj)
    for type_info in KICAD_TYPE_MAPPING.values():
        if type_info['proto_class'] == proto_type:
            return type_info['wrapper_class']
    return None


def convert_int(value):
    return int(value)
    
def convert_float(value):
    return float(value)

def convert_bool(value):
    return bool(value)

def convert_string(value):
    return str(value)

def convert_enum(enum_descriptor):
    enum_map = {}
    for value in enum_descriptor.values:
        enum_map[value.number] = value.name
    return enum_map

def convert_message(descriptor):
    args_dict = {}
    for field in descriptor.fields:
        args_dict[field.name] = {}
        if field.type == 11:  # FieldDescriptor.TYPE_MESSAGE
            args_dict[field.name][field.message_type.name] = convert_message(field.message_type)
        elif field.type == 14: # FieldDescriptor.TYPE_ENUM
            args_dict[field.name][field.enum_type.name] = convert_enum(field.enum_type)
        else:
            args_dict[field.name]['base_type'] = descriptor_type_map[field.type]
    return args_dict


def convert_proto_to_dict():
    """
    Convert a protobuf message to a dictionary representation.
    
    Args:
        proto_message: A protobuf message instance.
        
    Returns:
        dict: A dictionary representation of the protobuf message.
    """
    result = {}
    for name, message_class in KICAD_TYPE_MAPPING.items():
        result[name] = convert_message(message_class['proto_class'].DESCRIPTOR)

    return result 


BOARDITEM_TYPE_CONFIGS = convert_proto_to_dict()

# Define the required arguments for each item type.

BOARDITEM_TYPE_CONFIGS['Arc']['required_args']                  = ['start', 'end', 'center', 'angle']
BOARDITEM_TYPE_CONFIGS['BoardGraphicShape']['required_args']    = ['shape']
BOARDITEM_TYPE_CONFIGS['BoardText']['required_args']            = ['text']
BOARDITEM_TYPE_CONFIGS['BoardTextBox']['required_args']         = ['textbox']
BOARDITEM_TYPE_CONFIGS['Dimension']['required_args']            = ['text', 'text_position']
BOARDITEM_TYPE_CONFIGS['Field']['required_args']                = ['name', 'text']
BOARDITEM_TYPE_CONFIGS['Footprint3DModel']['required_args']     = ['filename', 'position', 'offset']
BOARDITEM_TYPE_CONFIGS['FootprintInstance']['required_args']    = ['position', 'definition'] # TODO
BOARDITEM_TYPE_CONFIGS['Net']['required_args']                  = ['code', 'name']
BOARDITEM_TYPE_CONFIGS['Pad']['required_args']                  = ['type']
BOARDITEM_TYPE_CONFIGS['Track']['required_args']                = ['start', 'end']
BOARDITEM_TYPE_CONFIGS['Via']['required_args']                  = ['position']
BOARDITEM_TYPE_CONFIGS['Zone']['required_args']                 = ['name', 'layers', 'outline']
# BOARDITEM_TYPE_CONFIGS['Group']['required_args']                = ['items']
    

if __name__ == "__main__":
    pprint(convert_proto_to_dict().keys())