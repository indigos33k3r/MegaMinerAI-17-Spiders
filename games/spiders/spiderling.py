# Generated by Creer at 03:58AM on April 24, 2016 UTC, git hash: '087b1901032ab5bed5806b24830233eac5c2de55'
# This is a simple class to represent the Spiderling object in the game. You can extend it by adding utility functions here in this file.

from games.spiders.spider import Spider

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add addtional import(s) here
# <<-- /Creer-Merge: imports -->>

class Spiderling(Spider):
    """The class representing the Spiderling in the Spiders game.

    A Spider spawned by the BroodMother.
    """

    def __init__(self):
        """Initializes a Spiderling with basic logic as provided by the Creer code generator."""
        Spider.__init__(self)

        # private attributes to hold the properties so they appear read only
        self._busy = ""
        self._moving_on_web = None
        self._moving_to_nest = None
        self._number_of_coworkers = 0
        self._work_remaining = 0



    @property
    def busy(self):
        """When empty string this Spiderling is not busy, and can act. Otherwise a string representing what it is busy with, e.g. 'Moving', 'Attacking'.

        :rtype: str
        """
        return self._busy


    @property
    def moving_on_web(self):
        """The Web this Spiderling is using to move. Null if it is not moving.

        :rtype: Web
        """
        return self._moving_on_web


    @property
    def moving_to_nest(self):
        """The Nest this Spiderling is moving to. Null if it is not moving.

        :rtype: Nest
        """
        return self._moving_to_nest


    @property
    def number_of_coworkers(self):
        """The number of Spiderlings busy with the same work this Spiderling is doing, speeding up the task.

        :rtype: int
        """
        return self._number_of_coworkers


    @property
    def work_remaining(self):
        """How much work needs to be done for this Spiderling to finish being busy. See docs for the Work forumla.

        :rtype: float
        """
        return self._work_remaining



    def attack(self, spiderling):
        """ Attacks another Spiderling

        Args:
            spiderling (Spiderling): The Spiderling to attack.

        Returns:
            bool: True if the attack was successful, false otherwise.
        """
        return self._run_on_server('attack', spiderling=spiderling)


    def move(self, web):
        """ Starts moving the Spiderling across a Web to another Nest.

        Args:
            web (Web): The Web you want to move across to the other Nest.

        Returns:
            bool: True if the move was successful, false otherwise.
        """
        return self._run_on_server('move', web=web)


    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you want to add any client side logic (such as state checking functions) this is where you can add them
    # <<-- /Creer-Merge: functions -->>
