from typing import Dict

from ..pcbmodule import PCBTool
from ...core.ActionFlowManager import ActionFlowManager
from ...core.mcp_manager import ToolManager
from ...utils.convert_proto import (
    BOARDITEM_TYPE_CONFIGS, 
    get_proto_class,
    get_wrapper_class,
    get_object_type
)

from kipy.geometry import Vector2, Angle
from kipy.proto.common.types import KIID
from google.protobuf import message_factory
from google.protobuf.descriptor import FieldDescriptor

from mcp.server.fastmcp import FastMCP

def convert_to_object(descriptor, args):
    wrapper = message_factory.GetMessageClass(descriptor)
    wrapper = wrapper()
    for field in descriptor.fields:
        if field.name in args:
            if field.type == FieldDescriptor.TYPE_MESSAGE:  
                if field.label == FieldDescriptor.LABEL_REPEATED:
                    # For repeated fields
                    repeated_field = getattr(wrapper, field.name)
                    for item in args[field.name]:
                        nested_obj = convert_to_object(field.message_type, item)
                        repeated_field.append(nested_obj)
                else:
                    # For single message fields
                    nested_obj = convert_to_object(
                        field.message_type, 
                        args[field.name]
                    )
                    getattr(wrapper, field.name).CopyFrom(nested_obj)

            else:
                if field.type == FieldDescriptor.TYPE_ENUM:
                    if field.label == FieldDescriptor.LABEL_REPEATED:
                        getattr(
                            wrapper, 
                            field.name, 
                        ).extend(args[field.name])
                    else:
                        setattr(
                        wrapper, 
                        field.name, 
                        args[field.name]
                    )
                    
                else:
                    setattr(
                        wrapper, 
                        field.name, 
                        args[field.name]
                    )

    return wrapper


def get_item_list_config(board, item_type: str):
    '''
    Retrieves the list of items of the specified type from the board.
    '''
    result = {}
    result['args'] = BOARDITEM_TYPE_CONFIGS[item_type]
    result['item_list'] = {
        item.id.value:item for item in board.get_items(
        get_object_type(item_type)
        )}
    return result


def get_items_by_id(board, item_type, id):
    '''
    In KiCad version 9.0.4 and below, get_items_by_id does not exist,
    so we use get_items to search for items.
    https://gitlab.com/kicad/code/kicad/-/merge_requests/2256
    '''
    item_dict = {item.id.value:item for item in board.get_items(get_object_type(item_type))}
    return item_dict.get(id)

            
