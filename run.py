import os
import sys
import requests

# API config (using env vars)
key = os.environ['TRELLO_KEY']
token = os.environ['TRELLO_TOKEN']
CREDENTIALS = {'key': key, 'token': token}

if not key or not token:
    raise RuntimeError(('Env vars TRELLO_KEY and TRELLO_TOKEN must be set. '
                        'See https://trello.com/app-key to obtain a '
                        'key/token pair'))


def get_board_id():
    if len(sys.argv) > 1:
        return sys.argv[1]
    print('Usage: python run.py BOARD_ID\n')
    print('Available Boards:')
    # fetch and print board IDs
    url = ('https://api.trello.com/1/members/me/boards'
           '?fields=name&key={key}&token={token}')
    resp = requests.get(url.format(**CREDENTIALS))
    boards = resp.json()
    for board in boards:
        print('{0} ({1})'.format(board['name'], board['id']))


def clear_all_votes_on_board(id):

    print('Clearing votes on board {0}'.format(id))

    # Trello API docs
    # https://developers.trello.com/docs/api-introduction

    # Fetch all cards on the board
    # GET /boards/{id}/cards
    # https://developers.trello.com/reference#boardsboardidtest
    get_cards_url = 'https://api.trello.com/1/boards/{id}/cards/?key={key}&token={token}'
    resp = requests.get(get_cards_url.format(id=id, **CREDENTIALS))
    cards = resp.json()

    # For each card with badges.votes > 0, get members voted
    # GET /cards/{id}/membersVoted
    # https://developers.trello.com/reference#cardsidmembersvoted
    delete_votes_url = 'https://api.trello.com/1/cards/{cardId}/membersVoted/{idMember}?key={key}&token={token}'
    for card in cards:
        name = card['name']
        card_id = card['id']
        num_votes = card['badges']['votes']
        if num_votes > 0:
            # Remove each member's vote from the card
            # DELETE /cards/{id}/membersVoted/{idMember}
            members_voted = card['idMembersVoted']
            for member_id in members_voted:
                resp = requests.delete(delete_votes_url.format(cardId=card_id,idMember=member_id, **CREDENTIALS))


if __name__ == '__main__':
    board_id = get_board_id()
    if board_id:
        clear_all_votes_on_board(board_id)
