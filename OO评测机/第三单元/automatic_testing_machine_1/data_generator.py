import random
import sys
import string
import math
from collections import defaultdict, deque

# --- Constants and Parameter Ranges ---
ALIAS_MAP = {
    "add_person": "ap",
    "add_relation": "ar",
    "modify_relation": "mr",
    "add_tag": "at",
    "del_tag": "dt",
    "add_to_tag": "att",
    "del_from_tag": "dft",
    "query_value": "qv",
    "query_circle": "qci",
    "query_triple_sum": "qts",
    "query_tag_age_var": "qtav",
    "query_best_acquaintance": "qba",
    "load_network": "ln",
    # New commands (from previous increment)
    "create_official_account": "coa",
    "delete_official_account": "doa",
    "contribute_article": "ca",
    "delete_article": "da",
    "follow_official_account": "foa",
    "query_shortest_path": "qsp",
    "query_best_contributor": "qbc",
    "query_received_articles": "qra",
    "query_tag_value_sum": "qtvs",
    "query_couple_sum": "qcs",
    # New commands (current increment)
    "add_message": "am",
    "add_red_envelope_message": "arem",
    "add_forward_message": "afm",
    "add_emoji_message": "aem",
    "send_message": "sm",
    "store_emoji_id": "sei",
    "delete_cold_emoji": "dce",
    "query_social_value": "qsv",
    "query_received_messages": "qrm",
    "query_popularity": "qp",
    "query_money": "qm",
}

# Reverse map for easier lookup: alias -> full_name
INSTRUCTION_MAP = {v: k for k, v in ALIAS_MAP.items()}

# Parameter Constraints
AGE_RANGE = (1, 200)
VALUE_RANGE = (1, 200) # Relation value >= 1 for addRelation normal behavior
MVAL_RANGE = (-200, 200) # modifyRelation value
NAME_LENGTH_RANGE = (1, 10) # Reduced for readability
N_RANGE = (1, 100) # Increased N range
TAG_PERSONS_LIMIT = 999 # From JML
ARTICLE_RECEIVED_LIMIT = 5 # From JML queryReceivedArticles
MESSAGE_RECEIVED_LIMIT = 5 # From JML getReceivedMessages

# Use a reasonable range for generated IDs to increase collision probability
ID_POOL_RANGE = (-200, 200) # Increased ID pool for higher collision chance
TAG_ID_POOL_RANGE = (-200, 200) # Increased TAG ID pool
ACCOUNT_ID_POOL_RANGE = (-200, 200) # New: Account ID pool
ARTICLE_ID_POOL_RANGE = (-200, 200) # New: Article ID pool
MESSAGE_ID_POOL_RANGE = (-200, 200) # New: Message ID pool
EMOJI_ID_POOL_RANGE = (-200, 200) # New: Emoji ID pool
SOCIAL_VALUE_RANGE = (0, 200) # Social value for normal message (can be 0)
MONEY_RANGE = (1, 1000) # Money for red envelope message (> 0 based on impl inspection)

# Message Types
MESSAGE_TYPE_PERSON = 0
MESSAGE_TYPE_TAG = 1

# Message Subtypes (simulated)
MESSAGE_SUBTYPE_NORMAL = 0
MESSAGE_SUBTYPE_EMOJI = 1
MESSAGE_SUBTYPE_RED_ENVELOPE = 2
MESSAGE_SUBTYPE_FORWARD = 3

# --- Global ID Tracking (for strict uniqueness across test run) ---
all_generated_message_ids = set()
all_generated_emoji_ids = set() # Also track emoji IDs globally for sei/qp/dce

# --- State Management ---
# Simulates the Network implementation's key data structures
network_state = {
    # persons: {id: {"name": name, "age": age, "acquaintances": {id: value}, "socialValue": int, "money": int, "receivedArticles": list[int], "messages": list[dict]}}
    "persons": {},
    # person_tags: {person_id: set(tag_ids_owned_by_this_person)} # Tracks tags owned by a person
    "person_tags": {},
    # tag_members: {(owner_id, tag_id): {member_id: age}} # Tracks which persons are IN a specific tag instance (owned by owner_id)
    "tag_members": {},
    # relations: { (min_id, max_id): value } mapping min/max pair to value for value > 0 relations
    "relations": {},

    # Accounts and Articles
    # accounts: {account_id: {"owner_id": int, "name": string, "followers": {person_id: contributions: int}, "articles": set(article_id)}}
    "accounts": {},
    # articles_map: {article_id: owner_person_id: int} # Tracks which person contributed which article
    "articles_map": {},

    # Messages and Emojis
    # messages: {message_id: {"id": int, "type": int, "socialValue": int, "person1_id": int, "person2_id": Optional[int], "tag_id": Optional[int], "emoji_id": Optional[int], "money": Optional[int], "article_id": Optional[int], "subtype": int}}
    "messages": {}, # Messages *currently* in the network (not yet sent)
    # emojiId2Heat: {emoji_id: heat_int}
    "emojiId2Heat": {},
    # emojiId2MessageId: {emoji_id: list[message_ids_using_this_emoji]} # To simulate deleteColdEmoji message removal
    "emojiId2MessageId": {},

    # State for aggregate queries
    "triple_sum": 0, # Calculated incrementally
    "couple_sum_dirty": True, # Flag indicating if couple_sum needs recalculation
}

def reset_state():
    global network_state, all_generated_message_ids, all_generated_emoji_ids
    network_state = {
        "persons": {},
        "person_tags": {},
        "tag_members": {},
        "relations": {},
        "accounts": {},
        "articles_map": {},
        "messages": {},
        "emojiId2Heat": {},
        "emojiId2MessageId": {},
        "triple_sum": 0,
        "couple_sum_dirty": True,
    }
    # Reset global ID tracking on load_network
    all_generated_message_ids = set()
    all_generated_emoji_ids = set()


# --- State Query Helper Functions ---
def get_existing_person_ids():
    return list(network_state["persons"].keys())

def get_existing_account_ids():
    return list(network_state["accounts"].keys())

def get_existing_article_ids():
    return list(network_state["articles_map"].keys())

def get_existing_message_ids():
     return list(network_state["messages"].keys())

def get_existing_emoji_ids():
     return list(network_state["emojiId2Heat"].keys())

def get_existing_relation_pairs():
    return list(network_state["relations"].keys())

def get_existing_tag_ids_for_person(person_id):
    return list(network_state["person_tags"].get(person_id, set()))

def get_persons_in_tag(owner_id, tag_id):
    return list(network_state["tag_members"].get((owner_id, tag_id), {}).keys())

def get_accounts_owned_by_person(person_id):
    return [acc_id for acc_id, acc_data in network_state["accounts"].items() if acc_data["owner_id"] == person_id]

def get_followers_of_account(account_id):
    acc_data = network_state["accounts"].get(account_id)
    if acc_data:
        return list(acc_data["followers"].keys())
    return []

def get_articles_of_account(account_id):
    acc_data = network_state["accounts"].get(account_id)
    if acc_data:
        return list(acc_data["articles"])
    return []

def bfs_reachable(start_id, state):
    """Finds all persons reachable from start_id in the network state using BFS."""
    if start_id not in state["persons"]:
        return set()

    reachable = set()
    queue = deque([start_id])
    visited = {start_id}
    reachable.add(start_id)

    while queue:
        current_id = queue.popleft()
        current_person = state["persons"].get(current_id)
        if current_person and "acquaintances" in current_person:
            for acquaintance_id in current_person["acquaintances"].keys():
                if acquaintance_id not in visited:
                    visited.add(acquaintance_id)
                    reachable.add(acquaintance_id)
                    queue.append(acquaintance_id)
    return reachable

# --- Helper Functions for Parameter Generation ---
def generate_random_id(id_type="person", used_ids=None):
    """Generates a random ID within the specified type's pool range."""
    # This helper is primarily for non-unique or local-scope IDs (e.g., relation value, age, tag ID for a new tag)
    # For person/account/article/message/emoji IDs, prefer specialized helpers below if uniqueness is needed.
    if id_type == "person": pool_range = ID_POOL_RANGE
    elif id_type == "account": pool_range = ACCOUNT_ID_POOL_RANGE
    elif id_type == "article": pool_range = ARTICLE_ID_POOL_RANGE
    elif id_type == "tag": pool_range = TAG_ID_POOL_RANGE
    elif id_type == "message": pool_range = MESSAGE_ID_POOL_RANGE # Note: Use get_random_unused_message_id for add message!
    elif id_type == "emoji": pool_range = EMOJI_ID_POOL_RANGE # Note: Use get_random_unused_emoji_id for store emoji!
    else: raise ValueError(f"Unknown ID type: {id_type}")

    id_pool = set(range(pool_range[0], pool_range[1] + 1))
    if used_ids is not None:
        available_ids = list(id_pool - set(used_ids))
        if available_ids:
            return random.choice(available_ids)

    return random.randint(pool_range[0], pool_range[1])


def get_random_non_existent_id(id_type="person"):
    """Generates an ID of a specific type that does not currently exist *in the network state dict*."""
    # This is useful for targeting PINF/OAINF/AINF/MINF *when the exception requires the ID to NOT exist in the state*.
    # For adding *new* entities that need global uniqueness, use get_random_unused_*_id functions.
    if id_type == "person":
        existing_ids = get_existing_person_ids()
        pool_range = ID_POOL_RANGE
    elif id_type == "account":
        existing_ids = get_existing_account_ids()
        pool_range = ACCOUNT_ID_POOL_RANGE
    elif id_type == "article":
        existing_ids = get_existing_article_ids()
        pool_range = ARTICLE_ID_POOL_RANGE
    elif id_type == "message":
        existing_ids = get_existing_message_ids()
        pool_range = MESSAGE_ID_POOL_RANGE
    elif id_type == "emoji":
        existing_ids = get_existing_emoji_ids()
        pool_range = EMOJI_ID_POOL_RANGE
    elif id_type == "tag":
         return None # Requires person context
    else: raise ValueError(f"Unknown ID type: {id_type}")

    all_possible_ids = set(range(pool_range[0], pool_range[1] + 1))
    existing_ids_set = set(existing_ids)

    available_ids = list(all_possible_ids - existing_ids_set)

    if available_ids:
        return random.choice(available_ids)
    else:
        return None


def get_random_unused_id(id_type="message", used_ids_set=None, pool_range=None, max_attempts=1000):
    """Generates a random ID that is not in the provided used_ids_set, within the pool range."""
    if used_ids_set is None:
         if id_type == "message": used_ids_set = all_generated_message_ids
         elif id_type == "emoji": used_ids_set = all_generated_emoji_ids
         else: raise ValueError(f"Uniqueness tracking not implemented for ID type: {id_type}")

    if pool_range is None:
         if id_type == "message": pool_range = MESSAGE_ID_POOL_RANGE
         elif id_type == "emoji": pool_range = EMOJI_ID_POOL_RANGE
         else: raise ValueError(f"Unknown pool range for ID type: {id_type}")

    total_pool_size = pool_range[1] - pool_range[0] + 1
    if len(used_ids_set) >= total_pool_size:
        #print(f"Warning: ID pool exhausted for type {id_type} within range {pool_range}. Cannot generate unused ID.", file=sys.stderr)
        return None # Pool exhausted

    attempts = 0
    while attempts < max_attempts:
        _id = random.randint(pool_range[0], pool_range[1])
        if _id not in used_ids_set:
            return _id
        attempts += 1

    # Fallback if random picking fails after many attempts (shouldn't happen if pool isn't truly exhausted)
    available_ids = list(set(range(pool_range[0], pool_range[1] + 1)) - used_ids_set)
    if available_ids:
         return random.choice(available_ids)

    # Truly exhausted or unluckily failed to find in max_attempts
    #print(f"Warning: Failed to find unused ID for type {id_type} after {max_attempts} attempts.", file=sys.stderr)
    return None # Indicate failure


