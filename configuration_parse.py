'''
Generates the ui-lovelace.yaml based on the template entities in configuration.yaml

Warning: replaces an existing ui-lovelace.yaml, so make sure to back up your old version

'''
import yaml
import os


class Loader(yaml.SafeLoader):
    # Loader class for "!include" in configuration.yaml
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node) -> list:
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, Loader)


def config_parse() -> None:
    config_load = None
    with open("configuration.yaml", "r") as stream:
        try:
            config_load = yaml.load(stream, Loader)
        except yaml.YAMLError as exc:
            print(exc)

    if not config_load:
        return

    ui_output_tags = []
    for item in config_load:
        parent_tag = config_load[item]
        if parent_tag and isinstance(parent_tag, list):  # Top level tags
            first_tag = parent_tag[0]

            # Checking if it is a template
            if first_tag and isinstance(first_tag, dict) and "platform" in first_tag:
                if first_tag["platform"] == "template" and len(first_tag) == 2:

                    # Getting the entities
                    for tag in first_tag:
                        if tag != "platform":
                            for entity_tag in first_tag[tag]:
                                # Adds entity and its name
                                entity = first_tag[tag][entity_tag]
                                entity_name = entity["friendly_name"] if "friendly_name" in entity else entity_tag
                                ui_output_tags.append(
                                    (item + "." + entity_tag, entity_name))  # Entity's id is its entity type + . + the entity tag

    if ui_output_tags:
        ui_cards = []
        # Create the cards on ui_lovelace.yaml
        for output_tag in ui_output_tags:
            ui_cards.append(
                {"type": "entities", "entities": [output_tag[0]], "name": output_tag[1]})
        ui_lovelace_yaml = {"title": "Helion", "views": [
            {"path": "helion", "title": "Helion", "icon": "mdi:home-variant", "cards": ui_cards}]}

        # Replaces existing ui_lovelace.yaml
        f = open("ui-lovelace.yaml", "w")
        f.write(yaml.dump(ui_lovelace_yaml))
        f.close()


if __name__ == "__main__":
    Loader.add_constructor('!include', Loader.include)
    config_parse()
