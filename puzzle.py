import random
import io
from PIL import Image, ImageDraw, ImageFont

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  THEMES  (20 themes, 50-70 words each)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEMES = {
    "animals": {
        "name": "Animals", "emoji": "🐾",
        "words": [
            "LION","TIGER","ELEPHANT","MONKEY","ZEBRA","GIRAFFE","PANDA","WOLF",
            "EAGLE","SNAKE","BEAR","FOX","DEER","PARROT","CHEETAH","JAGUAR","HIPPO",
            "RHINO","LEMUR","KOALA","BISON","LYNX","GORILLA","LEOPARD","CHIMPANZEE",
            "CROCODILE","FLAMINGO","PENGUIN","KANGAROO","OSTRICH","PEACOCK","HAMSTER",
            "RABBIT","HEDGEHOG","SQUIRREL","RACCOON","BADGER","OTTER","BEAVER","MOOSE",
            "BUFFALO","CAMEL","DONKEY","HORSE","CATTLE","SHEEP","GOAT","PIG","DUCK",
            "SWAN","PIGEON","SPARROW","FALCON","VULTURE","TOUCAN","PELICAN","STORK",
            "HERON","IBIS","MACAW","COCKATOO","IGUANA","GECKO","CHAMELEON","TORTOISE",
            "PYTHON","COBRA","MAMBA","MONITOR",
        ],
        "bg":          (10, 28, 48),
        "header_bg":   (6,  18, 34),
        "cell_bg":     (14, 42, 72),
        "cell_border": (28, 72, 110),
        "accent":      (56, 189, 248),
        "letter":      (220, 242, 255),
        "sub":         (120, 200, 240),
    },
    "fruits": {
        "name": "Fruits", "emoji": "🍎",
        "words": [
            "MANGO","APPLE","GRAPE","BANANA","ORANGE","PAPAYA","GUAVA","LEMON",
            "PEACH","PLUM","CHERRY","MELON","LITCHI","KIWI","BERRY","PEAR","APRICOT",
            "FIG","DATES","COCONUT","JACKFRUIT","POMEGRANATE","STRAWBERRY","BLUEBERRY",
            "RASPBERRY","BLACKBERRY","WATERMELON","PINEAPPLE","AVOCADO","MUSKMELON",
            "STARFRUIT","DRAGONFRUIT","PASSION","CUSTARD","MULBERRY","CRANBERRY",
            "GOOSEBERRY","TAMARIND","PERSIMMON","QUINCE","LOQUAT","SAPOTE","JUJUBE",
            "NECTARINE","TANGERINE","CLEMENTINE","MANDARIN","KUMQUAT","RAMBUTAN",
            "LONGAN","SOURSOP","BREADFRUIT","CARAMBOLA","FEIJOA","DURIAN","MANGOSTEEN",
            "SANTOL","SALAK","ATEMOYA","CHERIMOYA","ILAMA","JABOTICABA","LANGSAT",
            "MAMEY","PITAYA","TAMARILLO","UVILLA",
        ],
        "bg":          (28, 10, 0),
        "header_bg":   (48, 18, 0),
        "cell_bg":     (44, 18, 2),
        "cell_border": (96, 48, 4),
        "accent":      (251, 146, 60),
        "letter":      (255, 220, 175),
        "sub":         (240, 170, 100),
    },
    "ocean": {
        "name": "Ocean", "emoji": "🌊",
        "words": [
            "SHARK","WHALE","DOLPHIN","OCTOPUS","CORAL","TURTLE","SQUID","CRAB",
            "SALMON","LOBSTER","SEAHORSE","NARWHAL","CLAM","URCHIN","BARRACUDA",
            "PUFFERFISH","MANATEE","SEAL","WALRUS","JELLYFISH","SWORDFISH","TUNA",
            "HERRING","MACKEREL","ANCHOVY","SARDINE","GROUPER","SNAPPER","FLOUNDER",
            "HALIBUT","MARLIN","MANTA","STINGRAY","MORAY","ANGLERFISH","LANTERNFISH",
            "OARFISH","COELACANTH","NAUTILUS","ABALONE","CONCH","OYSTER","MUSSEL",
            "SCALLOP","SHRIMP","PRAWN","KRILL","STARFISH","SEAGRASS","KELP",
            "ANEMONE","BARNACLE","CUTTLEFISH","ISOPOD","AMPHIPOD","COPEPOD",
            "ZOOPLANKTON","PLANKTON","DUGONG","ORCA","BELUGA","PORPOISE","REMORA",
            "PILOTFISH","TRIGGERFISH","WRASSE","PARROTFISH","CLOWNFISH","SURGEONFISH",
        ],
        "bg":          (0, 20, 45),
        "header_bg":   (0, 30, 60),
        "cell_bg":     (0, 28, 58),
        "cell_border": (0, 78, 130),
        "accent":      (34, 211, 238),
        "letter":      (200, 248, 255),
        "sub":         (100, 225, 245),
    },
    "space": {
        "name": "Space", "emoji": "🚀",
        "words": [
            "SATURN","JUPITER","MARS","VENUS","URANUS","METEOR","COMET","GALAXY",
            "NEBULA","ASTEROID","ECLIPSE","COSMOS","ORBIT","PULSAR","QUASAR","NEUTRON",
            "SUPERNOVA","HUBBLE","VOYAGER","PLUTO","MERCURY","NEPTUNE","EUROPA","TITAN",
            "GANYMEDE","CALLISTO","DEIMOS","PHOBOS","CERES","ERIS","MAKEMAKE","HAUMEA",
            "AURORA","SOLSTICE","EQUINOX","ZENITH","APOGEE","PERIGEE","PERIHELION",
            "APHELION","PARALLAX","REDSHIFT","BLUESHIFT","SPECTRUM","PHOTON","PROTON",
            "ELECTRON","GRAVITON","BLACKHOLE","WORMHOLE","SINGULARITY","MAGNETAR",
            "PROTOSTAR","MAINSEQUENCE","REDGIANT","WHITEDWARF","BROWNDWARF","EXOPLANET",
            "KEPLER","CASSINI","PIONEER","GALILEO","JUNO","DAWN","ROSETTA","HAYABUSA",
            "OSIRIS","INSIGHT","PERSEVERANCE","CURIOSITY",
        ],
        "bg":          (6, 2, 20),
        "header_bg":   (12, 4, 38),
        "cell_bg":     (14, 4, 44),
        "cell_border": (48, 18, 130),
        "accent":      (167, 139, 250),
        "letter":      (235, 228, 255),
        "sub":         (190, 170, 255),
    },
    "sports": {
        "name": "Sports", "emoji": "⚽",
        "words": [
            "CRICKET","TENNIS","HOCKEY","BOXING","RUGBY","POLO","CHESS","GOLF",
            "KABADDI","ARCHERY","SWIMMING","CYCLING","ROWING","WRESTLING","JUDO",
            "BADMINTON","VOLLEYBALL","BASKETBALL","MARATHON","FENCING","SQUASH",
            "LACROSSE","HANDBALL","SOFTBALL","BASEBALL","FOOTBALL","NETBALL","CROQUET",
            "CURLING","BOBSLED","SKELETON","LUGE","BIATHLON","TRIATHLON","PENTATHLON",
            "DECATHLON","HURDLES","LONGJUMP","HIGHJUMP","POLEVAULT","DISCUS","HAMMER",
            "JAVELIN","SHOTPUT","SPRINT","RELAY","STEEPLECHASE","WEIGHTLIFTING",
            "POWERLIFTING","GYMNASTICS","TRAMPOLINE","ACROBATICS","SKATEBOARDING",
            "SURFING","SNOWBOARD","SKIING","ICESKATING","FIGURESKATING","SPEEDSKATING",
            "KARATE","TAEKWONDO","AIKIDO","KENDO","SUMO","MUAYTHAI","KICKBOXING",
            "FREEFALL","PARAGLIDING","ROCKCLIMBING","MOUNTAINBIKE",
        ],
        "bg":          (2, 22, 4),
        "header_bg":   (4, 34, 6),
        "cell_bg":     (4, 30, 6),
        "cell_border": (8, 88, 12),
        "accent":      (74, 222, 128),
        "letter":      (215, 252, 225),
        "sub":         (130, 235, 165),
    },
    "countries": {
        "name": "Countries", "emoji": "🌍",
        "words": [
            "INDIA","JAPAN","BRAZIL","FRANCE","CHINA","EGYPT","SPAIN","KENYA",
            "ITALY","PERU","NEPAL","GHANA","CANADA","RUSSIA","TURKEY","MEXICO",
            "SWEDEN","NORWAY","FINLAND","DENMARK","NIGERIA","GERMANY","AUSTRIA",
            "BELGIUM","PORTUGAL","GREECE","POLAND","UKRAINE","HUNGARY","ROMANIA",
            "BULGARIA","CROATIA","SERBIA","ALBANIA","GEORGIA","ARMENIA","JORDAN",
            "ISRAEL","LEBANON","SYRIA","IRAQ","IRAN","PAKISTAN","BANGLADESH","SRILANKA",
            "MYANMAR","THAILAND","VIETNAM","CAMBODIA","MALAYSIA","INDONESIA","PHILIPPINES",
            "SINGAPORE","TAIWAN","SOUTHKOREA","MONGOLIA","KAZAKHSTAN","UZBEKISTAN",
            "AZERBAIJAN","ETHIOPIA","TANZANIA","UGANDA","ANGOLA","ZAMBIA","ZIMBABWE",
            "MOZAMBIQUE","SENEGAL","CAMEROON","SUDAN","SOMALIA","RWANDA","BOTSWANA",
            "NAMIBIA","MADAGASCAR","MAURITIUS",
        ],
        "bg":          (28, 2, 38),
        "header_bg":   (48, 4, 58),
        "cell_bg":     (34, 4, 50),
        "cell_border": (84, 10, 130),
        "accent":      (232, 121, 249),
        "letter":      (250, 228, 255),
        "sub":         (235, 165, 252),
    },
    "food": {
        "name": "Food", "emoji": "🍕",
        "words": [
            "PIZZA","BURGER","NOODLES","SALAD","TACO","SUSHI","CURRY","BIRYANI",
            "PASTA","SANDWICH","WAFFLE","PANCAKE","DUMPLING","RAMEN","KEBAB","BURRITO",
            "GYOZA","FALAFEL","LASAGNA","SHAWARMA","MOMOS","DOSA","IDLI","VADA",
            "SAMOSA","PAKORA","POHA","UPMA","KHICHDI","PARATHA","NAAN","ROTI",
            "PURI","HALWA","LADOO","BARFI","JALEBI","GULAB","RASGULLA","KHEER",
            "KULFI","PEDA","MODAK","DHOKLA","KACHORI","BHATURA","CHOLE","RAJMA",
            "DALBAATI","BIRYAANI","PULAO","KORMA","NIHARI","HALEEM","KEEMA",
            "QORMA","PAYA","SAAG","PANEER","KADHAI","MAKHANI","TIKKA","TANDOORI",
            "GAZPACHO","PAELLA","RISOTTO","GOULASH","PIEROGI","BAKLAVA","HUMMUS",
            "TZATZIKI","MOUSSAKA","TAGINE","INJERA","JOLLOF","POUTINE",
        ],
        "bg":          (28, 6, 16),
        "header_bg":   (50, 10, 24),
        "cell_bg":     (36, 8, 18),
        "cell_border": (110, 24, 56),
        "accent":      (251, 113, 133),
        "letter":      (255, 228, 232),
        "sub":         (252, 160, 175),
    },
    "bollywood": {
        "name": "Bollywood", "emoji": "🎬",
        "words": [
            "SHOLAY","DILWALE","LAGAAN","DEVDAS","MUGHAL","BAJIRAO","DANGAL",
            "BRAHMASTRA","PATHAAN","SINGHAM","DHOOM","KRRISH","DHAMAAL","GOLMAAL",
            "BAAZIGAR","DEEWAR","AGNEEPATH","TAARE","ZINDAGI","GANGS","KABIR",
            "SULTAN","TIGER","RAEES","ROCKSTAR","BARFI","JAWAN","ANIMAL","KALKI",
            "PUSHPA","VIKRAM","BAHUBALI","MAGADHEERA","ROBOT","ENTHIRAN","GHAJINI",
            "SAAWARIYA","DEVDAAS","OMKARA","HAIDER","UDTA","MASAAN","KAPOOR",
            "BOMBAY","RANGEELA","DILJALE","DILRUBA","DAMINI","YAARANA","TEZAAB",
            "TRIDEV","TRISHUL","SHAKTI","KRANTI","COOLIE","MARD","TOOFAN","BETA",
            "HERA","PHERI","SINGH","ROWDY","WANTED","DABANGG","READY","BODYGUARD",
            "EK","THA","TIGER","KICK","BANG","BANG","PREM","RATAN","DHAN","PAYO",
            "DILBAR","DHADKAN",
        ],
        "bg":          (28, 18, 0),
        "header_bg":   (52, 28, 0),
        "cell_bg":     (34, 22, 0),
        "cell_border": (110, 70, 4),
        "accent":      (251, 191, 36),
        "letter":      (255, 244, 200),
        "sub":         (252, 215, 100),
    },
    "science": {
        "name": "Science", "emoji": "🔬",
        "words": [
            "ATOM","MOLECULE","ELECTRON","PROTON","NEUTRON","NUCLEUS","PHOTON",
            "QUANTUM","GRAVITY","FRICTION","VELOCITY","MOMENTUM","INERTIA","DENSITY",
            "PRESSURE","VOLTAGE","CURRENT","RESISTANCE","CAPACITOR","INDUCTOR",
            "TRANSISTOR","DIODE","LASER","PLASMA","ENTROPY","ENTHALPY","CATALYST",
            "ENZYME","PROTEIN","LIPID","CARBOHYDRATE","VITAMIN","MINERAL","HORMONE",
            "ANTIBODY","ANTIGEN","VACCINE","BACTERIA","VIRUS","FUNGI","PARASITE",
            "CHROMOSOME","GENOME","GENE","ALLELE","MUTATION","EVOLUTION","FOSSIL",
            "STRATA","MAGMA","IGNEOUS","SEDIMENT","METAMORPHIC","EROSION","TECTONIC",
            "SEISMIC","TSUNAMI","VOLCANO","HURRICANE","TORNADO","CYCLONE","MONSOON",
            "OSMOSIS","DIFFUSION","DIALYSIS","ELECTROLYSIS","PHOTOSYNTHESIS",
            "RESPIRATION","FERMENTATION","COMBUSTION","OXIDATION","REDUCTION",
        ],
        "bg":          (0, 28, 28),
        "header_bg":   (0, 18, 18),
        "cell_bg":     (0, 40, 42),
        "cell_border": (0, 100, 100),
        "accent":      (52, 211, 153),
        "letter":      (200, 255, 245),
        "sub":         (100, 230, 210),
    },
    "technology": {
        "name": "Technology", "emoji": "💻",
        "words": [
            "PYTHON","JAVA","KOTLIN","SWIFT","GOLANG","RUST","TYPESCRIPT","JAVASCRIPT",
            "CPLUSPLUS","CSHARP","RUBY","SCALA","HASKELL","ERLANG","ELIXIR","CLOJURE",
            "FORTRAN","COBOL","PASCAL","LISP","PROLOG","MATLAB","OCTAVE","JULIA",
            "DOCKER","KUBERNETES","TERRAFORM","ANSIBLE","JENKINS","GITHUB","GITLAB",
            "BITBUCKET","JIRA","CONFLUENCE","SLACK","NOTION","FIGMA","SKETCH",
            "PHOTOSHOP","ILLUSTRATOR","PREMIERE","AFTEREFFECTS","BLENDER","UNITY",
            "UNREAL","GODOT","PYGAME","OPENGL","VULKAN","DIRECTX","WEBGL","THREEJS",
            "REACT","ANGULAR","VUEJS","SVELTE","NEXTJS","NUXTJS","GATSBY","REMIX",
            "DJANGO","FLASK","FASTAPI","SPRING","LARAVEL","RAILS","EXPRESS","NESTJS",
            "MONGODB","POSTGRES","MYSQL","REDIS","CASSANDRA","ELASTICSEARCH","KAFKA",
        ],
        "bg":          (10, 10, 30),
        "header_bg":   (6, 6, 20),
        "cell_bg":     (16, 16, 46),
        "cell_border": (40, 40, 120),
        "accent":      (99, 179, 237),
        "letter":      (220, 235, 255),
        "sub":         (140, 190, 240),
    },
    "mythology": {
        "name": "Mythology", "emoji": "⚡",
        "words": [
            "ZEUS","HERA","POSEIDON","ATHENA","APOLLO","ARTEMIS","ARES","APHRODITE",
            "HERMES","HEPHAESTUS","DIONYSUS","DEMETER","PERSEPHONE","HADES","HESTIA",
            "CHRONOS","TITANS","PROMETHEUS","EPIMETHEUS","ATLAS","HERCULES","ACHILLES",
            "ODYSSEUS","PERSEUS","THESEUS","JASON","ORPHEUS","NARCISSUS","MIDAS",
            "ODIN","THOR","LOKI","FREYA","TYRE","HEIMDALL","BALDUR","FRIGG","SKADI",
            "NJORD","AEGIR","FENRIR","JORMUNGANDR","SLEIPNIR","HUGINN","MUNINN",
            "BRAHMA","VISHNU","SHIVA","LAKSHMI","SARASWATI","PARVATI","DURGA","KALI",
            "GANESHA","KARTIK","INDRA","VARUNA","AGNI","VAYU","SURYA","CHANDRA",
            "YAMA","KUBERA","HANUMAN","RAMA","KRISHNA","ARJUNA","OSIRIS","ISIS",
            "HORUS","ANUBIS","THOTH","SEKHMET","BASTET","RA","PTAH","SOBEK","SET",
        ],
        "bg":          (20, 10, 40),
        "header_bg":   (30, 14, 56),
        "cell_bg":     (28, 14, 52),
        "cell_border": (80, 40, 140),
        "accent":      (251, 191, 36),
        "letter":      (255, 248, 220),
        "sub":         (240, 210, 130),
    },
    "music": {
        "name": "Music", "emoji": "🎵",
        "words": [
            "GUITAR","PIANO","VIOLIN","DRUMS","TRUMPET","FLUTE","CELLO","VIOLA",
            "HARP","TROMBONE","CLARINET","SAXOPHONE","OBOE","BASSOON","ACCORDION",
            "SITAR","TABLA","MRIDANGAM","VEENA","SAROD","SANTOOR","BANSURI","SHEHNAI",
            "DHOLAK","DHOL","MRIDANG","KANJIRA","GHATAM","THAVIL","NADASWARAM",
            "BASS","TREBLE","MELODY","HARMONY","RHYTHM","TEMPO","TIMBRE","PITCH",
            "OCTAVE","CHORD","SCALE","MAJOR","MINOR","SHARP","FLAT","NATURAL",
            "ALLEGRO","ANDANTE","ADAGIO","PRESTO","FORTE","PIANO","MEZZO","SFORZANDO",
            "SYMPHONY","CONCERTO","SONATA","OPERA","BALLAD","PRELUDE","FUGUE","SUITE",
            "NOCTURNE","ETUDE","RHAPSODY","CANTATA","ORATORIO","MOTET","MADRIGAL",
            "RAGA","TALA","BHAJAN","QAWWALI","GHAZAL","THUMRI","DADRA","KAJRI",
        ],
        "bg":          (20, 0, 30),
        "header_bg":   (30, 0, 44),
        "cell_bg":     (28, 2, 40),
        "cell_border": (90, 10, 120),
        "accent":      (216, 180, 254),
        "letter":      (248, 240, 255),
        "sub":         (200, 160, 245),
    },
    "geography": {
        "name": "Geography", "emoji": "🗺️",
        "words": [
            "AMAZON","NILE","YANGTZE","MISSISSIPPI","GANGES","DANUBE","VOLGA","NIGER",
            "ZAMBEZI","COLORADO","ORINOCO","EUPHRATES","TIGRIS","INDUS","MEKONG",
            "HIMALAYAS","ANDES","ROCKIES","ALPS","PYRENEES","CAUCASUS","URALS","ATLAS",
            "KILIMANJARO","EVEREST","KANGCHENJUNGA","LHOTSE","MAKALU","ACONCAGUA",
            "SAHARA","GOBI","ARABIAN","ATACAMA","MOJAVE","SONORAN","THAR","KARAKUM",
            "KALAHARI","NAMIB","SIMPSON","PATAGONIA","ANTARCTICA","ARCTIC","SIBERIA",
            "AMAZON","CONGO","DAINTREE","BORNEO","SUMATRA","TAIGA","TUNDRA","PRAIRIE",
            "SAVANNA","STEPPE","WETLAND","ESTUARY","DELTA","LAGOON","FJORD","CANYON",
            "PLATEAU","PENINSULA","ARCHIPELAGO","ATOLL","ISTHMUS","STRAIT","CAPE",
            "GLACIER","ICEBERG","PERMAFROST","GEYSER","HOTSPRING","CAVERN","KARST",
        ],
        "bg":          (0, 20, 10),
        "header_bg":   (0, 30, 14),
        "cell_bg":     (0, 28, 12),
        "cell_border": (0, 90, 40),
        "accent":      (110, 231, 183),
        "letter":      (220, 255, 240),
        "sub":         (130, 220, 185),
    },
    "movies": {
        "name": "Movies", "emoji": "🎥",
        "words": [
            "INCEPTION","INTERSTELLAR","AVATAR","TITANIC","MATRIX","GLADIATOR",
            "BRAVEHEART","GLADIATOR","SCARFACE","GODFATHER","GOODFELLAS","CASINO",
            "PULPFICTION","RESERVOIR","PARASITE","JOKER","TENET","DUNKIRK","OPPENHEIMER",
            "BARBIE","DUNE","ARRIVAL","GRAVITY","MARTIAN","FURY","SELMA","SPOTLIGHT",
            "MOONLIGHT","NOMADLAND","BIRDMAN","WHIPLASH","BOYHOOD","REVENANT",
            "HACKSAW","DARKEST","SHAPE","GREENBOOK","CRASH","CHICAGO","PIANIST",
            "GLADIATOR","BEAUTIFUL","GLADIATOR","SILENCE","FARGO","BIGLEBOWSKI",
            "TRUMAN","ETERNAL","BUTTERFLY","PRESTIGE","SHINING","CLOCKWORK","KUBRICK",
            "LYNCH","FINCHER","NOLAN","SPIELBERG","SCORSESE","TARANTINO","KUBRICK",
            "COPPOLA","ANDERSON","VILLENEUVE","CUARON","IÑARRITU","COENS","ALMODOVAR",
            "BERGMAN","TARKOVSKY","KUROSAWA","LEONE","FELLINI","GODARD","TRUFFAUT",
        ],
        "bg":          (20, 10, 0),
        "header_bg":   (32, 16, 0),
        "cell_bg":     (28, 14, 2),
        "cell_border": (100, 50, 10),
        "accent":      (251, 146, 60),
        "letter":      (255, 235, 210),
        "sub":         (240, 185, 120),
    },
    "history": {
        "name": "History", "emoji": "🏛️",
        "words": [
            "CAESAR","CLEOPATRA","NAPOLEON","ALEXANDER","GENGHIS","SALADIN","ATTILA",
            "HANNIBAL","AUGUSTUS","HADRIAN","CONSTANTINE","JUSTINIAN","CHARLEMAGNE",
            "CRUSADES","RENAISSANCE","REFORMATION","REVOLUTION","COLONIALISM","EMPIRE",
            "REPUBLIC","DEMOCRACY","MONARCHY","FEUDALISM","ARISTOCRACY","OLIGARCHY",
            "PYRAMID","PARTHENON","COLOSSEUM","PANTHEON","ACROPOLIS","STONEHENGE",
            "MACHU","ANGKOR","BOROBUDUR","PERSEPOLIS","BABYLON","CARTHAGE","SPARTA",
            "ATHENS","THEBES","MEMPHIS","ROME","TROY","MYCENAE","KNOSSOS","UR",
            "NINEVEH","ASSUR","BABYLON","SUMER","AKKAD","EGYPT","INDUS","SHANG",
            "ZHOU","QING","MING","TANG","SONG","HAN","ROMAN","BYZANTINE","OTTOMAN",
            "MUGHAL","SAFAVID","MONGOL","VIKING","NORMAN","SAXON","FRANKISH","CELTIC",
            "AZTEC","MAYA","INCA","OLMEC","TOLTEC","ZAPOTEC","MISSISSIPPI","PUEBLO",
        ],
        "bg":          (30, 20, 10),
        "header_bg":   (44, 28, 12),
        "cell_bg":     (38, 24, 10),
        "cell_border": (110, 70, 30),
        "accent":      (245, 208, 130),
        "letter":      (255, 248, 220),
        "sub":         (230, 195, 110),
    },
    "cricket": {
        "name": "Cricket", "emoji": "🏏",
        "words": [
            "BATTING","BOWLING","FIELDING","WICKET","STUMPS","BAILS","CREASE","PITCH",
            "BOUNDARY","SIXER","FOUR","CENTURY","FIFTY","DUCK","GOLDEN","MAIDEN",
            "OVER","INNINGS","FOLLOW","DECLARATION","DRAW","TIE","SUPEROVER",
            "YORKER","BOUNCER","GOOGLY","DOOSRA","FLIPPER","CARROM","SEAMER","SWINGER",
            "SPINNER","PACER","ALLROUNDER","WICKETKEEPER","OPENER","NIGHTWATCHMAN",
            "PINCHITTER","TAILENDER","CAPTAIN","SKIPPER","UMPIRE","REFEREE","THIRD",
            "LEGBEFORE","CAUGHT","BOWLED","STUMPED","RUNOUT","HITWICKET","OBSTRUCTING",
            "NBALL","WIDEBALL","LEGBYE","BYE","OVERTHROW","POWERPLAY","DEATHOVER",
            "COLLARBONE","HELMET","GLOVES","PADS","THIGHGUARD","ABDOMINAL","GRILLE",
            "REDBALL","WHITEBALL","PINKBALL","DUKES","KOOKABURRA","SG","TURF",
            "SACHIN","KOHLI","ROHIT","DHONI","BUMRAH","ASHWIN","JADEJA","SHAMI",
        ],
        "bg":          (0, 22, 10),
        "header_bg":   (0, 32, 14),
        "cell_bg":     (2, 30, 12),
        "cell_border": (10, 100, 50),
        "accent":      (52, 211, 153),
        "letter":      (215, 255, 235),
        "sub":         (110, 230, 175),
    },
    "nature": {
        "name": "Nature", "emoji": "🌿",
        "words": [
            "ROSE","LOTUS","TULIP","ORCHID","JASMINE","LAVENDER","SUNFLOWER","DAISY",
            "LILY","MARIGOLD","HIBISCUS","MAGNOLIA","PEONY","DAHLIA","ZINNIA","POPPY",
            "DAFFODIL","HYACINTH","IRIS","PRIMROSE","VIOLET","PANSY","PETUNIA","ASTER",
            "OAK","MAPLE","PINE","CEDAR","BIRCH","WILLOW","BAMBOO","BANYAN","NEEM",
            "MANGO","TEAK","MAHOGANY","EBONY","ROSEWOOD","SANDALWOOD","WALNUT","CHESTNUT",
            "FERN","MOSS","LICHEN","ALGAE","CACTUS","SUCCULENT","MANGROVE","SEAGRASS",
            "MUSHROOM","TRUFFLE","MOREL","CHANTERELLE","PORCINI","SHIITAKE","OYSTER",
            "MONSOON","DRIZZLE","THUNDERSTORM","BLIZZARD","HAILSTORM","SNOWFALL","FOG",
            "RAINBOW","HALO","AURORA","MIRAGE","ECLIPSE","SOLSTICE","EQUINOX","ZENITH",
            "RIVER","STREAM","BROOK","WATERFALL","SPRING","LAKE","POND","SWAMP",
        ],
        "bg":          (4, 24, 4),
        "header_bg":   (6, 34, 6),
        "cell_bg":     (6, 32, 8),
        "cell_border": (12, 96, 20),
        "accent":      (134, 239, 172),
        "letter":      (220, 255, 225),
        "sub":         (150, 240, 175),
    },
    "vehicles": {
        "name": "Vehicles", "emoji": "🚗",
        "words": [
            "FERRARI","LAMBORGHINI","BUGATTI","MCLAREN","PAGANI","KOENIGSEGG","RIMAC",
            "PORSCHE","MERCEDES","BMW","AUDI","VOLKSWAGEN","TOYOTA","HONDA","NISSAN",
            "MAZDA","SUBARU","MITSUBISHI","LEXUS","INFINITI","ACURA","GENESIS","KIA",
            "HYUNDAI","TESLA","RIVIAN","LUCID","POLESTAR","VOLVO","JAGUAR","LANDROVER",
            "ROLLS","BENTLEY","ASTON","MASERATI","ALFA","FIAT","LANCIA","FERRARI",
            "HARLEY","DUCATI","YAMAHA","KAWASAKI","HONDA","SUZUKI","BMW","TRIUMPH",
            "BOEING","AIRBUS","CONCORDE","HERCULES","OSPREY","APACHE","CHINOOK","HAWK",
            "TITANIC","QUEEN","ENDEAVOUR","NAUTILUS","TRITON","ALVIN","SHINKAI","NEREID",
            "SPACEX","SOYUZ","SHUTTLE","ARIANE","FALCON","STARSHIP","DRAGON","CREW",
            "BULLET","MAGLEV","SHINKANSEN","EUROSTAR","ACELA","PENDOLINO","VELARO",
            "CATERPILLAR","KOMATSU","LIEBHERR","VOLVO","TEREX","MANITOWOC","GROVE",
        ],
        "bg":          (18, 10, 0),
        "header_bg":   (28, 14, 0),
        "cell_bg":     (24, 12, 2),
        "cell_border": (80, 44, 8),
        "accent":      (252, 165, 50),
        "letter":      (255, 240, 210),
        "sub":         (240, 195, 120),
    },
    "bodyparts": {
        "name": "Human Body", "emoji": "🫀",
        "words": [
            "BRAIN","HEART","LIVER","KIDNEY","LUNGS","STOMACH","PANCREAS","SPLEEN",
            "THYROID","PITUITARY","ADRENAL","THYMUS","APPENDIX","GALLBLADDER","BLADDER",
            "TRACHEA","BRONCHI","ALVEOLI","AORTA","VENA","ARTERY","CAPILLARY","VEIN",
            "NEURON","SYNAPSE","AXON","DENDRITE","CORTEX","CEREBELLUM","BRAINSTEM",
            "HIPPOCAMPUS","AMYGDALA","THALAMUS","HYPOTHALAMUS","RETINA","CORNEA",
            "COCHLEA","EARDRUM","MALLEUS","INCUS","STAPES","FEMUR","TIBIA","FIBULA",
            "PATELLA","HUMERUS","RADIUS","ULNA","CARPALS","METACARPAL","PHALANGES",
            "VERTEBRA","STERNUM","CLAVICLE","SCAPULA","PELVIS","SACRUM","COCCYX",
            "BICEPS","TRICEPS","DELTOID","TRAPEZIUS","LATISSIMUS","PECTORAL","GLUTEUS",
            "QUADRICEPS","HAMSTRING","CALF","ACHILLES","PLANTAR","ROTATOR","FLEXOR",
            "EPIDERMIS","DERMIS","MELANIN","KERATIN","COLLAGEN","ELASTIN","SEBACEOUS",
        ],
        "bg":          (28, 4, 14),
        "header_bg":   (42, 6, 20),
        "cell_bg":     (34, 6, 18),
        "cell_border": (110, 20, 60),
        "accent":      (249, 168, 212),
        "letter":      (255, 240, 248),
        "sub":         (245, 185, 220),
    },
    "games": {
        "name": "Games", "emoji": "🎮",
        "words": [
            "MINECRAFT","FORTNITE","ROBLOX","PUBG","VALORANT","CSGO","OVERWATCH",
            "LEAGUE","DOTA","HEARTHSTONE","STARCRAFT","WARCRAFT","DIABLO","WITCHER",
            "CYBERPUNK","ELDENRING","DARKSOULS","BLOODBORNE","SEKIRO","NIOH",
            "POKEMON","ZELDA","MARIO","METROID","KIRBY","SPLATOON","SMASH","PIKMIN",
            "HALO","GEARS","FABLE","FORZA","HORIZON","DESTINY","ANTHEM","OUTRIDERS",
            "GODOFWAR","SPIDERMAN","HORIZON","GHOST","RATCHET","RETURNAL","DEMONS",
            "FINALFANTASY","PERSONA","DRAGONQUEST","KINGDOMHEARTS","XENOBLADE",
            "RESIDENTEVIL","DEVILMAYCRY","MONSTERHUNTER","DEEPRISINGS","DRAGONSDOGMA",
            "FALLOUT","SKYRIM","OBLIVION","MORROWIND","STARFIELD","DRAGONAGE",
            "MASSEFFECT","BALDUR","DIVINITY","PILLARS","PATHFINDER","WASTELAND",
            "MINECRAFT","TERRARIA","STARDEW","HADES","CELESTE","HOLLOW","ORI",
        ],
        "bg":          (8, 4, 28),
        "header_bg":   (12, 6, 40),
        "cell_bg":     (12, 6, 36),
        "cell_border": (44, 20, 110),
        "accent":      (167, 139, 250),
        "letter":      (235, 228, 255),
        "sub":         (190, 165, 248),
    },
    "flags": {
        "name": "Flags & Nations", "emoji": "🚩",
        "words": [
            "TRICOLOR","CRESCENT","STRIPES","CANTON","ENSIGN","PENNANT","STANDARD",
            "EMBLEM","CREST","SHIELD","EAGLE","LION","DRAGON","MAPLE","CEDAR",
            "RISING","SETTING","CROSS","SALTIRE","NORDIC","UNION","JACK","STARS",
            "HAMMER","SICKLE","LAUREL","WREATH","OLIVE","BRANCH","SWORD","CROWN",
            "SCEPTER","ORB","FLEUR","LISE","THISTLE","SHAMROCK","DAFFODIL","LEEK",
            "DRAGON","UNICORN","GRIFFIN","PHOENIX","RAMPANT","PASSANT","COUCHANT",
            "AZURE","GULES","SABLE","ARGENT","VERT","PURPURE","TENNÉ","SANGUINE",
            "QUARTERLY","PER PALE","CHEVRON","FESS","BEND","PILE","PALL","GYRONNY",
            "ROUNDEL","MULLET","FLAUNCHES","CANTON","INESCUTCHEON","ORDINARY",
            "BLAZON","HERALD","ARMORY","TINCTURE","CHARGE","SUPPORTER","MOTTO",
        ],
        "bg":          (10, 10, 44),
        "header_bg":   (6, 6, 30),
        "cell_bg":     (14, 14, 58),
        "cell_border": (40, 40, 140),
        "accent":      (248, 68, 68),
        "letter":      (255, 235, 235),
        "sub":         (245, 160, 160),
    },
    "fashion": {
        "name": "Fashion", "emoji": "👗",
        "words": [
            "VOGUE","RUNWAY","COUTURE","CHANEL","GUCCI","PRADA","VERSACE","ARMANI",
            "DIOR","HERMES","BALENCIAGA","GIVENCHY","VALENTINO","BURBERRY","CARTIER",
            "LOUBOUTIN","MANOLO","JIMMY","MCQUEEN","WESTWOOD","MIYAKE","KENZO","LOEWE",
            "CELINE","LANVIN","BALMAIN","JACOBS","WANG","MCQUEEN","TISCI","ABLOH",
            "BLAZER","TRENCH","TUXEDO","KIMONO","SARI","KILT","PONCHO","KAFTAN",
            "CHIFFON","VELVET","CASHMERE","ORGANZA","TAFFETA","BROCADE","TWEED","DENIM",
            "STILETTO","PLATFORM","KITTEN","SLINGBACK","MULE","LOAFER","BROGUE","OXFORD",
            "CLUTCH","TOTE","SATCHEL","DUFFEL","HOBO","WRISTLET","CROSSBODY","BUCKET",
            "FASCINATOR","CLOCHE","BERET","FEDORA","TRILBY","BOATER","PILLBOX","TURBAN",
            "BROOCH","BANGLE","CHOKER","PENDANT","CUFFLINK","TIARA","CORSAGE","LAPEL",
        ],
        "bg":          (30, 0, 20),
        "header_bg":   (46, 0, 30),
        "cell_bg":     (38, 2, 26),
        "cell_border": (120, 10, 80),
        "accent":      (244, 114, 182),
        "letter":      (255, 235, 248),
        "sub":         (240, 170, 215),
    },
    "architecture": {
        "name": "Architecture", "emoji": "🏛️",
        "words": [
            "BAROQUE","GOTHIC","NEOCLASSICAL","MODERNIST","BRUTALIST","FUTURIST",
            "DECONSTRUCTIVIST","POSTMODERN","BAUHAUS","ARTDECO","CRAFTSMAN","COLONIAL",
            "ROMANESQUE","BYZANTINE","OTTOMAN","MUGHAL","DRAVIDIAN","NAGARA","VESARA",
            "PAGODA","ZIGGURAT","MASTABA","STUPA","TORII","MINARET","CAMPANILE","SPIRE",
            "NAVE","APSE","TRANSEPT","CHANCEL","NARTHEX","CLERESTORY","TRIFORIUM",
            "BUTTRESS","GARGOYLE","FINIAL","PINNACLE","PARAPET","BATTLEMENT","MERLON",
            "COLONNADE","PORTICO","LOGGIA","ARCADE","ATRIUM","ROTUNDA","CUPOLA","DOME",
            "PEDIMENT","ENTABLATURE","CORNICE","FRIEZE","ARCHITRAVE","CAPITAL","SHAFT",
            "PLINTH","STYLOBATE","CREPIDOMA","EUTHYNTERIA","FOUNDATION","KEYSTONE",
            "VOUSSOIR","SPRINGER","HAUNCH","SOFFIT","INTRADOS","EXTRADOS","SPANDREL",
        ],
        "bg":          (24, 18, 8),
        "header_bg":   (36, 26, 10),
        "cell_bg":     (30, 22, 10),
        "cell_border": (100, 76, 34),
        "accent":      (234, 179, 8),
        "letter":      (255, 248, 215),
        "sub":         (220, 190, 90),
    },
    "weather": {
        "name": "Weather", "emoji": "⛈️",
        "words": [
            "TYPHOON","CYCLONE","HURRICANE","TORNADO","WATERSPOUT","BLIZZARD","DERECHO",
            "HABOOB","SIROCCO","MISTRAL","CHINOOK","FOEHN","BORA","TRAMONTANE","LEVANTE",
            "THUNDERSTORM","LIGHTNING","SUPERCELL","MICROBURST","DOWNBURST","SQUALL",
            "CUMULUS","NIMBUS","STRATUS","CIRRUS","CUMULONIMBUS","ALTOCUMULUS","LENTICULAR",
            "MAMMATUS","ARCUS","PILEUS","VIRGA","PRECIPITATION","DRIZZLE","SLEET","HAIL",
            "SNOWFLAKE","BLIZZARD","WHITEOUT","FREEZING","PERMAFROST","HOARFROST","RIME",
            "TEMPERATURE","HUMIDITY","BAROMETRIC","PRESSURE","DEWPOINT","WINDCHILL",
            "FORECAST","RADAR","DOPPLER","SATELLITE","RADIOSONDE","ANEMOMETER","BAROMETER",
            "THERMOMETER","HYGROMETER","PYRANOMETER","PLUVIOMETER","CEILOMETER","LIDAR",
            "ISOTHERM","ISOBAR","ISOHYET","FRONT","TROUGH","RIDGE","VORTEX","JET",
        ],
        "bg":          (4, 18, 36),
        "header_bg":   (6, 24, 48),
        "cell_bg":     (6, 22, 44),
        "cell_border": (20, 80, 160),
        "accent":      (147, 197, 253),
        "letter":      (225, 242, 255),
        "sub":         (160, 215, 255),
    },
    "medicine": {
        "name": "Medicine", "emoji": "🏥",
        "words": [
            "CARDIOLOGY","NEUROLOGY","ONCOLOGY","PEDIATRICS","PSYCHIATRY","ORTHOPEDICS",
            "DERMATOLOGY","OPHTHALMOLOGY","OTOLARYNGOLOGY","UROLOGY","NEPHROLOGY",
            "GASTROENTEROLOGY","ENDOCRINOLOGY","HEMATOLOGY","IMMUNOLOGY","RHEUMATOLOGY",
            "PULMONOLOGY","RADIOLOGY","PATHOLOGY","ANESTHESIA","SURGERY","EMERGENCY",
            "DIAGNOSIS","PROGNOSIS","ETIOLOGY","SYMPTOM","SYNDROME","DISEASE","DISORDER",
            "INFLAMMATION","INFECTION","SEPSIS","NECROSIS","FIBROSIS","SCLEROSIS",
            "HYPERTENSION","DIABETES","ASTHMA","EPILEPSY","ALZHEIMER","PARKINSON",
            "STETHOSCOPE","SPHYGMOMANOMETER","OTOSCOPE","OPHTHALMOSCOPE","LARYNGOSCOPE",
            "ENDOSCOPE","COLONOSCOPE","BRONCHOSCOPE","LAPAROSCOPE","ARTHROSCOPE",
            "ANTIBIOTIC","ANTIVIRAL","ANALGESIC","ANTIPYRETIC","ANTICOAGULANT","DIURETIC",
            "VASODILATOR","BRONCHODILATOR","CORTICOSTEROID","IMMUNOSUPPRESSANT","VACCINE",
        ],
        "bg":          (0, 26, 20),
        "header_bg":   (0, 18, 14),
        "cell_bg":     (0, 36, 28),
        "cell_border": (0, 110, 80),
        "accent":      (52, 211, 153),
        "letter":      (210, 255, 240),
        "sub":         (100, 230, 190),
    },
    "literature": {
        "name": "Literature", "emoji": "📚",
        "words": [
            "SHAKESPEARE","TOLKIEN","DICKENS","AUSTEN","HEMINGWAY","FITZGERALD","ORWELL",
            "KAFKA","DOSTOYEVSKY","TOLSTOY","CHEKHOV","PUSHKIN","GOGOL","TURGENEV",
            "FLAUBERT","BALZAC","ZOLA","PROUST","CAMUS","SARTRE","BAUDELAIRE","RIMBAUD",
            "DANTE","BOCCACCIO","PETRARCH","CERVANTES","LORCA","NERUDA","BORGES","MARQUEZ",
            "TAGORE","PREMCHAND","MANTO","FAIZ","GHALIB","MIRZA","IQBAL","ANAND","RAO",
            "NARAYAN","RUSHDIE","GHOSH","SETH","DESAI","ADIGA","LAHIRI","CHANDRA",
            "METAPHOR","SIMILE","ALLITERATION","ONOMATOPOEIA","PERSONIFICATION","HYPERBOLE",
            "SOLILOQUY","MONOLOGUE","DIALOGUE","NARRATOR","PROTAGONIST","ANTAGONIST",
            "SONNET","HAIKU","ELEGY","ODE","BALLAD","EPIC","LYRIC","DRAMATIC",
            "DENOUEMENT","CLIMAX","SUBPLOT","FLASHBACK","FORESHADOWING","MOTIF","THEME",
        ],
        "bg":          (20, 10, 0),
        "header_bg":   (32, 14, 0),
        "cell_bg":     (26, 12, 2),
        "cell_border": (96, 50, 10),
        "accent":      (251, 146, 60),
        "letter":      (255, 238, 218),
        "sub":         (238, 185, 125),
    },
    "finance": {
        "name": "Finance", "emoji": "💰",
        "words": [
            "BITCOIN","ETHEREUM","BLOCKCHAIN","DEFI","STAKING","MINING","WALLET","LEDGER",
            "NASDAQ","SENSEX","NIFTY","DOWJONES","FTSE","NIKKEI","HANGSENG","SHANGHAI",
            "EQUITY","BOND","DERIVATIVE","FUTURES","OPTIONS","WARRANT","CONVERTIBLE",
            "DIVIDEND","YIELD","COUPON","MATURITY","DURATION","CONVEXITY","SPREAD",
            "PORTFOLIO","DIVERSIFICATION","HEDGING","ARBITRAGE","LEVERAGE","MARGIN",
            "BULLISH","BEARISH","VOLATILE","LIQUIDITY","SOLVENCY","LEVERAGE","BETA",
            "ALPHA","SHARPE","SORTINO","TREYNOR","JENSEN","CAPM","WACC","DCF","NPV",
            "IRR","PAYBACK","EBITDA","REVENUE","PROFIT","MARGIN","CASHFLOW","BALANCE",
            "INCOME","ASSET","LIABILITY","EQUITY","CAPITAL","RESERVES","GOODWILL",
            "DEPRECIATION","AMORTIZATION","IMPAIRMENT","PROVISION","ACCRUAL","DEFERRED",
        ],
        "bg":          (4, 20, 4),
        "header_bg":   (6, 30, 6),
        "cell_bg":     (6, 28, 8),
        "cell_border": (12, 100, 20),
        "accent":      (74, 222, 128),
        "letter":      (215, 255, 225),
        "sub":         (120, 230, 160),
    },
    "aviation": {
        "name": "Aviation", "emoji": "✈️",
        "words": [
            "AILERON","ELEVATOR","RUDDER","FLAP","SPOILER","SLAT","WINGLET","NACELLE",
            "FUSELAGE","COCKPIT","AVIONICS","AUTOPILOT","TRANSPONDER","ALTIMETER",
            "AIRSPEED","ATTITUDE","HORIZON","GYROSCOPE","COMPASS","PITOT","STATIC",
            "TAXIWAY","RUNWAY","APRON","TERMINAL","JETBRIDGE","HANGAR","TOWER","RADAR",
            "APPROACH","DEPARTURE","CLIMB","CRUISE","DESCENT","LANDING","TAKEOFF",
            "TURBOJET","TURBOFAN","TURBOPROP","TURBOSHAFT","RAMJET","SCRAMJET","PULSE",
            "MACH","SUBSONIC","TRANSONIC","SUPERSONIC","HYPERSONIC","STALL","FLUTTER",
            "WINGOVER","CHANDELLE","IMMELMANN","SPLIT","BARREL","CUBAN","HAMMERHEAD",
            "INSTRUMENT","VISUAL","IFRS","CLEARANCE","SQUAWK","MAYDAY","PANPAN","WILCO",
            "WAIVERED","CORRIDOR","AIRSPACE","RESTRICTED","PROHIBITED","DANGER","BUFFER",
        ],
        "bg":          (0, 14, 36),
        "header_bg":   (0, 20, 50),
        "cell_bg":     (0, 18, 46),
        "cell_border": (0, 60, 130),
        "accent":      (56, 189, 248),
        "letter":      (215, 242, 255),
        "sub":         (110, 200, 245),
    },
    "cooking": {
        "name": "Cooking", "emoji": "👨‍🍳",
        "words": [
            "JULIENNE","BRUNOISE","CHIFFONADE","MIREPOIX","SOFFRITTO","BATTUTO","TRINITY",
            "BLANCHING","BRAISING","BROILING","ROASTING","SAUTEING","POACHING","STEAMING",
            "STEWING","SIMMERING","REDUCTION","DEGLAZING","CARAMELIZING","FLAMBE","TEMPERING",
            "EMULSIFICATION","COAGULATION","GELATINIZATION","MAILLARD","DEXTRINIZATION",
            "BEURRE","BLANC","HOLLANDAISE","BERNAISE","VELOUTE","BECHAMEL","ESPAGNOLE",
            "SOUBISE","MORNAY","NANTUA","CARDINAL","NORMANDE","BRETONNE","AMBASSADRICE",
            "BRUNOISE","PAYSANNE","MACEDOINE","JARDINIERE","PRINTANIERE","CLAMART","FLORENTINE",
            "WHETSTONE","HONING","MANDOLINE","CHINOIS","TAMIS","BAIN","MARIE","RONDEAU",
            "SAUCEPAN","STOCKPOT","BRAZIER","SAUTE","SKILLET","PLANCHA","COMAL","TAGINE",
            "SPRINGFORM","BUNDT","RAMEKIN","SOUFFLE","TERRINE","MOULE","MADELEINE","FINANCIER",
        ],
        "bg":          (28, 8, 0),
        "header_bg":   (44, 12, 0),
        "cell_bg":     (36, 10, 2),
        "cell_border": (110, 40, 10),
        "accent":      (251, 113, 60),
        "letter":      (255, 235, 220),
        "sub":         (240, 175, 130),
    },
    "psychology": {
        "name": "Psychology", "emoji": "🧠",
        "words": [
            "COGNITION","PERCEPTION","ATTENTION","MEMORY","LEARNING","MOTIVATION","EMOTION",
            "PERSONALITY","TEMPERAMENT","ATTACHMENT","BONDING","EMPATHY","SYMPATHY","RAPPORT",
            "UNCONSCIOUS","SUBCONSCIOUS","PRECONSCIOUS","REPRESSION","SUPPRESSION","DENIAL",
            "PROJECTION","RATIONALIZATION","SUBLIMATION","DISPLACEMENT","REGRESSION","REACTION",
            "NARCISSISM","MASOCHISM","SADISM","EXHIBITIONISM","VOYEURISM","FETISHISM",
            "SCHIZOPHRENIA","BIPOLAR","DEPRESSION","ANXIETY","PHOBIA","OCD","PTSD","ADHD",
            "AUTISM","ASPERGER","DYSLEXIA","DYSCALCULIA","DYSPRAXIA","TOURETTE","APHASIA",
            "CLASSICAL","OPERANT","OBSERVATIONAL","INSIGHT","LATENT","COGNITIVE","BEHAVIORAL",
            "HUMANISTIC","EXISTENTIAL","PSYCHOANALYTIC","GESTALT","SYSTEMIC","NARRATIVE",
            "REINFORCEMENT","PUNISHMENT","EXTINCTION","HABITUATION","SENSITIZATION","PRIMING",
        ],
        "bg":          (16, 6, 30),
        "header_bg":   (24, 8, 44),
        "cell_bg":     (20, 8, 38),
        "cell_border": (70, 28, 120),
        "accent":      (192, 132, 252),
        "letter":      (242, 230, 255),
        "sub":         (200, 155, 245),
    },
    "ancient_wonders": {
        "name": "Ancient Wonders", "emoji": "🗿",
        "words": [
            "PYRAMID","SPHINX","COLOSSUS","ARTEMIS","MAUSOLEUM","LIGHTHOUSE","OLYMPIA",
            "HANGING","BABYLON","RHODES","HALICARNASSUS","EPHESUS","ALEXANDRIA","PHAROS",
            "ZEUS","CHRYSELEPHANTINE","PHIDIAS","LYSIPPOS","CHARES","PTOLEMY","SOSTRATOS",
            "NEBUCHADNEZZAR","SEMIRAMIS","CYRUS","DARIUS","XERXES","ARTAXERXES","MAUSOLUS",
            "ARTEMISIA","SCOPAS","BRYAXIS","TIMOTHEOS","LEOCHARES","PYTHIOS","SATYROS",
            "CALLIMACHUS","PHILO","ANTIPATER","PAUSANIAS","PLINY","HERODOTUS","STRABO",
            "DIODORUS","SICULUS","POLYBIUS","THUCYDIDES","PLUTARCH","JOSEPHUS","LIVY",
            "OBELISK","MONOLITH","STELE","CENOTAPH","TUMULUS","BARROW","DOLMEN","MENHIR",
            "ZIGGURAT","MASTABA","HYPOGEUM","CATACOMBS","NECROPOLIS","ACROPOLIS","AGORA",
            "FORUM","BASILICA","THERMAE","CIRCUS","AMPHITHEATER","ODEON","STADIUM",
        ],
        "bg":          (28, 20, 6),
        "header_bg":   (42, 28, 8),
        "cell_bg":     (34, 24, 8),
        "cell_border": (110, 80, 30),
        "accent":      (251, 191, 36),
        "letter":      (255, 248, 215),
        "sub":         (230, 200, 100),
    },
    "languages": {
        "name": "Languages", "emoji": "🗣️",
        "words": [
            "MANDARIN","SPANISH","ENGLISH","HINDI","ARABIC","PORTUGUESE","BENGALI","RUSSIAN",
            "JAPANESE","PUNJABI","SWAHILI","TURKISH","KOREAN","FRENCH","GERMAN","ITALIAN",
            "TAMIL","TELUGU","MARATHI","URDU","GUJARATI","KANNADA","MALAYALAM","ODIA",
            "SINHALESE","NEPALI","DZONGKHA","TIBETAN","MONGOLIAN","UYGHUR","KAZAKH","UZBEK",
            "PERSIAN","PASHTO","DARI","AMHARIC","HAUSA","YORUBA","IGBO","ZULU","XHOSA",
            "AFRIKAANS","SOMALI","MALAGASY","TAGALOG","JAVANESE","SUNDANESE","MALAY",
            "PHONEME","MORPHEME","SYNTAX","SEMANTICS","PRAGMATICS","LEXICON","GRAMMAR",
            "DIACRITIC","LIGATURE","IDEOGRAM","LOGOGRAPH","SYLLABARY","ALPHABET","ABJAD",
            "ABUGIDA","HIEROGLYPH","CUNEIFORM","RUNE","OGHAM","BRAILLE","MORSE","SEMAPHORE",
            "LINGUA","FRANCA","PIDGIN","CREOLE","DIALECT","SOCIOLECT","IDIOLECT","REGISTER",
        ],
        "bg":          (10, 4, 28),
        "header_bg":   (16, 6, 40),
        "cell_bg":     (14, 6, 36),
        "cell_border": (50, 24, 110),
        "accent":      (167, 139, 250),
        "letter":      (235, 228, 255),
        "sub":         (190, 165, 248),
    },
    "dinosaurs": {
        "name": "Dinosaurs", "emoji": "🦕",
        "words": [
            "TREX","VELOCIRAPTOR","TRICERATOPS","STEGOSAURUS","BRACHIOSAURUS","ANKYLOSAURUS",
            "SPINOSAURUS","ALLOSAURUS","DIPLODOCUS","APATOSAURUS","BRONTOSAURUS","CAMARASAURUS",
            "IGUANODON","HADROSAUR","PARASAUROLOPHUS","CORYTHOSAURUS","LAMBEOSAURUS",
            "PACHYCEPHALOSAURUS","STYRACOSAURUS","TOROSAURUS","PENTACERATOPS","PROTOCERATOPS",
            "PSITTACOSAURUS","CERATOPSIAN","ORNITHOPODA","SAUROPODA","THEROPODA","SAUROPODOMORPHA",
            "CRETACEOUS","JURASSIC","TRIASSIC","PERMIAN","CARBONIFEROUS","DEVONIAN","SILURIAN",
            "PTEROSAUR","PTERODACTYL","QUETZALCOATLUS","PTERANODON","DIMORPHODON","ARCHAEOPTERYX",
            "ICHTHYOSAUR","PLESIOSAUR","MOSASAUR","ELASMOSAURUS","PLIOSAUR","NOTHOSAUR",
            "FOSSIL","PALEONTOLOGY","EXCAVATION","STRATIGRAPHY","TAPHONOMY","CLADISTICS",
            "EXTINCTION","METEORITE","CHICXULUB","DECCAN","IRIDIUM","BOUNDARY","MASS",
        ],
        "bg":          (10, 24, 0),
        "header_bg":   (14, 36, 0),
        "cell_bg":     (12, 30, 2),
        "cell_border": (38, 110, 10),
        "accent":      (132, 204, 22),
        "letter":      (225, 255, 200),
        "sub":         (165, 230, 90),
    },
    "superheroes": {
        "name": "Superheroes", "emoji": "🦸",
        "words": [
            "SUPERMAN","BATMAN","SPIDERMAN","IRONMAN","CAPTAIN","THOR","HULK","WOLVERINE",
            "CYCLOPS","STORM","ROGUE","GAMBIT","NIGHTCRAWLER","COLOSSUS","BEAST","ANGEL",
            "DAREDEVIL","PUNISHER","ELEKTRA","GHOST","RIDER","BLADE","DOCTOR","STRANGE",
            "VISION","SCARLET","WITCH","QUICKSILVER","FALCON","WASP","ANT","MAN","HAWKEYE",
            "BLACKWIDOW","WARMACHINE","RESCUE","SHURI","OKOYE","NAKIA","AGATHA","WANDA",
            "DEADPOOL","CABLE","DOMINO","COLOSSUS","PSYLOCKE","JUBILEE","POLARIS","FORGE",
            "AQUAMAN","WONDER","WOMAN","FLASH","GREEN","LANTERN","CYBORG","ATOM","FIRESTORM",
            "ZATANNA","CONSTANTINE","SWAMP","THING","MARTIAN","MANHUNTER","HAWKMAN","HAWKGIRL",
            "SHAZAM","CAPTAIN","MARVEL","MISTER","TERRIFIC","ELONGATED","PLASTIC","ELASTIC",
            "INVINCIBLE","OMNI","MAN","ATOM","EVE","AMBER","AMBER","MOLECULE","SPAWN",
        ],
        "bg":          (14, 2, 28),
        "header_bg":   (22, 4, 40),
        "cell_bg":     (18, 4, 34),
        "cell_border": (72, 16, 130),
        "accent":      (248, 113, 113),
        "letter":      (255, 230, 230),
        "sub":         (240, 165, 165),
    },
    "chemistry": {
        "name": "Chemistry", "emoji": "⚗️",
        "words": [
            "HYDROGEN","HELIUM","LITHIUM","BERYLLIUM","BORON","CARBON","NITROGEN","OXYGEN",
            "FLUORINE","NEON","SODIUM","MAGNESIUM","ALUMINIUM","SILICON","PHOSPHORUS","SULFUR",
            "CHLORINE","ARGON","POTASSIUM","CALCIUM","SCANDIUM","TITANIUM","VANADIUM","CHROMIUM",
            "MANGANESE","IRON","COBALT","NICKEL","COPPER","ZINC","GALLIUM","GERMANIUM","ARSENIC",
            "SELENIUM","BROMINE","KRYPTON","RUBIDIUM","STRONTIUM","YTTRIUM","ZIRCONIUM",
            "NIOBIUM","MOLYBDENUM","TECHNETIUM","RUTHENIUM","RHODIUM","PALLADIUM","SILVER",
            "CADMIUM","INDIUM","TIN","ANTIMONY","TELLURIUM","IODINE","XENON","CESIUM","BARIUM",
            "COVALENT","IONIC","METALLIC","HYDROGEN","BOND","POLAR","NONPOLAR","DIPOLE",
            "VALENCE","ORBITAL","HYBRIDIZATION","RESONANCE","ISOMER","ENANTIOMER","POLYMER",
            "MONOMER","CATALYST","INHIBITOR","SUBSTRATE","PRODUCT","REACTANT","EQUILIBRIUM",
        ],
        "bg":          (0, 22, 20),
        "header_bg":   (0, 14, 14),
        "cell_bg":     (0, 32, 30),
        "cell_border": (0, 100, 90),
        "accent":      (45, 212, 191),
        "letter":      (200, 255, 250),
        "sub":         (90, 225, 210),
    },
    "art": {
        "name": "Art & Artists", "emoji": "🎨",
        "words": [
            "PICASSO","DAVINCI","REMBRANDT","MICHELANGELO","RAPHAEL","CARAVAGGIO","VERMEER",
            "MONET","RENOIR","DEGAS","CEZANNE","GAUGUIN","VANGOGH","SEURAT","SIGNAC",
            "MATISSE","DERAIN","VLAMINCK","BRAQUE","LEGER","DELAUNAY","KUPKA","KANDINSKY",
            "MONDRIAN","MALEVICH","LISSITZKY","TATLIN","RODCHENKO","POPOVA","STEPANOVA",
            "DALI","ERNST","MAGRITTE","MIRO","TANGUY","GIACOMETTI","DUCHAMP","PICABIA",
            "WARHOL","LICHTENSTEIN","JOHNS","RAUSCHENBERG","OLDENBURG","KOONS","HIRST",
            "BASQUIAT","HARING","SCHIELE","KLIMT","MUNCH","ENSOR","BECKMANN","NOLDE",
            "FRESCO","TEMPERA","ENCAUSTIC","GOUACHE","WATERCOLOR","ACRYLIC","OIL","PASTEL",
            "ETCHING","LITHOGRAPH","WOODCUT","LINOCUT","SCREENPRINT","MEZZOTINT","AQUATINT",
            "CHIAROSCURO","SFUMATO","PENTIMENTO","IMPASTO","GRISAILLE","TROMPE","FORESHORTENING",
        ],
        "bg":          (20, 4, 4),
        "header_bg":   (32, 6, 6),
        "cell_bg":     (26, 6, 6),
        "cell_border": (100, 20, 20),
        "accent":      (248, 113, 113),
        "letter":      (255, 232, 232),
        "sub":         (240, 165, 165),
    },
    "gemstones": {
        "name": "Gemstones", "emoji": "💎",
        "words": [
            "DIAMOND","RUBY","EMERALD","SAPPHIRE","AMETHYST","TOPAZ","OPAL","PEARL",
            "GARNET","TURQUOISE","AQUAMARINE","PERIDOT","CITRINE","TANZANITE","TOURMALINE",
            "SPINEL","ALEXANDRITE","CHRYSOBERYL","ZIRCON","MOISSANITE","RHODOLITE","TSAVORITE",
            "DEMANTOID","PARAIBA","PADPARADSCHA","ALEXANDRITE","CLINOHUMITE","PAINITE","TAAFFEITE",
            "BENITOITE","MUSGRAVITE","JEREMEJEVITE","GRANDIDIERITE","SERENDIBITE","POUDRETTEITE",
            "FLUORITE","CALCITE","QUARTZ","AGATE","JASPER","ONYX","CHALCEDONY","CARNELIAN",
            "BLOODSTONE","CHRYSOPRASE","AVENTURINE","MALACHITE","AZURITE","LAPIS","SODALITE",
            "OBSIDIAN","MOLDAVITE","TEKTITE","METEORITE","AMBER","CORAL","JET","IVORY",
            "HARDNESS","MOHS","REFRACTIVE","BIREFRINGENCE","PLEOCHROISM","FLUORESCENCE",
            "INCLUSION","CLARITY","CUT","CARAT","FACET","CABOCHON","BRILLIANT","MARQUISE",
        ],
        "bg":          (6, 4, 28),
        "header_bg":   (10, 6, 40),
        "cell_bg":     (8, 6, 34),
        "cell_border": (34, 22, 100),
        "accent":      (99, 179, 237),
        "letter":      (220, 240, 255),
        "sub":         (140, 195, 245),
    },
    "mythology2": {
        "name": "Eastern Myths", "emoji": "🐉",
        "words": [
            "DRAGON","PHOENIX","KIRIN","TORTOISE","TIGER","NEZHA","ERLANG","MONKEY",
            "GUANYIN","MAZU","GUAN","YU","CAISHEN","TUDIGONG","CHENGHUANG","LEIGONG",
            "DIANMU","FENGBO","YUSHI","LONGWANG","BIXIA","NÜWA","FUXI","SHENNONG",
            "HUANGDI","YANDI","CHIYOU","GONGGONG","ZHUANXU","DIJUN","XIHE","CHANGXI",
            "HOUYI","CHANG","KUAFU","XINGTIAN","JINGWEI","PANGU","HUNDUN","TAOTIE",
            "TENGU","KAPPA","TANUKI","KITSUNE","ONI","YOKAI","RAIJIN","FUJIN","IZANAGI",
            "IZANAMI","AMATERASU","TSUKIYOMI","SUSANOO","OKUNINUSHI","INARI","EBISU",
            "DAIKOKUTEN","BISHAMONTEN","BENZAITEN","HOTEI","JUROJIN","FUKUROKUJU",
            "BRAHMASTRA","CHAKRA","SUDARSHANA","KAUMODAKI","PINAKA","GANDIVA","VIJAYA",
            "SHARANGA","SARANGA","PASHUPATASTRA","BRAHMAANDA","VAISHNAVASTRA","NARAYANASTRA",
        ],
        "bg":          (24, 4, 0),
        "header_bg":   (36, 6, 0),
        "cell_bg":     (30, 6, 2),
        "cell_border": (110, 28, 10),
        "accent":      (251, 146, 60),
        "letter":      (255, 235, 215),
        "sub":         (238, 180, 120),
    },
    "ocean2": {
        "name": "Deep Ocean", "emoji": "🌊",
        "words": [
            "MARIANA","TRENCH","CHALLENGER","DEEP","HADAL","ABYSSAL","BATHYAL","MESOPELAGIC",
            "EPIPELAGIC","SUNLIGHT","TWILIGHT","MIDNIGHT","ABYSSOPELAGIC","HADALPELAGIC",
            "BIOLUMINESCENCE","CHEMOSYNTHESIS","HYDROTHERMAL","VENT","COLD","SEEP","METHANE",
            "TUBEWORM","POMPEII","YETI","CRAB","DUMBO","OCTOPUS","VAMPIRE","SQUID","GOBLIN",
            "MEGALODON","FRILLED","SHARK","VIPER","DRAGONFISH","ANGLERFISH","HATCHETFISH",
            "BARRELEYE","GLASSHEAD","LANTERNFISH","BIOLUMINESCENT","DINOFLAGELLATE","SIPHONOPHORE",
            "PYROSOME","SALP","MEDUSA","CTENOPHORE","PTEROPOD","POLYCHAETE","HOLOTHURIAN",
            "XENOPHYOPHORE","FORAMINIFERA","RADIOLARIAN","DIATOM","COCCOLITHOPHORE","SILICOFLAGELLATE",
            "THERMOCLINE","HALOCLINE","PYCNOCLINE","OXYCLINE","NUTRICLINE","CHEMOCLINE",
            "UPWELLING","DOWNWELLING","GYRE","EDDY","CURRENT","TIDE","INTERNAL","WAVE",
        ],
        "bg":          (0, 10, 30),
        "header_bg":   (0, 14, 42),
        "cell_bg":     (0, 12, 38),
        "cell_border": (0, 48, 110),
        "accent":      (34, 211, 238),
        "letter":      (200, 248, 255),
        "sub":         (80, 210, 235),
    },
    "planets": {
        "name": "Solar System", "emoji": "🪐",
        "words": [
            "MERCURY","VENUS","EARTH","MARS","JUPITER","SATURN","URANUS","NEPTUNE",
            "GANYMEDE","CALLISTO","TITAN","TRITON","EUROPA","ENCELADUS","MIMAS","DIONE",
            "RHEA","TETHYS","IAPETUS","OBERON","TITANIA","ARIEL","UMBRIEL","MIRANDA",
            "CHARON","NIX","HYDRA","KERBEROS","STYX","DYSNOMIA","WEYWOT","NAMAKA",
            "CORONA","CHROMOSPHERE","PHOTOSPHERE","CONVECTIVE","RADIATIVE","CORE",
            "SOLAR","FLARE","PROMINENCE","SUNSPOT","CME","MAGNETOSPHERE","VAN","ALLEN",
            "ASTEROID","BELT","TROJAN","CENTAUR","TRANS","NEPTUNIAN","KUIPER","OORT",
            "CERES","VESTA","PALLAS","HYGIEA","ERIS","PLUTO","MAKEMAKE","HAUMEA","SEDNA",
            "PERIHELION","APHELION","SEMIMAJOR","ECCENTRICITY","INCLINATION","LONGITUDE",
            "ASCENDING","NODE","ARGUMENT","PERIAPSIS","MEAN","ANOMALY","SIDEREAL","PERIOD",
        ],
        "bg":          (4, 2, 18),
        "header_bg":   (8, 4, 28),
        "cell_bg":     (10, 4, 34),
        "cell_border": (36, 16, 100),
        "accent":      (167, 139, 250),
        "letter":      (235, 228, 255),
        "sub":         (185, 165, 248),
    },

}