def get_random_non_existent_tag_id_for_person(person_id):
    existing_tag_ids = get_existing_tag_ids_for_person(person_id)
    tag_pool = set(range(TAG_ID_POOL_RANGE[0], TAG_ID_POOL_RANGE[1] + 1))
    available_tag_ids = list(tag_pool - set(existing_tag_ids))

    if available_tag_ids:
        return random.choice(available_tag_ids)
    else:
        return None


def generate_random_name(length_range=NAME_LENGTH_RANGE):
    length = random.randint(length_range[0], length_range[1])
    if length <= 0: length = 1
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_random_age(age_range=AGE_RANGE):
    return random.randint(age_range[0], age_range[1])

def generate_random_value(value_range=VALUE_RANGE):
    return random.randint(value_range[0], value_range[1])

def generate_random_mval(mval_range=MVAL_RANGE):
    return random.randint(mval_range[0], mval_range[1])

def generate_random_social_value(social_value_range=SOCIAL_VALUE_RANGE):
     return random.randint(social_value_range[0], social_value_range[1])

def generate_random_money(money_range=MONEY_RANGE):
     return random.randint(money_range[0], money_range[1])

def get_random_existing_person_id():
    existing_ids = get_existing_person_ids()
    if not existing_ids:
        return None
    return random.choice(existing_ids)

def get_random_existing_account_id():
    existing_ids = get_existing_account_ids()
    if not existing_ids:
        return None
    return random.choice(existing_ids)

def get_random_existing_article_id():
     existing_ids = get_existing_article_ids()
     if not existing_ids:
          return None
     return random.choice(existing_ids)

def get_random_existing_message_id():
     existing_ids = get_existing_message_ids()
     if not existing_ids:
          return None
     return random.choice(existing_ids)

def get_random_existing_emoji_id():
     existing_ids = get_existing_emoji_ids()
     if not existing_ids:
          return None
     return random.choice(existing_ids)

def get_random_existing_tag_id_for_person(person_id):
     existing_tag_ids = get_existing_tag_ids_for_person(person_id)
     if not existing_tag_ids:
         return None
     return random.choice(existing_tag_ids)

def get_random_person_in_tag(owner_id, tag_id):
     member_ids = get_persons_in_tag(owner_id, tag_id)
     if not member_ids:
          return None
     return random.choice(member_ids)

def get_random_person_not_in_tag(owner_id, tag_id):
     existing_person_ids = get_existing_person_ids()
     members_in_tag = set(get_persons_in_tag(owner_id, tag_id))
     persons_not_in_tag = [pid for pid in existing_person_ids if pid not in members_in_tag]
     if not persons_not_in_tag:
          return None
     return random.choice(persons_not_in_tag)

def get_random_account_owned_by_person(person_id):
    owned_accounts = get_accounts_owned_by_person(person_id)
    if not owned_accounts:
        return None
    return random.choice(owned_accounts)

def get_random_account_not_owned_by_person(person_id):
    existing_account_ids = get_existing_account_ids()
    non_owned_accounts = [acc_id for acc_id in existing_account_ids if network_state["accounts"][acc_id]["owner_id"] != person_id]
    if not non_owned_accounts:
        return None
    return random.choice(non_owned_accounts)

def get_random_follower_of_account(account_id):
    followers = get_followers_of_account(account_id)
    if not followers:
        return None
    return random.choice(followers)

def get_random_non_follower_of_account(account_id):
    existing_person_ids = get_existing_person_ids()
    followers = set(get_followers_of_account(account_id))
    non_followers = [pid for pid in existing_person_ids if pid not in followers]
    if not non_followers:
        return None
    return random.choice(non_followers)

def get_random_article_of_account(account_id):
    articles = get_articles_of_account(account_id)
    if not articles:
        return None
    return random.choice(articles)

def get_random_article_not_of_account(account_id):
     existing_articles = get_existing_article_ids()
     account_articles = set(get_articles_of_account(account_id))
     non_account_articles = [aid for aid in existing_articles if aid not in account_articles]
     if not non_account_articles:
          return None
     return random.choice(non_account_articles)

def get_random_article_person_has_received(person_id):
    received_articles = network_state["persons"].get(person_id, {}).get("receivedArticles", [])
    if not received_articles:
        return None
    return random.choice(received_articles)

def get_random_article_person_has_not_received(person_id):
     existing_articles = get_existing_article_ids()
     received_articles = set(network_state["persons"].get(person_id, {}).get("receivedArticles", []))
     unreceived_articles = [aid for aid in existing_articles if aid not in received_articles]
     if not unreceived_articles:
          return None
     return random.choice(unreceived_articles)


# --- Exception/Outcome Keys ---
OUTCOME_NORMAL = "normal"
GENERATOR_TARGET_OUTCOME_MAP = {
    ("ap", "EPI"): "EqualPersonIdException",
    ("ar", "PINF_id1"): "PersonIdNotFoundException",
    ("ar", "PINF_id2"): "PersonIdNotFoundException",
    ("ar", "ERE"): "EqualRelationException",
    ("mr", "PINF_id1"): "PersonIdNotFoundException",
    ("mr", "PINF_id2"): "PersonIdNotFoundException",
    ("mr", "EPI"): "EqualPersonIdException",
    ("mr", "RNF"): "RelationNotFoundException",
    ("at", "PINF"): "PersonIdNotFoundException",
    ("at", "ETI"): "EqualTagIdException",
    ("dt", "PINF"): "PersonIdNotFoundException",
    ("dt", "TINF"): "TagIdNotFoundException",
    ("att", "PINF_p1"): "PersonIdNotFoundException",
    ("att", "PINF_p2"): "PersonIdNotFoundException",
    ("att", "EPI_id1_eq_id2"): "EqualPersonIdException",
    ("att", "RNF"): "RelationNotFoundException",
    ("att", "TINF"): "TagIdNotFoundException",
    ("att", "EPI_in_tag"): "EqualPersonIdException",
    ("dft", "PINF_p1"): "PersonIdNotFoundException",
    ("dft", "PINF_p2"): "PersonIdNotFoundException",
    ("dft", "TINF"): "TagIdNotFoundException",
    ("dft", "PINF_not_in_tag"): "PersonIdNotFoundException",
    ("qv", "PINF_id1"): "PersonIdNotFoundException",
    ("qv", "PINF_id2"): "PersonIdNotFoundException",
    ("qv", "RNF"): "RelationNotFoundException",
    ("qci", "PINF_id1"): "PersonIdNotFoundException",
    ("qci", "PINF_id2"): "PersonIdNotFoundException",
    ("qtav", "PINF"): "PersonIdNotFoundException",
    ("qtav", "TINF"): "TagIdNotFoundException",
    ("qba", "PINF"): "PersonIdNotFoundException",
    ("qba", "ANE"): "AcquaintanceNotFoundException",

    ("coa", "PINF"): "PersonIdNotFoundException",
    ("coa", "EOAI"): "EqualOfficialAccountIdException",
    ("doa", "PINF"): "PersonIdNotFoundException",
    ("doa", "OAINF"): "OfficialAccountIdNotFoundException",
    ("doa", "DAPermissionDenied"): "DeleteOfficialAccountPermissionDeniedException",
    ("ca", "PINF"): "PersonIdNotFoundException",
    ("ca", "OAINF"): "OfficialAccountIdNotFoundException",
    ("ca", "EAI"): "EqualArticleIdException",
    ("ca", "ContributePermissionDenied"): "ContributePermissionDeniedException",
    ("da", "PINF"): "PersonIdNotFoundException",
    ("da", "OAINF"): "OfficialAccountIdNotFoundException",
    ("da", "AINF"): "ArticleIdNotFoundException",
    ("da", "DAPermissionDenied"): "DeleteArticlePermissionDeniedException",
    ("foa", "PINF"): "PersonIdNotFoundException",
    ("foa", "OAINF"): "OfficialAccountIdNotFoundException",
    ("foa", "EPI_follower"): "EqualPersonIdException",
    ("qsp", "PINF_id1"): "PersonIdNotFoundException",
    ("qsp", "PINF_id2"): "PersonIdNotFoundException",
    ("qsp", "PathNotFound"): "PathNotFoundException",
    ("qbc", "OAINF"): "OfficialAccountIdNotFoundException",
    ("qra", "PINF"): "PersonIdNotFoundException",
    ("qtvs", "PINF"): "PersonIdNotFoundException",
    ("qtvs", "TINF"): "TagIdNotFoundException",

    ("am", "EMI"): "EqualMessageIdException",
    ("am", "EINF"): "EmojiIdNotFoundException",
    ("am", "AINF"): "ArticleIdNotFoundException",
    ("am", "AINF_NotReceived"): "ArticleIdNotFoundException",
    ("am", "EPI_p1_eq_p2"): "EqualPersonIdException",
    ("sm", "MINF"): "MessageIdNotFoundException",
    ("sm", "RNF"): "RelationNotFoundException",
    ("sm", "TINF"): "TagIdNotFoundException",
    ("sei", "EEI"): "EqualEmojiIdException",
    ("qsv", "PINF"): "PersonIdNotFoundException",
    ("qrm", "PINF"): "PersonIdNotFoundException",
    ("qp", "EINF"): "EmojiIdNotFoundException",
    ("qm", "PINF"): "PersonIdNotFoundException",
}

ALL_TARGET_KEYS = list(GENERATOR_TARGET_OUTCOME_MAP.keys())

# --- Command Generators (Strict Outcome) ---

def generate_ap(state, target_key=None):
    existing_ids = get_existing_person_ids()
    _id = None
    params = {}
    outcome = None

    if target_key == ("ap", "EPI"):
        if existing_ids:
            _id = random.choice(existing_ids)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        _id = get_random_non_existent_id("person")
        if _id is None: return None, None, None
        outcome = OUTCOME_NORMAL
    else: return None, None, None

    if _id is None: return None, None, None

    name = generate_random_name()
    age = generate_random_age()
    params = {"id": _id, "name": name, "age": age}
    cmd_str = f"ap {_id} {name} {age}"
    return cmd_str, params, outcome

def generate_ar(state, target_key=None):
    existing_ids = get_existing_person_ids()
    id1, id2 = None, None
    params = {}
    outcome = None

    if target_key and target_key[0] == "ar" and "PINF" in target_key[1]:
        non_existent_id = get_random_non_existent_id("person")
        if non_existent_id is None: return None, None, None

        if len(existing_ids) == 0: return None, None, None

        if target_key == ("ar", "PINF_id1"):
            id1 = non_existent_id
            id2 = random.choice(existing_ids) if existing_ids else get_random_non_existent_id("person")
            if id2 is None: return None, None, None
        elif target_key == ("ar", "PINF_id2"):
            id1 = random.choice(existing_ids) if existing_ids else get_random_non_existent_id("person")
            id2 = non_existent_id
            if id1 is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

    elif target_key == ("ar", "EPI"):
        if existing_ids:
            id1 = random.choice(existing_ids)
            id2 = id1
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("ar", "ERE"):
        linked_pairs = list(state["relations"].keys())
        if linked_pairs:
            min_id, max_id = random.choice(linked_pairs)
            id1, id2 = random.choice([(min_id, max_id), (max_id, min_id)])
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        non_linked_pairs = [(i, j) for i in existing_ids for j in existing_ids if i != j and (min(i, j), max(i, j)) not in state["relations"]]
        if non_linked_pairs:
            id1, id2 = random.choice(non_linked_pairs)
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if id1 is None or id2 is None: return None, None, None

    value = generate_random_value()
    params = {"id1": id1, "id2": id2, "value": value}
    cmd_str = f"ar {id1} {id2} {value}"
    return cmd_str, params, outcome

