from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units


class MacroManager:

    macro_actions = []

    def __init__(self, bot):
        self.bot = bot
        self.hq = None
        self.structures = []
        self.pool_name = "SpawningPool"
        # self.larva: Units = Units([], self)
        # dk why you need to typecast this as a unit
        # self.hq: Unit = self.bot.townhalls.first

        # self.hq = structures.firstexpansion
        #        self.used_tumors: Set[int] = set()
        self.inject_interval = 100


    def add_structure(self, structure: Unit):
        self.structures.append(structure)

    async def build_pool(self):  # Build spawning pool
        if not len(list(filter(lambda struct: struct.name == self.pool_name, self.structures))) == 1: 
            if not self.bot.already_pending(UnitTypeId.SPAWNINGPOOL):
                if self.bot.can_afford(UnitTypeId.SPAWNINGPOOL):
                    await self.bot.build(
                        UnitTypeId.SPAWNINGPOOL,
                        near=self.bot.townhalls.first.position.towards(self.bot.game_info.map_center, 5),
                    )

    # async def build_gas(self):
    #     if self.bot.can_afford(UnitTypeId.EXTRACTOR):
    #         # May crash if we dont have any drones
    #         for hatch in self.bot.townhalls.ready:
    #             for vg in self.bot.vespene_geyser.closer_than(10, hatch):
    #                 if not self.bot.worker_en_route_to_build(UnitTypeId.EXTRACTOR):
    #                     await self.bot.build(UnitTypeId.EXTRACTOR, vg)
    #                     break


 

        
    # hatcheries = filter(lambda x: x if x.name == "Hatchery", self.structures)

    # def _position_blocks_expansion(self, pos):
    #     """
    #     TODO: figure out why Union and self.expansion_locations_list say they have an error yet no issues arise in the code.  Suspect Pylint is goofed.
    #     Note: used pos: Union[Point2, Unit] instead of just pos: Point2 in attempt to fix a y is -1, self.height is 176 error.  Seems to work...

    #     From Glenn: You don't need to instantiate pos in this function because you're passing a position to this function. Python already knows what it is.
    #                 Also, put these docstring inside the function you are referring to.
    #                 we should do that for future TODO's as well.
    #     """

    #     blocks_expansion = False
    #     for expansion in self.bot.expansion_locations_list:
    #         if pos.distance_to(expansion) < 6:
    #             blocks_expansion = True
    #             break
    #     return blocks_expansion

    # # Glenn: Idk where this belongs
    # # TODO: Will need to add an array or vector of buildings for "worker_en_route_to_build" to check instead of only HATCHERY
    # # TODO: Check for max number of hatcheries

    # async def expand(self):       
    #     # Expands to nearest location when 300 minerals are available up to maximum 5 hatcheries
    #     if (
    #         self.bot.townhalls.ready.amount + self.bot.already_pending(UnitTypeId.HATCHERY)
    #         < 5
    #     ):
    #         if self.bot.can_afford(UnitTypeId.HATCHERY):
    #             await self.bot.expand_now()

    async def build_drone(self, larvae: UnitTypeId, drone: UnitTypeId, overlord: UnitTypeId):
        # corrects game opening ->12:drone, 13:overlord, 14:drone, then 3 drones when OL pop
        if (
            larvae
            and self.bot.can_afford(drone)
            and (self.bot.supply_left > 1 or self.bot.already_pending(overlord))
            >= 1
        ):
            if (
                self.bot.supply_workers
                - self.bot.worker_en_route_to_build(UnitTypeId.HATCHERY)
                + self.bot.already_pending(drone)
            ) < (
                self.bot.townhalls.amount
                + self.bot.placeholders(UnitTypeId.HATCHERY).amount
            ) * 22:
                larvae.random.train(drone)

    async def build_overlords(self, larvae: UnitTypeId, overlord: UnitTypeId):
        """
        TODO: Will need to figure out if we need to create more than 200 supply OLs

        """
        # works with build_drones, ensures at game opening, only one OL is pending
        if self.bot.supply_used <= 13 and self.bot.already_pending(overlord) < 1:
            larvae.random.train(overlord)
        # after we're above 13 supply, complete the normal OL method
        elif (
            self.bot.supply_cap > 14
            and self.bot.supply_left < 2
            and larvae
            and self.bot.can_afford(overlord)
            and self.bot.already_pending(overlord) < 2
        ):
            larvae.random.train(overlord)

    def update_townhalls(self, townhalls):
        self.townhalls = townhalls
    # async def build_queens(self):
    #     # larva queens
    #     if (
    #         self.structures(UnitTypeId.SPAWNINGPOOL).ready
    #         and self.queens.amount + self.already_pending(UnitTypeId.QUEEN) < 6
    #     ):
    #         if self.can_afford(UnitTypeId.QUEEN):
    #             for hatchery in self.hatcheries:
    #                 if hatchery.is_idle:
    #                     hatchery.train(UnitTypeId.QUEEN)
    #                     self.assign_queen()