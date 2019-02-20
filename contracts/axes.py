from ontology.interop.System.Runtime import *
from ontology.interop.System.Storage import *
from ontology.interop.System.ExecutionEngine import *
from ontology.builtins import *
from ontology.interop.Ontology.Runtime import *
from ontology.interop.Ontology.Native import *
from ontology.interop.System.Action import *

BuyAxeAction = RegisterAction('buy_axe', 'key', 'sn', 'buyer', 'bid', 'tickets', 'cur_amount')
AwardAction = RegisterAction('award', 'axe_key', 'axe_sn', 'to_addr', 'bonus', 'lucky_number')

GM = Base58ToAddress('AdS9RHQxeReZyiqGanC2NGFDRngRVkJ9qm')

# ONG Big endian Script Hash: 0x0200000000000000000000000000000000000000
OngContract = Base58ToAddress("AFmseVrdL9f9oyCzZefL9tG6UbvhfRZMHJ")

ctx = GetContext()
selfAddr = GetExecutingScriptHash()


def Main(operation, args):
    if operation == 'init':
        return init()
    if operation == 'get_is_initialized':
        return get_is_initialized()
    if operation == 'upsert_axe':
        if len(args) != 3:
            return False
        return upsert_axe(args[0], args[1], args[2])
    if operation == 'query_fee_rate':
        return query_fee_rate()
    if operation == 'set_fee_rate':
        if len(args) != 1:
            return False
        return set_fee_rate(args[0])
    if operation == 'query_axes':
        return query_axes()
    if operation == 'query_axe':
        if len(args) != 1:
            return False
        return query_axe(args[0])
    if operation == 'buy_axe':
        if len(args) != 3:
            return False
        return buy_axe(args[0], args[1], args[2])
    if operation == 'award':
        if len(args) != 1:
            return False
        return award(args[0])
    if operation == 'query_round_records':
        if len(args) != 2:
            return False
        return query_round_records(args[0], args[1])
    if operation == 'query_round_result':
        if len(args) != 2:
            return False
        return query_round_result(args[0], args[1])
    if operation == 'query_buyer_bought':
        if len(args) != 1:
            return False
        return query_buyer_bought(args[0])

    return


def init():
    RequireWitness(GM)

    if not Get(ctx, k_init()):
        keys = ['wooden', 'stone', 'iron', 'gold', 'diamond']
        factor = 100000000  # 0.1
        prices = [2 * factor, 5 * factor, 10 * factor, 10 * factor, 20 * factor]
        counts = [50 * 1, 100 * 1, 150 * 1, 200 * 1, 300 * 1]
        i = 0
        axes = []
        for key in keys:
            axe = {
                'key': key,
                'sn': 1,
                'cur_amount': 0,
                'counter': 0,
                'time_sum': 0,
                'part_price': prices[i],
                'part_count': counts[i],
                'price': Mul(prices[i], counts[i])
            }
            axes.append(axe)
            Put(ctx, k_round_records(key, 1), Serialize([]))
            i = i + 1

        Put(ctx, k_axes(), Serialize(axes))
        Put(ctx, k_fee_rate(), 3)
        Put(ctx, k_init(), True)
        return True

    return False


def get_is_initialized():
    if Get(ctx, k_init()):
        return True
    return False


def upsert_axe(key, part_price, part_count):
    RequireWitness(GM)

    axes = Deserialize(Get(ctx, k_axes()))
    new_axes = []
    new_axe = None
    for axe in axes:
        if axe['key'] == key:
            new_axe = axe
        else:
            new_axes.append(axe)

    price = Mul(part_price, part_count)
    if not new_axe:
        new_axe = {
            'key': key,
            'sn': 1,
            'cur_amount': 0,
            'counter': 0,
            'time_sum': 0
        }

    new_axe['part_price'] = part_price
    new_axe['part_count'] = part_count
    new_axe['price'] = price

    new_axes.append(new_axe)
    Put(ctx, k_axes(), Serialize(new_axes))
    return True


def get_axe(key):
    """

    :param str key:
    :rtype: dict | None
    """
    axes = Deserialize(Get(ctx, k_axes()))
    for axe in axes:
        if axe['key'] == key:
            return axe

    return None


def query_fee_rate():
    return Get(ctx, k_fee_rate())


def set_fee_rate(rate):
    RequireWitness(GM)
    if rate < 3 or rate > 20:
        return False
    Put(ctx, k_fee_rate(), rate)
    return True


def query_axes():
    return Get(ctx, k_axes())


def query_axe(key):
    return Serialize(get_axe(key))


def del_axe(key):
    axes = Deserialize(Get(ctx, k_axes()))
    new_axes = []
    for axe in axes:
        if axe['key'] != key:
            new_axes.append(axe)
    Put(ctx, k_axes(), Serialize(new_axes))


def save_axe(axe):
    del_axe(axe['key'])
    axes = Deserialize(Get(ctx, k_axes()))
    axes.append(axe)
    Put(ctx, k_axes(), Serialize(axes))


def record_buyer_bought(buyer, axe_key, axe_sn):
    records_raw = Get(ctx, k_buyer_bought(buyer))
    if not records_raw:
        records = [{'key': axe_key, 'sn': axe_sn}]
        Put(ctx, k_buyer_bought(buyer), Serialize(records))
        return

    records = Deserialize(records_raw)
    found = False
    for r in records:
        if r['key'] == axe_key and r['sn'] == axe_sn:
            found = True
            break

    if not found:
        records.append({
            'key': axe_key,
            'sn': axe_sn,
        })
        Put(ctx, k_buyer_bought(buyer), Serialize(records))