def generate_mr(state, target_key=None):
    existing_ids = get_existing_person_ids()
    id1, id2 = None, None
    params = {}
    outcome = None

    if target_key and target_key[0] == "mr" and "PINF" in target_key[1]:
        non_existent_id = get_random_non_existent_id("person")
        if non_existent_id is None: return None, None, None

        if len(existing_ids) == 0: return None, None, None
        if len(existing_ids) == 1: return None, None, None

        if target_key == ("mr", "PINF_id1"):
            id1 = non_existent_id
            id2 = random.choice(existing_ids)
        elif target_key == ("mr", "PINF_id2"):
            id1 = random.choice(existing_ids)
            id2 = non_existent_id
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

    elif target_key == ("mr", "EPI"):
        if existing_ids:
            id1 = random.choice(existing_ids)
            id2 = id1
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("mr", "RNF"):
        non_linked_pairs = [(i, j) for i in existing_ids for j in existing_ids if i != j and (min(i, j), max(i, j)) not in state["relations"]]
        if non_linked_pairs:
            id1, id2 = random.choice(non_linked_pairs)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        linked_pairs = list(state["relations"].keys())
        if linked_pairs:
            min_id, max_id = random.choice(linked_pairs)
            id1, id2 = random.choice([(min_id, max_id), (max_id, min_id)])
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if id1 is None or id2 is None: return None, None, None

    m_val = generate_random_mval()
    params = {"id1": id1, "id2": id2, "m_val": m_val}
    cmd_str = f"mr {id1} {id2} {m_val}"
    return cmd_str, params, outcome

def generate_at(state, target_key=None):
    existing_ids = get_existing_person_ids()
    person_id = None
    tag_id = None
    params = {}
    outcome = None

    if target_key == ("at", "PINF"):
        person_id = get_random_non_existent_id("person")
        tag_id = generate_random_id("tag")
        if person_id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("at", "ETI"):
        persons_with_tags = [pid for pid in existing_ids if get_existing_tag_ids_for_person(pid)]
        if persons_with_tags:
            person_id = random.choice(persons_with_tags)
            tag_id = get_random_existing_tag_id_for_person(person_id)
            if tag_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        if existing_ids:
            person_id = random.choice(existing_ids)
            tag_id = get_random_non_existent_tag_id_for_person(person_id)
            if tag_id is None: return None, None, None
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if person_id is None or tag_id is None: return None, None, None

    params = {"person_id": person_id, "tag_id": tag_id}
    cmd_str = f"at {person_id} {tag_id}"
    return cmd_str, params, outcome


def generate_dt(state, target_key=None):
    existing_ids = get_existing_person_ids()
    person_id = None
    tag_id = None
    params = {}
    outcome = None

    if target_key == ("dt", "PINF"):
        person_id = get_random_non_existent_id("person")
        tag_id = generate_random_id("tag")
        if person_id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("dt", "TINF"):
        if existing_ids:
            person_id = random.choice(existing_ids)
            tag_id = get_random_non_existent_tag_id_for_person(person_id)
            if tag_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        persons_with_tags = [pid for pid in existing_ids if get_existing_tag_ids_for_person(pid)]
        if persons_with_tags:
            person_id = random.choice(persons_with_tags)
            tag_id = get_random_existing_tag_id_for_person(person_id)
            if tag_id is None: return None, None, None
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if person_id is None or tag_id is None: return None, None, None

    params = {"person_id": person_id, "tag_id": tag_id}
    cmd_str = f"dt {person_id} {tag_id}"
    return cmd_str, params, outcome


def generate_att(state, target_key=None):
    existing_ids = get_existing_person_ids()
    id1, id2 = None, None
    tag_id = None
    params = {}
    outcome = None

    if target_key and target_key[0] == "att" and "PINF" in target_key[1]:
        non_existent_id = get_random_non_existent_id("person")
        if non_existent_id is None: return None, None, None

        if len(existing_ids) == 0: return None, None, None

        if target_key == ("att", "PINF_p1"):
            id1 = non_existent_id
            id2 = random.choice(existing_ids)
        elif target_key == ("att", "PINF_p2"):
            id1 = random.choice(existing_ids)
            id2 = non_existent_id
        tag_id = generate_random_id("tag")
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

    elif target_key == ("att", "EPI_id1_eq_id2"):
        if existing_ids:
            id1 = random.choice(existing_ids)
            id2 = id1
            tag_id = generate_random_id("tag")
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("att", "RNF"):
        valid_attempts = []
        for i in existing_ids:
             for j in existing_ids:
                  if i != j and (min(i, j), max(i, j)) not in state["relations"]:
                       p1_id, p2_id = i, j
                       p2_tags = get_existing_tag_ids_for_person(p2_id)
                       if p2_tags:
                            tag_id = random.choice(list(p2_tags))
                            valid_attempts.append((p1_id, p2_id, tag_id))
        if valid_attempts:
            id1, id2, tag_id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("att", "TINF"):
        valid_attempts = []
        for min_id, max_id in state["relations"].keys():
            id1, id2 = random.choice([(min_id, max_id), (max_id, min_id)])
            if id1 == id2: continue
            tag_id = get_random_non_existent_tag_id_for_person(id2)
            if tag_id is not None:
                valid_attempts.append((id1, id2, tag_id))

        if valid_attempts:
            id1, id2, tag_id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("att", "EPI_in_tag"):
        valid_attempts = []
        for (owner_id, tid), members in state["tag_members"].items():
            p2_id = owner_id
            p2_person_exists = p2_id in state["persons"]
            if p2_person_exists:
                for p1_id in members:
                    p1_person_exists = p1_id in state["persons"]
                    if p1_person_exists and p1_id != p2_id:
                         if (min(p1_id, p2_id), max(p1_id, p2_id)) in state["relations"]:
                             valid_attempts.append((p1_id, p2_id, tid))

        if valid_attempts:
            id1, id2, tag_id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        valid_attempts = []
        for i in existing_ids:
            for j in existing_ids:
                if i != j and (min(i, j), max(i, j)) in state["relations"]:
                    p1_id, p2_id = i, j
                    p2_tags = get_existing_tag_ids_for_person(p2_id)
                    for tag_id in p2_tags:
                        tag_key = (p2_id, tag_id)
                        if p1_id not in state["tag_members"].get(tag_key, {}) and len(state["tag_members"].get(tag_key, {})) < TAG_PERSONS_LIMIT:
                            valid_attempts.append((p1_id, p2_id, tag_id))

        if valid_attempts:
            id1, id2, tag_id = random.choice(valid_attempts)
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if id1 is None or id2 is None or tag_id is None: return None, None, None

    params = {"id1": id1, "id2": id2, "tag_id": tag_id}
    cmd_str = f"att {id1} {id2} {tag_id}"
    return cmd_str, params, outcome


def generate_dft(state, target_key=None):
    existing_ids = get_existing_person_ids()
    id1, id2 = None, None
    tag_id = None
    params = {}
    outcome = None

    if target_key and target_key[0] == "dft" and "PINF" in target_key[1]:
         if len(existing_ids) == 0: return None, None, None

         if target_key == ("dft", "PINF_p1"):
             non_existent_id = get_random_non_existent_id("person")
             if non_existent_id is None: return None, None, None
             id1 = non_existent_id
             id2 = random.choice(existing_ids)
             tag_id = generate_random_id("tag")
             outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
         elif target_key == ("dft", "PINF_p2"):
             non_existent_id = get_random_non_existent_id("person")
             if non_existent_id is None: return None, None, None
             id1 = random.choice(existing_ids)
             id2 = non_existent_id
             tag_id = generate_random_id("tag")
             outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
         elif target_key == ("dft", "PINF_not_in_tag"):
             valid_attempts = []
             for p2_id in existing_ids:
                 p2_tags = get_existing_tag_ids_for_person(p2_id)
                 for tid in p2_tags:
                     tag_key = (p2_id, tid)
                     persons_not_in_tag_members = [pid for pid in existing_ids if pid not in state["tag_members"].get(tag_key, {})]
                     if persons_not_in_tag_members:
                         id1 = random.choice(persons_not_in_tag_members)
                         id2 = p2_id
                         tag_id = tid
                         valid_attempts.append((id1, id2, tag_id))
             if valid_attempts:
                 id1, id2, tag_id = random.choice(valid_attempts)
                 outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
             else: return None, None, None
         else: return None, None, None

    elif target_key == ("dft", "TINF"):
        if existing_ids:
            id1 = random.choice(existing_ids)
            id2 = random.choice(existing_ids)
            tag_id = get_random_non_existent_tag_id_for_person(id2)
            if tag_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        valid_attempts = []
        for (owner_id, tid), members in state["tag_members"].items():
            p2_id = owner_id
            for p1_id in members:
                valid_attempts.append((p1_id, p2_id, tid))

        if valid_attempts:
            id1, id2, tag_id = random.choice(valid_attempts)
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if id1 is None or id2 is None or tag_id is None: return None, None, None

    params = {"id1": id1, "id2": id2, "tag_id": tag_id}
    cmd_str = f"dft {id1} {id2} {tag_id}"
    return cmd_str, params, outcome


def generate_qv(state, target_key=None):
    existing_ids = get_existing_person_ids()
    id1, id2 = None, None
    params = {}
    outcome = None

    if target_key and target_key[0] == "qv" and "PINF" in target_key[1]:
        non_existent_id = get_random_non_existent_id("person")
        if non_existent_id is None: return None, None, None

        if len(existing_ids) == 0: return None, None, None

        if target_key == ("qv", "PINF_id1"):
            id1 = non_existent_id
            id2 = random.choice(existing_ids)
        elif target_key == ("qv", "PINF_id2"):
            id1 = random.choice(existing_ids)
            id2 = non_existent_id
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

    elif target_key == ("qv", "RNF"):
        non_linked_pairs = [(i, j) for i in existing_ids for j in existing_ids if i != j and (min(i, j), max(i, j)) not in state["relations"]]
        if non_linked_pairs:
            id1, id2 = random.choice(non_linked_pairs)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        linked_pairs = list(state["relations"].keys())
        if linked_pairs:
            min_id, max_id = random.choice(linked_pairs)
            id1, id2 = random.choice([(min_id, max_id), (max_id, min_id)])
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if id1 is None or id2 is None: return None, None, None

    params = {"id1": id1, "id2": id2}
    cmd_str = f"qv {id1} {id2}"
    return cmd_str, params, outcome


def generate_qci(state, target_key=None):
    existing_ids = get_existing_person_ids()
    id1, id2 = None, None
    params = {}
    outcome = None

    if target_key and target_key[0] == "qci" and "PINF" in target_key[1]:
        non_existent_id = get_random_non_existent_id("person")
        if non_existent_id is None: return None, None, None

        if len(existing_ids) == 0: return None, None, None

        if target_key == ("qci", "PINF_id1"):
            id1 = non_existent_id
            id2 = random.choice(existing_ids)
        elif target_key == ("qci", "PINF_id2"):
            id1 = random.choice(existing_ids)
            id2 = non_existent_id
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

    elif target_key is None: # Try normal
        if existing_ids:
            id1 = random.choice(existing_ids)
            id2 = random.choice(existing_ids)
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if id1 is None or id2 is None: return None, None, None

    params = {"id1": id1, "id2": id2}
    cmd_str = f"qci {id1} {id2}"
    return cmd_str, params, outcome


