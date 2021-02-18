from sc2 import BotAI
from sc2.unit import Unit
from sc2.units import Units

from queens_sc2.base_unit import BaseUnit
from queens_sc2.policy import Policy


class Defence(BaseUnit):
    def __init__(self, bot: BotAI, defence_policy: Policy):
        super().__init__(bot)
        self.last_transfusion: float = 0.0
        self.policy = defence_policy

    async def handle_unit(
        self,
        air_threats_near_bases: Units,
        ground_threats_near_bases: Units,
        unit: Unit,
        priority_enemy_units: Units,
        th_tag: int = 0,
    ) -> None:

        if priority_enemy_units:
            await self.do_queen_micro(unit, priority_enemy_units)
        elif self.policy.attack_condition():
            await self.do_queen_offensive_micro(unit, self.policy.attack_target)
        elif self.policy.defend_against_ground and ground_threats_near_bases:
            await self.do_queen_micro(unit, ground_threats_near_bases)
        elif self.policy.defend_against_air and air_threats_near_bases:
            await self.do_queen_micro(unit, air_threats_near_bases)
        elif unit.distance_to(self.policy.rally_point) > 12:
            unit.move(self.policy.rally_point)

    def update_policy(self, policy: Policy) -> None:
        self.policy = policy