def buy_axe(key, buyer, bid):
    """

    :param str key:
    :param str buyer:
    :param int bid:
    :return:
    """
    axe = get_axe(key)
    if not axe:
        return False

    # validates and normalizes the bid value
    part_price = axe['part_price']
    if bid < part_price:
        return False

    cur_amount = axe['cur_amount']
    price = axe['price']
    max_bid = Sub(price, cur_amount)
    bid = min(bid, max_bid)

    bid_part_cnt = Div(bid, part_price)
    bid_overflow = Sub(bid, Mul(part_price, bid_part_cnt))
    bid = Sub(bid, bid_overflow)

    # transfers ong
    buyer_addr = Base58ToAddress(buyer)
    param = state(buyer_addr, selfAddr, bid)
    res = Invoke(0, OngContract, "transfer", [param])
    if res != b'\x01':
        raise Exception("unable to refine: transfer ong error.")

    # issues tickets
    counter = axe['counter']
    tickets = []
    sn = axe['sn']
    for _ in range(bid_part_cnt):
        ticket = Add(counter, 1)
        tickets.append(ticket)
        ticket_key = k_round_ticket(key, sn, ticket)
        Put(ctx, ticket_key, buyer_addr)
        counter = ticket

    # records progress
    axe['counter'] = counter
    axe['cur_amount'] = Add(cur_amount, bid)
    axe['time_sum'] = axe['time_sum'] + GetTime()
    save_axe(axe)

    # append a buying record
    records_key = k_round_records(key, sn)
    records = Deserialize(Get(ctx, records_key))
    record = {
        'buyer': buyer,
        'bid': bid,
        'tickets': tickets,
        'time': GetTime()
    }
    records.append(record)
    Put(ctx, records_key, Serialize(records))

    # records buyer bought
    record_buyer_bought(buyer, key, sn)

    # broadcast
    BuyAxeAction(key, sn, buyer, bid, tickets, axe['cur_amount'])

    if axe['cur_amount'] == price:
        award(key)

    return True


def award(axe_key):
    axe = get_axe(axe_key)
    if not axe:
        return False

    price = axe['price']
    cur_amount = axe['cur_amount']

    if cur_amount != price:
        return False

    # computes lucky number
    time_sum = axe['time_sum']
    part_count = axe['part_count']
    quo = time_sum / part_count
    lucky = time_sum - quo * part_count + 1

    # computes bonus and fee
    fee_rate = Get(ctx, k_fee_rate())
    fee = fee_rate * price / 100
    bonus = price - fee

    # sends bonus
    sn = axe['sn']
    ticket_key = k_round_ticket(axe_key, sn, lucky)
    to_acc = Get(ctx, ticket_key)
    param = state(selfAddr, to_acc, bonus)
    res = Invoke(0, OngContract, "transfer", [param])
    if res != b'\x01':
        raise Exception("unable to award user: transfer ont error.")

    # sends fee
    param = state(selfAddr, GM, fee)
    res = Invoke(0, OngContract, "transfer", [param])
    if res != b'\x01':
        raise Exception("unable to fee to GM: transfer ont error.")

    # start a fresh round
    axe['sn'] = Add(sn, 1)
    axe['cur_amount'] = 0
    axe['counter'] = 0
    axe['time_sum'] = 0
    save_axe(axe)

    result = {
        'to_acc': to_acc,
        'bonus': bonus,
        'lucky': lucky
    }
    Put(ctx, k_round_result(axe_key, sn), Serialize(result))

    records_key = k_round_records(axe_key, axe['sn'])
    Put(ctx, records_key, Serialize([]))

    # broadcast
    AwardAction(axe_key, sn, to_acc, bonus, lucky)
    return True


def query_round_records(key, sn):
    return Get(ctx, k_round_records(key, sn))


def query_round_result(key, sn):
    return Get(ctx, k_round_result(key, sn))


def query_buyer_bought(buyer):
    key = k_buyer_bought(buyer)
    raw = Get(ctx, key)
    if raw:
        return raw
    return Serialize([])


def k_init():
    return 'initialized'


def k_axes():
    return 'axes'


def k_fee_rate():
    return 'fee_rate'


def k_round(axe_key, axe_sn):
    return concat('round', concat(axe_key, axe_sn))


def k_round_records(axe_key, axe_sn):
    return concat(k_round(axe_key, axe_sn), 'records')


def k_round_ticket(axe_key, axe_sn, ticket):
    prefix = concat(k_round(axe_key, axe_sn), 'ticket')
    return concat(prefix, ticket)


def k_round_result(axe_key, axe_sn):
    return concat(k_round(axe_key, axe_sn), 'result')


def k_buyer_bought(buyer):
    return concat('buyer_bought', buyer)


# ===================== libs =====================

def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)


def Require(condition):
    """
    If condition is not satisfied, return false
    :param condition: required condition
    :return: True or false
    """
    if not condition:
        Revert()
    return True


def RequireWitness(witness):
    """
    Checks the transaction sender is equal to the witness. If not
    satisfying, revert the transaction.
    :param witness: required transaction sender
    :return: True if transaction sender or revert the transaction.
    """
    Require(CheckWitness(witness))
    return True


def Add(a, b):
    """
    Adds two numbers, throws on overflow.
    """
    c = a + b
    Require(c >= a)
    return c


def Sub(a, b):
    """
    Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    Require(a >= b)
    return a - b


def Mul(a, b):
    """
    Multiplies two numbers, throws on overflow.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    if a == 0:
        return 0
    c = a * b
    Require(c / a == b)
    return c


def Div(a, b):
    """
    Integer division of two numbers, truncating the quotient.
    """
    Require(b > 0)
    c = a / b
    return c
