import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.unit import Unit
import logging
from genmgr import GeneralManager
from MapAnalyzer import MapData
from queens_sc2.queens import Queens
from queen_policy import QueenPolicy

# logging.basicConfig(
#     level=logging.DEBUG,
#     filename="egbot.log",
#     datefmt="%d-%m-%y %H:%M:%S",
#     format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d | %(message)s",
# )


class EGbot(sc2.BotAI):
    def __init__(self):
        self.qp = None
        self.gm = GeneralManager(self)
        self.logger = logging.getLogger()
        self.iteration = 0
        self.md = None
        self.queens = None

    async def on_start(self):
        self.md = MapData(self)
        # logic: thinking we find paths to enemy base and then spread creep via that
        # TODO: Would we pass the list of paths to queen policy?
        self.grid_points = self.md.get_pyastar_grid()
        self.paths = self.md.pathfind(self.grid_points)
        self.qp = QueenPolicy(self, self.paths)
        self.queens = Queens(self, self.qp.get_policy())

    async def on_step(self, iteration):
        self.iteration = iteration
        if iteration == 0:
            await self.chat_send("(glhf)")
        await self.gm.manage()
        logging.info('Iteration: %s' % iteration)

    async def on_before_start(self):
        mfs = self.mineral_field.closer_than(10, self.townhalls.random)
        for drone in self.units(UnitTypeId.DRONE):
            drone.gather(mfs.closest_to(drone))

    async def on_building_construction_complete(self, unit: Unit):
        if unit.type_id == UnitTypeId.HATCHERY:
            if self.mineral_field:
                mf = self.mineral_field.closest_to(unit)
                unit.smart(mf)

    async def on_unit_created(self, unit):
        pass

    async def on_unit_destroyed(self, unit_tag: int):
        pass

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        pass




def main():
    """Setting realtime=False makes the game/bot play as fast as possible"""
    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()

