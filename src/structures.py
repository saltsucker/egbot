from sc2.unit import Unit

class NewStructure:
    def __init__(self, unit, name):
        self.tag = unit.tag
        self.name = name
        self.unit = unit
        self.position = unit.position

class SpawningPool(NewStructure):
    def __init__(self, unit):
        super().__init__(unit, 'SpawningPool')

class Hatchery(NewStructure):
    def __init__(self, unit):
        super().__init__(unit, 'Hatchery')
        self.hq = False
        self.is_lair = False
        self.is_hive = False
        self.position = unit.position
        self.assigned_queen_tag = None
        
class Extractor(NewStructure):
    def __init__(self, unit):
        super().__init__(unit, 'Extractor')