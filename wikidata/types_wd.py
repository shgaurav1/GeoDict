# coding=utf-8
from urllib.parse import urlparse
from dateutil.parser import parse


def parseDate(date):
    AD_BC_identifier = date[0]
    date.lstrip('+-')
    return AD_BC_identifier, parse(date, fuzzy=True)


class Type(object):
    """docstring for Type."""

    def __init__(self, typeName):
        self.type_name = typeName

    def extractData(self, propId, isMultiple, data):
        if isMultiple:
            return self.extractMultiple(propId, data)
        return self.extractSingle(propId, data)

    def extractMultiple(self, propID, data):
        return []

    def extractSingle(self, propID, data):
        return []

    def check_conformity(self, propID, data):
        return True


class EntityID(Type):
    def __init__(self):
        super(EntityID, Type.__init__(self, "EntityID"))

    def extractMultiple(self, propID, data):
        result = []
        for i in range(len(data['claims'][propID])):
            result.append(data['claims'][propID][i]['mainsnak']['datavalue']['value']['id'])
        return result

    def extractSingle(self, propID, data):
        return data['claims'][propID][0]['mainsnak']['datavalue']['value']['id']

    def check_conformity(self, propID, data):
        try:
            data['claims'][propID][0]['mainsnak']['datavalue']['value']['id']
            return True
        except Exception as e:
            return False


class String(Type):
    def __init__(self):
        super(String, Type.__init__(self, "String"))

    def extractMultiple(self, propID, data):
        result = []
        for i in range(len(data['claims'][propID])):
            result.append(data['claims'][propID][i]['mainsnak']['datavalue']['value'])
        return result

    def extractSingle(self, propID, data):
        return data['claims'][propID][0]['mainsnak']['datavalue']['value']

    def check_conformity(self, propID, data):
        try:
            data['claims'][propID][0]['mainsnak']['datavalue']['value']
            return True
        except Exception as e:
            return False


class Coordinates(Type):
    def __init__(self):
        super(Coordinates, Type.__init__(self, "Coordinates"))

    def extractMultiple(self, propID, data):
        result = []
        for i in range(len(data['claims'][propID])):
            result.append(self.parse_coord(data['claims'][propID][i]['mainsnak']['datavalue']['value']))
        return result

    def extractSingle(self, propID, data):
        return self.parse_coord(data['claims'][propID][0]['mainsnak']['datavalue']['value'])

    def parse_coord(self, data):
        return {"lat": data["latitude"], "lon": data["longitude"]}

    def check_conformity(self, propID, data):
        try:
            self.parse_coord(data['claims'][propID][0]['mainsnak']['datavalue']['value'])
            return True
        except Exception as e:
            return False


class URL(Type):
    def __init__(self):
        super(URL, Type.__init__(self, "URL"))

    def extractMultiple(self, propID, data):
        result = []
        for i in range(len(data['claims'][propID])):
            result.append(urlparse(data['claims'][propID][i]['mainsnak']['datavalue']['value']))
        return result

    def extractSingle(self, propID, data):
        return urlparse(data['claims'][propID][0]['mainsnak']['datavalue']['value'])

    def check_conformity(self, propID, data):
        try:
            urlparse(data['claims'][propID][0]['mainsnak']['datavalue']['value'])
            return True
        except Exception as e:
            return False


###
class Time(Type):
    def __init__(self):
        super(Time, Type.__init__(self, "Time"))

    def extractMultiple(self, propID, data):
        result = []
        for i in range(len(data['claims'][propID])):
            result.append(parsedate(data['claims'][propID][i]['mainsnak']['datavalue']['value']['time']))
        return result

    def extractSingle(self, propID, data):
        return parsedate(data['claims'][propID][0]['mainsnak']['datavalue']['value']["time"])

    def check_conformity(self, propID, data):
        try:
            parsedate(data['claims'][propID][0]['mainsnak']['datavalue']['value']["time"])
            return True
        except Exception as e:
            return False


class Quantity(Type):
    def __init__(self):
        super(Quantity, Type.__init__(self, "int"))

    def extractMultiple(self, propID, data):
        result = []
        for i in range(len(data['claims'][propID])):
            val=int(data['claims'][propID][i]['mainsnak']['datavalue']['value']["amount"].replace("+","").replace("-",""))
            data2=data['claims'][propID][i]
            date=""
            if "qualifiers" in data2:
                if "P585" in data2["qualifiers"]:
                    date=data2['qualifiers']["P585"][0]['datavalue']['value']["time"]
            result.append({"quantity":val,"date":date})
        return result

    def extractSingle(self, propID, data):
        date=""
        data2=data['claims'][propID][0]
        if "qualifiers" in data2:
            if "P585" in data2["qualifiers"]:
                date=data2['qualifiers']["P585"][0]['datavalue']['value']["time"]
        return {"quantity":int(data['claims'][propID][0]['mainsnak']['datavalue']['value']["amount"].replace("[^\d.,]","")),"date":date}

    def check_conformity(self, propID, data):
        try:
            int(data['claims'][propID][0]['mainsnak']['datavalue']['value']["amount"].replace("[^\d.,]",""))
            return True
        except Exception as e:
            return False


class ExternalIdentifier(Type):
    def __init__(self):
        super(ExternalIdentifier, Type.__init__(self, "ExternalIdentifier"))

    def extractMultiple(self, propID, data):
        result = []
        for i in range(len(data['claims'][propID])):
            result.append(data['claims'][propID][i]['mainsnak']['datavalue']['value'])
        return result

    def extractSingle(self, propID, data):
        return data['claims'][propID][0]['mainsnak']['datavalue']['value']

    def check_conformity(self, propID, data):
        try:
            data['claims'][propID][0]['mainsnak']['datavalue']['value']
            return True
        except Exception as e:
            return False
