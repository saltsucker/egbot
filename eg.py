import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.unit import Unit
import logging
from genmgr import GeneralManager
from MapAnalyzer import MapData
from queens_sc2.queens import INJECT_POLICY, Queens
from queen_policy import QueenPolicy
from logger import Sc2Logger

logging.basicConfig(
    level=logging.DEBUG,
    filename="egbot.log",
    datefmt="%d-%m-%y %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d | %(message)s",
)


class EGbot(sc2.BotAI):
    def __init__(self):
        self.qp = None
        self.gm = GeneralManager(self)
        self.iteration = 0
        self.md = None
        self.queens = None
        self.logger = Sc2Logger()

    async def on_start(self):
        self.md = MapData(self)
        # logic: thinking we find paths to enemy base and then spread creep via that
        # TODO: Would we pass the list of paths to queen policy?
        self.grid_points = self.md.get_pyastar_grid()

        await self.control_enemy()

        hq = self.townhalls.first.position
        enemy_hq = self.enemy_start_locations[0]
        creep_locs = self.expansion_locations_list

        for loc in creep_locs[:5]:
            if loc == hq:
                continue
            
            self.paths = self.md.pathfind(hq, loc, self.grid_points, sensitivity = 7)

        self.qp = QueenPolicy(self, self.paths)
        policy = self.qp.get_policy()
        self.queens = Queens(self, True, policy)
        self.inject_queens = Queens(self, True, INJECT_POLICY)

   

    async def on_step(self, iteration):
        self.iteration = iteration
        if iteration == 0:
            await self.chat_send("(glhf)")
        await self.gm.manage()
        await self.queens.manage_queens(iteration)
        await self.inject_queens.manage_queens(iteration)
        # logging.info('Iteration: %s' % iteration)
        if self.iteration % 100 == 0:
            await self.log_info()

    async def on_before_start(self):
        mfs = self.mineral_field.closer_than(10, self.townhalls.random)
        for drone in self.units(UnitTypeId.DRONE):
            drone.gather(mfs.closest_to(drone))

    async def on_building_construction_complete(self, unit: Unit):
        if unit.type_id == UnitTypeId.HATCHERY:
            if self.mineral_field:
                mf = self.mineral_field.closest_to(unit)
                unit.smart(mf)

    async def on_unit_created(self, unit: Unit):
        pass

    async def on_unit_destroyed(self, unit_tag: int):
        self.queens.remove_unit(unit_tag)
        pass

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        pass

    async def log_info(self):
        res = await self.logger.log_worker_distribution(self)
        logging.info(res)


    async def control_enemy(self):
        self.client.debug_control_enemy()

def main():
    """Setting realtime=False makes the game/bot play as fast as possible"""
    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()


