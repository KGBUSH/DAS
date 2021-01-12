from rdflib import Graph, Literal
from rdflib.plugins.sparql import prepareQuery

class Building():
    """
    Used for defining building ontology
    include set operator: set add and set minus
    """
    def __init__(self, buildingID, ontology):
        self.buildingID = buildingID
        self.ontology = ontology

        # This is only a temp fix for caching
        cache = Building.__SUBSYSTEM_LOOKUP__
        if buildingID not in cache:
            cache[buildingID] = {}    
            for sub in ["AHU", "CHILLER", "VAV", "ZONE", "WEATHER", "SOLAR_PANEL"]:
                if sub not in cache[buildingID]:
                    cache[buildingID][sub] = self.extract_subsys(sub)

    def __str__(self):
        return """Building Object:
    ID: {0},
    Ontology: {1}""".format(self.buildingID, self.ontology)
    
    def __repr__(self):
        return """[ Building Object: #ID {0}, #Ontology {1} ... ]""".format(self.buildingID, self.ontology)

    def __add__(self, b):
        if self.buildingID == b.buildingID:
            return Building(self.buildingID, self.ontology + b.ontology)
        else:
            raise TypeError("Can't add ontology from different Building")

    def __sub__(self, b):
        if self.buildingID == b.buildingID:
            return Building(self.buildingID, self.ontology - b.ontology)
        else:
            raise TypeError("Can't take difference from different Building")

    def __mul__(self, b):
        if self.buildingID == b.buildingID:
            ontology1 = self.ontology
            ontology2 = b.ontology
            retval = Graph()
            for (prefix, uri) in set(list(ontology1.namespaces()) + list(ontology2.namespaces())):
                retval.bind(prefix, uri)
            for x in ontology2:
                if x in ontology1:
                    retval.add(x)
            return Building(self.buildingID, retval)
        else:
            raise TypeError("Can't intersect from different Building")

    __or__ = __add__
    __and__ = __mul__

    __subsystem_predicate__ = [ "brick:hasPoint", "brick:hasPart", "brick:hasUuid", "rdf:type" ]
    __SUBSYSTEM_LOOKUP__ = {}

    def forwardQuery(g, retval, sub):
        predicates = ",".join(Building.__subsystem_predicate__)
        # q = prepareQuery(""" select ?sub ?pred ?obj where { ?sub ?pred ?obj . filter ( ?pred IN (%s) ) . }"""%predicates)
        q = """ select ?sub ?pred ?obj where { ?sub ?pred ?obj . filter ( ?pred IN (%s) ) . }"""%predicates
        for row in g.query(q, initBindings = { "sub": sub } ):
            if row[-1] != None:
                retval.add(row)
                Building.forwardQuery(g, retval, row[-1])
    
    def backwardQuery(g, retval, obj):
        q = prepareQuery(""" select ?sub ?pred ?obj where { ?sub ?pred ?obj . }""")
        for row in g.query(q, initBindings = { "obj": obj } ):
            if row[0] != None:
                retval.add(row)
                Building.backwardQuery(g, retval, row[0])

    def extract_subsys(self, subsystem):

        # Cache lookup
        if self.buildingID in Building.__SUBSYSTEM_LOOKUP__ and \
            subsystem in Building.__SUBSYSTEM_LOOKUP__[self.buildingID]:
            return Building.__SUBSYSTEM_LOOKUP__[self.buildingID][subsystem]

        g = self.ontology
        retval = Graph()
        for (prefix, uri) in g.namespaces():
            retval.bind(prefix, uri)
        query = """ select ?sub ?pred ?obj where { ?sub ?pred ?obj . filter (?pred = rdf:type && ?obj = brick:%s) .} """%subsystem
        for (sub, pred, obj) in g.query(query):
            retval.add((sub, pred, obj))
            Building.forwardQuery(g, retval, sub)

        return BuildingSub(self.buildingID, subsystem, retval)

    def extract_functional(self, functional):
        g = self.ontology  # todo: this is graph
        retval = Graph()
        for (prefix, uri) in g.namespaces():
            retval.bind(prefix, uri)
        query = """ select ?sub ?pred ?obj where { ?sub ?pred ?obj . filter ( regex(lcase(str(?sub)), '%s') || regex(lcase(str(?obj)), '%s') ) .}"""%(functional.lower(), functional.lower())

        # todo RDF 的lib的query的实现，输入sparql，
        for (sub, pred, obj) in g.query(query):
            retval.add((sub, pred, obj))

        return BuildingSub(self.buildingID, functional, retval)

class BuildingSub(Building):
    """
    Sub-Ontology of a building
    """
    def __init__(self, BuildingID, subID, ontology):
        self.subID = subID
        super().__init__(BuildingID, ontology)