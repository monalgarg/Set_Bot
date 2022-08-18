#!/usr/bin/python

import sys
import copy

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

class Card:
    def __init__(self, p1: int, p2: int, p3: int, p4: int, coor: tuple):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.coor = coor

    def __str__(self):
        l = [str(x) for x in [self.p1, self.p2, self.p3, self.p4]]
        return " ".join(l)

    def is_set(self, card1, card2):
        if (self.p1 + card1.p1 + card2.p1) % 3 != 0:
            return False
        if (self.p2 + card1.p2 + card2.p2) % 3 != 0:
            return False
        if (self.p3 + card1.p3 + card2.p3) % 3 != 0:
            return False
        if (self.p4 + card1.p4 + card2.p4) % 3 != 0:
            return False
        return True

class Board:
    def __init__(self, cards):
        assert len(cards) >= 12
        self.cards = cards

        self.card_placement = [c.coor for c in self.cards] 
        self.card_placement.sort()

        global key_mapping
        key_mapping = ['1', '2', '3', 'q', 'w', 'e', 'a', 's', 'd', 'z', 'x', 'c', '4', '5', '6', 'r', 't', 'y', 'f', 'g', 'h']

        self.card_placement_key_mapping = dict(zip(self.card_placement, key_mapping[0:len(self.card_placement)]))
        
    def __str__(self):
        card_str_list = [str(c) for c in self.cards]
        return "\n".join(card_str_list)

    def find_set_helper(self, card_set):
        if len(card_set) == 3:
            card1 = self.cards[card_set[0]]
            card2 = self.cards[card_set[1]]
            card3 = self.cards[card_set[2]]
            if card1.is_set(card2, card3):
                return card1, card2, card3
            return None
        
        start = card_set[-1] + 1 if card_set else 0
        for x in range(start,len(self.cards)):
            card_set_copy = copy.deepcopy(card_set)
            card_set_copy += [x]
            res = self.find_set_helper(card_set_copy)
            if res:
                return res

    def find_set(self):
        card_set = self.find_set_helper([])

        res = []
        for c in card_set:
            coor = c.coor
            res += [self.card_placement_key_mapping[coor]]

        return res

class SetSolver:
    def __init__(self, game_name: str, timer: int):
        # Normalzing dictonaries
        global color_dict, shape_dict, shading_dict
        color_dict = {'#ff0101': 0, '#008002': 1, '#800080': 2}
        shape_dict = {'oval': 0, 'diamond': 1, 'squiggle': 2}
        shading_dict = {'empty': 0, 'striped': 1, 'filled': 2}

        # initialize game name and get initial board
        self.game_name = game_name
        self.create_driver()
        self.board = self.build_board()

        while True:
            print(self.solve_board())
            time.sleep(timer) 
        
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

        def get_coor(card):
            transform_prop = get_attrs(card)["style"].split(';')[1]
            translate_coor = transform_prop[transform_prop.find('(')+1:transform_prop.find(')')].split(', ')
            return (int(translate_coor[0][:-2]), int(translate_coor[1][:-2]))

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

            coordinates = get_coor(card)
            card = Card(card_num, card_color, card_shape, card_shading, coordinates)
            card_list.append(card)

        board = Board(card_list)
        return board

    def solve_board(self):
        card_set = self.board.find_set()
        return card_set

if __name__ == '__main__':
    SetSolver(sys.argv[1], sys.argv[2])
