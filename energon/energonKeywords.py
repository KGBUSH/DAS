from pyparsing import Keyword, MatchFirst

SELECT = Keyword("SELECT", caseless = True)
FROM = Keyword("FROM", caseless = True)
WHERE = Keyword("WHERE", caseless = True)
FILTER = Keyword("FILTER", caseless = True)
LABEL = Keyword("LABEL", caseless = True)
AND = Keyword("AND", caseless = True)
OR = Keyword("OR", caseless = True)

SUBSYSTEM_LOOKUP = ["AHU", "CHILLER", "VAV", "ZONE", "WEATHER", "SOLAR_PANEL"]