#!/usr/bin/python

import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

class Card:
    def __init__(self, p1: int, p2: int, p3: int, p4: int):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

    def __str__(self):
        l = [str(x) for x in [self.p1, self.p2, self.p3, self.p4]]
        return " ".join(l)

class Board:
    def __init__(self, cards):
        assert len(cards) >= 12
        self.cards = cards

    def __str__(self):
        card_str_list = [str(c) for c in self.cards]
        return "\n".join(card_str_list)

    def find_set(self):
        pass

class SetSolver:
    def __init__(self, game_name: str):
        # Normalzing dictonaries
        global color_dict, shape_dict, shading_dict
        color_dict = {'#ff0101': 0, '#008002': 1, '#800080': 2}
        shape_dict = {'oval': 0, 'diamond': 1, 'squiggle': 2}
        shading_dict = {'empty': 0, 'striped': 1, 'filled': 2}

        # initialize game name and get initial board
        self.game_name = game_name
        self.create_driver()
        self.board = self.build_board()
        print(str(self.board))
        
    def create_driver(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://setwithfriends.com/game/" + self.game_name)
        assert "Set with Friends" in self.driver.title

        # to hit enter
        # TODO: make this automatic
        time.sleep(5) 

    def build_board(self):
        top_table = self.driver.find_elements(By.CSS_SELECTOR, '.MuiGrid-root.jss10.MuiBox-root.jss33.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-sm-8.MuiGrid-grid-md-6')
        assert len(top_table) == 1
        table = top_table[0].find_element(By.CSS_SELECTOR, '.MuiPaper-root.MuiPaper-elevation1.MuiPaper-rounded')
        cards = table.find_elements(By.CSS_SELECTOR, '[style*="visible"]')

        def get_attrs(ele):
            attrs=self.driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',ele)
            return attrs

        card_list = []
        for card in cards:
            card_info = card.find_elements(By.CSS_SELECTOR, 'svg')

            # get properities of the card
            ## NUMBER ##
            card_num = len(card_info) 

            card_item = card_info[0] # take any item within the card, they are all the same

            card_item_outer = card_item.find_element(By.CSS_SELECTOR, '[stroke]')
            ##COLOR##
            # #800080 = purple
            # #ff0101 = red
            # #008002 = green
            card_color = get_attrs(card_item_outer)["stroke"]

            ## SHAPE ## 
            # diamond, squiggle, oval
            card_shape = get_attrs(card_item_outer)['href'][1:] 

            ## SHADING ##
            # 0 = empty
            # 1 = striped
            # 2 = filled
            card_item_inner = card_item.find_element(By.CSS_SELECTOR, '[mask]')
            card_item_inner_attrs = get_attrs(card_item_inner)
            if card_item_inner_attrs["fill"] == "transparent":
                card_shading = "empty" 
            elif card_item_inner_attrs["mask"] == "url(#mask-stripe)":
                card_shading = "striped" 
            else:
                card_shading = "filled" 

            # 'normalize' card properties so all are in range [0,1,2]
            card_num = card_num - 1
            card_color = color_dict[card_color]
            card_shape = shape_dict[card_shape]
            card_shading = shading_dict[card_shading] 

            card = Card(card_num, card_color, card_shape, card_shading)
            card_list.append(card)

        board = Board(card_list)
        return board

if __name__ == '__main__':
    SetSolver(sys.argv[1])
