'''
Generates ui-lovelace.yaml based on entities in configuration.yaml, with optional arguments

Replaces an existing ui-lovelace.yaml, so make sure to back up your old version


usage: change_ui_cards.py [-h] [-a [ADD [ADD ...]]] [-c] [-d [DELETE [DELETE ...]]]

optional arguments:
  -h, --help            show help message and exit
  -a [ADD [ADD ...]], --add [ADD [ADD ...]]
                        Add given space-separated entities to ui-lovelace.yaml, empty will add all defined entities
  -c, --configuration   Process configuration.yaml to update list of entities to draw from (must be included during
                        first run)
  -d [DELETE [DELETE ...]], --delete [DELETE [DELETE ...]]
                        Delete given space-separated entities from ui-lovelace.yaml, empty will delete all entities.
                        Note that an empty argument for --add will supercede this command.

'''
import argparse
import os
import yaml


class Loader(yaml.SafeLoader):
    # Loader class for '!include' in configuration.yaml
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node) -> list:
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, Loader)


def parse_ui_lovelace() -> list:
    '''
    Parses entities on the current ui-lovelace.yaml and returns a list of entities.
    '''
    ui_load = None
    try:
        with open('ui-lovelace.yaml', 'r') as stream:
            ui_load = yaml.load(stream, Loader)
    except FileNotFoundError as e:
        raise FileNotFoundError('No ui-lovelace.yaml to parse.') from e
    except yaml.YAMLError as exc:
        print(exc)

    if not ui_load:
        return

    current_entities = []
    if 'views' in ui_load:
        cards = ui_load['views'][0]  # List of all cards on ui
        for card in cards['cards']:
            if 'type' in card and card['type'] == 'vertical-stack':
                # parses the following: {'cards': [{'entities': ['entity.id']}], 'title': 'Entity Title'}
                entity = card['cards'][0]['entities'][0]
                title = card['title'] if 'title' in card else ''
                current_entities.append((entity, title))

    return current_entities


def config_parse_all() -> list:
    '''
    Parses entire configuration.yaml, and creates or replaces the entities.txt list of entities, returning the new list.
    '''
    config_load = None
    try:
        with open('configuration.yaml', 'r') as stream:
            config_load = yaml.load(stream, Loader)
    except FileNotFoundError as e:
        raise FileNotFoundError('No configuration.yaml to process.') from e
    except yaml.YAMLError as exc:
        print(exc)

    if not config_load:
        return

    ui_output_tags = []
    for item in config_load:
        parent_tag = config_load[item]  # List of items under each tag
        if item and item == 'input_select':  # Input_select tags
            for input_select in parent_tag:
                current_name = parent_tag[input_select]['name']
                if current_name:
                    current_name = current_name.split(',')[0]
                select_name = current_name if current_name else input_select
                ui_output_tags.append(
                    ('input_select.' + input_select, select_name))

        elif parent_tag and isinstance(parent_tag, list):  # Other tags
            first_tag = parent_tag[0]

            # Template tags (switches etc)
            if first_tag and isinstance(first_tag, dict) and 'platform' in first_tag:
                if first_tag['platform'] == 'template' and len(first_tag) == 2:

                    # Getting the entities
                    for tag in first_tag:
                        if tag != 'platform':
                            for entity_tag in first_tag[tag]:
                                # Adds entity and its name
                                entity = first_tag[tag][entity_tag]
                                entity_name = entity['friendly_name'] if 'friendly_name' in entity else entity_tag
                                ui_output_tags.append(
                                    (item + '.' + entity_tag, entity_name))  # Entity's id is its entity type + . + the entity tag
    if ui_output_tags:
        with open('entities.txt', 'w') as entities_file:
            for tag in ui_output_tags:
                entities_file.write(tag[0] + ',' + tag[1] + '\n')
        print('Generated new entities.txt')

    return ui_output_tags


def parse_existing() -> list:
    '''
    Parses existing entities.txt and returns the list of entities.
    '''
    ui_output_tags = []
    try:
        with open('entities.txt', 'r') as entities:
            for entity in entities:
                split_entity = entity.rstrip().split(',')
                ui_output_tags.append((split_entity[0], split_entity[1]))
    except FileNotFoundError as e:
        raise FileNotFoundError(
            'No entities.txt! Please parse the configuration.yaml first with the -c argument.') from e

    return ui_output_tags


def modify_ui(tags_list: list, sort: bool = False, compare_list: list = None) -> None:
    '''
    Modifies the ui-lovelace.yaml cards to be the given list of entities. Optionally sorts list and compares to a different list.
    '''
    if tags_list or tags_list == []:
        if sort:
            tags_list.sort(key=lambda x: x[1])  # Sort tags by the entity name
        # Create the cards on ui-lovelace.yaml
        ui_cards = []

        # Add custom Helion panel card
        ui_cards.append({'type': 'custom:helion-card'})

        for output_tag in tags_list:
            ui_cards.append(
                {'type': 'vertical-stack', 'title': output_tag[1], 'cards': [{'type': 'entities', 'entities': [output_tag[0]]}]})
        ui_lovelace_yaml = {'title': 'Helion', 'views': [
            {'path': 'helion', 'title': 'Helion', 'icon': 'mdi:home-variant', 'cards': ui_cards}]}

        # Replaces existing ui-lovelace.yaml
        with open('ui-lovelace.yaml', 'w') as f:
            f.write(yaml.dump(ui_lovelace_yaml))

        if compare_list and tags_list == compare_list:
            print('No update to ui-lovelace.yaml')
        else:
            print('Updated ui-lovelace.yaml')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create cards on the Home Assistant Lovelace dashboard.')
    parser.add_argument(
        '-a', '--add',
        help='Add given space-separated entities to ui-lovelace.yaml, empty will add all defined entities',
        nargs='*')
    parser.add_argument(
        '-c', '--configuration',
        help='Process configuration.yaml to update list of entities to draw from (must be included during first run)',
        action='store_true')
    parser.add_argument(
        '-d', '--delete',
        help='Delete given space-separated entities from ui-lovelace.yaml, empty will delete all entities. Note that an empty argument for --add  will supercede this command.',
        nargs='*')

    args = parser.parse_args()

    Loader.add_constructor('!include', Loader.include)

    print('Entities to add:', args.add if args.add != [] else 'All')

    print('Entities to delete:', args.delete if args.delete != [] else 'All')

    entities = config_parse_all() if args.configuration else parse_existing()
    original_cards = parse_ui_lovelace()
    current_cards = original_cards.copy()

    if args.delete:  # Delete given entities
        for delete_entity in args.delete:
            found = False
            for entity in list(current_cards):
                if entity[0] == delete_entity:
                    current_cards.remove(entity)
                    found = True
                    break
            if not found:
                print(delete_entity,
                      'was not deleted because it was not on the dashboard')

    elif not args.delete and args.delete != None:  # Clear list of entities
        current_cards = []

    if args.add:
        for add_entity in args.add:
            found = False
            for entity in entities:
                if entity[0] == add_entity:
                    current_cards.append(entity)
                    found = True
                    break
            if not found:
                print(add_entity, 'was not added because it was not in defined entities')
        modify_ui(current_cards, compare_list=original_cards)
    elif not args.add and args.add != None:  # Adds all entities
        modify_ui(entities, sort=True)

    # Otherwise just check if cards were modified at all (deletion)
    elif args.add == None:
        modify_ui(current_cards, compare_list=original_cards)