def generate_qts(state, target_key=None):
    if target_key is not None: return None, None, None
    cmd_str = "qts"
    params = {}
    outcome = OUTCOME_NORMAL
    return cmd_str, params, outcome


def generate_qtav(state, target_key=None):
    existing_ids = get_existing_person_ids()
    person_id = None
    tag_id = None
    params = {}
    outcome = None

    if target_key == ("qtav", "PINF"):
        person_id = get_random_non_existent_id("person")
        tag_id = generate_random_id("tag")
        if person_id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("qtav", "TINF"):
        if existing_ids:
            person_id = random.choice(existing_ids)
            tag_id = get_random_non_existent_tag_id_for_person(person_id)
            if tag_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        persons_with_tags = [pid for pid in existing_ids if get_existing_tag_ids_for_person(pid)]
        if persons_with_tags:
            person_id = random.choice(persons_with_tags)
            tag_id = get_random_existing_tag_id_for_person(person_id)
            if tag_id is None: return None, None, None
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if person_id is None or tag_id is None: return None, None, None

    params = {"person_id": person_id, "tag_id": tag_id}
    cmd_str = f"qtav {person_id} {tag_id}"
    return cmd_str, params, outcome


def generate_qba(state, target_key=None):
    existing_ids = get_existing_person_ids()
    _id = None
    params = {}
    outcome = None

    if target_key == ("qba", "PINF"):
        _id = get_random_non_existent_id("person")
        if _id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("qba", "ANE"):
        persons_with_no_acquaintances = [pid for pid, data in state["persons"].items() if not data.get("acquaintances", {})]
        if persons_with_no_acquaintances:
            _id = random.choice(persons_with_no_acquaintances)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        persons_with_acquaintances = [pid for pid, data in state["persons"].items() if data.get("acquaintances", {})]
        if persons_with_acquaintances:
            _id = random.choice(persons_with_acquaintances)
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if _id is None: return None, None, None

    params = {"id": _id}
    cmd_str = f"qba {_id}"
    return cmd_str, params, outcome

def generate_ln(state, target_key=None):
    if target_key is not None: return None, None, None

    reset_state() # ln resets the network state and global ID tracking

    n_range = list(N_RANGE)
    max_possible_n = ID_POOL_RANGE[1] - ID_POOL_RANGE[0] + 1
    if n_range[1] > max_possible_n:
         if max_possible_n < n_range[0]:
             n_range = (0, 0)
         else:
              n_range = (n_range[0], max_possible_n)

    n = random.randint(n_range[0], n_range[1])

    ids = []
    if n > 0:
        id_pool = list(range(ID_POOL_RANGE[0], ID_POOL_RANGE[1] + 1))
        if len(id_pool) < n:
             n = len(id_pool)
             if n == 0: ids = []
             else: ids = random.sample(id_pool, n)
        else:
            ids = random.sample(id_pool, n)

    names = [generate_random_name() for _ in range(n)]
    ages = [generate_random_age() for _ in range(n)]

    values_matrix = []
    if n > 1:
        for i in range(n - 1):
            row = [random.randint(0, VALUE_RANGE[1]) for _ in range(i + 1)]
            values_matrix.append(row)

    output = f"ln {n}\n"
    output += (" ".join(map(str, ids)) + "\n") if n > 0 else "\n"
    output += (" ".join(names) + "\n") if n > 0 else "\n"
    output += (" ".join(map(str, ages)) + "\n") if n > 0 else "\n"
    if n > 1:
         for row in values_matrix:
            output += " ".join(map(str, row)) + "\n"

    for i in range(n):
        person_id = ids[i]
        state["persons"][person_id] = {"name": names[i], "age": ages[i], "acquaintances": {},
                                       "socialValue": 0, "money": 0, "receivedArticles": [], "messages": []}
        state["person_tags"][person_id] = set()

    if n > 1:
        for i in range(n - 1):
            for j in range(i + 1):
                id1 = ids[i + 1]
                id2 = ids[j]
                value = values_matrix[i][j]
                if value > 0:
                     state["persons"][id1]["acquaintances"][id2] = value
                     state["persons"][id2]["acquaintances"][id1] = value
                     state["relations"][(min(id1, id2), max(id1, id2))] = value

    state["triple_sum"] = 0
    state["couple_sum_dirty"] = True

    person_list = list(state["persons"].keys())
    for i in range(len(person_list)):
        for j in range(i + 1, len(person_list)):
            for k in range(j + 1, len(person_list)):
                 p1_id, p2_id, p3_id = person_list[i], person_list[j], person_list[k]
                 if (min(p1_id, p2_id), max(p1_id, p2_id)) in state["relations"] and \
                    (min(p2_id, p3_id), max(p2_id, p3_id)) in state["relations"] and \
                    (min(p3_id, p1_id), max(p3_id, p1_id)) in state["relations"]:
                     state["triple_sum"] += 1

    params = {"n": n, "ids": ids, "names": names, "ages": ages, "values_matrix": values_matrix}
    return output, params, OUTCOME_NORMAL