THEME_LIST = list(THEMES.keys())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GRID BUILDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIRS = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]


def _empty(size: int) -> list:
    return [[""] * size for _ in range(size)]


def _place(grid: list, word: str, size: int):
    # Only use words that actually fit in the grid
    if len(word) > size:
        return None
    for _ in range(300):
        dr, dc = random.choice(DIRS)
        r, c   = random.randint(0, size-1), random.randint(0, size-1)
        er      = r + dr * (len(word)-1)
        ec      = c + dc * (len(word)-1)
        if not (0 <= er < size and 0 <= ec < size):
            continue
        cells, ok = [], True
        for i in range(len(word)):
            nr, nc = r+dr*i, c+dc*i
            if grid[nr][nc] not in ("", word[i]):
                ok = False; break
            cells.append((nr, nc))
        if ok:
            for (nr, nc), ch in zip(cells, word):
                grid[nr][nc] = ch
            return cells
    return None


def _fill(grid: list, size: int):
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for r in range(size):
        for c in range(size):
            if not grid[r][c]:
                grid[r][c] = random.choice(alpha)


def build_puzzle(theme_key: str, size: int, n_words: int) -> tuple:
    """Returns (grid, words_list, placed_list)."""
    # Filter words that fit in this grid size AND are at least 3 letters
    eligible = [w for w in THEMES[theme_key]["words"] if 3 <= len(w) <= size]
    if not eligible:
        eligible = [w for w in THEMES[theme_key]["words"] if len(w) <= size]
    # Use a larger pool buffer for higher word counts so we always have
    # enough candidates to successfully place n_words on the grid.
    pool_size = min(len(eligible), max(n_words + 20, n_words * 3))
    pool = random.sample(eligible, pool_size)
    grid = _empty(size)
    words, placed = [], []
    for w in pool:
        if len(words) >= n_words:
            break
        cells = _place(grid, w, size)
        if cells:
            words.append(w)
            placed.append({"word": w, "cells": cells})
    _fill(grid, size)
    if not words:
        raise ValueError(f"build_puzzle: 0 words placed for theme={theme_key} size={size}")
    return grid, words, placed


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IMAGE RENDERER  (High Quality)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CELL   = 56          # base cell size (was 44)
PAD    = 22          # padding around grid
HDR_H  = 100         # header height (was 80)
CORNER = 10          # cell corner radius
SCALE  = 2           # supersampling factor for anti-aliasing