class CreateItemFlowManager(ActionFlowManager, PCBTool):
    """A class that manages the step-by-step flow of Create Item"""
    
    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
        
        self._register_tool()

    def _register_tool(self):
        self.action_setter(self.create_item_step_1)
        self.action_setter(self.create_item_step_2)
        self.action_setter(self.create_item_step_3)
        
    # TODO: 
    # Will change to a class that manages the step-by-step flow of create_item. 
    # Writing functions one by one like this is not ideal.
    def create_item_step_1(self):
        """ # create_item_1
        
        Entrance tool to create a new item in the PCB design.
        This function serves as an entry point and acts like --help before directly using the kicad.board API.
        If you already know the types, you can skip this function and call create_item_step_2 directly.
     
        Returns:
            Available item types.
            
        Next action:
            create_item_step_2
        """
        # Item creation logic (e.g., creating an item using PCB tools)
        board_item_type = BOARDITEM_TYPE_CONFIGS.keys()

        return self.response_formatter(board_item_type)
    
        
    def create_item_step_2(
        self, 
        item_type: str
        ):
        """ # create_item_2
        
        Returns the types of arguments required for creating the next item.
        The operation of Footprint is handled by searching the footprint table.
        
        Args:
            item_type (str): The item type (e.g., 'footprint', 'symbol')
        
        Return: 
            dict: Type hints for the arguments required to create the item
            
        Next action:
            create_item_step_3
        """

        return self.response_formatter(BOARDITEM_TYPE_CONFIGS[item_type])
    
    
    def create_item_step_3(
        self, 
        item_type: str, 
        args: dict
        ):
        """ # create_item_3
        
        Creates the item with the specified type and arguments.
        
        Other arguments than required_args are treated as optional.
        
        Args:
            item_type (str): The item type (e.g., 'footprint', 'symbol')
            args (dict): The arguments required to create the item
        
        Returns:
            str: The ID or name of the created item
            
        Next action:
            verify_pcb_step_1
        """
        self.initialize_board() # Initialize the board
        
        new_class = convert_to_object(get_proto_class(item_type).DESCRIPTOR, args)
        kipy_wrapper = get_wrapper_class(item_type)
        
        # Create the item using the KiCad API
        try:
            item_id = self.board.create_items(kipy_wrapper(new_class))
            return self.response_formatter(item_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create the item: {str(e)}")
    
    
    
class EditItemFlowManager(ActionFlowManager, PCBTool):
    """A class that manages the step-by-step flow of Edit Item"""
    
    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
        
        self._register_tool()


    def _register_tool(self):
        self.action_setter(self.edit_item_step_1)
        self.action_setter(self.edit_item_step_2)
        self.action_setter(self.edit_item_step_3)
    
    
    def edit_item_step_1(self):
        """ # edit_item_1
        
        Entrance tool to edit item in the PCB design.
        This function serves as an entry point and acts like --help before directly using the kicad.board API.
        If you already know the types, you can skip this function and call edit_item_step_2 directly.
        
        Returns:
            list: A list of item types
            
        Next action:
            edit_item_step_2
        """
        item_types = BOARDITEM_TYPE_CONFIGS.keys()
        return self.response_formatter(item_types)
    
    
    def edit_item_step_2(self, item_type: str): 
        """ # edit_item_2
        
        This function retrieves the list of items of the specified type.
        
        Args:
            item_type (str): The item type (e.g., 'footprint', 'symbol')
        
        Returns:
            item_list: A list of items of that type
            args: Type hints for the arguments required to create the item
            
        Next action:
            edit_item_step_3
        """
        self.item_type_cache = item_type # version 9.0.0
        
        result = get_item_list_config(self.board, item_type)
        return self.response_formatter(result)


    # TODO: Add the ability to edit multiple items.
    # ex) edit_item_step_3(item_id: Sequence[str], args: Dict)
    def edit_item_step_3(self, item_id: str, args: Dict):
        """ # edit_item_3
        
        Edits the specified item with the provided arguments.
        It is recommended to exclude properties such as position and orientation since move_item exists separately.
            
        Args:
            item_id (str): ID of the item to be edited
            args (Dict): Properties of the item to be edited
            
        Returns:
            str: ID or name of the edited item
            
        Next action:
            verify_pcb_step_1
        """
        self.initialize_board() # Initialize the board
        
        
        id = KIID()
        id.value = item_id
        # target_item_proto = self.board.get_items_by_id([id])[0].proto # version 9.0.4
        
        # Get the item protocol wrapper
        target_item_proto = get_items_by_id(
            board=self.board, 
            item_type=self.item_type_cache, 
            id=item_id
            ).proto  # version 9.0.0
        
        
        # Get the protocol class for the item type
        new_class = convert_to_object(target_item_proto.DESCRIPTOR, args)

        # Overwrite the field values of the existing item with the new values
        for field_descriptor, value in new_class.ListFields():
            _cls = getattr(target_item_proto, field_descriptor.name)
            _cls.CopyFrom(value)
            
        # Create a new item protocol wrapper
        return_wrapper = get_wrapper_class(target_item_proto.DESCRIPTOR.name)(target_item_proto)
        try:
            edit_item = self.board.update_items(return_wrapper)
            return self.response_formatter(edit_item)
        except Exception as e:
            raise RuntimeError(f"Failed to move the item: {str(e)}")
        
        
        
class MoveItemFlowManager(ActionFlowManager, PCBTool):
    """A class that manages the step-by-step flow of move Item"""
    
    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
        
        self._register_tool()


    def _register_tool(self):
        self.action_setter(self.move_item_step_1)
        self.action_setter(self.move_item_step_2)
        self.action_setter(self.move_item_step_3)
    
    
    def move_item_step_1(self):
        """ # move_item_1
        
            Entrance tool to move item in the PCB design.
            This function serves as an entry point and acts like --help before directly using the kicad.board API.
            If you already know the types, you can skip this function and call move_item_step_2 directly.
        Returns:
            list: A list of item types
            
        Next action:
            move_item_step_2
        """
        
        item_types = BOARDITEM_TYPE_CONFIGS.keys()
        return self.response_formatter(item_types)
    
    
    def move_item_step_2(self, item_type: str): 
        """ # move_item_2
        
        This function retrieves the list of items of the specified type.
        
        Args:
            item_type (str): The item type (e.g., 'footprint', 'symbol')
        
        Returns:
            item_list: A list of items of that type
            args: Type hints for the arguments required to create the item
            
        Next action:
            move_item_step_3
        """
        self.item_type_cache = item_type # version 9.0.0
        
        result = {
        item.id.value:item for item in self.board.get_items(
        get_object_type(item_type)
        )}
        return self.response_formatter(result)


    # TODO: Add the ability to modify multiple items.
    # ex) move_item_step_3(item_id: Sequence[str], args: Dict)
    def move_item_step_3(self, item_id: str, args: Dict):
        """ # move_item_3
        
        Args:
            item_id (str): ID of the item to be modified
            args: 

                if item_type is 'track', args should contain:
                    start (Tuple[int, int]): Position to add to the item's start position (x, y units)
                    end (Tuple[int, int]):  Position to add to the item's end position (x, y units)
                else, args should contain:
                    xy_nm (Optional[Tuple[int, int]]): Position to add to the item's original location (x, y units, optional)
                    angle (Optional[int]): New rotation angle for the item (degrees, optional)
                
        Returns:
            str: ID or name of the modified item
            
        Next action:
            verify_pcb_step_1
        """
        self.initialize_board() # Initialize the board
        
        # will be added in version 9.0.4
        
        # id = KIID()
        # id.value = item_id
        
        # target_item = self.board.get_items_by_id([id])[0] 
        
        target_item = get_items_by_id(
            board=self.board, 
            item_type=self.item_type_cache, 
            id=item_id
            )  # version 9.0.0
        
        if isinstance(target_item, get_wrapper_class('Track')):
            # For 'Track', we need to handle start and end positions
            start = args.get('start')
            end = args.get('end')
            
            if start is not None:
                x_start, y_start = start
                target_item.start += Vector2.from_xy(x_start, y_start)
            
            if end is not None:
                x_end, y_end = end
                target_item.end += Vector2.from_xy(x_end, y_end)
        else:
            xy_nm = args.get('xy_nm')
            angle = args.get('angle')
            
            # Update the item's position and orientation
            if xy_nm is not None:
                x_nm, y_nm = xy_nm
                target_item.position += Vector2.from_xy(x_nm, y_nm)
        
            if angle is not None:
                target_item.orientation += Angle.from_degrees(angle)

        try:
            move_item = self.board.update_items(target_item)
            return self.response_formatter(move_item)
        except Exception as e:
            raise RuntimeError(f"Failed to move the item: {str(e)}")
        
        
        
class RemoveItemFlowManager(ActionFlowManager):
    """A class that manages the step-by-step flow of remove Item"""
    
    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
        
        self._register_tool()


    def _register_tool(self):
        self.action_setter(self.remove_item_step_1)
    
    
    def remove_item_step_1(self, item_ids: list[str]):
        """ # move_item_1
        
        Returns:
            item_ids (list): List of item IDs to be removed.
            
        Next action:
            verify_pcb_step_1
        """
        self._initialize_board()
        
        
        kiid_ids = []
        for item_id in item_ids:
            kiid = KIID()
            kiid.value = item_id
            kiid_ids.append(kiid)
        
        response = self.board.remove_items_by_id(kiid_ids)
        return self.response_formatter(response)
    
    

class BoardAnalyzer(ToolManager, PCBTool):
    '''
    A class that gathers tools for analyzing the board and retrieving information, used in manipulate_tool. 
    '''

    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
        
        self.add_tool(self.get_board_status)        
        self.add_tool(self.get_items_by_type)        
        self.add_tool(self.get_item_type_args_hint)        
        
        
    def get_board_status(self):
        f'''
        Retrieves the status of the current board.
        Returns:
            str: A string indicating the status of the board.
        '''
        self.initialize_board()
        result = {}
        for item_type in BOARDITEM_TYPE_CONFIGS.keys():
            item_wrapper = get_object_type(item_type)
            try:
                result[item_type] = [item for item in self.board.get_items(get_object_type(item_type))]
            except Exception as e:
                result[item_type] = f'Not yet implemented, {str(e)}'
        return result
        
    
    def get_items_by_type(self, item_type: str):
        f'''
        Retrieves the list of items of the specified type from the board.
        The item_type should be one of the keys in BOARDITEM_TYPE_CONFIGS.
        BOARDITEM_TYPE_CONFIGS.keys(): {BOARDITEM_TYPE_CONFIGS.keys()}
        
        Args:
            item_type (str): The type of items to retrieve.
        Returns:
            dict: A dictionary containing the list of items of the specified type.
        '''
        self.initialize_board()
        
        result = {
            item.id.value:item for item in self.board.get_items(
            get_object_type(item_type)
            )}
        return result
    
    
    def get_item_type_args_hint(self, item_type: str):
        '''
        Retrieves the configuration arguments for a specific board item type.
        
        Args:
            item_type (str): The type of board item.
        Returns:
            dict: A dictionary containing the configuration arguments for the specified item type.    
        '''
        self.initialize_board()
        
        result = BOARDITEM_TYPE_CONFIGS[item_type]
        return result
    
    
class ManipulationTools:
    
    @classmethod
    def register_tools(self, mcp: FastMCP):
        '''
        Registers the manipulation tools with the given MCP instance.
        
        Args:
            mcp (FastMCP): The MCP instance to register the tools with.
        '''
        # Register flow managers
        CreateItemFlowManager(mcp)
        EditItemFlowManager(mcp)
        MoveItemFlowManager(mcp)
        RemoveItemFlowManager(mcp)
        
        # Register board analyzer
        BoardAnalyzer(mcp)