def generate_coa(state, target_key=None):
    existing_persons = get_existing_person_ids()
    existing_accounts = get_existing_account_ids()
    person_id = None
    account_id = None
    params = {}
    outcome = None

    if target_key == ("coa", "PINF"):
        person_id = get_random_non_existent_id("person")
        account_id = generate_random_id("account")
        if person_id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("coa", "EOAI"):
        if existing_persons and existing_accounts:
            person_id = random.choice(existing_persons)
            account_id = random.choice(existing_accounts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None:
        if existing_persons:
            person_id = random.choice(existing_persons)
            account_id = get_random_non_existent_id("account")
            if account_id is None: return None, None, None
            outcome = OUTCOME_NORMAL
        else: return None, None, None

    if person_id is None or account_id is None: return None, None, None

    account_name = generate_random_name()
    params = {"person_id": person_id, "account_id": account_id, "account_name": account_name}
    cmd_str = f"coa {person_id} {account_id} {account_name}"
    return cmd_str, params, outcome


def generate_doa(state, target_key=None):
    existing_persons = get_existing_person_ids()
    existing_accounts = get_existing_account_ids()
    person_id = None
    account_id = None
    params = {}
    outcome = None

    if target_key == ("doa", "PINF"):
        non_existent_person = get_random_non_existent_id("person")
        if non_existent_person is None: return None, None, None
        person_id = non_existent_person
        account_id = random.choice(existing_accounts) if existing_accounts else generate_random_id("account")
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("doa", "OAINF"):
        if existing_persons:
            person_id = random.choice(existing_persons)
            account_id = get_random_non_existent_id("account")
            if account_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("doa", "DAPermissionDenied"):
        valid_attempts = []
        for acc_id, acc_data in state["accounts"].items():
            owner_id = acc_data["owner_id"]
            non_owners = [pid for pid in existing_persons if pid != owner_id]
            if non_owners:
                person_id = random.choice(non_owners)
                account_id = acc_id
                valid_attempts.append((person_id, account_id))
        if valid_attempts:
            person_id, account_id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None:
        valid_attempts = []
        for person_id in existing_persons:
             owned_accounts = get_accounts_owned_by_person(person_id)
             if owned_accounts:
                  account_id = random.choice(owned_accounts)
                  valid_attempts.append((person_id, account_id))
        if valid_attempts:
            person_id, account_id = random.choice(valid_attempts)
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if person_id is None or account_id is None: return None, None, None

    params = {"person_id": person_id, "account_id": account_id}
    cmd_str = f"doa {person_id} {account_id}"
    return cmd_str, params, outcome


def generate_ca(state, target_key=None):
    existing_persons = get_existing_person_ids()
    existing_accounts = get_existing_account_ids()
    existing_articles = get_existing_article_ids()
    person_id = None
    account_id = None
    article_id = None
    params = {}
    outcome = None

    if target_key == ("ca", "PINF"):
        non_existent_person = get_random_non_existent_id("person")
        if non_existent_person is None: return None, None, None
        person_id = non_existent_person
        account_id = random.choice(existing_accounts) if existing_accounts else generate_random_id("account")
        article_id = generate_random_id("article")
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("ca", "OAINF"):
        if existing_persons:
            person_id = random.choice(existing_persons)
            account_id = get_random_non_existent_id("account")
            article_id = generate_random_id("article")
            if account_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("ca", "EAI"):
        valid_attempts = []
        for acc_id, acc_data in state["accounts"].items():
            followers = get_followers_of_account(acc_id)
            articles_of_account = get_articles_of_account(acc_id)
            if followers and articles_of_account:
                person_id = random.choice(followers)
                account_id = acc_id
                article_id = random.choice(articles_of_account)
                valid_attempts.append((person_id, account_id, article_id))
        if valid_attempts:
            person_id, account_id, article_id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("ca", "ContributePermissionDenied"):
        valid_attempts = []
        for acc_id in existing_accounts:
            non_follower = get_random_non_follower_of_account(acc_id)
            article_id = get_random_non_existent_id("article")
            if non_follower is not None and article_id is not None:
                 person_id = non_follower
                 account_id = acc_id
                 valid_attempts.append((person_id, account_id, article_id))
        if valid_attempts:
             person_id, account_id, article_id = random.choice(valid_attempts)
             outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None:
        valid_attempts = []
        for acc_id, acc_data in state["accounts"].items():
            followers = get_followers_of_account(acc_id)
            article_id = get_random_non_existent_id("article")
            if followers and article_id is not None:
                person_id = random.choice(followers)
                account_id = acc_id
                valid_attempts.append((person_id, account_id, article_id))
        if valid_attempts:
            person_id, account_id, article_id = random.choice(valid_attempts)
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if person_id is None or account_id is None or article_id is None: return None, None, None

    article_name = generate_random_name()
    params = {"person_id": person_id, "account_id": account_id, "article_id": article_id, "article_name": article_name}
    cmd_str = f"ca {person_id} {account_id} {article_id} {article_name}"
    return cmd_str, params, outcome


def generate_da(state, target_key=None):
    existing_persons = get_existing_person_ids()
    existing_accounts = get_existing_account_ids()
    existing_articles = get_existing_article_ids()
    person_id = None
    account_id = None
    article_id = None
    params = {}
    outcome = None

    if target_key == ("da", "PINF"):
        non_existent_person = get_random_non_existent_id("person")
        if non_existent_person is None: return None, None, None
        person_id = non_existent_person
        account_id = random.choice(existing_accounts) if existing_accounts else generate_random_id("account")
        article_id = random.choice(existing_articles) if existing_articles else generate_random_id("article")
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("da", "OAINF"):
        if existing_persons:
            person_id = random.choice(existing_persons)
            account_id = get_random_non_existent_id("account")
            article_id = random.choice(existing_articles) if existing_articles else generate_random_id("article")
            if account_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("da", "AINF"):
        valid_attempts = []
        for acc_id, acc_data in state["accounts"].items():
            owner_id = acc_data["owner_id"]
            article_id = get_random_article_not_of_account(acc_id)
            if article_id is not None:
                person_id = owner_id
                account_id = acc_id
                valid_attempts.append((person_id, account_id, article_id))
        if valid_attempts:
            person_id, account_id, article_id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("da", "DAPermissionDenied"):
        valid_attempts = []
        for acc_id, acc_data in state["accounts"].items():
             articles_of_account = get_articles_of_account(acc_id)
             non_owners = [pid for pid in existing_persons if pid != acc_data["owner_id"]]
             if articles_of_account and non_owners:
                  person_id = random.choice(non_owners)
                  account_id = acc_id
                  article_id = random.choice(articles_of_account)
                  valid_attempts.append((person_id, account_id, article_id))
        if valid_attempts:
            person_id, account_id, article_id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None:
        valid_attempts = []
        for acc_id, acc_data in state["accounts"].items():
            owner_id = acc_data["owner_id"]
            articles_of_account = get_articles_of_account(acc_id)
            if articles_of_account:
                person_id = owner_id
                account_id = acc_id
                article_id = random.choice(articles_of_account)
                valid_attempts.append((person_id, account_id, article_id))
        if valid_attempts:
            person_id, account_id, article_id = random.choice(valid_attempts)
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if person_id is None or account_id is None or article_id is None: return None, None, None

    params = {"person_id": person_id, "account_id": account_id, "article_id": article_id}
    cmd_str = f"da {person_id} {account_id} {article_id}"
    return cmd_str, params, outcome


def generate_foa(state, target_key=None):
    existing_persons = get_existing_person_ids()
    existing_accounts = get_existing_account_ids()
    person_id = None
    account_id = None
    params = {}
    outcome = None

    if target_key == ("foa", "PINF"):
        non_existent_person = get_random_non_existent_id("person")
        if non_existent_person is None: return None, None, None
        person_id = non_existent_person
        account_id = random.choice(existing_accounts) if existing_accounts else generate_random_id("account")
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("foa", "OAINF"):
        if existing_persons:
            person_id = random.choice(existing_persons)
            account_id = get_random_non_existent_id("account")
            if account_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("foa", "EPI_follower"):
        valid_attempts = []
        for acc_id, acc_data in state["accounts"].items():
            followers = get_followers_of_account(acc_id)
            if followers:
                person_id = random.choice(followers)
                account_id = acc_id
                valid_attempts.append((person_id, account_id))
        if valid_attempts:
            person_id, account_id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None:
        valid_attempts = []
        for acc_id in existing_accounts:
            non_follower = get_random_non_follower_of_account(acc_id)
            if non_follower is not None:
                 person_id = non_follower
                 account_id = acc_id
                 valid_attempts.append((person_id, account_id))
        if valid_attempts:
             person_id, account_id = random.choice(valid_attempts)
             outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if person_id is None or account_id is None: return None, None, None

    params = {"person_id": person_id, "account_id": account_id}
    cmd_str = f"foa {person_id} {account_id}"
    return cmd_str, params, outcome


def generate_qsp(state, target_key=None):
    existing_ids = get_existing_person_ids()
    id1, id2 = None, None
    params = {}
    outcome = None

    if target_key and target_key[0] == "qsp" and "PINF" in target_key[1]:
        non_existent_id = get_random_non_existent_id("person")
        if non_existent_id is None: return None, None, None

        if len(existing_ids) == 0: return None, None, None

        if target_key == ("qsp", "PINF_id1"):
            id1 = non_existent_id
            id2 = random.choice(existing_ids)
        elif target_key == ("qsp", "PINF_id2"):
            id1 = random.choice(existing_ids)
            id2 = non_existent_id
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

    elif target_key == ("qsp", "PathNotFound"):
        if len(existing_ids) < 2: return None, None, None

        start_node = random.choice(existing_ids)
        reachable_set = bfs_reachable(start_node, state)

        unreachable_candidates = [pid for pid in existing_ids if pid not in reachable_set]

        if unreachable_candidates:
            id1 = start_node
            id2 = random.choice(unreachable_candidates)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None:
        if not existing_ids: return None, None, None

        id1 = random.choice(existing_ids)
        reachable_set = bfs_reachable(id1, state)
        if reachable_set:
            id2 = random.choice(list(reachable_set))
            outcome = OUTCOME_NORMAL
        else:
             if len(existing_ids) > 1:
                 if id1 in state["persons"] and not state["persons"][id1]["acquaintances"]:
                     id2 = id1
                     outcome = OUTCOME_NORMAL
                 else:
                      return None, None, None
             elif len(existing_ids) == 1:
                 id2 = id1
                 outcome = OUTCOME_NORMAL
             else: return None, None, None

    else: return None, None, None

    if id1 is None or id2 is None: return None, None, None

    params = {"id1": id1, "id2": id2}
    cmd_str = f"qsp {id1} {id2}"
    return cmd_str, params, outcome


def generate_qbc(state, target_key=None):
    existing_accounts = get_existing_account_ids()
    account_id = None
    params = {}
    outcome = None

    if target_key == ("qbc", "OAINF"):
        account_id = get_random_non_existent_id("account")
        if account_id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key is None:
        if existing_accounts:
            account_id = random.choice(existing_accounts)
            outcome = OUTCOME_NORMAL
        else: return None, None, None

    if account_id is None: return None, None, None

    params = {"account_id": account_id}
    cmd_str = f"qbc {account_id}"
    return cmd_str, params, outcome


def generate_qra(state, target_key=None):
    existing_persons = get_existing_person_ids()
    person_id = None
    params = {}
    outcome = None

    if target_key == ("qra", "PINF"):
        person_id = get_random_non_existent_id("person")
        if person_id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key is None:
        if existing_persons:
            person_id = random.choice(existing_persons)
            outcome = OUTCOME_NORMAL
        else: return None, None, None

    if person_id is None: return None, None, None

    params = {"person_id": person_id}
    cmd_str = f"qra {person_id}"
    return cmd_str, params, outcome


def generate_qtvs(state, target_key=None):
    existing_persons = get_existing_person_ids()
    person_id = None
    tag_id = None
    params = {}
    outcome = None

    if target_key == ("qtvs", "PINF"):
        person_id = get_random_non_existent_id("person")
        tag_id = generate_random_id("tag")
        if person_id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("qtvs", "TINF"):
        if existing_persons:
            person_id = random.choice(existing_persons)
            tag_id = get_random_non_existent_tag_id_for_person(person_id)
            if tag_id is None: return None, None, None
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        persons_with_tags = [pid for pid in existing_persons if get_existing_tag_ids_for_person(pid)]
        if persons_with_tags:
            person_id = random.choice(persons_with_tags)
            tag_id = get_random_existing_tag_id_for_person(person_id)
            if tag_id is None: return None, None, None
            outcome = OUTCOME_NORMAL
        else: return None, None, None
    else: return None, None, None

    if person_id is None or tag_id is None: return None, None, None

    params = {"person_id": person_id, "tag_id": tag_id}
    cmd_str = f"qtvs {person_id} {tag_id}"
    return cmd_str, params, outcome


def generate_qcs(state, target_key=None):
    if target_key is not None: return None, None, None
    cmd_str = "qcs"
    params = {}
    outcome = OUTCOME_NORMAL
    return cmd_str, params, outcome

# New Command Generators (current increment)

def generate_am(state, target_key=None):
    existing_persons = get_existing_person_ids()
    existing_messages = get_existing_message_ids()
    existing_emoji = get_existing_emoji_ids()
    existing_articles = get_existing_article_ids()

    message_id = None
    social_value = None
    _type = None
    person_id1 = None
    person_id2 = None
    tag_id = None
    subtype = None
    emoji_id = None
    money = None
    article_id = None

    params = {}
    outcome = None
    cmd_str = None

    # --- Exception Targets ---
    if target_key == ("am", "EMI"):
        # Need existing message ID from the *current* state (messages not yet sent)
        message_id = get_random_existing_message_id()
        if message_id is None: return None, None, None
        # Other parameters don't strictly matter for this exception, but make them valid if possible
        if existing_persons:
            person_id1 = random.choice(existing_persons)
            _type = random.choice([0, 1])
            if _type == 0:
                 person_id2 = random.choice(existing_persons)
            else:
                 person_id2 = 0
                 tag_id = generate_random_id("tag") # Tag ID can be anything for this exception
        else: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

    # For all other targets (which require adding a *new* message), generate a globally unique ID
    elif target_key == ("am", "EINF"):
        message_id = get_random_unused_id("message") # Need a new, unused message ID
        if message_id is None: return None, None, None # Cannot generate new message

        non_existent_emoji = get_random_non_existent_id("emoji") # Need non-existent emoji_id
        if non_existent_emoji is None:
            # If we generated a message_id but can't trigger EINF, we should probably discard the message_id
            # and return None,None,None. But the current get_random_unused_id adds it immediately.
            # This highlights a tricky interaction. Let's assume pool exhaustion is rare and continue.
            # A more robust generator might backtrack or use a try-and-reserve system.
            # For simplicity here, if we can't trigger the target after getting a unique ID, we fail this slot.
            return None, None, None

        emoji_id = non_existent_emoji
        social_value = emoji_id # Social value rule for EmojiMessage
        subtype = MESSAGE_SUBTYPE_EMOJI # Force Emoji type
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

        if existing_persons:
             person_id1 = random.choice(existing_persons)
             _type = random.choice([0, 1])
             if _type == 0:
                 other_persons = [pid for pid in existing_persons if pid != person_id1]
                 if other_persons: person_id2 = random.choice(other_persons)
                 else: person_id2 = person_id1
             else:
                 person_id2 = 0
                 owned_tags = get_existing_tag_ids_for_person(person_id1)
                 if owned_tags: tag_id = random.choice(owned_tags)
                 else: tag_id = generate_random_id("tag")
        else: return None, None, None

    elif target_key == ("am", "AINF"):
        message_id = get_random_unused_id("message")
        if message_id is None: return None, None, None

        # Case 1: !containsArticle(articleId)
        non_existent_article = get_random_non_existent_id("article")
        if non_existent_article is None: return None, None, None
        article_id = non_existent_article
        social_value = abs(article_id) % 200
        subtype = MESSAGE_SUBTYPE_FORWARD
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]

        if existing_persons:
            person_id1 = random.choice(existing_persons)
            _type = random.choice([0, 1])
            if _type == 0:
                 other_persons = [pid for pid in existing_persons if pid != person_id1]
                 if other_persons: person_id2 = random.choice(other_persons)
                 else: person_id2 = person_id1
            else:
                 person_id2 = 0
                 owned_tags = get_existing_tag_ids_for_person(person_id1)
                 if owned_tags: tag_id = random.choice(owned_tags)
                 else: tag_id = generate_random_id("tag")
        else: return None, None, None


    elif target_key == ("am", "AINF_NotReceived"):
         message_id = get_random_unused_id("message")
         if message_id is None: return None, None, None

         # Case 2: containsArticle(articleId) && !p1.getReceivedArticles().contains(articleId)
         valid_attempts = []
         for p1_id in existing_persons:
              art_not_received = get_random_article_person_has_not_received(p1_id)
              if art_not_received is not None:
                   _type = random.choice([0, 1])
                   if _type == 0:
                       other_persons = [pid for pid in existing_persons if pid != p1_id]
                       if not other_persons: continue
                       person_id2 = random.choice(other_persons)
                       valid_attempts.append((p1_id, _type, person_id2, None, art_not_received))
                   else:
                        owned_tags = get_existing_tag_ids_for_person(p1_id)
                        if not owned_tags: continue
                        tag_id = random.choice(owned_tags)
                        valid_attempts.append((p1_id, _type, None, tag_id, art_not_received))

         if not valid_attempts: return None, None, None # Cannot find scenario for AINF_NotReceived

         person_id1, _type, person_id2, tag_id, article_id = random.choice(valid_attempts)

         social_value = abs(article_id) % 200
         subtype = MESSAGE_SUBTYPE_FORWARD
         outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]


    elif target_key == ("am", "EPI_p1_eq_p2"):
        message_id = get_random_unused_id("message")
        if message_id is None: return None, None, None

        if existing_persons:
            person_id1 = random.choice(existing_persons)
            person_id2 = person_id1
            _type = MESSAGE_TYPE_PERSON

            subtype = random.choice([MESSAGE_SUBTYPE_NORMAL, MESSAGE_SUBTYPE_EMOJI, MESSAGE_SUBTYPE_RED_ENVELOPE, MESSAGE_SUBTYPE_FORWARD])
            # Generate subtype-specific parameters, they don't prevent the EPI exception
            if subtype == MESSAGE_SUBTYPE_NORMAL:
                 social_value = generate_random_social_value()
            elif subtype == MESSAGE_SUBTYPE_EMOJI:
                 emoji_id = generate_random_id("emoji")
                 social_value = emoji_id
            elif subtype == MESSAGE_SUBTYPE_RED_ENVELOPE:
                 money = generate_random_money()
                 social_value = money * 5
            elif subtype == MESSAGE_SUBTYPE_FORWARD:
                 article_id = get_random_existing_article_id() # Need existing article for FM
                 if article_id is None: return None, None, None # Cannot generate FM if no articles exist
                 social_value = abs(article_id) % 200

            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None

    # --- Normal Case ---
    elif target_key is None:
        message_id = get_random_unused_id("message") # Need a new, unused message ID
        if message_id is None: return None, None, None

        if not existing_persons: return None, None, None

        person_id1 = random.choice(existing_persons)
        _type = random.choice([MESSAGE_TYPE_PERSON, MESSAGE_TYPE_TAG])

        if _type == MESSAGE_TYPE_PERSON:
            other_persons = [pid for pid in existing_persons if pid != person_id1]
            if not other_persons: return None, None, None
            person_id2 = random.choice(other_persons)
            tag_id = None

            subtype = random.choice([MESSAGE_SUBTYPE_NORMAL, MESSAGE_SUBTYPE_EMOJI, MESSAGE_SUBTYPE_RED_ENVELOPE, MESSAGE_SUBTYPE_FORWARD])
            if subtype == MESSAGE_SUBTYPE_NORMAL:
                social_value = generate_random_social_value()
            elif subtype == MESSAGE_SUBTYPE_EMOJI:
                emoji_id = get_random_existing_emoji_id() # Need existing emoji
                if emoji_id is None: return None, None, None
                social_value = emoji_id
            elif subtype == MESSAGE_SUBTYPE_RED_ENVELOPE:
                money = generate_random_money()
                social_value = money * 5
            elif subtype == MESSAGE_SUBTYPE_FORWARD:
                article_id = get_random_article_person_has_received(person_id1) # Need received article
                if article_id is None: return None, None, None
                social_value = abs(article_id) % 200

        else: # _type == MESSAGE_TYPE_TAG
            person_id2 = None
            owned_tags = get_existing_tag_ids_for_person(person_id1) # Need existing tag
            if not owned_tags: return None, None, None
            tag_id = random.choice(owned_tags)

            subtype = random.choice([MESSAGE_SUBTYPE_NORMAL, MESSAGE_SUBTYPE_EMOJI, MESSAGE_SUBTYPE_RED_ENVELOPE, MESSAGE_SUBTYPE_FORWARD])
            if subtype == MESSAGE_SUBTYPE_NORMAL:
                social_value = generate_random_social_value()
            elif subtype == MESSAGE_SUBTYPE_EMOJI:
                emoji_id = get_random_existing_emoji_id()
                if emoji_id is None: return None, None, None
                social_value = emoji_id
            elif subtype == MESSAGE_SUBTYPE_RED_ENVELOPE:
                money = generate_random_money()
                social_value = money * 5
            elif subtype == MESSAGE_SUBTYPE_FORWARD:
                article_id = get_random_article_person_has_received(person_id1)
                if article_id is None: return None, None, None
                social_value = abs(article_id) % 200

        if social_value is None: return None, None, None
        if _type == MESSAGE_TYPE_PERSON and person_id2 is None: return None, None, None
        if _type == MESSAGE_TYPE_TAG and tag_id is None: return None, None, None

        outcome = OUTCOME_NORMAL

    # --- If we successfully determined parameters for any case, construct command ---
    # Add the newly generated message_id to the global set if it's for a NEW message (not EMI target)
    if message_id is not None and target_key != ("am", "EMI"):
         all_generated_message_ids.add(message_id)
         # For AEM, the emoji_id might be *new* or *existing*. We only track generated *new* emoji IDs.
         if subtype == MESSAGE_SUBTYPE_EMOJI and target_key != ("am", "EINF") and emoji_id is not None:
              # If emoji_id was newly generated and not already stored, add it to tracked set
              # This is only for cases where AEM is generated *normally* or for non-EINF exceptions
              pass # Emoji ID uniqueness is handled by sei and get_random_unused_id('emoji')


    if message_id is None or person_id1 is None or _type is None or social_value is None:
        return None, None, None

    cmd_parts = []
    if subtype == MESSAGE_SUBTYPE_EMOJI: cmd_parts.append(ALIAS_MAP["add_emoji_message"])
    elif subtype == MESSAGE_SUBTYPE_RED_ENVELOPE: cmd_parts.append(ALIAS_MAP["add_red_envelope_message"])
    elif subtype == MESSAGE_SUBTYPE_FORWARD: cmd_parts.append(ALIAS_MAP["add_forward_message"])
    else: cmd_parts.append(ALIAS_MAP["add_message"])

    cmd_parts.append(str(message_id))

    if subtype == MESSAGE_SUBTYPE_EMOJI: cmd_parts.append(str(emoji_id))
    elif subtype == MESSAGE_SUBTYPE_RED_ENVELOPE: cmd_parts.append(str(money))
    elif subtype == MESSAGE_SUBTYPE_FORWARD: cmd_parts.append(str(article_id))
    else: cmd_parts.append(str(social_value))

    cmd_parts.append(str(_type))
    cmd_parts.append(str(person_id1))

    if _type == MESSAGE_TYPE_PERSON:
        cmd_parts.append(str(person_id2))
    else:
        cmd_parts.append(str(tag_id))

    cmd_str = " ".join(cmd_parts)

    params = {
        "id": message_id,
        "type": _type,
        "socialValue": social_value,
        "person1_id": person_id1,
        "person2_id": person_id2 if _type == MESSAGE_TYPE_PERSON else None,
        "tag_id": tag_id if _type == MESSAGE_TYPE_TAG else None,
        "subtype": subtype,
        "emoji_id": emoji_id,
        "money": money,
        "article_id": article_id,
    }

    return cmd_str, params, outcome