HI_FILLS = [
    (56,189,248,130),(251,191,36,130),(167,139,250,130),(52,211,153,130),
    (248,113,113,130),(251,146,60,130),(196,181,253,130),(110,231,183,130),
]
HI_STROKES = [
    (56,189,248),(251,191,36),(167,139,250),(52,211,153),
    (248,113,113),(251,146,60),(196,181,253),(110,231,183),
]


def _rr(draw, x, y, w, h, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r,
                            fill=fill, outline=outline, width=width)


def _font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _blend(color, alpha_factor, bg):
    """Blend color onto bg with alpha_factor 0-1."""
    return tuple(int(c * alpha_factor + b * (1 - alpha_factor))
                 for c, b in zip(color[:3], bg))


def render_image(theme_key: str, grid: list, placed: list,
                 found_words: list, round_num: int,
                 size: int) -> bytes:
    t = THEMES[theme_key]

    # Scale cell size for larger grids
    cell = max(36, CELL - max(0, size - 8) * 2)
    s    = SCALE  # supersampling

    W = size * cell + PAD * 2
    H = size * cell + PAD * 2 + HDR_H

    # ── Draw at 2× resolution then downsample ──────────────────────
    W2, H2 = W * s, H * s
    cell2, pad2, hdr2, corner2 = cell*s, PAD*s, HDR_H*s, CORNER*s

    base = Image.new("RGB", (W2, H2), t["bg"])
    draw = ImageDraw.Draw(base)

    # ── Subtle gradient-like background with vignette dots ──────────
    dot_col = tuple(min(v + 20, 255) for v in t["bg"])
    dot_dim  = tuple(max(v - 5, 0) for v in t["bg"])
    for x in range(0, W2, 28):
        for y in range(0, H2, 28):
            # fade dots toward corners for vignette feel
            cx_dist = abs(x - W2//2) / (W2//2)
            cy_dist = abs(y - H2//2) / (H2//2)
            dist    = (cx_dist**2 + cy_dist**2) ** 0.5
            col = dot_col if dist < 0.6 else dot_dim
            r   = s if dist < 0.4 else 1
            draw.ellipse([x-r, y-r, x+r, y+r], fill=col)

    # ── Header with gradient illusion ──────────────────────────────
    for i in range(hdr2):
        ratio = i / hdr2
        blended = tuple(int(t["header_bg"][j] + (t["bg"][j] - t["header_bg"][j]) * ratio * 0.3)
                        for j in range(3))
        draw.line([(0, i), (W2, i)], fill=blended)

    # accent bar under header (thick, glowing look)
    bar_h = 4 * s
    draw.rectangle([0, hdr2 - bar_h, W2, hdr2], fill=t["accent"])
    # subtle glow above bar
    glow_col = tuple(min(v + 60, 255) for v in t["accent"])
    draw.rectangle([0, hdr2 - bar_h - s, W2, hdr2 - bar_h], fill=glow_col)

    # ── Fonts (scaled for supersampling) ───────────────────────────
    letter_size  = max(14, 22 - max(0, size - 8) * 1) * s
    title_size   = 26 * s
    sub_size     = 15 * s
    tag_size     = 11 * s

    FONT_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    FONT_REG   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    FONT_MONO  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

    f_title  = _font(FONT_BOLD, title_size)
    f_sub    = _font(FONT_REG,  sub_size)
    f_letter = _font(FONT_MONO, letter_size)
    f_tag    = _font(FONT_BOLD, tag_size)

    # ── Title with shadow ───────────────────────────────────────────
    title    = f"{t['name'].upper()}  WORD  GRID"
    tw       = draw.textlength(title, font=f_title)
    tx, ty   = (W2 - tw) / 2, 14 * s
    # shadow
    shadow   = tuple(max(v - 40, 0) for v in t["accent"])
    draw.text((tx + 2, ty + 2), title, fill=shadow,    font=f_title)
    draw.text((tx,     ty),     title, fill=t["accent"], font=f_title)

    # ── Subtitle ────────────────────────────────────────────────────
    sub = (f"Round {round_num}  •  {len(placed)} words  •  "
           f"Found: {len(found_words)}/{len(placed)}")
    sw  = draw.textlength(sub, font=f_sub)
    draw.text(((W2 - sw) / 2, 52 * s), sub, fill=t["sub"], font=f_sub)

    # ── Corner accent dots ──────────────────────────────────────────
    r_dot = 6 * s
    for cx, cy in [(pad2 - 6*s, hdr2 + pad2 - 6*s),
                   (W2 - pad2 + 6*s, hdr2 + pad2 - 6*s),
                   (pad2 - 6*s, H2 - pad2 + 6*s),
                   (W2 - pad2 + 6*s, H2 - pad2 + 6*s)]:
        draw.ellipse([cx - r_dot, cy - r_dot, cx + r_dot, cy + r_dot], fill=t["accent"])

    # ── Grid outline / shadow ───────────────────────────────────────
    gx0 = pad2 - 4
    gy0 = hdr2 + pad2 - 4
    gx1 = pad2 + size * cell2 + 4
    gy1 = hdr2 + pad2 + size * cell2 + 4
    draw.rounded_rectangle([gx0, gy0, gx1, gy1], radius=corner2 + 4,
                            outline=t["accent"], width=2*s)

    # ── Build found-cell map ────────────────────────────────────────
    found_map: dict = {}
    for fi, fw in enumerate(found_words):
        pw = next((p for p in placed if p["word"] == fw), None)
        if pw:
            for c in pw["cells"]:
                found_map[c] = fi

    overlay = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    ov      = ImageDraw.Draw(overlay)

    # ── Draw cells ─────────────────────────────────────────────────
    for r in range(size):
        for c in range(size):
            x = pad2 + c * cell2
            y = hdr2 + pad2 + r * cell2
            letter = grid[r][c]

            # cell shadow (subtle depth)
            shadow_col = tuple(max(v - 10, 0) for v in t["cell_bg"])
            _rr(draw, x + 2, y + 2, cell2 - 2, cell2 - 2, corner2, fill=shadow_col)

            # cell body
            _rr(draw, x + 1, y + 1, cell2 - 2, cell2 - 2, corner2,
                fill=t["cell_bg"], outline=t["cell_border"], width=2)

            # subtle inner highlight on top edge
            hi_col = tuple(min(v + 25, 255) for v in t["cell_bg"])
            draw.line([(x + corner2, y + 2), (x + cell2 - corner2, y + 2)], fill=hi_col, width=s)

            # highlight overlay for found words
            if (r, c) in found_map:
                fi = found_map[(r, c)]
                _rr(ov, x + 1, y + 1, cell2 - 2, cell2 - 2, corner2,
                    fill=HI_FILLS[fi % len(HI_FILLS)],
                    outline=HI_STROKES[fi % len(HI_STROKES)], width=3)

            # letter with shadow
            lw = draw.textlength(letter, font=f_letter)
            lx = x + (cell2 - lw) / 2
            ly = y + (cell2 - letter_size) / 2
            shadow_l = tuple(max(v - 50, 0) for v in t["letter"])
            draw.text((lx + 1, ly + 1), letter, fill=shadow_l, font=f_letter)
            draw.text((lx,     ly),     letter, fill=t["letter"], font=f_letter)

    # ── Merge highlight overlay ─────────────────────────────────────
    merged = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    d2 = ImageDraw.Draw(merged)

    # ── Word labels on found cells ─────────────────────────────────
    for fi, fw in enumerate(found_words):
        pw = next((p for p in placed if p["word"] == fw), None)
        if pw and pw["cells"]:
            r0, c0 = pw["cells"][0]
            x = pad2 + c0 * cell2 + 4
            y = hdr2 + pad2 + r0 * cell2 + 3
            col = HI_STROKES[fi % len(HI_STROKES)]
            # shadow
            d2.text((x + 1, y + 1), fw[:5], fill=(0, 0, 0), font=f_tag)
            d2.text((x,     y),     fw[:5], fill=col,        font=f_tag)

    # ── Downsample to final size (anti-aliasing) ────────────────────
    final = merged.resize((W, H), Image.LANCZOS)

    buf = io.BytesIO()
    final.save(buf, format="PNG", optimize=True, compress_level=6)
    buf.seek(0)
    return buf.read()
