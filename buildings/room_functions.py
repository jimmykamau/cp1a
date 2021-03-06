import sys


from .amity_class import Amity
current_rooms = Amity()


from .office_class import Office
from .livingspace_class import LivingSpace
import humans as humans_functions
from amity_db.models_functions import \
    add_rooms, populate_rooms, populate_room_occupants


def populate_rooms_from_db():
    rooms_from_db = populate_rooms()
    for room in rooms_from_db:
        room_details = [{
            "room_capacity": room.room_capacity,
            "room_name": room.room_name,
            "room_type": room.room_type,
            "people_allocated": []
        }]
        if room.room_type == "Living space":
            created_room = {r["room_name"]: LivingSpace(
                **r) for r in room_details}
            current_rooms.available_livingspaces.append(room.room_name)
        elif room.room_type == "Office":
            created_room = {r["room_name"]: Office(**r) for r in room_details}
            current_rooms.available_offices.append(room.room_name)

        room_occupants = populate_room_occupants(room.room_name)
        for occupant in room_occupants:
            created_room[room_details[0]["room_name"]
                         ].add_person_to_room(occupant.person_id)

        current_rooms.rooms.update(created_room)

    return " [*] Rooms successfully loaded from database...\n"


def create_room(args):
    """
    Create rooms based on user's input
    """

    room_type = None

    if room_type is None:
        room_option = input(
            "Enter the room type; O for Office and L for Living space: ")
        room_type = room_option.upper()

    if room_type == "L":
        rooms = [
            {
                "room_capacity": 4,
                "room_name": r,
                "room_type": "Living space",
                "people_allocated": []
            }
            for r in args["<room_name>"]
        ]
        created_rooms = {r["room_name"]: LivingSpace(**r) for r in rooms}

        for r in args["<room_name>"]:
            current_rooms.available_livingspaces.append(r)

    elif room_type == "O":
        rooms = [{"room_capacity": 6, "room_name": r, "room_type": "Office",
                  "people_allocated": []} for r in args["<room_name>"]]
        created_rooms = {r["room_name"]: Office(**r) for r in rooms}
        for r in args["<room_name>"]:
            current_rooms.available_offices.append(r)

    else:
        message = \
            "Allowed commands are only 'O' for Office and 'L' for Living space"
        return message

    try:
        current_rooms.rooms.update(created_rooms)
        message = "The rooms"
        for room in args["<room_name>"]:
            message += " " + str(room)
        message += " have been created successfully"

    except Exception:
        message = "Error encountered while creating rooms"

    return(message)


def list_rooms():
    """
    List the rooms in Amity. Returns information about all rooms in Amity
    """

    message = ""
    if len(current_rooms.rooms) == 0:
        return "No rooms have been created"

    try:
        for room in current_rooms.rooms:
            message += ("\nROOM NAME: {}\n"
                        "ROOM TYPE: {}\n"
                        "ROOM CAPACITY: {}\n"
                        "NUMBER OF OCCUPANTS: {}\n"
                        "NUMBER OF EMPTY SLOTS: {}\n"
                        .format(
                            current_rooms.rooms[room].room_name,
                            current_rooms.rooms[room].room_type,
                            current_rooms.rooms[room].room_capacity,
                            len(current_rooms.rooms[room].people_allocated),
                            int(
                                current_rooms.rooms[room].room_capacity
                            ) - int(
                                len(current_rooms.rooms[room].people_allocated)
                            )
                        )
                        )
    except Exception:
        message = "Error while retrieving room information"

    return message


def room_occupants(args):
    """
    Return the occupants of a room
    """

    try:
        message = "OCCUPANTS OF {}:".format(args["<room_name>"])
        if len(current_rooms.rooms[args["<room_name>"]].people_allocated) == 0:
            return "No occupants in this room"
        for person_id in \
                current_rooms.rooms[args["<room_name>"]].people_allocated:
            message += "\n{}".format(
                humans_functions.person_functions.people[person_id].name)
        return message
    except Exception:
        return "Error while retrieving room information"


def print_allocations(args):
    """
    Return a list of allocations
    """

    message = ""
    for room in current_rooms.rooms:
        message += "{}\n".format(current_rooms.rooms[room].room_name)
        message += "-" * 40
        message += "\n"
        for person_id in current_rooms.rooms[room].people_allocated:
            message += "{}, ".format(
                humans_functions.person_functions.people[person_id].name)
        message += "\n\n\n"

    if args['-o'] and ['<file_location>'] is not None:
        filename = args['<file_location>']
        try:
            with open(filename, 'wt') as f:
                f.write(message)
            message = "Allocations have been printed to {}".format(filename)
        except Exception:
            message = str(sys.exc_info()[0])
    elif (
        args['<file_location>'] is not None and
        args['-o'] is False
    ) or (
        args['-o'] is not False and
        args['<file_location>'] is None
    ):
        message = "Specify the file to output to after the `-o` argument"

    return message


def add_rooms_to_db():
    return add_rooms(current_rooms.rooms)
