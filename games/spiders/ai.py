# This is where you build your AI for the Spiders game.

from joueur.base_ai import BaseAI

import random

rps = {"Weaver" : {"Weaver", "Cutter"},
       "Cutter" : {"Cutter", "Spitter"},
       "Spitter" : {"Spitter", "Weaver"}}

prime_rps = {"Weaver" : "Cutter",
             "Cutter" : "Spitter",
             "Spitter" : "Weaver"}

def is_valid_web(spider, web):
    if web.strength > web.load:
        return True
    mine = [on_web for on_web in web.spiderlings if on_web.owner == spider.owner]
    if len(mine) > (len(web.spiderlings) / 2):
        return False
    return True
        

def is_valid_spit_connection(spider, nest):
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
        return "Spiders Python Player" # REPLACE THIS WITH YOUR TEAM NAME



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
        self.my_brood = [spider for spider in self.player.spiders if spider.game_object_name == "BroodMother"][0]
        self.their_brood = [spider for spider in self.player.other_player.spiders if spider.game_object_name == "BroodMother"][0]
        self.need_jobs = [spider for spider in self.player.spiders if spider.game_object_name != "BroodMother" and spider.busy == ""]
    
    def spawn(self):
        while self.my_brood.eggs > 0:
            spider_type = random.choice(["Cutter", "Weaver", "Spitter"])
            print("Spawning", spider_type)
            self.my_brood.spawn(spider_type)

    def do_attack(self, spider):
        if spider.busy != "":
            print("Trying to attack with a busy spider")
            return True
        targets = [target for target in spider.nest.spiders
                   if target.owner != spider.owner and
                   not target.is_dead and 
                   target.game_object_name in rps[spider.game_object_name]]
        if targets:
            prime_targets = [target for target in targets if prime_rps[spider.game_object_name] == target.game_object_name]
            if prime_targets:
                targets = prime_targets
            # TODO Preferential attack based on busy
            target = random.choice(targets)
            print(spider.game_object_name, "attacking", target.game_object_name)
            spider.attack(target)
            assert not spider.is_dead or target.is_dead, "Suicide without gain!"
            return True
        return False
    
    def do_move(self, spider):
        if spider.busy != "":
            print("Trying to move with a busy spider")
            return True
        valid_webs = [web for web in spider.nest.webs if is_valid_web(spider, web)]
        if len(valid_webs) == 0:
            return False
        # TODO Better move choice logic
        best = random.choice(spider.nest.webs)
        print("Moving spider")
        spider.move(best)
        return True
    
    def do_spit(self, spider):
        if spider.busy != "":
            print("Trying to spit with a busy spider")
            return True
        if spider.game_object_name != "Spitter":
            print("Trying to spit with", spider.game_object_name)
            return False
        valid_nests = [nest for nest in self.game.nests if is_valid_spit_connection(spider, nest)]
        if len(valid_nests) == 0:
            return False
        brood_nest = [nest for nest in valid_nests if nest == self.their_brood.nest]
        if brood_nest:
            valid_nests = brood_nest
        choice = random.choice(valid_nests)
        spider.spit(choice)
        return True
    
    def run_turn(self):
        """ This is called every time it is this AI.player's turn.

        Returns:
            bool: Represents if you want to end your turn. True means end your turn, False means to keep your turn going and re-call this function.
        """
        print("Starting turn:", self.game.current_turn, "Time remaining:", self.player.time_remaining)
        # TODO Consume
        # TODO Special actions
        self.setup()
        self.spawn()
        
        for spider in self.need_jobs:
            if self.do_attack(spider):
                # Attacks cause spiders to be busy, right?
                assert (spider.is_dead or spider.busy != ""), "Attacked but not busy?"
                continue
            if spider.game_object_name == "Spitter":
                if self.do_spit(spider):
                    assert spider.busy != "", "Spit but not busy?"
                    continue
            if self.do_move(spider):
                assert (spider.is_dead or spider.busy != ""), "Moved but not busy?"
                continue
        return True
        # This is ShellAI, it is very simple, and demonstrates how to use all
        # the game objects in Spiders.
        spider = random.choice(self.player.spiders)

        if spider.game_object_name == "BroodMother":
            brood_mother = spider
            choice = random.randint(1, 10)

            if choice == 1: # try to consume a spiderling 10% of the time
                if len(brood_mother.nest.spiders) > 1:
                    otherSpider = random.choice(brood_mother.nest.spiders)
                    if otherSpider != brood_mother:
                        print("BroodMother #" + brood_mother.id +
                              " consuming " + otherSpider.game_object_name +
                              " #" + otherSpider.id)
                        brood_mother.consume(otherSpider)
            else: # try to spawn a Spiderling
                if brood_mother.eggs > 0:
                    # get a random spiderling type to spawn a new
                    # Spiderling of that type
                    randomSpiderlingType = random.choice(["Cutter", "Weaver", "Spitter"])
                    print("BroodMother #" + brood_mother.id +
                          " spawning " + randomSpiderlingType)
                    brood_mother.spawn(randomSpiderlingType)
        else: # it is a Spiderling
            spiderling = spider

            if spiderling.busy == "": # then it is NOT busy
                choice = random.randint(0, 2)

                if choice == 0: # try to move somewhere
                    if len(spiderling.nest.webs) > 0:
                        web = random.choice(spiderling.nest.webs)
                        print("Spiderling " + spiderling.game_object_name +
                              " #" + spiderling.id + " moving on Web #" + web.id)
                        spiderling.move(web)
                elif choice == 1: # try to attack something
                    if len(spiderling.nest.spiders) > 1:
                        otherSpider = random.choice(spiderling.nest.spiders)
                        if otherSpider.owner != spiderling.owner: # attack the enemy!
                            spiderling.attack(otherSpider)
                else: # do something unique based on Spiderling type
                    if spiderling.game_object_name == "Spitter":
                        spitter = spiderling
                        enemysNest = self.player.other_player.brood_mother.nest

                        # look for an existing web to the enemy home nest
                        webExists = any(True
                                        for web in enemysNest.webs
                                        if spitter.nest in (web.nest_a, web.nest_b))

                        if not webExists:
                            print("Spitter #" + spitter.id +
                                  " spitting to Nest #" + enemysNest.id)
                            spitter.spit(enemysNest)
                    elif spiderling.game_object_name == "Cutter":
                        cutter = spiderling
                        if len(cutter.nest.webs) > 0:
                            web = random.choice(cutter.nest.webs)
                            print("Cutter #" + cutter.id +
                                  " cutting Web #" + web.id)
                            cutter.cut(web)
                    elif spiderling.game_object_name == "Weaver":
                        weaver = spiderling
                        if len(weaver.nest.webs) > 0:
                            web = random.choice(weaver.nest.webs)
                            if random.randint(0,1) == 1:
                                print("Weaver #" + weaver.id +
                                      " strengthening Web #" + web.id)
                                weaver.strengthen(web)
                            else:
                                print("Weaver #" + weaver.id +
                                      " weakening Web #" + web.id)
                                weaver.weaken(web)
        return True # To signify that we are done with our turn