def generate_sm(state, target_key=None):
    existing_messages = get_existing_message_ids()
    _id = None
    params = {}
    outcome = None

    if target_key == ("sm", "MINF"):
        _id = get_random_non_existent_id("message")
        if _id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key == ("sm", "RNF"):
        valid_attempts = []
        for msg_id, msg_data in state["messages"].items():
             if msg_data["type"] == MESSAGE_TYPE_PERSON:
                  p1_id = msg_data["person1_id"]
                  p2_id = msg_data["person2_id"]
                  if p1_id in state["persons"] and p2_id in state["persons"] and \
                     (min(p1_id, p2_id), max(p1_id, p2_id)) not in state["relations"]:
                       valid_attempts.append(msg_id)
        if valid_attempts:
            _id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key == ("sm", "TINF"):
        valid_attempts = []
        for msg_id, msg_data in state["messages"].items():
             if msg_data["type"] == MESSAGE_TYPE_TAG:
                  p1_id = msg_data["person1_id"]
                  tag_id = msg_data["tag_id"]
                  if p1_id in state["persons"] and \
                     tag_id not in state["person_tags"].get(p1_id, set()):
                       valid_attempts.append(msg_id)
        if valid_attempts:
            _id = random.choice(valid_attempts)
            outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
        else: return None, None, None
    elif target_key is None: # Try normal
        valid_attempts = []
        for msg_id, msg_data in state["messages"].items():
            msg_type = msg_data["type"]
            p1_id = msg_data["person1_id"]
            if p1_id not in state["persons"]: continue
            if msg_type == MESSAGE_TYPE_PERSON:
                 p2_id = msg_data["person2_id"]
                 if p2_id not in state["persons"]: continue
                 if (min(p1_id, p2_id), max(p1_id, p2_id)) in state["relations"]:
                      valid_attempts.append(msg_id)
            else:
                 tag_id = msg_data["tag_id"]
                 if tag_id in state["person_tags"].get(p1_id, set()):
                      valid_attempts.append(msg_id)

        if valid_attempts:
            _id = random.choice(valid_attempts)
            outcome = OUTCOME_NORMAL
        else: return None, None, None

    if _id is None: return None, None, None

    params = {"id": _id}
    cmd_str = f"sm {_id}"
    return cmd_str, params, outcome


def generate_sei(state, target_key=None):
    existing_emoji = get_existing_emoji_ids()
    _id = None
    params = {}
    outcome = None

    if target_key == ("sei", "EEI"):
        # Need existing emoji ID from the *current* state (emojis not yet deleted)
        _id = get_random_existing_emoji_id()
        if _id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key is None: # Try normal
        # Need a new, unused emoji ID globally
        _id = get_random_unused_id("emoji")
        if _id is None: return None, None, None
        outcome = OUTCOME_NORMAL
        # Add the newly generated emoji_id to the global set
        all_generated_emoji_ids.add(_id)
    else: return None, None, None

    if _id is None: return None, None, None

    params = {"id": _id}
    cmd_str = f"sei {_id}"
    return cmd_str, params, outcome


def generate_dce(state, target_key=None):
    if target_key is not None: return None, None, None

    limit = random.randint(-100, 100)
    if random.random() < 0.3:
         if network_state["emojiId2Heat"]:
              existing_heats = list(network_state["emojiId2Heat"].values())
              if existing_heats:
                   chosen_heat = random.choice(existing_heats)
                   limit = max(0, chosen_heat + random.randint(-10, 10))
         else:
              limit = random.randint(1, 5)

    params = {"limit": limit}
    cmd_str = f"dce {limit}"
    outcome = OUTCOME_NORMAL
    return cmd_str, params, outcome


def generate_qsv(state, target_key=None):
    existing_persons = get_existing_person_ids()
    _id = None
    params = {}
    outcome = None

    if target_key == ("qsv", "PINF"):
        _id = get_random_non_existent_id("person")
        if _id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key is None: # Try normal
        _id = get_random_existing_person_id()
        if _id is None: return None, None, None
        outcome = OUTCOME_NORMAL
    else: return None, None, None

    if _id is None: return None, None, None

    params = {"id": _id}
    cmd_str = f"qsv {_id}"
    return cmd_str, params, outcome


def generate_qrm(state, target_key=None):
    existing_persons = get_existing_person_ids()
    _id = None
    params = {}
    outcome = None

    if target_key == ("qrm", "PINF"):
        _id = get_random_non_existent_id("person")
        if _id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key is None: # Try normal
        _id = get_random_existing_person_id()
        if _id is None: return None, None, None
        outcome = OUTCOME_NORMAL
    else: return None, None, None

    if _id is None: return None, None, None

    params = {"id": _id}
    cmd_str = f"qrm {_id}"
    return cmd_str, params, outcome


