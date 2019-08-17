#-*- coding:utf-8 -*-
import sys, os
import json
import requests

url = 'http://127.0.0.1:5000/'
server_url = 'http://117.78.4.26:5001/'


# 0 -> 地主上家; 1 -> 地主; 2 -> 地主下家
payload1 = {
    'role_id': 0,
    'last_taken': {
        0: [],
        1: [],
        2: [],
    },
    'cur_cards':[], # 无需保持顺序
    'history': { # 各家走过的牌的历史数据
        0: [],
        1: [],
        2: [],
    },
    'left': { # 各家剩余的牌
        0: 17,
        1: 20,
        2: 17,
    },
    'debug': False, # 是否返回debug
}


def split_handcards(cards):
    # Split Cards Series into a prettier list
    r""" Handcards string spliter
    Split Cards Series into a prettier list which sorted DESCEDNING

    Args:
        cards: a string, which indicate a group of cards

    Output:
        hand_cards: a string

    """
    hand_cards = []
    cards_rank = [
        '3', '4', '5', '6', '7', '8', '9', '10',
        'J', 'Q', 'K', 'A', '2', 'X', 'D'
    ]
    for card in cards:
        # NOTE: '10' contrains 2 chars which should be seperately considered
        if card != '1' and card != '0':
            hand_cards.append(card)
        elif card == '1':
            hand_cards.append('10')
        elif card == '0':
            pass
        else:
            pass
    # bubble sort
    length = len(hand_cards)
    for index in range(length):
        for i in range(1, length - index):
            if (
                cards_rank.index(hand_cards[i - 1]) <
                    cards_rank.index(hand_cards[i])):
                hand_cards[i-1], hand_cards[i] = hand_cards[i], hand_cards[i-1]

    split_res = []
    # convert the str-style to int
    for card in hand_cards:
        split_res.append(cards_rank.index(card) + 3)
    
    return split_res


def refresh_payload1(last_0, last_1, my_id):
    if my_id == 0:
        payload1['last_taken'][1] = last_0
        payload1['last_taken'][2] = last_1
        payload1['history'][1].extend(last_0)
        payload1['history'][2].extend(last_1)
        payload1['left'][1] -= len(last_0)
        payload1['left'][2] -= len(last_1)

    elif my_id == 1:
        payload1['last_taken'][2] = last_0
        payload1['last_taken'][0] = last_1
        payload1['history'][2].extend(last_0)
        payload1['history'][0].extend(last_1)
        payload1['left'][2] -= len(last_0)
        payload1['left'][0] -= len(last_1)

    elif my_id == 2:
        payload1['last_taken'][0] = last_0
        payload1['last_taken'][1] = last_1
        payload1['history'][0].extend(last_0)
        payload1['history'][1].extend(last_1)
        payload1['left'][0] -= len(last_0)
        payload1['left'][1] -= len(last_1)
    
    else:
        raise ValueError(
            'my_id should be 0,1,2, got: {}'
            .format(my_id)
        )

if __name__ == "__main__":    
    # get my_handcard 
    # NOTE:只需输入一个不带空格的字符串即可，3-9,10-K,A,2,X,D
    my_handcard = input('input your handcard:')
    payload1['cur_cards'] = split_handcards(my_handcard)

    my_id = input('input your id:')
    # get my_id
    my_id = int(my_id)
    payload1['role_id'] = my_id

    if my_id == 0:
        # 自己是地主上家
        while(True):
            input_lld = input('input lld: ')
            landlord = split_handcards(input_lld)
            input_down = input('input lld down: ')
            landlord_down = split_handcards(input_down)
            refresh_payload1(landlord, landlord_down, 0)
            res = requests.post(server_url, json=payload1)
            print(
                'landlord_up, you play: {}'
                .format(json.loads(res.content))
            )
            # payload1['cur_cards'] = list(set(payload1['cur_cards']) - set(json.loads(res.content)['data']))
            for card in json.loads(res.content)['data']:
                payload1['cur_cards'].remove(card)
            payload1['last_taken'][0] = json.loads(res.content)['data']
            payload1['history'][0].extend(json.loads(res.content)['data'])
            payload1['left'][0] -= len(json.loads(res.content)['data'])
            
            if payload1['left'][0] == 0 or payload1['left'][2] == 0:
                print('you win')
                break
            elif payload1['left'][1] == 0:
                print('you loss')
                break
            else:
                pass

    elif my_id == 1:
        # 自己是地主
        while(True):
            input_down = input('input lld down: ')
            landlord_down = split_handcards(input_down)
            input_up = input('input lld up: ')
            landlord_up = split_handcards(input_up)
            refresh_payload1(landlord_down, landlord_up, 1)
            res = requests.post(server_url, json=payload1)
            print(
                'landlord, you play: {}'
                .format(json.loads(res.content))
            )
            # payload1['cur_cards'] = list(set(payload1['cur_cards']) - set(json.loads(res.content)['data']))
            for card in json.loads(res.content)['data']:
                payload1['cur_cards'].remove(card)
            
            payload1['last_taken'][1] = json.loads(res.content)['data']
            payload1['history'][1].extend(json.loads(res.content)['data'])
            payload1['left'][1] -= len(json.loads(res.content)['data'])
            
            if payload1['left'][0] == 0 or payload1['left'][2] == 0:
                print('you loss')
                break
            elif payload1['left'][1] == 0:
                print('you win')
                break
            else:
                pass

    elif my_id == 2:
        # 自己是地主下家
        while(True):
            input_lld_up = input('input lld up: ')
            landlord_up = split_handcards(input_lld_up)
            input_lld = input('input lld: ')
            landlord = split_handcards(input_lld)
            refresh_payload1(landlord_up, landlord, 2)
            res = requests.post(server_url, json=payload1)
            print(
                'landlord_up, you play: {}'
                .format(json.loads(res.content))
            )
            # payload1['cur_cards'] = list(set(payload1['cur_cards']) - set(json.loads(res.content)['data']))
            for card in json.loads(res.content)['data']:
                payload1['cur_cards'].remove(card)
            payload1['last_taken'][2] = json.loads(res.content)['data']
            payload1['history'][2].extend(json.loads(res.content)['data'])
            payload1['left'][2] -= len(json.loads(res.content)['data'])
            
            if payload1['left'][0] == 0 or payload1['left'][2] == 0:
                print('you win')
                break
            elif payload1['left'][1] == 0:
                print('you loss')
                break
            else:
                pass

    else:
        raise ValueError(
            'my_id should be 0,1,2, got: {}'
            .format(my_id)
        )
