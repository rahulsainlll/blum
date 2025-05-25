"""
Configuration file for target Instagram accounts
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Target accounts list
TARGET_ACCOUNTS = [
    # Real Madrid Players
    "vinijr", "rodrigo", "federicovalverde", "casemiro", "lukamodric10", 
    "toni.kroos", "davidalaba", "antoniorudiger", "eder.militao", "nachofdez",
    "dani.carvajal", "ferlandmendy", "thibautcourtois", "andriylunin",
    "rodrygo", "marcoasensio", "dani.ceballos", "aurelienchouameni",
    "eduardocamavinga", "karimbenzema",
    
    # Barcelona Players
    "lewy.official", "pedri", "gavi", "frenkiedejong", "terstegen",
    "joaofelix", "raphinha", "joaocancelo", "kounde", "araujo",
    "balde", "christensen", "gundogan", "torres", "robertlewandowski",
    
    # Premier League Stars
    "haaland", "kevindebruyne", "marcusrashford", "brunofernandes",
    "salah", "van_dijk", "alissonbecker", "trentarnold66",
    "bukayosaka87", "martinelli", "saka", "rice", "odegaard",
    
    # Other Top Players
    "mbappe", "neymarjr", "messi", "cr7", "bellingham",
    "kimmich", "musiala", "goretzka", "kane", "sonny",
    "lewandowski", "benzema", "modric", "kroos", "courtois",
    "alisson", "ederson", "van_dijk", "rubendias", "cancelo",
    "kdb", "salah", "mane", "sterling", "foden",
    "mount", "pulisic", "havertz", "kante", "jorginho",
    "thiago", "fabinho", "henderson", "wijnaldum", "firmino",
    "jesus", "aguero", "silva", "gundogan", "mahrez",
    "sane", "coman", "goretzka", "kimmich", "neuer",
    "terstegen", "pique", "busquets", "pedri", "gavi",
    "fati", "dembele", "griezmann", "suarez", "cavani",
    "pogba", "kante", "benzema", "mbappe", "neymar",
    "messi", "cr7", "lewandowski", "haaland", "kane",
    "sonny", "salah", "mane", "sterling", "foden"
]

# Configuration from environment variables
POSTS_PER_ACCOUNT = int(os.getenv('POSTS_PER_ACCOUNT'))
BREAK_BETWEEN_ACCOUNTS = int(os.getenv('BREAK_BETWEEN_ACCOUNTS'))
BREAK_BETWEEN_BATCHES = int(os.getenv('BREAK_BETWEEN_BATCHES'))
BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
MAX_ACTIONS_PER_DAY = int(os.getenv('MAX_ACTIONS_PER_DAY'))
MAX_ACCOUNTS_PER_DAY = int(os.getenv('MAX_ACCOUNTS_PER_DAY'))
