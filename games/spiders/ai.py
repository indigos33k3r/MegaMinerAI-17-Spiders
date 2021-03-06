# This is where you build your AI for the Spiders game.

from joueur.base_ai import BaseAI

import random

# Given a spider type, what can they kill
rps = {"Weaver": {"Weaver", "Spitter"},
       "Cutter": {"Cutter", "Weaver"},
       "Spitter": {"Spitter", "Cutter"}}
# Given a spider type, what can they kill without dying themselves
prime_rps = {"Weaver": "Spitter",
             "Cutter": "Weaver",
             "Spitter": "Cutter"}


def is_valid_web(spider, web):
    if web.strength > web.load:
        return True
    mine = [on_web for on_web in web.spiderlings if on_web.owner == spider.owner]
    if len(mine) > (len(web.spiderlings) / 2):
        return False
    return True


def is_valid_spit_connection(spider, nest):
    if spider.nest == nest:
        return False
    for web in spider.nest.webs:
        if web.nest_a == nest or web.nest_b == nest:
            return False
    return True


class AI(BaseAI):
    """ The basic AI functions that are the same between games. """

    def get_name(self):
        """ This is the name you send to the server so your AI will control the player named this string.

        Returns
            str: The name of your Player.
        """
        return "the-goldman-clause"

    def start(self):
        """ This is called once the game starts and your AI knows its playerID and game. You can initialize your AI here.
        """

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are tracking anything you can update it here.
        """

    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why you won or lost.
        """

    def setup(self):
        '''
        Create some useful collections
        '''
        self.my_brood = [spider for spider in self.player.spiders
                         if spider.game_object_name == "BroodMother"][0]
        self.their_brood = [spider for spider in self.player.other_player.spiders
                            if spider.game_object_name == "BroodMother"][0]
        self.need_jobs = [spider for spider in self.player.spiders
                          if spider.game_object_name != "BroodMother" and spider.busy == ""]

    def spawn(self):
        '''
        Handes spawn logic, which is basically just "fill the world with Spitters"
        '''
        while self.my_brood.eggs > 0:
            self.my_brood.spawn("Spitter")

    def do_attack(self, spider):
        '''
        If there is an enemy with you that you can kill, kill it.
        Prefers kills that don't kill you too.
        '''
        if spider.busy != "":
            print("Trying to attack with a busy spider")
            return True
        if spider.nest == self.my_brood.nest:
            # Never attack at your own brood nest,
            # since there can't be any enemies
            return False
        # Find living enemies you can kill
        targets = [target for target in spider.nest.spiders
                   if target.owner != spider.owner and
                   not target.is_dead and
                   target.game_object_name in rps[spider.game_object_name]]
        if targets:
            # Prefer enemies that don't get you killed
            prime_targets = [target for target in targets if
                             prime_rps[spider.game_object_name] ==
                             target.game_object_name]
            if prime_targets:
                targets = prime_targets
            target = random.choice(targets)
            print(spider.game_object_name, "attacking", target.game_object_name)
            spider.attack(target)
            return True
        return False

    def defensive_move(self, spider):
        '''
        Find webs connected to spider.nest that contain enemy spiders,
        and try to break that web by overloading it
        '''
        if spider.busy != "":
            print("Trying to defensively move a busy spider")
            return True
        if len(spider.nest.spiders) == 1:
            # Lone spiders have to hold the nest
            return False
        need_defense = []
        for web in spider.nest.webs:
            if web.strength < web.load:
                continue
            for on_web in web.spiderlings:
                if on_web.owner != spider.owner:
                    need_defense.append(web)
                    break
        if need_defense:
            # Choose the web closest to breaking to do first
            web = min(need_defense, key=lambda web: web.strength - web.load)
            print("Incoming asshole!")
            spider.move(web)
            return True
        return False

    def expand_move(self, spider):
        '''
        Look for places you don't know you control, and try to control them
        '''
        if len(spider.nest.spiders) == 1:
            # Lone spiders have to hold the nest
            return False
        if spider.busy != "":
            print("Trying to expand move a busy spider")
            return True
        valid_webs = [web for web in spider.nest.webs
                      if is_valid_web(spider, web)]
        if not valid_webs:
            return False
        # TODO Include "in flight" spiders
        empty_both = [web for web in valid_webs if len(web.spiderlings) == 0 and
                      (len(web.nest_a.spiders) == 0 or len(web.nest_b.spiders) == 0)]
        if empty_both:
            valid_webs = empty_both
        else:
            # If there are no empty nests, try to attack their broodmother
            brood = [web for web in valid_webs
                     if web.nest_a == self.their_brood
                     or web.nest_b == self.their_brood]
            if brood:
                print("BROOD WARS")
                valid_webs = brood
        # Prefer webs with low load
        choice = min(valid_webs, key=lambda web: len(web.spiderlings))
        spider.move(choice)
        return True

    def spray_spit(self, spider):
        '''
        Make a bunch of random connections, preferentially to empty nests.
        If there are no empty nests, connect to their broodmother
        '''
        if spider.busy != "":
            print("Trying to spit with a busy spider")
            return True
        if spider.game_object_name != "Spitter":
            print("Trying to spit with", spider.game_object_name)
            return False
        valid_nests = [nest for nest in self.game.nests
                       if is_valid_spit_connection(spider, nest)]
        if len(valid_nests) == 0:
            return False
        # TODO Add "in flight" spiders
        empty_nests = [nest for nest in valid_nests if len(nest.spiders) == 0]
        if empty_nests:
            valid_nests = empty_nests
        else:
            brood = [nest for nest in valid_nests if nest ==
                     self.their_brood.nest]
            if brood and spider.nest != self.my_brood.nest:
                print("GO AFTER THE BROOD")
                valid_nests = brood
        choice = random.choice(valid_nests)
        spider.spit(choice)
        return True

    def run_turn(self):
        '''
        Each non busy spider tries to
        1. Attack enemy spiders in their nest
        2. Overload webs that have enemy spiders on them.
        3. Move until there is exactly 1 spider at all nests
        4. If they are a Spitter, try to connect to nests with no spiders 
        '''
        self.setup()
        print("Starting turn:", self.game.current_turn, "Time remaining:",
              self.player.time_remaining, "Score:", self.my_brood.health, self.their_brood.health)
        self.spawn()
        # Rerun setup to find spawned things
        self.setup()
        for spider in self.need_jobs:
            if self.do_attack(spider):
                continue
            if self.defensive_move(spider):
                continue
            if self.expand_move(spider):
                continue
            if spider.game_object_name == "Spitter":
                if self.spray_spit(spider):
                    continue
        return True