def generate_qp(state, target_key=None):
    existing_emoji = get_existing_emoji_ids()
    _id = None
    params = {}
    outcome = None

    if target_key == ("qp", "EINF"):
        # Need non-existent emoji ID from the *current* state (emojis not yet deleted)
        _id = get_random_non_existent_id("emoji")
        if _id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key is None: # Try normal
        # Need existing emoji ID from the *current* state
        _id = get_random_existing_emoji_id()
        if _id is None: return None, None, None
        outcome = OUTCOME_NORMAL
    else: return None, None, None

    if _id is None: return None, None, None

    params = {"id": _id}
    cmd_str = f"qp {_id}"
    return cmd_str, params, outcome


def generate_qm(state, target_key=None):
    existing_persons = get_existing_person_ids()
    _id = None
    params = {}
    outcome = None

    if target_key == ("qm", "PINF"):
        _id = get_random_non_existent_id("person")
        if _id is None: return None, None, None
        outcome = GENERATOR_TARGET_OUTCOME_MAP[target_key]
    elif target_key is None: # Try normal
        _id = get_random_existing_person_id()
        if _id is None: return None, None, None
        outcome = OUTCOME_NORMAL
    else: return None, None, None

    if _id is None: return None, None, None

    params = {"id": _id}
    cmd_str = f"qm {_id}"
    return cmd_str, params, outcome


# --- State Update Functions ---
def update_state_ap(state, params):
    _id = params["id"]
    if _id not in state["persons"]:
        state["persons"][_id] = {"name": params["name"], "age": params["age"], "acquaintances": {},
                                 "socialValue": 0, "money": 0, "receivedArticles": [], "messages": []}
        state["person_tags"][_id] = set()
        state["couple_sum_dirty"] = True

def update_state_ar(state, params):
    id1 = params["id1"]
    id2 = params["id2"]
    value = params["value"]
    pair = (min(id1, id2), max(id1, id2))
    if id1 in state["persons"] and id2 in state["persons"] and id1 != id2 and pair not in state["relations"]:
        state["persons"][id1]["acquaintances"][id2] = value
        state["persons"][id2]["acquaintances"][id1] = value
        state["relations"][pair] = value
        p1_acquaintances = set(state["persons"][id1]["acquaintances"].keys())
        p2_acquaintances = set(state["persons"][id2]["acquaintances"].keys())
        common_acquaintances = p1_acquaintances.intersection(p2_acquaintances)
        common_acquaintances = [pid for pid in common_acquaintances if pid != id1 and pid != id2]
        state["triple_sum"] += len(common_acquaintances)
        state["couple_sum_dirty"] = True

def update_state_mr(state, params):
    id1 = params["id1"]
    id2 = params["id2"]
    m_val = params["m_val"]
    pair = (min(id1, id2), max(id1, id2))
    if id1 in state["persons"] and id2 in state["persons"] and id1 != id2 and pair in state["relations"]:
        old_value = state["relations"][pair]
        new_value = old_value + m_val

        if new_value > 0:
            state["persons"][id1]["acquaintances"][id2] = new_value
            state["persons"][id2]["acquaintances"][id1] = new_value
            state["relations"][pair] = new_value
            state["couple_sum_dirty"] = True

        else:
            if id1 in state["person_tags"] and id2 in state["person_tags"]:
                for tag_id_owned_by_id1 in set(state["person_tags"].get(id1, set())):
                    tag_key = (id1, tag_id_owned_by_id1)
                    if tag_key in state["tag_members"] and id2 in state["tag_members"][tag_key]:
                         del state["tag_members"][tag_key][id2]

                for tag_id_owned_by_id2 in set(state["person_tags"].get(id2, set())):
                     tag_key = (id2, tag_id_owned_by_id2)
                     if tag_key in state["tag_members"] and id1 in state["tag_members"][tag_key]:
                          del state["tag_members"][tag_key][id1]

            if id2 in state["persons"][id1]["acquaintances"]:
                 del state["persons"][id1]["acquaintances"][id2]
            if id1 in state["persons"][id2]["acquaintances"]:
                del state["persons"][id2]["acquaintances"][id1]
            if pair in state["relations"]:
                del state["relations"][pair]

            p1_acquaintances_before = set(state["persons"][id1]["acquaintances"].keys()) | {id2}
            p2_acquaintances_before = set(state["persons"][id2]["acquaintances"].keys()) | {id1}
            common_acquaintances = p1_acquaintances_before.intersection(p2_acquaintances_before)
            common_acquaintances = [pid for pid in common_acquaintances if pid != id1 and pid != id2]
            state["triple_sum"] -= len(common_acquaintances)

            state["couple_sum_dirty"] = True

def update_state_at(state, params):
    person_id = params["person_id"]
    tag_id = params["tag_id"]
    if person_id in state["persons"] and tag_id not in state["person_tags"].get(person_id, set()):
        state["person_tags"].setdefault(person_id, set()).add(tag_id)
        state["tag_members"][(person_id, tag_id)] = {}

def update_state_dt(state, params):
    person_id = params["person_id"]
    tag_id = params["tag_id"]
    if person_id in state["persons"] and tag_id in state["person_tags"].get(person_id, set()):
        state["person_tags"][person_id].remove(tag_id)
        tag_key = (person_id, tag_id)
        if tag_key in state["tag_members"]:
            del state["tag_members"][tag_key]

def update_state_att(state, params):
    id1 = params["id1"]
    id2 = params["id2"]
    tag_id = params["tag_id"]
    tag_key = (id2, tag_id)
    if id1 in state["persons"] and id2 in state["persons"] and id1 != id2 and \
       (min(id1, id2), max(id1, id2)) in state["relations"] and \
       tag_id in state["person_tags"].get(id2, set()):
       if id1 not in state["tag_members"].get(tag_key, {}) and len(state["tag_members"].get(tag_key, {})) < TAG_PERSONS_LIMIT:
            p1_age = state["persons"][id1]["age"]
            state["tag_members"].setdefault(tag_key, {})[id1] = p1_age


def update_state_dft(state, params):
    id1 = params["id1"]
    id2 = params["id2"]
    tag_id = params["tag_id"]
    tag_key = (id2, tag_id)
    if id1 in state["persons"] and id2 in state["persons"] and \
       tag_id in state["person_tags"].get(id2, set()) and \
       id1 in state["tag_members"].get(tag_key, {}):
        del state["tag_members"][tag_key][id1]


def update_state_coa(state, params):
    person_id = params["person_id"]
    account_id = params["account_id"]
    account_name = params["account_name"]
    if person_id in state["persons"] and account_id not in state["accounts"]:
        state["accounts"][account_id] = {
            "owner_id": person_id,
            "name": account_name,
            "followers": {person_id: 0},
            "articles": set(),
        }


def update_state_doa(state, params):
    person_id = params["person_id"]
    account_id = params["account_id"]
    if person_id in state["persons"] and account_id in state["accounts"] and state["accounts"][account_id]["owner_id"] == person_id:
        del state["accounts"][account_id]
        state["couple_sum_dirty"] = True


def update_state_ca(state, params):
    person_id = params["person_id"]
    account_id = params["account_id"]
    article_id = params["article_id"]
    if person_id in state["persons"] and account_id in state["accounts"] and \
       article_id not in state["articles_map"] and \
       person_id in state["accounts"][account_id]["followers"]:

        acc_data = state["accounts"][account_id]
        acc_data["articles"].add(article_id)
        state["articles_map"][article_id] = person_id
        acc_data["followers"][person_id] += 1

        for follower_id in acc_data["followers"].keys():
            if follower_id in state["persons"]:
                 state["persons"][follower_id]["receivedArticles"].insert(0, article_id)
                 if len(state["persons"][follower_id]["receivedArticles"]) > ARTICLE_RECEIVED_LIMIT:
                      state["persons"][follower_id]["receivedArticles"] = state["persons"][follower_id]["receivedArticles"][:ARTICLE_RECEIVED_LIMIT]


def update_state_da(state, params):
    person_id = params["person_id"]
    account_id = params["account_id"]
    article_id = params["article_id"]
    if person_id in state["persons"] and account_id in state["accounts"] and \
       article_id in state["accounts"][account_id]["articles"] and \
       state["accounts"][account_id]["owner_id"] == person_id:

        acc_data = state["accounts"][account_id]
        contributor_id = state["articles_map"].get(article_id)

        acc_data["articles"].remove(article_id)
        if article_id in state["articles_map"]:
            del state["articles_map"][article_id]
        if contributor_id is not None and contributor_id in acc_data["followers"]:
             acc_data["followers"][contributor_id] -= 1
             state["couple_sum_dirty"] = True

        for follower_id in acc_data["followers"].keys():
             if follower_id in state["persons"]:
                 state["persons"][follower_id]["receivedArticles"] = [
                     aid for aid in state["persons"][follower_id]["receivedArticles"] if aid != article_id
                 ]


def update_state_foa(state, params):
    person_id = params["person_id"]
    account_id = params["account_id"]
    if person_id in state["persons"] and account_id in state["accounts"] and \
       person_id not in state["accounts"][account_id]["followers"]:
        state["accounts"][account_id]["followers"][person_id] = 0
        state["couple_sum_dirty"] = True


def update_state_am(state, params):
    _id = params["id"]
    _type = params["type"]
    social_value = params["socialValue"]
    person1_id = params["person1_id"]
    person2_id = params["person2_id"]
    tag_id = params["tag_id"]
    subtype = params["subtype"]
    emoji_id = params.get("emoji_id")
    money = params.get("money")
    article_id = params.get("article_id")

    if _id in state["messages"]: return
    if person1_id not in state["persons"]: return
    if _type == MESSAGE_TYPE_PERSON:
        if person2_id not in state["persons"]: return
        if person1_id == person2_id: return
    else:
        if person1_id not in state["persons"] or tag_id not in state["person_tags"].get(person1_id, set()): return

    if subtype == MESSAGE_SUBTYPE_EMOJI:
        if emoji_id not in state["emojiId2Heat"]: return
    elif subtype == MESSAGE_SUBTYPE_FORWARD:
        if article_id not in state["articles_map"]: return

    message_data = {
        "id": _id,
        "type": _type,
        "socialValue": social_value,
        "person1_id": person1_id,
        "person2_id": person2_id if _type == MESSAGE_TYPE_PERSON else None,
        "tag_id": tag_id if _type == MESSAGE_TYPE_TAG else None,
        "subtype": subtype,
        "emoji_id": emoji_id,
        "money": money,
        "article_id": article_id,
    }
    state["messages"][_id] = message_data

    if subtype == MESSAGE_SUBTYPE_EMOJI:
        state["emojiId2MessageId"].setdefault(emoji_id, []).append(_id)

