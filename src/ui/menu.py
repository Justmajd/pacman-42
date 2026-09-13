from dataclasses import dataclass

@dataclass
class Menu:
    options: list[str]
    selected_index: int = 0

    def move_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1

    def move_down(self):
        if self.selected_index < len(self.options) - 1:
            self.selected_index += 1

    def selected_option(self):
        return self.options[self.selected_index]