from player import Player
import xml.etree.ElementTree as ET
import dicttoxml as dxml
import player_pb2 as proto_p

class PlayerFactory:
    def to_json(self, players):
        player_list = []
        for player in players:
            keys = {"nickname": None, "email": None, "date_of_birth": None, "xp": None, "class": None}
            keys["nickname"] = player.nickname
            keys["email"] = player.email
            keys["date_of_birth"] = player.date_of_birth.strftime("%Y-%m-%d")
            keys["xp"] = player.xp
            keys["class"] = player.cls
            player_list.append(keys)
        return player_list

    def from_json(self, list_of_dict):
        players = []
        for atr in list_of_dict:
            player = Player(atr["nickname"], atr["email"], atr["date_of_birth"], atr["xp"], atr["class"])
            players.append(player)
        return players

    def from_xml(self, xml_string):
        root = ET.fromstring(xml_string)
        players_dict = []
        for player in root:
            for atr in player:
                if atr.tag == "nickname":
                    name = atr.text
                if atr.tag == "email":
                    email = atr.text
                if atr.tag == "date_of_birth":
                    date_of_birth = atr.text
                if atr.tag == "xp":
                    xp = atr.text
                if atr.tag == "class":
                    cls = atr.text
            new_Player = Player(name, email, date_of_birth, int(xp), cls)
            players_dict.append(new_Player)
        return players_dict

    def to_xml(self, list_of_players):

        players_dicts = []

        for player in list_of_players:
            player.date_of_birth = player.date_of_birth.strftime('%Y-%m-%d')
            player_atr = vars(player)
            player_atr['class'] = player_atr['cls']
            del player_atr['cls']
            players_dicts.append(player_atr)

        xml = dxml.dicttoxml(players_dicts, attr_type=False, custom_root='data', item_func=lambda x: 'player')

        return xml

    def from_protobuf(self, binary):
        players_list = proto_p.PlayersList()
        players_list.ParseFromString(binary)

        players = []

        for item in players_list.player:
            players.append(Player(
                item.nickname,
                item.email,
                item.date_of_birth,
                item.xp,
                proto_p.Class.Name(item.cls)
            ))

        return players

    def to_protobuf(self, list_of_players):
        players_list = proto_p.PlayersList()

        for player in list_of_players:
            p_player = players_list.player.add()

            setattr(p_player, 'nickname', player.nickname)
            setattr(p_player, 'email', player.email)
            setattr(p_player, 'date_of_birth', player.date_of_birth.strftime("%Y-%m-%d"))
            setattr(p_player, 'xp', player.xp)
            setattr(p_player, 'cls', getattr(proto_p.Class, player.cls))

        return players_list.SerializeToString()