def update_state_sm(state, params):
    _id = params["id"]
    message = state["messages"].get(_id)

    if message is None: return
    p1_id = message["person1_id"]
    p1 = state["persons"].get(p1_id)
    if p1 is None: return

    if message["type"] == MESSAGE_TYPE_PERSON:
        p2_id = message["person2_id"]
        p2 = state["persons"].get(p2_id)
        if p2 is None: return
        if (min(p1_id, p2_id), max(p1_id, p2_id)) not in state["relations"]: return

        p1["socialValue"] += message["socialValue"]
        p2["socialValue"] += message["socialValue"]

        if message["subtype"] == MESSAGE_SUBTYPE_RED_ENVELOPE:
            p1["money"] -= message["money"]
            p2["money"] += message["money"]

        elif message["subtype"] == MESSAGE_SUBTYPE_FORWARD:
            article_id = message["article_id"]
            p2["receivedArticles"].insert(0, article_id)
            if len(p2["receivedArticles"]) > ARTICLE_RECEIVED_LIMIT:
                 p2["receivedArticles"] = p2["receivedArticles"][:ARTICLE_RECEIVED_LIMIT]

        elif message["subtype"] == MESSAGE_SUBTYPE_EMOJI:
             emoji_id = message["emoji_id"]
             if emoji_id in state["emojiId2Heat"]:
                 state["emojiId2Heat"][emoji_id] += 1

        p2["messages"].insert(0, message)
        if len(p2["messages"]) > MESSAGE_RECEIVED_LIMIT:
             p2["messages"] = p2["messages"][:MESSAGE_RECEIVED_LIMIT]

    else:
        tag_id = message["tag_id"]
        if tag_id not in state["person_tags"].get(p1_id, set()): return

        tag_key = (p1_id, tag_id)
        tag_members_dict = state["tag_members"].get(tag_key)
        if tag_members_dict is None: return

        p1["socialValue"] += message["socialValue"]

        num_members = len(tag_members_dict)
        if num_members > 0:
            if message["subtype"] == MESSAGE_SUBTYPE_RED_ENVELOPE:
                 money_per_person = message["money"] // num_members
                 p1["money"] -= money_per_person * num_members

            if message["subtype"] == MESSAGE_SUBTYPE_FORWARD:
                 article_id = message["article_id"]

            for member_id in tag_members_dict.keys():
                 member_person = state["persons"].get(member_id)
                 if member_person:
                      member_person["socialValue"] += message["socialValue"]
                      if message["subtype"] == MESSAGE_SUBTYPE_RED_ENVELOPE:
                           member_person["money"] += money_per_person
                      elif message["subtype"] == MESSAGE_SUBTYPE_FORWARD:
                           member_person["receivedArticles"].insert(0, article_id)
                           if len(member_person["receivedArticles"]) > ARTICLE_RECEIVED_LIMIT:
                               member_person["receivedArticles"] = member_person["receivedArticles"][:ARTICLE_RECEIVED_LIMIT]

                      member_person["messages"].insert(0, message)
                      if len(member_person["messages"]) > MESSAGE_RECEIVED_LIMIT:
                           member_person["messages"] = member_person["messages"][:MESSAGE_RECEIVED_LIMIT]

        if message["subtype"] == MESSAGE_SUBTYPE_EMOJI:
             emoji_id = message["emoji_id"]
             if emoji_id in state["emojiId2Heat"]:
                 state["emojiId2Heat"][emoji_id] += 1

    del state["messages"][_id]
    if message["subtype"] == MESSAGE_SUBTYPE_EMOJI:
        emoji_id = message["emoji_id"]
        if emoji_id in state["emojiId2MessageId"]:
            try:
                if _id in state["emojiId2MessageId"][emoji_id]:
                    state["emojiId2MessageId"][emoji_id].remove(_id)
                if not state["emojiId2MessageId"][emoji_id]:
                     del state["emojiId2MessageId"][emoji_id]
            except ValueError:
                pass


def update_state_sei(state, params):
    _id = params["id"]
    if _id in state["emojiId2Heat"]: return

    state["emojiId2Heat"][_id] = 0
    state["emojiId2MessageId"][_id] = []

def update_state_dce(state, params):
    limit = params["limit"]

    emoji_ids_to_check = list(state["emojiId2Heat"].keys())
    cold_emoji_ids = [emoji_id for emoji_id in emoji_ids_to_check if state["emojiId2Heat"][emoji_id] < limit]

    messages_to_remove_ids = set()
    for emoji_id in cold_emoji_ids:
        if emoji_id in state["emojiId2MessageId"]:
            messages_to_remove_ids.update(state["emojiId2MessageId"][emoji_id])
            del state["emojiId2MessageId"][emoji_id]

    for msg_id in messages_to_remove_ids:
        if msg_id in state["messages"]:
            del state["messages"][msg_id]

    for emoji_id in cold_emoji_ids:
        del state["emojiId2Heat"][emoji_id]


# Corrected STATE_UPDATE_FUNCTIONS dictionary using full command names as keys
STATE_UPDATE_FUNCTIONS = {
    "add_person": update_state_ap,
    "add_relation": update_state_ar,
    "modify_relation": update_state_mr,
    "add_tag": update_state_at,
    "del_tag": update_state_dt,
    "add_to_tag": update_state_att,
    "del_from_tag": update_state_dft,
    "create_official_account": update_state_coa,
    "delete_official_account": update_state_doa,
    "contribute_article": update_state_ca,
    "delete_article": update_state_da,
    "follow_official_account": update_state_foa,
    "add_message": update_state_am,
    "add_red_envelope_message": update_state_am,
    "add_forward_message": update_state_am,
    "add_emoji_message": update_state_am,
    "send_message": update_state_sm,
    "store_emoji_id": update_state_sei,
    "delete_cold_emoji": update_state_dce,
}


COMMAND_GENERATORS = {
    alias: func
    for alias, func in {
        "ap": generate_ap,
        "ar": generate_ar,
        "mr": generate_mr,
        "at": generate_at,
        "dt": generate_dt,
        "att": generate_att,
        "dft": generate_dft,
        "qv": generate_qv,
        "qci": generate_qci,
        "qts": generate_qts,
        "qtav": generate_qtav,
        "qba": generate_qba,
        "ln": generate_ln,
        "coa": generate_coa,
        "doa": generate_doa,
        "ca": generate_ca,
        "da": generate_da,
        "foa": generate_foa,
        "qsp": generate_qsp,
        "qbc": generate_qbc,
        "qra": generate_qra,
        "qtvs": generate_qtvs,
        "qcs": generate_qcs,
        "am": generate_am,
        "aem": generate_am,
        "arem": generate_am,
        "afm": generate_am,
        "sm": generate_sm,
        "sei": generate_sei,
        "dce": generate_dce,
        "qsv": generate_qsv,
        "qrm": generate_qrm,
        "qp": generate_qp,
        "qm": generate_qm,
    }.items()
}

# Map specific aliases back to the shared generator function
SHARED_GENERATOR_MAP = {
    "aem": "am",
    "arem": "am",
    "afm": "am",
}


# Probability Configuration
COMMAND_WEIGHTS = {
    "ap": 8, "ar": 8, "mr": 9,
    "at": 6, "dt": 4, "att": 8, "dft": 5,
    "coa": 6, "doa": 4, "foa": 7, "ca": 10, "da": 9,
    "sei": 7, "aem": 8, "arem": 8, "afm": 9, "sm": 12, "dce": 6,
    "qv": 5, "qci": 7, "qts": 3, "qba": 7, "qcs": 8, "qsp": 11,
    "qtav": 9, "qtvs": 9,
    "qbc": 6, "qra": 7,
    "qsv": 6, "qrm": 8, "qp": 6, "qm": 6,
}

EXCEPTION_SLOT_PROBABILITY = 0.7

# --- Main Generator Logic ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_data.py <total_instructions>", file=sys.stderr)
        sys.exit(1)

    try:
        total_instructions = int(sys.argv[1])
        if total_instructions < 0:
             print("Error: Total instructions cannot be negative.", file=sys.stderr)
             sys.exit(1)

    except ValueError as e:
        print(f"Error: Invalid number of instructions. {e}", file=sys.stderr)
        sys.exit(1)

    reset_state()

    instructions_count = 0

    if total_instructions > 0:
        cmd_str, params, outcome = generate_ln(network_state, target_key=None)
        if cmd_str is not None:
            print(cmd_str, end="")
            instructions_count += 1
        else:
            print(f"FATAL ERROR: Failed to generate initial ln command.", file=sys.stderr)
            sys.exit(1)

    generator_specific_targets = defaultdict(list)
    for target_key in ALL_TARGET_KEYS:
         cmd_alias, exc_key = target_key
         actual_generator_alias = SHARED_GENERATOR_MAP.get(cmd_alias, cmd_alias)
         generator_specific_targets[actual_generator_alias].append(target_key)

    ungenerated_targets = []
    for targets_list in generator_specific_targets.values():
        ungenerated_targets.extend(targets_list)
    random.shuffle(ungenerated_targets)

    command_choices = []
    for cmd_alias, weight in COMMAND_WEIGHTS.items():
        if weight > 0:
            command_choices.extend([cmd_alias] * weight)

    if not command_choices and instructions_count < total_instructions and not ungenerated_targets:
         print("Error: No commands with positive weight defined for normal generation and all exceptions generated.", file=sys.stderr)
         sys.exit(1)


    while instructions_count < total_instructions:

        generated_for_slot = False
        attempts_for_slot = 0
        max_slot_attempts = len(ALIAS_MAP) * 5 + len(ALL_TARGET_KEYS) * 2

        while not generated_for_slot and attempts_for_slot < max_slot_attempts:
            attempts_for_slot += 1

            cmd_str, params, outcome = None, None, None
            attempt_was_exception = False
            attempt_target_key = None

            if ungenerated_targets and random.random() < EXCEPTION_SLOT_PROBABILITY:
                attempt_was_exception = True
                attempt_target_key = ungenerated_targets[0]
                cmd_alias_for_target, internal_exc_key = attempt_target_key
                actual_generator_alias = SHARED_GENERATOR_MAP.get(cmd_alias_for_target, cmd_alias_for_target)

                cmd_func = COMMAND_GENERATORS.get(actual_generator_alias)
                if cmd_func:
                     cmd_str, params, outcome = cmd_func(network_state, target_key=attempt_target_key)
                     if cmd_str is not None:
                        print(cmd_str)
                        ungenerated_targets.pop(0)
                        generated_for_slot = True
                else:
                     print(f"FATAL ERROR: No generator found for alias {actual_generator_alias} derived from target {attempt_target_key}.", file=sys.stderr)
                     sys.exit(1)

            if not generated_for_slot:
                 if not command_choices:
                      continue

                 cmd_alias = random.choice(command_choices)
                 actual_generator_alias = SHARED_GENERATOR_MAP.get(cmd_alias, cmd_alias)
                 cmd_func = COMMAND_GENERATORS.get(actual_generator_alias)

                 if cmd_func:
                    cmd_str, params, outcome = cmd_func(network_state, target_key=None)
                    if cmd_str is not None:
                        if outcome != OUTCOME_NORMAL:
                            print(f"FATAL ERROR: Generator {actual_generator_alias} returned outcome '{outcome}' when aiming for normal (target_key=None). Generated command was: {cmd_str}", file=sys.stderr)
                            sys.exit(1)

                        print(cmd_str)
                        update_func_alias = cmd_str.split()[0]
                        full_command_name = INSTRUCTION_MAP.get(update_func_alias)
                        update_func = STATE_UPDATE_FUNCTIONS.get(full_command_name)
                        if update_func:
                             update_func(network_state, params)
                        generated_for_slot = True
                 else:
                      print(f"FATAL ERROR: No generator function found for selected normal alias {cmd_alias} (actual generator: {actual_generator_alias}).", file=sys.stderr)
                      sys.exit(1)


        if not generated_for_slot:
             print(f"Warning: Could not generate *any* command (exception or normal) for slot {instructions_count + 1} after {attempts_for_slot} attempts. Network state might be saturated or generators have issues. Ungenerated exceptions left: {len(ungenerated_targets)}.", file=sys.stderr)
             break

        instructions_count += 1

    sys.stdout.flush()