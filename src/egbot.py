import sys,os
from contextlib import suppress
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
#from sc2.position import Point2, Point3



class EGbot(sc2.BotAI):
    def __init__(self):
        self.creep_queen_tags = []
        self.larva_queen_tags = []
        self.defense_queens = [] # just created for fun
        


    #Do these actions every step
    async def on_step(self, iteration):
        self.hq: Unit = self.townhalls.first # will need to account for if it's destroyed
        self.queens: Units = self.units(UnitTypeId.QUEEN)
        self.hatcheries = self.townhalls.ready
        larvae: Units = self.larva
        '''On_step actions'''
        # Send workers across bases
        await self.distribute_workers(1.0)
        await self.build_drones(larvae)
        await self.build_overlords(larvae)
        await self.expand()
        await self.build_spawning_pool()
        await self.build_queens()
        await self.larva_inject()
        await self.build_gas()
        await self.spread_creep()
        

        
        # If we have less than 22 drones, build drones
        # TODO: Will need to add an array or vector of buildings for "worker_en_route_to_build" to check instead of only HATCHERY
        # TODO: Check for max number of hatcheries
    async def build_drones(self, larvae):
        #variables
        if larvae and self.can_afford(UnitTypeId.DRONE): 
            if (self.supply_workers - self.worker_en_route_to_build(UnitTypeId.HATCHERY) + 
                self.already_pending(UnitTypeId.DRONE)) < (self.townhalls.amount + self.placeholders(UnitTypeId.HATCHERY).amount) * 22:
                larva: Unit = larvae.random
                larva.train(UnitTypeId.DRONE)
                return
        
    async def build_overlords(self, larvae):
        '''
            TODO: Will need to figure out if we need to create more than 200 supply OLs

        '''
        if (self.supply_left < 2 and larvae
            and self.can_afford(UnitTypeId.OVERLORD)
            and self.already_pending(UnitTypeId.OVERLORD) < 2):
            larvae.random.train(UnitTypeId.OVERLORD)
  
    async def expand(self):
        # Expands to nearest location when 300 minerals are available up to maximum 3 hatcheries
        if self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY) < 3:
            if self.can_afford(UnitTypeId.HATCHERY):
                await self.expand_now()

    async def build_spawning_pool(self):
        hq: Unit = self.townhalls.first
        
        # Build spawning pool
        if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
               await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position.towards(self.game_info.map_center, 5))

    '''TODO: Assign creep queens to creep queens list, larva queens to larva queen list.
    '''



    async def larva_inject(self):
        hatcheries = self.townhalls.ready #list of ready hatcheries
        queens = self.units(UnitTypeId.QUEEN)  # list of queens

        # TODO: use queen tags instead
        for hatchery in hatcheries:
            for queen in queens.closer_than(5.0, hatchery):
                if queen.energy >= 25:
                    queen(AbilityId.EFFECT_INJECTLARVA, hatchery)


    async def spread_creep(self):
        # TODO: queen spread
        # queen_build_tumor = AbilityId.BUILD_CREEPTUMOR_QUEEN
        # creep_build_tumor = AbilityId.ZERGBUILD_CREEPTUMOR
        # hatcheries = self.townhalls.ready # list of ready hatcheries
        #                                   # list of queens
        # # 
        # queens = self.units(UnitTypeId.QUEEN)  # list of queens
        
        # # pick or build a queen
        
        # if len(hatcheries) > 1:
        #     second_hatch = hatcheries[1]
        #     for queen in queens.closer_than(5.0, second_hatch):
        #         if queen and second_hatch.is_idle: 
        #             second_hatch.train(UnitTypeId.QUEEN)  

        # creep_queens.append(second_hatch.train(UnitTypeId.QUEEN))
        # creep_queens[0](queen_build_tumor)
        # cq = creep_queens[0]
            
        # if cq.is_idle:
        #     cq(queen_build_tumor)
        # goto an area near the end of creep
        # build tumor
        
        pass
        # TODO: tumor spread


    #TODO: implement strategy here - really only need one extractor in the beginning
    async def build_gas(self):  
        if (self.structures(UnitTypeId.SPAWNINGPOOL) and self.gas_buildings.amount + 
            self.already_pending(UnitTypeId.EXTRACTOR) < 8):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                # May crash if we dont have any drones
                for hatch in self.townhalls.ready:
                    for vg in self.vespene_geyser.closer_than(10, hatch):
                        drone: Unit = self.workers.random
                        drone.build_gas(vg)
                        break
                        
    # moves excess drones to next location
    # TODO: Possibly where we can create Queens upon building completion.
    async def on_building_construction_complete(self, unit: Unit):
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY and self.mineral_field:
            mf = self.mineral_field.closest_to(unit)
            unit.smart(mf) # sets gathering location to mineral patch near recently built hatch


    async def build_queens(self):
        # larva queens
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready and self.queens.amount + self.already_pending(UnitTypeId.QUEEN) < 6:
            if self.can_afford(UnitTypeId.QUEEN): #check to afford
                for hatchery in self.hatcheries: # loop through available hatcheries each step
                    close_queens = self._get_close_queens(hatchery) #find list of queens close to hatchery
                    # if # of larva queens = 3 then build creep queen
                    if close_queens and hatchery.is_idle and len(self.larva_queen_tags) >= 3:
                        hatchery.train(UnitTypeId.QUEEN)
                    if not close_queens and hatchery.is_idle: # creates larva queen
                        hatchery.train(UnitTypeId.QUEEN)

    async def on_unit_created(self, unit: Unit):
        """ Override this in your bot class. This function is called when a unit is created."""
        if unit.type_id is UnitTypeId.QUEEN:
            if len(self.larva_queen_tags) < 3:
                self.larva_queen_tags.append(unit.tag)
            else:
                self.creep_queen_tags.append(unit.tag)
    
    # TODO: Save this for later: # creep_queens: Units = self.units(UnitTypeId.QUEEN).closer_than(5.0, hq)    


    def _get_close_queens(self, hatchery):
        return self.queens.closer_than(5.0, hatchery)
    

# Setting realtime=False makes the game/bot play as fast as possible
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=False)

